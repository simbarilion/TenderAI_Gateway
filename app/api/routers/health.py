"""Эндпоинты проверки состояния сервиса."""

import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.db.redis import get_redis_client
from app.db.session import get_session_factory
from app.schemas.health import HealthResponse, ReadyResponse
from app.services.health import HealthService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])
_health = HealthService()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Liveness: приложение запущено."""
    return HealthResponse()


@router.get("/health/ready")
async def ready() -> JSONResponse:
    """Readiness: PostgreSQL и Redis отвечают. Ошибка соединения даёт 503."""
    postgres_ok = False
    redis_ok = False
    try:
        factory = get_session_factory()
        async with factory() as session:
            postgres_ok = await _health.check_postgres(session)
    except Exception as exc:
        logger.exception("Не удалось проверить PostgreSQL %s", exc)
        redis_ok = True
    try:
        redis_ok = await _health.check_redis(get_redis_client())
    except Exception as exc:
        logger.exception("Не удалось проверить Redis %s", exc)

    payload = ReadyResponse(
        status="ok" if postgres_ok and redis_ok else "unavailable",
        postgres="ok" if postgres_ok else "unavailable",
        redis="ok" if redis_ok else "unavailable",
    )
    status_code = 200 if postgres_ok and redis_ok else 503
    return JSONResponse(status_code=status_code, content=payload.model_dump())
