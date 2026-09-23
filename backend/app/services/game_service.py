"""Game service functions."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.analytics.metrics import effective_field_goal_percentage, true_shooting_percentage
from app.models.game import Game
from app.models.player import Player
from app.models.player_game_stats import PlayerGameStats
from app.models.team import Team
from app.schemas.game import GameDetailRead, GamePlayerStatsRead, GameTeamTotals, ManualGameCreate


class GameAlreadyExistsError(ValueError):
    pass


class InvalidGameRosterError(ValueError):
    pass


def list_team_games(db: Session, team_id: int, owner_id: int) -> list[Game] | None:
    team = db.scalar(select(Team).where(Team.id == team_id, Team.owner_id == owner_id))
    if team is None:
        return None

    return list(
        db.scalars(
            select(Game)
            .where(Game.team_id == team_id)
            .order_by(Game.game_date.desc(), Game.opponent)
        ).all()
    )


def get_game_detail(db: Session, game_id: int, owner_id: int) -> GameDetailRead | None:
    game = db.scalar(
        select(Game)
        .join(Team)
        .options(selectinload(Game.player_stats).selectinload(PlayerGameStats.player))
        .where(Game.id == game_id, Team.owner_id == owner_id)
    )
    if game is None:
        return None

    stats = sorted(game.player_stats, key=lambda stat: (-stat.points, stat.player.name))
    player_stats = [
        GamePlayerStatsRead(
            player_id=stat.player_id,
            player_name=stat.player.name,
            minutes=stat.minutes,
            points=stat.points,
            rebounds=stat.rebounds,
            assists=stat.assists,
            steals=stat.steals,
            blocks=stat.blocks,
            turnovers=stat.turnovers,
            fgm=stat.fgm,
            fga=stat.fga,
            three_pm=stat.three_pm,
            three_pa=stat.three_pa,
            ftm=stat.ftm,
            fta=stat.fta,
            true_shooting_percentage=round(
                true_shooting_percentage(stat.points, stat.fga, stat.fta), 3
            ),
            effective_field_goal_percentage=round(
                effective_field_goal_percentage(stat.fgm, stat.fga, stat.three_pm), 3
            ),
        )
        for stat in stats
    ]

    totals = _sum_game_stats(stats)
    return GameDetailRead(
        id=game.id,
        team_id=game.team_id,
        game_date=game.game_date,
        opponent=game.opponent,
        created_at=game.created_at,
        player_stats=player_stats,
        team_totals=totals,
    )


def create_manual_game(
    db: Session,
    team_id: int,
    payload: ManualGameCreate,
    owner_id: int,
) -> GameDetailRead | None:
    team = db.scalar(select(Team).where(Team.id == team_id, Team.owner_id == owner_id))
    if team is None:
        return None

    opponent = payload.opponent.strip()
    existing_game = db.scalar(
        select(Game).where(
            Game.team_id == team_id,
            Game.game_date == payload.game_date,
            func.lower(Game.opponent) == opponent.casefold(),
        )
    )
    if existing_game is not None:
        raise GameAlreadyExistsError("A game against this opponent already exists on that date")

    player_ids = {stat.player_id for stat in payload.player_stats}
    valid_player_ids = set(
        db.scalars(
            select(Player.id).where(Player.team_id == team_id, Player.id.in_(player_ids))
        ).all()
    )
    if valid_player_ids != player_ids:
        raise InvalidGameRosterError("Every stat line must belong to a player on this team")

    game = Game(team_id=team_id, game_date=payload.game_date, opponent=opponent)
    db.add(game)
    db.flush()
    for stat in payload.player_stats:
        values = stat.model_dump(exclude={"player_id"})
        db.add(PlayerGameStats(game_id=game.id, player_id=stat.player_id, **values))

    db.commit()
    result = get_game_detail(db, game.id, owner_id)
    if result is None:
        raise RuntimeError("Created game could not be loaded")
    return result


def _sum_game_stats(stats: list[PlayerGameStats]) -> GameTeamTotals:
    values = {
        field: sum(getattr(stat, field) for stat in stats)
        for field in (
            "minutes",
            "points",
            "rebounds",
            "assists",
            "steals",
            "blocks",
            "turnovers",
            "fgm",
            "fga",
            "three_pm",
            "three_pa",
            "ftm",
            "fta",
        )
    }
    return GameTeamTotals(
        **values,
        true_shooting_percentage=round(
            true_shooting_percentage(values["points"], values["fga"], values["fta"]), 3
        ),
        effective_field_goal_percentage=round(
            effective_field_goal_percentage(values["fgm"], values["fga"], values["three_pm"]), 3
        ),
    )
