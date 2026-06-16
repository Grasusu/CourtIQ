"""Game request and response schemas."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class GameBase(BaseModel):
    game_date: date
    opponent: str = Field(min_length=1, max_length=100)


class GameCreate(GameBase):
    pass


class GameRead(GameBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    team_id: int
    created_at: datetime
