"""Общие Pydantic-схемы HTTP-ответов."""

from pydantic import BaseModel, ConfigDict, Field


class ErrorResponse(BaseModel):
    """Тело ошибки приложения: код, текст и идентификатор запроса."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "error": "rate_limit_exceeded",
                    "message": "Превышен лимит: не более 5 запросов в минуту.",
                    "request_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                }
            ]
        }
    )

    error: str = Field(description="Машиночитаемый код: authentication_error, rate_limit_exceeded и др.")
    message: str = Field(description="Текст ошибки для клиента без внутренних деталей.")
    request_id: str = Field(description="Значение заголовка X-Request-ID для поиска записи в логах.")
