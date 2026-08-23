"""SQL-запросы к таблице API-ключей."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import APIKey


class APIKeyRepository:
    """Ищет ключи по хешу."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_active_by_hash(self, key_hash: str) -> APIKey | None:
        """Возвращает активный ключ вместе с пользователем или None.
        Неактивный ключ не возвращается.
        """
        stmt = (
            select(APIKey)
            .options(joinedload(APIKey.user))
            .where(APIKey.key_hash == key_hash, APIKey.is_active.is_(True))
        )
        result = await self._session.execute(stmt)
        return result.unique().scalar_one_or_none()
