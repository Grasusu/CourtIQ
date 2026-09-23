"""Player game stat request and response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


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


class ManualPlayerGameStatsCreate(PlayerGameStatsBase):
    player_id: int

    @model_validator(mode="after")
    def validate_shooting_totals(self):
        if self.fgm > self.fga:
            raise ValueError("Field goals made cannot exceed attempts")
        if self.three_pm > self.three_pa:
            raise ValueError("Three-pointers made cannot exceed attempts")
        if self.ftm > self.fta:
            raise ValueError("Free throws made cannot exceed attempts")
        if self.three_pm > self.fgm:
            raise ValueError("Three-pointers made cannot exceed total field goals made")
        if self.three_pa > self.fga:
            raise ValueError("Three-point attempts cannot exceed total field goal attempts")

        expected_points = 2 * (self.fgm - self.three_pm) + 3 * self.three_pm + self.ftm
        if self.points != expected_points:
            raise ValueError(f"Points must equal shooting totals ({expected_points})")
        return self


class PlayerGameStatsRead(PlayerGameStatsBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    player_id: int
    game_id: int
    created_at: datetime
