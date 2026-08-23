"""Зависимости HTTP-слоя: текущий пользователь и сервисы generate."""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.exceptions import AuthenticationError
from app.core.http_client import get_http_client
from app.db.dependencies import get_redis, get_session
from app.repositories.ai_request_log import AIRequestLogRepository
from app.repositories.api_key import APIKeyRepository
from app.services.ai import AIService
from app.services.auth import AuthenticatedUser, AuthService
from app.services.generation import GenerationService
from app.services.rate_limit import RateLimitService

_bearer = HTTPBearer(auto_error=False)


def _settings() -> Settings:
    """Отдаёт кэшированные настройки приложения."""
    return get_settings()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    session: AsyncSession = Depends(get_session),
) -> AuthenticatedUser:
    """Читает Bearer-ключ и проверяет его через AuthService.

    `auto_error=False`, чтобы пустой заголовок давал наш 401, а не 403 Swagger.
    """
    if credentials is None or not credentials.credentials.strip():
        raise AuthenticationError()
    return await AuthService(APIKeyRepository(session)).authenticate(credentials.credentials)


def get_generation_service(
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    settings: Settings = Depends(_settings),
) -> GenerationService:
    """Собирает сервисы лимита запросов пользователя, AI сервиса и лога на один запрос."""
    return GenerationService(
        rate_limit=RateLimitService(
            redis,
            settings.rate_limit_requests,
            settings.rate_limit_window_seconds,
        ),
        ai_service=AIService(get_http_client(), settings.xai_model, settings.xai_api_key),
        logs=AIRequestLogRepository(session),
        session=session,
        default_model=settings.xai_model,
    )
