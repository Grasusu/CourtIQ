"""Demo-data helpers for local development and portfolio walkthroughs."""

from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.player import Player
from app.models.team import Team
from app.schemas.demo import DemoResetResult, DemoSeedResult
from app.services.upload_service import import_box_score_csv


DEMO_TEAM_NAME = "CourtIQ Demo"
DEMO_SEASON = "2025-26"
DEMO_CSV_PATH = Path(__file__).resolve().parents[3] / "sample_data" / "demo_multi_game.csv"


def seed_demo_data(db: Session, reset: bool = False, owner_id: int | None = None) -> DemoSeedResult:
    if reset:
        reset_demo_data(db, owner_id=owner_id)

    query = select(Team).where(func.lower(Team.name) == DEMO_TEAM_NAME.casefold())
    if owner_id is not None:
        query = query.where(Team.owner_id == owner_id)

    team = db.scalar(query)
    if team is None:
        team = Team(name=DEMO_TEAM_NAME, season=DEMO_SEASON, owner_id=owner_id)
        db.add(team)
        db.commit()
        db.refresh(team)

    upload_result = import_box_score_csv(db, team.id, DEMO_CSV_PATH, owner_id=owner_id)
    player_count = db.scalar(select(func.count()).select_from(Player).where(Player.team_id == team.id)) or 0

    return DemoSeedResult(
        team_id=team.id,
        team_name=team.name,
        player_count=player_count,
        upload=upload_result,
    )


def reset_demo_data(db: Session, owner_id: int | None = None) -> DemoResetResult:
    query = select(Team).where(func.lower(Team.name) == DEMO_TEAM_NAME.casefold())
    if owner_id is not None:
        query = query.where(Team.owner_id == owner_id)

    demo_teams = list(db.scalars(query).all())
    for team in demo_teams:
        db.delete(team)

    db.commit()
    return DemoResetResult(deleted_teams=len(demo_teams))
