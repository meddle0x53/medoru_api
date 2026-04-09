from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.kanji import router as kanji_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(kanji_router, prefix="/api/v1")
