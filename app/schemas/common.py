"""Общие Pydantic-схемы HTTP-ответов."""

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Тело ошибки приложения: код, текст и идентификатор запроса."""

    error: str = Field(description="Код ошибки.")
    message: str = Field(description="Текст ошибки для клиента.")
    request_id: str = Field(description="Значение заголовка X-Request-ID.")
