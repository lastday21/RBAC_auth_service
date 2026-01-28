from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

from app.core.auth_jwt import (
    get_current_user,
    _get_bearer_token,
    raise_not_authenticated,
)
from app.db.session import get_db
from app.models.revoked_token import RevokedToken
from app.models.user import User
from app.core.password import hash_password, verify_password
from app.schemas.auth_schema import RegisterRequest, UserOut
from app.schemas.auth_schema import LoginRequest, TokenResponse
from app.core.jwt import create_access_token, decode_access_token

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


@auth_router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()

    user = db.query(User).filter(User.email == email).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials"
        )
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials"
        )

    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}


@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None),
    user: UserOut = Depends(get_current_user),
):
    token = _get_bearer_token(authorization)

    try:
        payload = decode_access_token(token)
    except Exception:
        raise_not_authenticated()

    jti = payload.get("jti")
    exp = payload.get("exp")
    if not jti or not exp:
        raise_not_authenticated()

    expires_at = datetime.fromtimestamp(int(exp), tz=timezone.utc)

    revoked = RevokedToken(jti=str(jti), user_id=user.id, expire_at=expires_at)
    db.add(revoked)

    try:
        db.flush()
    except IntegrityError:
        db.rollback()

    return None
