"""Team routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.team import TeamCreate, TeamRead
from app.services.team_service import create_team, list_teams


router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("", response_model=TeamRead, status_code=201)
def create_team_route(
    payload: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return create_team(db, payload, owner_id=current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("", response_model=list[TeamRead])
def list_teams_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_teams(db, owner_id=current_user.id)
