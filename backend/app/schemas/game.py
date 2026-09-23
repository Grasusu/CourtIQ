"""Game request and response schemas."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.player_game_stats import ManualPlayerGameStatsCreate


class GameBase(BaseModel):
    game_date: date
    opponent: str = Field(min_length=1, max_length=100)


class GameCreate(GameBase):
    pass


class ManualGameCreate(GameBase):
    player_stats: list[ManualPlayerGameStatsCreate] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_players(self):
        player_ids = [stat.player_id for stat in self.player_stats]
        if len(player_ids) != len(set(player_ids)):
            raise ValueError("Each player can appear only once per game")
        return self


class GameRead(GameBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    team_id: int
    created_at: datetime


class GamePlayerStatsRead(BaseModel):
    player_id: int
    player_name: str
    minutes: float
    points: int
    rebounds: int
    assists: int
    steals: int
    blocks: int
    turnovers: int
    fgm: int
    fga: int
    three_pm: int
    three_pa: int
    ftm: int
    fta: int
    true_shooting_percentage: float
    effective_field_goal_percentage: float


class GameTeamTotals(BaseModel):
    minutes: float
    points: int
    rebounds: int
    assists: int
    steals: int
    blocks: int
    turnovers: int
    fgm: int
    fga: int
    three_pm: int
    three_pa: int
    ftm: int
    fta: int
    true_shooting_percentage: float
    effective_field_goal_percentage: float


class GameDetailRead(GameRead):
    player_stats: list[GamePlayerStatsRead]
    team_totals: GameTeamTotals
