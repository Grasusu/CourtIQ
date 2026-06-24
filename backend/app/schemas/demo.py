"""Demo-data response schemas."""

from app.schemas.upload import UploadResult

from pydantic import BaseModel


class DemoSeedResult(BaseModel):
    team_id: int
    team_name: str
    player_count: int
    upload: UploadResult


class DemoResetResult(BaseModel):
    deleted_teams: int
