from app.db.session import engine
from app.db.base import Base
from app.models.user import User  # noqa: F401
from app.models.revoked_token import RevokedToken  # noqa: F401
from app.models.role import Role  # noqa: F401
from app.models.user_role import UserRole  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
