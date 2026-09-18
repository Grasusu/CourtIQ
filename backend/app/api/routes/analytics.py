"""Analytics routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.analytics import PlayerAnalyticsRead, PlayerComparisonRead, TeamAnalyticsRead
from app.services.analytics_service import get_player_analytics, get_player_comparison, get_team_analytics


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


@router.get("/teams/{team_id}/player-comparison", response_model=PlayerComparisonRead)
def get_player_comparison_route(
    team_id: int,
    player_ids: Annotated[list[int], Query(min_length=2, max_length=4)],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        comparison = get_player_comparison(db, team_id, player_ids, owner_id=current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if comparison is None:
        raise HTTPException(status_code=404, detail="Team not found")

    return comparison
