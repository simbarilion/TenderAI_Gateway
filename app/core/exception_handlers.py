import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import ErrorCode, GatewayError
from app.core.logging import REQUEST_ID_HEADER, get_request_id

logger = logging.getLogger(__name__)


def _error_body(*, error: ErrorCode, message: str) -> dict[str, str]:
    """Собирает единообразное JSON-тело ошибки.
    Args:
        error: код из `ErrorCode`.
        message: Текст для клиента.
    Returns:
        Словарь `error`, `message`, `request_id` для ответа.
    """
    return {
        "error": error.value,
        "message": message,
        "request_id": get_request_id(),
    }


async def handle_gateway_error(_: Request, exc: GatewayError) -> JSONResponse:
    """Превращает доменное исключение сервиса в HTTP-ответ приложения.
    Args:
        _: Запрос, на котором сработало исключение.
        exc: Ошибка сервисного слоя с уже выбранным статусом и кодом.
    Returns:
        JSON с полями `error`, `message`, `request_id`.
    """
    logger.warning("Доменная ошибка Gateway: %s", exc.error)
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(error=exc.error, message=exc.message),
        headers={REQUEST_ID_HEADER: get_request_id()},
    )


async def handle_http_exception(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Дополняет стандартные HTTP-ошибки FastAPI полем `request_id`.
    Args:
        _: Запрос.
        exc: Исключение фреймворка.
    Returns:
        JSON ответ.
    """
    error = ErrorCode.NOT_FOUND if exc.status_code == 404 else ErrorCode.HTTP_ERROR
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(
            error=error,
            message=str(exc.detail),
        ),
        headers={REQUEST_ID_HEADER: get_request_id()},
    )


async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
    """Отдаёт 422, если тело запроса или параметры не прошли Pydantic валидацию.
    Args:
        _: Запрос с невалидным телом или query.
        exc: Исключение валидации.
    Returns:
        JSON 422 без перечисления внутренних путей полей.
    """
    logger.info("Ошибка валидации запроса: %s", exc.errors())
    return JSONResponse(
        status_code=422,
        content=_error_body(
            error=ErrorCode.VALIDATION_ERROR,
            message="Тело или параметры запроса не прошли валидацию.",
        ),
        headers={REQUEST_ID_HEADER: get_request_id()},
    )


async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
    """Ловит непредвиденное исключение и скрывает внутренности от клиента.
    Args:
        _: Запрос, во время которого произошёл сбой.
        exc: Исключение.
    Returns:
        JSON 500 с общим текстом и `request_id` для поиска записи в логах.
    """
    logger.exception("Необработанное исключение: %s", exc)
    return JSONResponse(
        status_code=500,
        content=_error_body(
            error=ErrorCode.INTERNAL_ERROR,
            message="Внутренняя ошибка сервера.",
        ),
        headers={REQUEST_ID_HEADER: get_request_id()},
    )


def register_exception_handlers(application: FastAPI) -> None:
    """Регистрирует обработчики доменных, валидационных и непредвиденных ошибок."""
    application.add_exception_handler(GatewayError, handle_gateway_error)
    application.add_exception_handler(StarletteHTTPException, handle_http_exception)
    application.add_exception_handler(RequestValidationError, handle_validation_error)
    application.add_exception_handler(Exception, handle_unexpected_error)
