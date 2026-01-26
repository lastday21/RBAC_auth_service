from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = Field(default="test", alias="APP_ENV")

    database_url: str | None = Field(default=None, alias="DATABASE_URL")

    jwt_secret: str = Field(default="something_token", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_ttl_minutes: int = Field(default=30, alias="JWT_ACCESS_TTL_MINUTES")


@lru_cache
def get_settings() -> Settings:
    return Settings()
