"""Analytics routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.analytics import PlayerAnalyticsRead, TeamAnalyticsRead
from app.services.analytics_service import get_player_analytics, get_team_analytics


router = APIRouter(tags=["analytics"])


@router.get("/players/{player_id}/analytics", response_model=PlayerAnalyticsRead)
def get_player_analytics_route(
    player_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analytics = get_player_analytics(db, player_id, owner_id=current_user.id)
    if analytics is None:
        raise HTTPException(status_code=404, detail="Player not found")

    return analytics


@router.get("/teams/{team_id}/analytics", response_model=TeamAnalyticsRead)
def get_team_analytics_route(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analytics = get_team_analytics(db, team_id, owner_id=current_user.id)
    if analytics is None:
        raise HTTPException(status_code=404, detail="Team not found")

    return analytics
