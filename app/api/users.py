from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth_jwt import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth_schema import UpdateProfileRequest, UserOut

users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.get("/me", response_model=UserOut)
def read_me(user: User = Depends(get_current_user)):
    return user


@users_router.patch("/me", response_model=UserOut)
def update_me(
    payload: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.full_name is not None:
        current_user.full_name = payload.full_name

    if payload.email is not None:
        email = payload.email.strip().lower()
        if not email:
            raise HTTPException(status_code=400, detail="email must not be empty")
        current_user.email = email

    db.add(current_user)
    try:
        db.flush()
    except IntegrityError:
        raise HTTPException(status_code=409, detail="email already registered")

    return current_user


@users_router.delete("/me", response_model=UserOut)
def delete_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.is_active = False

    db.add(current_user)
    db.flush()

    return current_user
