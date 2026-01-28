from typing import NoReturn

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.jwt import decode_access_token
from app.db.session import get_db
from app.models.revoked_token import RevokedToken
from app.models.user import User


def raise_not_authenticated() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="not authenticated",
    )


def _get_bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise_not_authenticated()

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise_not_authenticated()

    return parts[1]


def get_current_user(
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None),
) -> User:
    token = _get_bearer_token(authorization)

    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub", ""))
        jti = payload.get("jti")
    except Exception:
        raise_not_authenticated()

    if not jti:
        raise_not_authenticated()

    revoked = db.query(RevokedToken).filter(RevokedToken.jti == str(jti)).first()
    if revoked:
        raise_not_authenticated()

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise_not_authenticated()

    return user
