"""Demo-data routes for local MVP walkthroughs."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.demo import DemoResetResult, DemoSeedResult
from app.services.demo_service import reset_demo_data, seed_demo_data


router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/seed", response_model=DemoSeedResult, status_code=201)
def seed_demo_data_route(reset: bool = False, db: Session = Depends(get_db)):
    return seed_demo_data(db, reset=reset)


@router.delete("/reset", response_model=DemoResetResult)
def reset_demo_data_route(db: Session = Depends(get_db)):
    return reset_demo_data(db)
