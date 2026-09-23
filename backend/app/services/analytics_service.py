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
    latest_standard_score,
    percentile_rank,
    points_per_minute,
    recent_form_delta,
    recent_rolling_average,
    true_shooting_percentage,
    weighted_linear_forecast,
)
from app.models.game import Game
from app.models.player import Player
from app.models.player_game_stats import PlayerGameStats
from app.models.team import Team
from app.schemas.analytics import (
    PlayerAnalyticsRead,
    PlayerComparisonRead,
    PlayerForecastRead,
    PlayerGameInsight,
    PlayerImpactProfileRead,
    PlayerIntelligenceRead,
    PlayerSignalRead,
    TeamAnalyticsRead,
    TeamPlayerSummary,
    TeamTrendPoint,
)


def get_player_comparison(
    db: Session,
    team_id: int,
    player_ids: list[int],
    owner_id: int,
) -> PlayerComparisonRead | None:
    team = db.scalar(select(Team).where(Team.id == team_id, Team.owner_id == owner_id))
    if team is None:
        return None

    unique_player_ids = list(dict.fromkeys(player_ids))
    if len(unique_player_ids) != len(player_ids):
        raise ValueError("Select each player only once")

    team_player_ids = set(
        db.scalars(
            select(Player.id).where(
                Player.team_id == team_id,
                Player.id.in_(unique_player_ids),
            )
        ).all()
    )
    if team_player_ids != set(unique_player_ids):
        raise ValueError("Every selected player must belong to this team")

    analytics = [
        get_player_analytics(db, player_id, owner_id=owner_id)
        for player_id in unique_player_ids
    ]

    return PlayerComparisonRead(
        team_id=team.id,
        team_name=team.name,
        players=[player for player in analytics if player is not None],
    )


def get_player_analytics(db: Session, player_id: int, owner_id: int | None = None) -> PlayerAnalyticsRead | None:
    query = select(Player).where(Player.id == player_id)
    if owner_id is not None:
        query = query.join(Team).where(Team.owner_id == owner_id)

    player = db.scalar(query)
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
            intelligence=_build_player_intelligence(db, player, []),
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
        intelligence=_build_player_intelligence(db, player, stats),
    )


def get_team_analytics(db: Session, team_id: int, owner_id: int | None = None) -> TeamAnalyticsRead | None:
    query = select(Team).where(Team.id == team_id)
    if owner_id is not None:
        query = query.where(Team.owner_id == owner_id)

    team = db.scalar(query)
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


def _build_player_intelligence(
    db: Session,
    player: Player,
    stats: list[PlayerGameStats],
) -> PlayerIntelligenceRead:
    points = [float(stat.points) for stat in stats]
    forecast = weighted_linear_forecast(points)
    form_delta = recent_form_delta(points)

    if forecast is None:
        forecast_read = PlayerForecastRead(
            projected_points=None,
            interval_low=None,
            interval_high=None,
            trend_per_game=0.0,
            confidence="insufficient",
            sample_size=len(points),
            model_description="At least three games are required for a forecast.",
        )
    else:
        forecast_read = PlayerForecastRead(
            projected_points=forecast.projected_value,
            interval_low=forecast.interval_low,
            interval_high=forecast.interval_high,
            trend_per_game=forecast.trend_per_game,
            confidence=forecast.confidence,
            sample_size=forecast.sample_size,
            model_description="Recency-weighted linear trend with a residual-error interval.",
        )

    profile = _build_impact_profile(db, player, stats)
    signals = _build_player_signals(points, forecast_read, form_delta)
    return PlayerIntelligenceRead(
        forecast=forecast_read,
        impact_profile=profile,
        recent_form_delta=form_delta,
        recommendation=_build_recommendation(profile, forecast_read),
        signals=signals,
    )


def _build_impact_profile(
    db: Session,
    player: Player,
    player_stats: list[PlayerGameStats],
) -> PlayerImpactProfileRead:
    team_stats = list(
        db.scalars(
            select(PlayerGameStats)
            .join(Player)
            .where(Player.team_id == player.team_id)
        ).all()
    )
    grouped: dict[int, list[PlayerGameStats]] = defaultdict(list)
    for stat in team_stats:
        grouped[stat.player_id].append(stat)

    if not player_stats or not grouped:
        return PlayerImpactProfileRead(
            archetype="Insufficient data",
            scoring=0,
            playmaking=0,
            rebounding=0,
            defense=0,
            efficiency=0,
        )

    features = {player_id: _player_feature_values(stats) for player_id, stats in grouped.items()}
    current = features[player.id]
    profile_values = {
        name: percentile_rank(current[name], [values[name] for values in features.values()])
        for name in current
    }
    archetype = _classify_archetype(profile_values)
    return PlayerImpactProfileRead(archetype=archetype, **profile_values)


