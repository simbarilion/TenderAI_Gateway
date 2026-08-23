"""Проверки готовности PostgreSQL и Redis."""

import logging

from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class HealthService:
    """Отвечает, доступна ли инфраструктура PostgreSQL."""

    async def check_postgres(self, session: AsyncSession) -> bool:
        """Выполняет `SELECT 1`. Любая ошибка считается недоступностью."""
        try:
            await session.execute(text("SELECT 1"))
        except Exception as exc:
            logger.exception("PostgreSQL недоступен %s", exc)
            return False
        return True

    async def check_redis(self, redis: Redis) -> bool:
        """Проверяет, доступен ли Redis: выполняет PING. Любая ошибка считается недоступностью."""
        try:
            await redis.ping()
        except Exception as exc:
            logger.exception("Redis недоступен %s", exc)
            return False
        return True
