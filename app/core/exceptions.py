"""Доменные исключения TenderAI Gateway"""

from enum import StrEnum


class ErrorCode(StrEnum):
    """Закрытый набор кодов ошибки в теле HTTP-ответа."""

    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    UPSTREAM_TIMEOUT = "upstream_timeout"
    UPSTREAM_AUTH_ERROR = "upstream_auth_error"
    UPSTREAM_RATE_LIMITED = "upstream_rate_limited"
    UPSTREAM_UNAVAILABLE = "upstream_unavailable"
    VALIDATION_ERROR = "validation_error"
    NOT_FOUND = "not_found"
    INTERNAL_ERROR = "internal_error"
    HTTP_ERROR = "http_error"


class GatewayError(Exception):
    """Базовое исключение Gateway, которое сервисы поднимают вместо HTTPException."""

    def __init__(
        self,
        message: str,
        *,
        error: ErrorCode,
        status_code: int,
    ) -> None:
        """Сохраняет человекочитаемое сообщение, код и HTTP-статус."""
        super().__init__(message)
        self.message = message
        self.error = error
        self.status_code = status_code


class AuthenticationError(GatewayError):
    """Клиент не представил ключ или ключ не найден среди активных записей.
    Соответствует HTTP 401.
    """

    def __init__(self, message: str = "API-ключ отсутствует или недействителен.") -> None:
        """Создаёт ошибку аутентификации с пояснением для клиента.
        Args:
            message: Причина отказа. Не должна раскрывать, существует ли ключ.
        """
        super().__init__(
            message,
            error=ErrorCode.AUTHENTICATION_ERROR,
            status_code=401,
        )


class AuthorizationError(GatewayError):
    """Ключ или владелец найдены, но доступ запрещён: запись отключена.
    Соответствует HTTP 403.
    """

    def __init__(self, message: str = "API-ключ или пользователь заблокированы.") -> None:
        """Создаёт ошибку авторизации с пояснением для клиента.
        Args:
            message: Почему доступ закрыт после успешного опознания ключа.
        """
        super().__init__(
            message,
            error=ErrorCode.AUTHORIZATION_ERROR,
            status_code=403,
        )


class RateLimitExceededError(GatewayError):
    """Пользователь исчерпал настроенный лимит Gateway.
    Соответствует HTTP 429 площадки.
    """

    def __init__(
        self,
        message: str = "Превышен лимит: не более 5 запросов в минуту.",
    ) -> None:
        """
        Args:
            message: Текст для клиента без деталей ключа Redis.
        """
        super().__init__(
            message,
            error=ErrorCode.RATE_LIMIT_EXCEEDED,
            status_code=429,
        )


class UpstreamTimeoutError(GatewayError):
    """Внешний LLM не ответил за отведённый таймаут.
    Соответствует HTTP 504.
    """

    def __init__(
        self,
        message: str = "Внешний ИИ-сервис не ответил вовремя.",
    ) -> None:
        """Создаёт ошибку таймаута обращения к провайдеру.
        Args:
            message: Текст для клиента без стека HTTPX.
        """
        super().__init__(
            message,
            error=ErrorCode.UPSTREAM_TIMEOUT,
            status_code=504,
        )


class UpstreamAuthError(GatewayError):
    """Провайдер отклонил серверный ключ Gateway: ошибка конфигурации.
    Соответствует HTTP 503.
    """

    def __init__(
        self,
        message: str = "Внешний ИИ-сервис отклонил серверный ключ доступа.",
    ) -> None:
        """Создаёт ошибку авторизации на стороне провайдера.
        Args:
            message: Текст для клиента без самого серверного секрета.
        """
        super().__init__(
            message,
            error=ErrorCode.UPSTREAM_AUTH_ERROR,
            status_code=503,
        )


class UpstreamRateLimitedError(GatewayError):
    """Провайдер вернул собственный 429: квота xAI, не лимит площадки.
    Соответствует HTTP 502.
    """

    def __init__(
        self,
        message: str = "Внешний ИИ-сервис временно ограничил частоту запросов.",
    ) -> None:
        """Создаёт ошибку rate limit внешнего провайдера.
        Args:
            message: Текст, явно указывающий на upstream, а не на площадку.
        """
        super().__init__(
            message,
            error=ErrorCode.UPSTREAM_RATE_LIMITED,
            status_code=502,
        )


class UpstreamUnavailableError(GatewayError):
    """Провайдер недоступен: 5xx или иной неожиданный отказ сервиса.
    Соответствует HTTP 502.
    """

    def __init__(
        self,
        message: str = "Внешний ИИ-сервис недоступен.",
    ) -> None:
        """Создаёт ошибку недоступности внешнего сервиса.
        Args:
            message: Текст для клиента без сырого тела ответа xAI.
        """
        super().__init__(
            message,
            error=ErrorCode.UPSTREAM_UNAVAILABLE,
            status_code=502,
        )
