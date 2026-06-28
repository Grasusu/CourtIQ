"""Game routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.game import GameRead
from app.services.game_service import list_team_games


router = APIRouter(tags=["games"])


@router.get("/teams/{team_id}/games", response_model=list[GameRead])
def list_team_games_route(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    games = list_team_games(db, team_id, owner_id=current_user.id)
    if games is None:
        raise HTTPException(status_code=404, detail="Team not found")

    return games
