"""Схемы проверки работоспособности."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Приложение запущено и принимает HTTP."""

    status: str = "ok"


class ReadyResponse(BaseModel):
    """Готовность зависимостей: PostgreSQL и Redis."""

    status: str
    postgres: str
    redis: str
