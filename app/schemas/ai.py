"""Схемы запроса и ответа генерации."""

from pydantic import BaseModel, ConfigDict, Field


class GenerateRequest(BaseModel):
    """Вход пользователя. Системная инструкция площадки сюда не входит."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "prompt": (
                        "Проанализируй риски для IT-подрядчика. "
                        "Срок — 30 дней, нужны веб, мобильное приложение, REST API "
                        "и интеграция с тремя внешними системами. Бюджет фиксированный."
                    )
                }
            ]
        }
    )

    prompt: str = Field(
        min_length=1,
        max_length=8000,
        description="Текст задания для модели: описание тендера, ТЗ или вопрос по рискам.",
        examples=["Проанализируй техническое задание и найди недостающие требования по безопасности и интеграциям."],
    )


class GenerateResponse(BaseModel):
    """Успешный ответ Gateway: текст модели и её идентификатор."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "response": "Основные риски: сжатый срок, фиксированный бюджет и три внешние интеграции.",
                    "model": "grok-3-mini",
                }
            ]
        }
    )

    response: str = Field(description="Текст ответа модели без системной инструкции.")
    model: str = Field(description="Имя модели, которую вернул провайдер или настройки Gateway.")
