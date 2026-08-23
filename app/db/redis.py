"""Клиент Redis для счётчика rate limit. Подключение открывается в lifespan."""

from redis.asyncio import Redis

_redis: Redis | None = None


async def init_redis(redis_url: str) -> None:
    """Создаёт async-клиент Redis.
    Args:
        redis_url: URL вида `redis://localhost:6379/0`.
    """
    global _redis
    _redis = Redis.from_url(redis_url, decode_responses=True)


async def dispose_redis() -> None:
    """Закрывает соединение с Redis при остановке приложения."""
    global _redis
    if _redis is not None:
        await _redis.aclose()
    _redis = None


def get_redis_client() -> Redis:
    """Возвращает клиент, созданный в `init_redis`.
    Raises:
        RuntimeError: Если вызвать до инициализации или после `dispose_redis`.
    """
    if _redis is None:
        raise RuntimeError("Клиент Redis не инициализирован.")
    return _redis
