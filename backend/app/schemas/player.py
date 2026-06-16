"""Player request and response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PlayerBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    position: str | None = Field(default=None, max_length=20)
    jersey_number: int | None = Field(default=None, ge=0, le=99)


class PlayerCreate(PlayerBase):
    pass


class PlayerRead(PlayerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    team_id: int
    created_at: datetime
