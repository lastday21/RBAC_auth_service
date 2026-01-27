import pytest
from sqlalchemy import create_engine, text

from app.core.settings import get_settings


@pytest.mark.integration
def test_db_connection_select_1():
    settings = get_settings()
    db_url = settings.database_url

    if not db_url:
        pytest.skip("DATABASE_URL is not set")

    engine = create_engine(db_url)

    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar()

    assert result == 1
