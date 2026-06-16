"""Analytics response schemas."""

from datetime import date

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
