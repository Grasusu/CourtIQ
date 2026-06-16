"""Team request and response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TeamBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    season: str | None = Field(default=None, max_length=20)


class TeamCreate(TeamBase):
    pass


class TeamRead(TeamBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
