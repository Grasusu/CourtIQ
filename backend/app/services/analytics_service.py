"""Analytics service functions."""

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
from app.schemas.analytics import PlayerAnalyticsRead, PlayerGameInsight


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
        summary=_build_summary(player.name, stats),
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


def _build_summary(player_name: str, stats: list[PlayerGameStats]) -> str:
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
