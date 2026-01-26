from fastapi import APIRouter
from app.core.settings import get_settings

health_router = APIRouter()


@health_router.get("/health")
def health():
    settings = get_settings()
    return {"status": "ok", "env": settings.app_env}
