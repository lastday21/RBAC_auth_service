from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.settings import get_settings


def get_engine() -> Engine:
    settings = get_settings()

    db_url = getattr(settings, "database_url", None)
    if not db_url:
        raise RuntimeError("database_url is not set in settings")

    return create_engine(db_url)


SessionLocal = sessionmaker(expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    with SessionLocal(bind=get_engine()) as db:
        yield db
