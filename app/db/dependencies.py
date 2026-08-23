"""Зависимости FastAPI для PostgreSQL и Redis."""

from collections.abc import AsyncIterator

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.redis import get_redis_client
from app.db.session import get_session_factory


async def get_session() -> AsyncIterator[AsyncSession]:
    """Отдаёт AsyncSession на один запрос и закрывает её после ответа."""
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session


def get_redis() -> Redis:
    """Отдаёт клиент Redis, созданный в lifespan."""
    return get_redis_client()
