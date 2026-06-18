"""Team service functions."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.team import Team
from app.schemas.team import TeamCreate


def create_team(db: Session, payload: TeamCreate) -> Team:
    name = payload.name.strip()
    existing_team = db.scalar(select(Team).where(func.lower(Team.name) == name.casefold()))
    if existing_team is not None:
        raise ValueError("Team name already exists")

    team = Team(name=name, season=payload.season)
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


def get_team(db: Session, team_id: int) -> Team | None:
    return db.get(Team, team_id)


def list_teams(db: Session) -> list[Team]:
    return list(db.scalars(select(Team).order_by(Team.name)).all())
