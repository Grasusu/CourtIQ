"""Authentication service functions."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import TokenRead, UserCreate, UserLogin


def register_user(db: Session, payload: UserCreate) -> TokenRead:
    email = payload.email.lower()
    existing_user = db.scalar(select(User).where(func.lower(User.email) == email))
    if existing_user is not None:
        raise ValueError("Email is already registered")

    user = User(email=email, password_hash=hash_password(payload.password), role="coach")
    db.add(user)
    db.commit()
    db.refresh(user)

    return TokenRead(access_token=create_access_token(str(user.id)), user=user)


def authenticate_user(db: Session, payload: UserLogin) -> TokenRead | None:
    user = db.scalar(select(User).where(func.lower(User.email) == payload.email.lower()))
    if user is None or not verify_password(payload.password, user.password_hash):
        return None

    return TokenRead(access_token=create_access_token(str(user.id)), user=user)
