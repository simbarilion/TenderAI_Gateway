"""Агрегирующий API-роутер приложения."""

from fastapi import APIRouter

from app.api.routers.ai import router as ai_router
from app.api.routers.health import router as health_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(ai_router)
