from fastapi import FastAPI
from app.core.settings import get_settings

from app.api.health import health_router

app = FastAPI()

settings = get_settings()

app.include_router(health_router)
