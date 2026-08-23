"""Общий HTTPX-клиент для вызова AI. Подключение открывается в lifespan."""

import httpx

_http_client: httpx.AsyncClient | None = None


def init_http_client(base_url: str, timeout_seconds: float, api_key: str) -> None:
    """Создаёт AsyncClient с базовым URL, таймаутом и серверным ключом xAI."""
    global _http_client
    _http_client = httpx.AsyncClient(
        base_url=base_url.rstrip("/"),
        timeout=timeout_seconds,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )


async def dispose_http_client() -> None:
    """Закрывает HTTPX-клиент при остановке приложения."""
    global _http_client
    if _http_client is not None:
        await _http_client.aclose()
    _http_client = None


def get_http_client() -> httpx.AsyncClient:
    """Возвращает клиент, созданный в `init_http_client`.
    Raises:
        RuntimeError: Если вызвать до инициализации или после `dispose_http_client`.
    """
    if _http_client is None:
        raise RuntimeError("HTTPX-клиент не инициализирован.")
    return _http_client
