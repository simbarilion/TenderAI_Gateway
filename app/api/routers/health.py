"""Эндпоинты проверки состояния сервиса."""

import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.openapi import HEALTH_RESPONSES, READY_RESPONSES
from app.db.redis import get_redis_client
from app.db.session import get_session_factory
from app.schemas.health import HealthResponse, ReadyResponse
from app.services.health import HealthService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])
_health = HealthService()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Liveness-проверка",
    description=(
        "Показывает, что процесс FastAPI запущен и отвечает на HTTP.\n\n"
        "Эндпоинт не требует API-ключа. "
        "**Что вернётся**\n"
        '- `200` и `{"status": "ok"}` — процесс жив'
    ),
    responses=HEALTH_RESPONSES,
)
async def health() -> HealthResponse:
    """Liveness: приложение запущено."""
    return HealthResponse()


@router.get(
    "/health/ready",
    response_model=ReadyResponse,
    summary="Readiness-проверка",
    description=(
        "Проверяет PostgreSQL (`SELECT 1`) и Redis (`PING`).\n\n"
        "Эндпоинт не требует API-ключа. "
        "Ошибка соединения не превращается в 500: клиент получает 503 и видит, "
        "какая зависимость недоступна.\n\n"
        "**Что вернётся**\n"
        "- `200` — обе зависимости `ok`, можно вызывать generate\n"
        "- `503` — `status=unavailable`, в полях `postgres` и `redis` указано `ok` или `unavailable`"
    ),
    responses=READY_RESPONSES,
)
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
