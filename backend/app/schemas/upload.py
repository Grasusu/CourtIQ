"""Upload response schemas."""

from pydantic import BaseModel


class UploadResult(BaseModel):
    team_id: int
    rows_processed: int
    games_created: int
    players_created: int
    stats_created: int
    stats_updated: int
