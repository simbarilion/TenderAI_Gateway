"""Оркестрация generate: лимит, вызов модели, технический лог."""

import time
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    UpstreamAuthError,
    UpstreamRateLimitedError,
    UpstreamTimeoutError,
    UpstreamUnavailableError,
)
from app.models.enums import AIRequestStatus
from app.repositories.ai_request_log import AIRequestLogRepository
from app.services.ai import AIGenerateResult, AIService
from app.services.rate_limit import RateLimitService

_PROVIDER = "xai"


class GenerationService:
    """Склеивает rate limit, Grok и запись лога. Prompt и ответ в БД не пишет."""

    def __init__(
        self,
        rate_limit: RateLimitService,
        ai_service: AIService,
        logs: AIRequestLogRepository,
        session: AsyncSession,
        default_model: str,
    ) -> None:
        self._rate_limit = rate_limit
        self._ai = ai_service
        self._logs = logs
        self._session = session
        self._default_model = default_model

    async def generate(self, user_id: UUID, prompt: str) -> AIGenerateResult:
        """Проверяет лимит, вызывает модель и пишет лог. При ошибке провайдера лог всё равно сохраняется."""
        await self._rate_limit.check(user_id)

        started = time.perf_counter()
        status = AIRequestStatus.UPSTREAM_ERROR
        model = self._default_model
        try:
            result = await self._ai.generate(prompt)
            status = AIRequestStatus.SUCCESS
            model = result.model
            return result
        except UpstreamTimeoutError:
            status = AIRequestStatus.TIMEOUT
            raise
        except UpstreamRateLimitedError:
            status = AIRequestStatus.RATE_LIMITED
            raise
        except (UpstreamAuthError, UpstreamUnavailableError):
            status = AIRequestStatus.UPSTREAM_ERROR
            raise
        finally:
            latency_ms = int((time.perf_counter() - started) * 1000)
            await self._logs.create(
                user_id=user_id,
                provider=_PROVIDER,
                model=model,
                status=status,
                latency_ms=latency_ms,
            )
            await self._session.commit()
