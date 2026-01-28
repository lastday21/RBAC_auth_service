from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.models.user import User
from app.core.password import hash_password
from app.schemas.auth_schema import RegisterRequest, UserOut

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post(
    "/register", response_model=UserOut, status_code=status.HTTP_201_CREATED
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    if payload.password != payload.password_confirm:
        raise HTTPException(status_code=400, detail="passwords do not match")

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=409, detail="email already registered")

    user = User(
        email=email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        is_active=True,
    )

    db.add(user)

    try:
        db.flush()
    except IntegrityError:
        raise HTTPException(status_code=409, detail="email already registered")

    return user
