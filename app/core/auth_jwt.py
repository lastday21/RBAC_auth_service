from typing import NoReturn

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.jwt import decode_access_token
from app.db.session import get_db
from app.models.revoked_token import RevokedToken
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


def raise_not_authenticated() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="not authenticated",
    )


def _get_bearer_token(credentials: HTTPAuthorizationCredentials | None) -> str:
    if credentials is None:
        raise_not_authenticated()

    token = credentials.credentials
    if not token:
        raise_not_authenticated()

    return token


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> User:
    token = _get_bearer_token(credentials)

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
