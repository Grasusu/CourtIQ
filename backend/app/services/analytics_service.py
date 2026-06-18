"""Analytics service functions."""

from collections import defaultdict
from math import isinf
from statistics import mean

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics.metrics import (
    assist_to_turnover_ratio,
    consistency_score,
    effective_field_goal_percentage,
    points_per_minute,
    recent_rolling_average,
    true_shooting_percentage,
)
from app.models.game import Game
from app.models.player import Player
from app.models.player_game_stats import PlayerGameStats
from app.models.team import Team
from app.schemas.analytics import (
    PlayerAnalyticsRead,
    PlayerGameInsight,
    TeamAnalyticsRead,
    TeamPlayerSummary,
    TeamTrendPoint,
)


def get_player_analytics(db: Session, player_id: int) -> PlayerAnalyticsRead | None:
    player = db.get(Player, player_id)
    if player is None:
        return None

    stats = list(
        db.scalars(
            select(PlayerGameStats)
            .join(Game)
            .where(PlayerGameStats.player_id == player_id)
            .order_by(Game.game_date)
        ).all()
    )

    if not stats:
        return PlayerAnalyticsRead(
            player_id=player.id,
            player_name=player.name,
            games_played=0,
            average_minutes=0.0,
            average_points=0.0,
            average_rebounds=0.0,
            average_assists=0.0,
            points_per_minute=0.0,
            assist_to_turnover_ratio=0.0,
            true_shooting_percentage=0.0,
            effective_field_goal_percentage=0.0,
            consistency_score=0.0,
            last_five_points=[],
            best_game=None,
            worst_game=None,
            summary=f"{player.name} has no recorded games yet.",
        )

    points = [stat.points for stat in stats]
    total_minutes = sum(stat.minutes for stat in stats)
    total_points = sum(stat.points for stat in stats)
    total_rebounds = sum(stat.rebounds for stat in stats)
    total_assists = sum(stat.assists for stat in stats)
    total_turnovers = sum(stat.turnovers for stat in stats)
    total_fgm = sum(stat.fgm for stat in stats)
    total_fga = sum(stat.fga for stat in stats)
    total_three_pm = sum(stat.three_pm for stat in stats)
    total_fta = sum(stat.fta for stat in stats)

    ratio = assist_to_turnover_ratio(total_assists, total_turnovers)
    ratio_value: float | str = "inf" if isinf(ratio) else round(ratio, 3)

    best_stat = max(stats, key=lambda stat: stat.points)
    worst_stat = min(stats, key=lambda stat: stat.points)

    return PlayerAnalyticsRead(
        player_id=player.id,
        player_name=player.name,
        games_played=len(stats),
        average_minutes=round(mean([stat.minutes for stat in stats]), 2),
        average_points=round(total_points / len(stats), 2),
        average_rebounds=round(total_rebounds / len(stats), 2),
        average_assists=round(total_assists / len(stats), 2),
        points_per_minute=round(points_per_minute(total_points, total_minutes), 3),
        assist_to_turnover_ratio=ratio_value,
        true_shooting_percentage=round(true_shooting_percentage(total_points, total_fga, total_fta), 3),
        effective_field_goal_percentage=round(
            effective_field_goal_percentage(total_fgm, total_fga, total_three_pm),
            3,
        ),
        consistency_score=round(consistency_score(points), 3),
        last_five_points=recent_rolling_average([float(point) for point in points], min(5, len(points))),
        best_game=_to_game_insight(best_stat),
        worst_game=_to_game_insight(worst_stat),
        summary=_build_player_summary(player.name, stats),
    )


def get_team_analytics(db: Session, team_id: int) -> TeamAnalyticsRead | None:
    team = db.get(Team, team_id)
    if team is None:
        return None

    players = list(db.scalars(select(Player).where(Player.team_id == team_id)).all())
    stats = list(
        db.scalars(
            select(PlayerGameStats)
            .join(Game)
            .where(Game.team_id == team_id)
            .order_by(Game.game_date, Game.opponent)
        ).all()
    )

    if not stats:
        return TeamAnalyticsRead(
            team_id=team.id,
            team_name=team.name,
            roster_size=len(players),
            games_played=0,
            average_team_points=0.0,
            average_team_rebounds=0.0,
            average_team_assists=0.0,
            average_team_turnovers=0.0,
            true_shooting_percentage=0.0,
            effective_field_goal_percentage=0.0,
            top_scorers=[],
            game_trends=[],
            summary=f"{team.name} has no recorded games yet.",
        )

    game_trends = _build_team_game_trends(stats)
    top_scorers = _build_team_player_summaries(stats)
    total_points = sum(stat.points for stat in stats)
    total_rebounds = sum(stat.rebounds for stat in stats)
    total_assists = sum(stat.assists for stat in stats)
    total_turnovers = sum(stat.turnovers for stat in stats)
    total_fgm = sum(stat.fgm for stat in stats)
    total_fga = sum(stat.fga for stat in stats)
    total_three_pm = sum(stat.three_pm for stat in stats)
    total_fta = sum(stat.fta for stat in stats)
    games_played = len(game_trends)

    return TeamAnalyticsRead(
        team_id=team.id,
        team_name=team.name,
        roster_size=len(players),
        games_played=games_played,
        average_team_points=round(total_points / games_played, 2),
        average_team_rebounds=round(total_rebounds / games_played, 2),
        average_team_assists=round(total_assists / games_played, 2),
        average_team_turnovers=round(total_turnovers / games_played, 2),
        true_shooting_percentage=round(true_shooting_percentage(total_points, total_fga, total_fta), 3),
        effective_field_goal_percentage=round(
            effective_field_goal_percentage(total_fgm, total_fga, total_three_pm),
            3,
        ),
        top_scorers=top_scorers[:5],
        game_trends=game_trends,
        summary=_build_team_summary(team.name, game_trends, top_scorers),
    )


