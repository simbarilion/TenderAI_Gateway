"""Лимит запросов пользователя. Не зависит от квоты внешнего LLM."""

from uuid import UUID

from redis.asyncio import Redis

from app.core.exceptions import RateLimitExceededError


class RateLimitService:
    """Считает запросы в Redis: ключ `rate_limit:{user_id}`:
    - max_requests: сколько запросов разрешено;
    - window_seconds: за какой период считается лимит.
    """

    def __init__(self, redis: Redis, max_requests: int, window_seconds: int) -> None:
        self._redis = redis
        self._max_requests = max_requests
        self._window_seconds = window_seconds

    async def check(self, user_id: UUID) -> None:
        """Увеличивает счётчик и поднимает `RateLimitExceededError`, если лимит исчерпан.
        TTL выставляется только при создании ключа, чтобы окно не сдвигалось каждым запросом.
        """
        redis_key = f"rate_limit:{user_id}"
        async with self._redis.pipeline(transaction=True) as pipe:
            pipe.incr(redis_key)  # увеличивает значение ключа на 1
            pipe.ttl(redis_key)  # cколько секунд осталось жить Redis-ключу
            count, ttl = await pipe.execute()

        if int(ttl) == -1:  # если ключ только что создан и TTL еще не установлен, устанавливает TTL = window_seconds
            await self._redis.expire(redis_key, self._window_seconds)

        if int(count) > self._max_requests:
            raise RateLimitExceededError()
