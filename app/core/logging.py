"""Настройка структурированного логирования с привязкой к запросу.
Модуль отвечает только за формат записей и за `request_id` в contextvars.
Он не пишет access-лог HTTP и не маскирует заголовки — это задача middleware.
"""

from __future__ import annotations

import logging
import sys
from contextvars import ContextVar, Token

REQUEST_ID_HEADER = "X-Request-ID"
_MISSING_REQUEST_ID = "-"

_request_id_ctx: ContextVar[str] = ContextVar("request_id", default=_MISSING_REQUEST_ID)


def get_request_id() -> str:
    """Возвращает идентификатор текущего HTTP-запроса из контекста задачи."""
    return _request_id_ctx.get()


def set_request_id(request_id: str) -> Token[str]:
    """Запоминает идентификатор запроса в contextvars текущей asyncio-задачи.
    Args:
        request_id: Значение заголовка `X-Request-ID` или только что созданный UUID.
    Returns:
        Токен `ContextVar`, который нужно передать в `reset_request_id`.
    """
    return _request_id_ctx.set(request_id)


def reset_request_id(token: Token[str]) -> None:
    """Восстанавливает предыдущий `request_id` после обработки запроса.
    Args:
        token: Токен, полученный из `set_request_id` на входе в middleware.
    """
    _request_id_ctx.reset(token)


class RequestIdFilter(logging.Filter):
    """Добавляет в каждую запись поле `request_id` из contextvars.
    Фильтр не порождает идентификатор сам: если запроса нет, в лог уйдёт `-`.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """Обогащает запись текущим request id и всегда пропускает её дальше."""
        record.request_id = get_request_id()
        return True


def setup_logging(level: str) -> None:
    """Настраивает корневой логгер процесса в stdout."""
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s [request_id=%(request_id)s] %(message)s")
    handler.setFormatter(formatter)
    handler.addFilter(RequestIdFilter())

    root_logger.handlers.clear()
    root_logger.addHandler(handler)
