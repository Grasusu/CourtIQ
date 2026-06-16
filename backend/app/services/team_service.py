"""Team service functions."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.team import Team
from app.schemas.team import TeamCreate


def create_team(db: Session, payload: TeamCreate) -> Team:
    team = Team(name=payload.name.strip(), season=payload.season)
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


def get_team(db: Session, team_id: int) -> Team | None:
    return db.get(Team, team_id)


def list_teams(db: Session) -> list[Team]:
    return list(db.scalars(select(Team).order_by(Team.name)).all())
