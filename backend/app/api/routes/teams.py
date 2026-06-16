"""Team routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.team import TeamCreate, TeamRead
from app.services.team_service import create_team, list_teams


router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("", response_model=TeamRead, status_code=201)
def create_team_route(payload: TeamCreate, db: Session = Depends(get_db)):
    return create_team(db, payload)


@router.get("", response_model=list[TeamRead])
def list_teams_route(db: Session = Depends(get_db)):
    return list_teams(db)
