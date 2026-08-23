"""SQL-запросы к техническому логу вызовов LLM."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AIRequestLog
from app.models.enums import AIRequestStatus


class AIRequestLogRepository:
    """Пишет факт обращения к провайдеру без prompt и ответа модели."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        user_id: UUID,
        provider: str,
        model: str,
        status: AIRequestStatus,
        latency_ms: int | None,
    ) -> AIRequestLog:
        """Добавляет запись лога в сессию и делает flush без вызова коммита."""
        log = AIRequestLog(
            user_id=user_id,
            provider=provider,
            model=model,
            status=status,
            latency_ms=latency_ms,
        )
        self._session.add(log)
        await self._session.flush()
        return log
