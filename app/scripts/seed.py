"""Seed: демо-пользователь тендерной площадки и один активный API-ключ.

Запуск: poetry run seed
Нужны настроенный .env и применённые миграции.
Сырой ключ печатается один раз — его нужно сохранить для заголовка Authorization: Bearer <api_key>.
В БД хранится только хеш.
"""

import asyncio
import secrets

from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_api_key
from app.db.session import dispose_db, get_session_factory, init_db
from app.models import APIKey, User

SEED_USERNAME = "tender-analyst"
SEED_KEY_NAME = "Аналитик тендеров"


async def seed() -> None:
    """Создаёт пользователя и ключ, если их ещё нет, и печатает сырой ключ в stdout."""
    settings = get_settings()
    init_db(settings.resolve_database_url(), echo=settings.debug)
    try:
        factory = get_session_factory()
        async with factory() as session:
            existing = await session.scalar(select(User).where(User.username == SEED_USERNAME))
            if existing is not None:
                print(f"Seed уже применён: пользователь {SEED_USERNAME} существует.")
                print("Сырой ключ больше не печатается. Для Authorization используйте сохранённый api_key.")
                return

            raw_key = secrets.token_urlsafe(32)
            user = User(username=SEED_USERNAME, is_active=True)
            session.add(user)
            await session.flush()
            session.add(
                APIKey(
                    user_id=user.id,
                    key_hash=hash_api_key(raw_key),
                    name=SEED_KEY_NAME,
                    is_active=True,
                )
            )
            await session.commit()

            print(f"username: {SEED_USERNAME}")
            print(f"api_key: {raw_key}")
            print("Сохраните api_key: он нужен для Authorization: Bearer <api_key>.")
            print("Повторный seed ключ не покажет, в базе хранится только хеш.")
    finally:
        await dispose_db()


def main() -> None:
    """Точка входа для запуска скрипта."""
    asyncio.run(seed())


if __name__ == "__main__":
    main()
