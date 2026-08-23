"""Зависимости FastAPI для слоя базы данных."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session_factory


async def get_session() -> AsyncIterator[AsyncSession]:
    """Отдаёт AsyncSession на один запрос и закрывает её после ответа."""
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session
