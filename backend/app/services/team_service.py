"""Team service functions."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.team import Team
from app.schemas.team import TeamCreate


def create_team(db: Session, payload: TeamCreate, owner_id: int) -> Team:
    name = payload.name.strip()
    existing_team = db.scalar(select(Team).where(func.lower(Team.name) == name.casefold()))
    if existing_team is not None:
        raise ValueError("Team name already exists")

    team = Team(name=name, season=payload.season, owner_id=owner_id)
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


def get_team(db: Session, team_id: int, owner_id: int | None = None) -> Team | None:
    query = select(Team).where(Team.id == team_id)
    if owner_id is not None:
        query = query.where(Team.owner_id == owner_id)

    return db.scalar(query)


def list_teams(db: Session, owner_id: int) -> list[Team]:
    return list(
        db.scalars(
            select(Team)
            .where(Team.owner_id == owner_id)
            .order_by(Team.name)
        ).all()
    )
