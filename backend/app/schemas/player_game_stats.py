"""Player game stat request and response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PlayerGameStatsBase(BaseModel):
    minutes: float = Field(ge=0)
    points: int = Field(ge=0)
    rebounds: int = Field(ge=0)
    assists: int = Field(ge=0)
    steals: int = Field(ge=0)
    blocks: int = Field(ge=0)
    turnovers: int = Field(ge=0)
    fgm: int = Field(ge=0)
    fga: int = Field(ge=0)
    three_pm: int = Field(ge=0)
    three_pa: int = Field(ge=0)
    ftm: int = Field(ge=0)
    fta: int = Field(ge=0)


class PlayerGameStatsCreate(PlayerGameStatsBase):
    player_id: int
    game_id: int


class PlayerGameStatsRead(PlayerGameStatsBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    player_id: int
    game_id: int
    created_at: datetime
