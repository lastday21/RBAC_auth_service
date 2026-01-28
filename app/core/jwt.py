import uuid
from datetime import datetime, timezone, timedelta

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
        "type": "acces",
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm="HS256")

    return token
