"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import TokenRead, UserCreate, UserLogin, UserRead
from app.services.auth_service import authenticate_user, register_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenRead, status_code=201)
def register_route(payload: UserCreate, db: Session = Depends(get_db)):
    try:
        return register_user(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/login", response_model=TokenRead)
def login_route(payload: UserLogin, db: Session = Depends(get_db)):
    token = authenticate_user(db, payload)
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return token


@router.get("/me", response_model=UserRead)
def me_route(current_user: User = Depends(get_current_user)):
    return current_user
