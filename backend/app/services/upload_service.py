"""CSV import service for box-score uploads."""

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics.validators import BoxScoreRow, parse_box_score_csv
from app.models.game import Game
from app.models.player import Player
from app.models.player_game_stats import PlayerGameStats
from app.models.team import Team
from app.schemas.upload import UploadResult


def import_box_score_csv(
    db: Session,
    team_id: int,
    file_path: str | Path,
    owner_id: int | None = None,
) -> UploadResult:
    query = select(Team).where(Team.id == team_id)
    if owner_id is not None:
        query = query.where(Team.owner_id == owner_id)

    team = db.scalar(query)
    if team is None:
        raise ValueError(f"Team {team_id} does not exist")

    rows = parse_box_score_csv(file_path)

    players = {
        player.name.casefold(): player
        for player in db.scalars(select(Player).where(Player.team_id == team_id)).all()
    }
    games = {
        (game.game_date, game.opponent.casefold()): game
        for game in db.scalars(select(Game).where(Game.team_id == team_id)).all()
    }

    games_created = 0
    players_created = 0
    stats_created = 0
    stats_updated = 0

    for row in rows:
        player = players.get(row.player.casefold())
        if player is None:
            player = Player(team_id=team_id, name=row.player)
            db.add(player)
            db.flush()
            players[row.player.casefold()] = player
            players_created += 1

        game_key = (row.game_date, row.opponent.casefold())
        game = games.get(game_key)
        if game is None:
            game = Game(team_id=team_id, game_date=row.game_date, opponent=row.opponent)
            db.add(game)
            db.flush()
            games[game_key] = game
            games_created += 1

        existing_stats = db.scalar(
            select(PlayerGameStats).where(
                PlayerGameStats.player_id == player.id,
                PlayerGameStats.game_id == game.id,
            )
        )

        values = _stats_values(row)
        if existing_stats is None:
            db.add(PlayerGameStats(player_id=player.id, game_id=game.id, **values))
            stats_created += 1
        else:
            for field, value in values.items():
                setattr(existing_stats, field, value)
            stats_updated += 1

    db.commit()

    return UploadResult(
        team_id=team_id,
        rows_processed=len(rows),
        games_created=games_created,
        players_created=players_created,
        stats_created=stats_created,
        stats_updated=stats_updated,
    )


def _stats_values(row: BoxScoreRow) -> dict[str, float | int]:
    return {
        "minutes": row.minutes,
        "points": row.points,
        "rebounds": row.rebounds,
        "assists": row.assists,
        "steals": row.steals,
        "blocks": row.blocks,
        "turnovers": row.turnovers,
        "fgm": row.fgm,
        "fga": row.fga,
        "three_pm": row.three_pm,
        "three_pa": row.three_pa,
        "ftm": row.ftm,
        "fta": row.fta,
    }
