import uuid
from datetime import datetime, timezone, timedelta
from typing import Any

import jwt


from app.core.settings import get_settings


def create_access_token(user_id: int) -> str:
    settings = get_settings()

    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=settings.jwt_access_ttl_minutes)

    payload = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "jti": str(uuid.uuid4()),
        "type": "access",
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm="HS256")

    return token


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"],
            options={"require": ["sub", "exp"]},
        )
        return payload
    except jwt.ExpiredSignatureError as e:
        raise ValueError("token expired") from e
    except jwt.InvalidTokenError as e:
        raise ValueError("Invalid token") from e