def _to_game_insight(stat: PlayerGameStats) -> PlayerGameInsight:
    return PlayerGameInsight(
        game_id=stat.game.id,
        game_date=stat.game.game_date,
        opponent=stat.game.opponent,
        points=stat.points,
        rebounds=stat.rebounds,
        assists=stat.assists,
        minutes=stat.minutes,
        true_shooting_percentage=round(true_shooting_percentage(stat.points, stat.fga, stat.fta), 3),
        effective_field_goal_percentage=round(
            effective_field_goal_percentage(stat.fgm, stat.fga, stat.three_pm),
            3,
        ),
    )


def _build_player_summary(player_name: str, stats: list[PlayerGameStats]) -> str:
    season_ppg = mean([stat.points for stat in stats])
    recent_stats = stats[-5:]
    recent_ppg = mean([stat.points for stat in recent_stats])

    if recent_ppg > season_ppg + 2:
        trend = "trending above"
    elif recent_ppg < season_ppg - 2:
        trend = "trending below"
    else:
        trend = "close to"

    return (
        f"{player_name} is averaging {recent_ppg:.1f} points over the recent sample, "
        f"{trend} the season average of {season_ppg:.1f}."
    )


def _build_team_game_trends(stats: list[PlayerGameStats]) -> list[TeamTrendPoint]:
    grouped: dict[int, list[PlayerGameStats]] = defaultdict(list)
    for stat in stats:
        grouped[stat.game_id].append(stat)

    trend_points: list[TeamTrendPoint] = []
    for game_stats in grouped.values():
        game = game_stats[0].game
        trend_points.append(
            TeamTrendPoint(
                game_id=game.id,
                game_date=game.game_date,
                opponent=game.opponent,
                points=sum(stat.points for stat in game_stats),
                rebounds=sum(stat.rebounds for stat in game_stats),
                assists=sum(stat.assists for stat in game_stats),
                turnovers=sum(stat.turnovers for stat in game_stats),
            )
        )

    return sorted(trend_points, key=lambda trend: trend.game_date)


def _build_team_player_summaries(stats: list[PlayerGameStats]) -> list[TeamPlayerSummary]:
    grouped: dict[int, list[PlayerGameStats]] = defaultdict(list)
    for stat in stats:
        grouped[stat.player_id].append(stat)

    summaries: list[TeamPlayerSummary] = []
    for player_stats in grouped.values():
        player = player_stats[0].player
        total_points = sum(stat.points for stat in player_stats)
        total_rebounds = sum(stat.rebounds for stat in player_stats)
        total_assists = sum(stat.assists for stat in player_stats)
        total_fgm = sum(stat.fgm for stat in player_stats)
        total_fga = sum(stat.fga for stat in player_stats)
        total_three_pm = sum(stat.three_pm for stat in player_stats)
        total_fta = sum(stat.fta for stat in player_stats)
        games_played = len(player_stats)

        summaries.append(
            TeamPlayerSummary(
                player_id=player.id,
                player_name=player.name,
                games_played=games_played,
                average_points=round(total_points / games_played, 2),
                average_rebounds=round(total_rebounds / games_played, 2),
                average_assists=round(total_assists / games_played, 2),
                true_shooting_percentage=round(true_shooting_percentage(total_points, total_fga, total_fta), 3),
                effective_field_goal_percentage=round(
                    effective_field_goal_percentage(total_fgm, total_fga, total_three_pm),
                    3,
                ),
            )
        )

    return sorted(summaries, key=lambda summary: summary.average_points, reverse=True)


def _build_team_summary(
    team_name: str,
    game_trends: list[TeamTrendPoint],
    top_scorers: list[TeamPlayerSummary],
) -> str:
    if not game_trends:
        return f"{team_name} has no recorded games yet."

    scoring_average = mean([trend.points for trend in game_trends])
    leader = top_scorers[0].player_name if top_scorers else "No player"

    return (
        f"{team_name} recorded {len(game_trends)} games with an average of "
        f"{scoring_average:.1f} team points. {leader} leads the current sample in scoring."
    )
