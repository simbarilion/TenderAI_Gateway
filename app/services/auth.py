"""Проверка пользовательского API-ключа по хешу в PostgreSQL."""

from dataclasses import dataclass
from uuid import UUID

from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.security import hash_api_key
from app.repositories.api_key import APIKeyRepository


@dataclass(frozen=True, slots=True)
class AuthenticatedUser:
    """Данные владельца ключа после успешной проверки. Сырой ключ сюда не попадает."""

    user_id: UUID
    username: str
    api_key_id: UUID


class AuthService:
    """Опознаёт ключ и проверяет, что ключ и пользователь не заблокированы."""

    def __init__(self, api_key_repository: APIKeyRepository) -> None:
        self._api_keys = api_key_repository

    async def authenticate(self, raw_key: str) -> AuthenticatedUser:
        """Возвращает владельца ключа или поднимает 401/403.
        Пустой и неизвестный ключ — `AuthenticationError`.
        Найденный, но отключённый ключ или пользователь — `AuthorizationError`.
        """
        normalized = raw_key.strip()
        if not normalized:
            raise AuthenticationError()

        api_key = await self._api_keys.get_by_hash(hash_api_key(normalized))
        if api_key is None:
            raise AuthenticationError()
        if not api_key.is_active or not api_key.user.is_active:
            raise AuthorizationError()

        return AuthenticatedUser(
            user_id=api_key.user_id,
            username=api_key.user.username,
            api_key_id=api_key.id,
        )
