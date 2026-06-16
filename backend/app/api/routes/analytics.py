"""Analytics routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.analytics import PlayerAnalyticsRead
from app.services.analytics_service import get_player_analytics


router = APIRouter(tags=["analytics"])


@router.get("/players/{player_id}/analytics", response_model=PlayerAnalyticsRead)
def get_player_analytics_route(player_id: int, db: Session = Depends(get_db)):
    analytics = get_player_analytics(db, player_id)
    if analytics is None:
        raise HTTPException(status_code=404, detail="Player not found")

    return analytics
