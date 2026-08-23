"""Схемы запроса и ответа генерации."""

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """Вход пользователя. Системная инструкция сюда не входит."""

    prompt: str = Field(min_length=1, max_length=8000, description="Текст задания для модели.")


class GenerateResponse(BaseModel):
    """Успешный ответ Gateway без служебных полей провайдера."""

    response: str
    model: str
