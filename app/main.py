"""Точка входа FastAPI-приложения TenderAI Gateway.

Модуль собирает приложение: настройки, логирование, lifespan, middleware и обработчики доменных ошибок.
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import Settings, get_settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import RequestIdMiddleware
from app.db.session import dispose_db, init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Открывает и закрывает жизненный цикл процесса."""
    settings: Settings = app.state.settings
    init_db(settings.resolve_database_url(), echo=settings.debug)
    logger.info("Запуск %s", settings.app_name)
    try:
        yield
    finally:
        await dispose_db()
        logger.info("Остановка %s", settings.app_name)


def create_app() -> FastAPI:
    """Собирает приложение: логи, middleware, handlers, lifespan."""
    settings = get_settings()
    setup_logging(settings.log_level)

    application = FastAPI(
        title=settings.app_name,
        description=("API Gateway тендерной IT-площадки: проверка ключа, лимит запросов и проксирование к Grok."),
        lifespan=lifespan,
        debug=settings.debug,
    )
    application.state.settings = settings
    application.add_middleware(RequestIdMiddleware)
    register_exception_handlers(application)
    return application


app = create_app()