def _player_feature_values(stats: list[PlayerGameStats]) -> dict[str, float]:
    minutes = max(sum(stat.minutes for stat in stats), 1.0)
    assists = sum(stat.assists for stat in stats)
    turnovers = sum(stat.turnovers for stat in stats)
    ratio = assist_to_turnover_ratio(assists, turnovers)
    turnover_control = 4.0 if isinf(ratio) else min(ratio, 4.0)
    total_points = sum(stat.points for stat in stats)
    total_fga = sum(stat.fga for stat in stats)
    total_fta = sum(stat.fta for stat in stats)
    return {
        "scoring": total_points / minutes,
        "playmaking": (assists / minutes) * (1 + turnover_control / 4),
        "rebounding": sum(stat.rebounds for stat in stats) / minutes,
        "defense": sum(stat.steals + stat.blocks for stat in stats) / minutes,
        "efficiency": true_shooting_percentage(total_points, total_fga, total_fta),
    }


def _classify_archetype(profile: dict[str, int]) -> str:
    if profile["scoring"] >= 70 and profile["playmaking"] >= 70:
        return "Primary creator"
    if profile["scoring"] >= 70 and profile["defense"] >= 70:
        return "Two-way scorer"
    if profile["scoring"] >= 70 and profile["efficiency"] >= 70:
        return "Efficient scorer"

    strongest = max(profile, key=profile.get)
    return {
        "scoring": "Volume scorer",
        "playmaking": "Floor general",
        "rebounding": "Glass specialist",
        "defense": "Defensive disruptor",
        "efficiency": "Efficiency specialist",
    }[strongest]


def _build_player_signals(
    points: list[float],
    forecast: PlayerForecastRead,
    form_delta: float,
) -> list[PlayerSignalRead]:
    signals: list[PlayerSignalRead] = []
    if forecast.projected_points is not None:
        if forecast.trend_per_game >= 0.75:
            signals.append(PlayerSignalRead(
                level="positive",
                title="Scoring trajectory rising",
                detail=f"The weighted model is adding {forecast.trend_per_game:.1f} points per game.",
            ))
        elif forecast.trend_per_game <= -0.75:
            signals.append(PlayerSignalRead(
                level="watch",
                title="Scoring trajectory cooling",
                detail=f"The weighted model is declining {abs(forecast.trend_per_game):.1f} points per game.",
            ))

    if form_delta >= 2:
        signals.append(PlayerSignalRead(
            level="positive",
            title="Recent form above baseline",
            detail=f"The latest sample is {form_delta:.1f} points above the previous period.",
        ))
    elif form_delta <= -2:
        signals.append(PlayerSignalRead(
            level="watch",
            title="Recent form below baseline",
            detail=f"The latest sample is {abs(form_delta):.1f} points below the previous period.",
        ))

    standard_score = latest_standard_score(points)
    if standard_score is not None and abs(standard_score) >= 1.5:
        direction = "above" if standard_score > 0 else "below"
        signals.append(PlayerSignalRead(
            level="positive" if standard_score > 0 else "watch",
            title="Unusual latest performance",
            detail=f"The latest game was {abs(standard_score):.1f} standard deviations {direction} the prior baseline.",
        ))

    if not signals:
        signals.append(PlayerSignalRead(
            level="neutral",
            title="Stable performance pattern",
            detail="No material scoring shift or unusual latest result was detected.",
        ))
    return signals[:3]


def _build_recommendation(profile: PlayerImpactProfileRead, forecast: PlayerForecastRead) -> str:
    profile_values = {
        "scoring": profile.scoring,
        "playmaking": profile.playmaking,
        "rebounding": profile.rebounding,
        "defense": profile.defense,
        "efficiency": profile.efficiency,
    }
    weakest = min(profile_values, key=profile_values.get)
    recommendations = {
        "scoring": "Create one more high-value scoring action per game through cuts, transition, or paint touches.",
        "playmaking": "Prioritize advantage reads and track potential assists alongside turnovers in the next training block.",
        "rebounding": "Add an explicit box-out and rebound target before increasing offensive volume.",
        "defense": "Track deflections and matchup stops to develop the defensive signal beyond steals and blocks.",
        "efficiency": "Review shot selection by zone and shift attempts toward the player's most efficient locations.",
    }
    recommendation = recommendations[weakest]
    if forecast.trend_per_game <= -0.75:
        recommendation += " Reduce volatility first; the current scoring trend is moving down."
    return recommendation
