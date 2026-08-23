"""Метаданные OpenAPI: описание сервиса, теги и примеры ошибок."""

from typing import Any

from app.schemas.common import ErrorResponse

OPENAPI_TAGS = [
    {
        "name": "health",
        "description": "Проверки работоспособности процесса и зависимостей PostgreSQL / Redis.",
    },
    {
        "name": "ai",
        "description": (
            "Проксирование prompt в AI модель: проверка API-ключа, лимит 5 запросов в минуту "
            "на пользователя и разбор ошибок внешнего провайдера."
        ),
    },
]

API_DESCRIPTION = """
API Gateway тендерной IT-площадки. Приложение проверяет ключ, ограничивает частоту
запросов и проксирует prompt в AI модель. Анализ тендера делает модель.

**Основные сценарии**
- `POST /api/v1/ai/generate` — проверить Bearer-ключ, лимит и получить ответ модели
- `GET /health` — liveness: процесс запущен
- `GET /health/ready` — readiness: PostgreSQL и Redis отвечают

**Авторизация**
- Заголовок `Authorization: Bearer <api_key>`
- Ключ выдаёт `poetry run seed`; в PostgreSQL хранится только SHA-256 хеш

**Ограничения**
- Не больше 5 запросов в минуту на пользователя (`rate_limit:{user_id}` в Redis)
- Свой лимит Gateway — HTTP 429 (`rate_limit_exceeded`)
- 429 xAI не маскируется под 429 площадки: это HTTP 502 (`upstream_rate_limited`)
- Prompt и ответ модели в базу не пишутся

**Идентификация запроса**
- Заголовок `X-Request-ID`: принимается только валидный UUID, иначе сервер создаёт новый
- Тот же id возвращается в ответе и в поле `request_id` тела ошибки
"""

OPENAPI_CONTACT = {
    "name": "Popova Nadezhda",
    "email": "nadezhdapopova13@yandex.ru",
}


def _error_example(error: str, message: str) -> dict[str, str]:
    """Собирает пример тела `ErrorResponse` для Swagger."""
    return {
        "error": error,
        "message": message,
        "request_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    }


def error_response(description: str, error: str, message: str) -> dict[str, Any]:
    """Описание ошибочного ответа: текст, схема и пример JSON."""
    return {
        "description": description,
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": _error_example(error, message),
            }
        },
    }


GENERATE_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": "Модель вернула текст. Поле `response` — ответ модели, `model` — имя модели.",
    },
    401: error_response(
        "Нет заголовка Authorization, ключ пустой или хеш не найден.",
        "authentication_error",
        "API-ключ отсутствует или недействителен.",
    ),
    403: error_response(
        "Ключ найден, но ключ или пользователь отключены (`is_active=false`).",
        "authorization_error",
        "API-ключ или пользователь заблокированы.",
    ),
    422: error_response(
        "Тело запроса не прошло валидацию: нет `prompt`, пустая строка или длиннее 8000 символов.",
        "validation_error",
        "Тело или параметры запроса не прошли валидацию.",
    ),
    429: error_response(
        "Пользователь исчерпал лимит Gateway: больше 5 запросов за текущую минуту. ИИ-сервис не вызывался.",
        "rate_limit_exceeded",
        "Превышен лимит: не более 5 запросов в минуту.",
    ),
    502: error_response(
        "Ошибка внешнего провайдера: 429 xAI (`upstream_rate_limited`) или 5xx (`upstream_unavailable`).",
        "upstream_unavailable",
        "Внешний ИИ-сервис недоступен.",
    ),
    503: error_response(
        "xAI отклонил серверный ключ Gateway (`XAI_API_KEY`). Это не пользовательский API-ключ площадки.",
        "upstream_auth_error",
        "Внешний ИИ-сервис отклонил серверный ключ доступа.",
    ),
    504: error_response(
        "Таймаут или сетевой сбой при обращении к xAI.",
        "upstream_timeout",
        "Внешний ИИ-сервис не ответил вовремя.",
    ),
    500: error_response(
        "Непредвиденная ошибка сервера. Ищите запись в логах по `request_id`.",
        "internal_error",
        "Внутренняя ошибка сервера.",
    ),
}

HEALTH_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": "Процесс запущен и принимает HTTP. Зависимости не проверяются.",
        "content": {
            "application/json": {
                "example": {"status": "ok"},
            }
        },
    },
}

READY_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": "PostgreSQL и Redis отвечают. Можно принимать generate.",
        "content": {
            "application/json": {
                "example": {"status": "ok", "postgres": "ok", "redis": "ok"},
            }
        },
    },
    503: {
        "description": "Одна или обе зависимости недоступны. Поля `postgres` и `redis` показывают, какая именно.",
        "content": {
            "application/json": {
                "example": {
                    "status": "unavailable",
                    "postgres": "ok",
                    "redis": "unavailable",
                }
            }
        },
    },
}
