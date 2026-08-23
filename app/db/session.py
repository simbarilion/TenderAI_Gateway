"""Создание AsyncEngine и фабрики сессий. Подключение открывается в lifespan."""

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def init_db(database_url: str, echo: bool = False) -> None:
    """Инициализирует асинхронный движок engine и фабрику сессий.
    Args:
        database_url: url вида `postgresql+asyncpg://...`.
        echo: Если True, SQLAlchemy пишет SQL в лог.
    """
    global _engine, _session_factory
    _engine = create_async_engine(database_url, echo=echo, pool_pre_ping=True)
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)


async def dispose_db() -> None:
    """Закрывает пул соединений при остановке приложения."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_factory = None


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Возвращает фабрику сессий, созданную в `init_db`.
    Raises:
        RuntimeError: Если вызвать до инициализации или после `dispose_db`.
    """
    if _session_factory is None:
        raise RuntimeError("Фабрика сессий не инициализирована.")
    return _session_factory
