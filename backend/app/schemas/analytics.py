"""Analytics response schemas."""

from datetime import date
from typing import Literal

from pydantic import BaseModel


class PlayerGameInsight(BaseModel):
    game_id: int
    game_date: date
    opponent: str
    points: int
    rebounds: int
    assists: int
    minutes: float
    true_shooting_percentage: float
    effective_field_goal_percentage: float


class PlayerForecastRead(BaseModel):
    projected_points: float | None
    interval_low: float | None
    interval_high: float | None
    trend_per_game: float
    confidence: Literal["insufficient", "low", "medium", "high"]
    sample_size: int
    model_description: str


class PlayerImpactProfileRead(BaseModel):
    archetype: str
    scoring: int
    playmaking: int
    rebounding: int
    defense: int
    efficiency: int


class PlayerSignalRead(BaseModel):
    level: Literal["positive", "neutral", "watch"]
    title: str
    detail: str


class PlayerIntelligenceRead(BaseModel):
    forecast: PlayerForecastRead
    impact_profile: PlayerImpactProfileRead
    recent_form_delta: float
    recommendation: str
    signals: list[PlayerSignalRead]


class PlayerAnalyticsRead(BaseModel):
    player_id: int
    player_name: str
    games_played: int
    average_minutes: float
    average_points: float
    average_rebounds: float
    average_assists: float
    points_per_minute: float
    assist_to_turnover_ratio: float | str
    true_shooting_percentage: float
    effective_field_goal_percentage: float
    consistency_score: float
    last_five_points: list[float | None]
    best_game: PlayerGameInsight | None
    worst_game: PlayerGameInsight | None
    summary: str
    intelligence: PlayerIntelligenceRead


class TeamPlayerSummary(BaseModel):
    player_id: int
    player_name: str
    games_played: int
    average_points: float
    average_rebounds: float
    average_assists: float
    true_shooting_percentage: float
    effective_field_goal_percentage: float


class TeamTrendPoint(BaseModel):
    game_id: int
    game_date: date
    opponent: str
    points: int
    rebounds: int
    assists: int
    turnovers: int


class TeamAnalyticsRead(BaseModel):
    team_id: int
    team_name: str
    roster_size: int
    games_played: int
    average_team_points: float
    average_team_rebounds: float
    average_team_assists: float
    average_team_turnovers: float
    true_shooting_percentage: float
    effective_field_goal_percentage: float
    top_scorers: list[TeamPlayerSummary]
    game_trends: list[TeamTrendPoint]
    summary: str


class PlayerComparisonRead(BaseModel):
    team_id: int
    team_name: str
    players: list[PlayerAnalyticsRead]
