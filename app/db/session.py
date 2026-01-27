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


engine: Engine = get_engine()

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
