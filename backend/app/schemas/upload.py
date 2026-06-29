"""Upload response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UploadResult(BaseModel):
    team_id: int
    rows_processed: int
    games_created: int
    players_created: int
    stats_created: int
    stats_updated: int


class UploadJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    team_id: int
    owner_id: int
    filename: str
    status: str
    rows_processed: int
    games_created: int
    players_created: int
    stats_created: int
    stats_updated: int
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
