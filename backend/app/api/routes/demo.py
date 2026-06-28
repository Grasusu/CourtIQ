"""Demo-data routes for local MVP walkthroughs."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_optional_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.demo import DemoResetResult, DemoSeedResult
from app.services.demo_service import reset_demo_data, seed_demo_data


router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/seed", response_model=DemoSeedResult, status_code=201)
def seed_demo_data_route(
    reset: bool = False,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    return seed_demo_data(db, reset=reset, owner_id=current_user.id if current_user else None)


@router.delete("/reset", response_model=DemoResetResult)
def reset_demo_data_route(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    return reset_demo_data(db, owner_id=current_user.id if current_user else None)
