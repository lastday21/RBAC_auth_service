from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI

from app.api.health import health_router
from app.core.settings import get_settings
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_settings()
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(health_router)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
