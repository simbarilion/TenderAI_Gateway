"""HTTP-middleware сквозных заголовков TenderAI Gateway."""

from collections.abc import Awaitable, Callable
from uuid import UUID, uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import REQUEST_ID_HEADER, reset_request_id, set_request_id


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Протягивает ``X-Request-ID`` через запрос, ответ и логи."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Читает или создаёт request id, вызывает следующее звено и пишет заголовок ответа.
        Args:
            request: Входящий HTTP-запрос.
            call_next: Следующий обработчик цепочки.
        Returns:
            Ответ приложения с заголовком ``X-Request-ID``.
        Raises:
            BaseException: Пробрасывает исключение дальше, но перед этим
            сбрасывает contextvars, чтобы id не утёк в соседний запрос.
        """
        incoming = request.headers.get(REQUEST_ID_HEADER, "").strip()
        try:
            request_id = str(UUID(incoming))
        except (ValueError, AttributeError):
            request_id = str(uuid4())
        token = set_request_id(request_id)
        try:
            response = await call_next(request)
            response.headers[REQUEST_ID_HEADER] = request_id
            return response
        finally:
            reset_request_id(token)
