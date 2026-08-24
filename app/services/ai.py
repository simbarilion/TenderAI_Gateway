"""Вызов Grok через OpenAI-совместимый Chat Completions."""

import logging
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.ai_prompts import TENDER_ASSISTANT_SYSTEM_PROMPT
from app.core.exceptions import (
    UpstreamAuthError,
    UpstreamRateLimitedError,
    UpstreamTimeoutError,
    UpstreamUnavailableError,
)


@dataclass(frozen=True, slots=True)
class AIGenerateResult:
    """Ответ AI модели."""

    text: str
    model: str


logger = logging.getLogger(__name__)


class AIService:
    """Проксирует prompt в AI и мапит ошибки провайдера в кастомные исключения приложения."""

    def __init__(self, client: httpx.AsyncClient, model: str, api_key: str = "") -> None:
        self._client = client
        self._model = model
        self._api_key = api_key

    async def generate(self, prompt: str) -> AIGenerateResult:
        """Отправляет system + user в `/chat/completions` и возвращает текст ответа."""
        if not self._api_key.strip():
            raise UpstreamAuthError(
                "Не задан серверный ключ LLM (XAI_API_KEY). Нужен бесплатный ключ Groq, не ключ из seed."
            )

        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": TENDER_ASSISTANT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        }
        try:
            response = await self._client.post("/chat/completions", json=payload)
        except httpx.TimeoutException as exc:
            raise UpstreamTimeoutError() from exc
        except httpx.RequestError as exc:
            raise UpstreamUnavailableError() from exc

        logger.info("Ответ xAI: HTTP %s, модель %s", response.status_code, self._model)
        self._raise_for_upstream_status(response.status_code)
        return self._parse_success(response)

    def _parse_success(self, response: httpx.Response) -> AIGenerateResult:
        """Достаёт текст из choices[0].message.content."""
        try:
            data: dict[str, Any] = response.json()
            text = data["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise UpstreamUnavailableError() from exc
        if not isinstance(text, str) or not text.strip():
            raise UpstreamUnavailableError()
        model = data.get("model")
        return AIGenerateResult(
            text=text,
            model=model if isinstance(model, str) and model else self._model,
        )

    @staticmethod
    def _raise_for_upstream_status(status_code: int) -> None:
        """Превращает HTTP-статус xAI в исключение приложения."""
        if 200 <= status_code < 300:
            return
        if status_code == 429:
            raise UpstreamRateLimitedError()
        if status_code in {401, 403}:
            raise UpstreamAuthError()
        if status_code >= 500:
            raise UpstreamUnavailableError()
        raise UpstreamUnavailableError()
