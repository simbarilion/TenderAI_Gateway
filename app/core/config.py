"""Настройки конфигурации приложения."""

from functools import lru_cache
from pathlib import Path
from urllib.parse import quote

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Корневая директория репозитория
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_ENV_FILE = _PROJECT_ROOT / ".env"


def normalize_async_database_url(url: str) -> str:
    """Приводит postgres/postgresql URL к виду для SQLAlchemy + asyncpg."""
    if url.startswith("postgresql+asyncpg://"):
        return url
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


class Settings(BaseSettings):
    """Настройки приложения, загружаемые из переменных окружения."""

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = Field(
        default="TenderAI_Gateway",
        description="Имя сервиса в OpenAPI и в стартовых логах.",
    )
    debug: bool = Field(
        default=False,
        description="Режим отладки FastAPI. В проде должен быть выключен.",
    )
    log_level: str = Field(
        default="INFO",
        description="Уровень корневого логгера: DEBUG, INFO, WARNING, ERROR.",
    )

    db_host: str = Field(default="localhost", description="Хост PostgreSQL.")
    db_port: int = Field(default=5432, description="Порт PostgreSQL.")
    db_user: str = Field(default="postgres", description="Пользователь PostgreSQL.")
    db_password: str = Field(default="postgres", description="Пароль PostgreSQL.")
    db_name: str = Field(default="tenderai", description="Имя базы PostgreSQL.")
    database_url: str | None = Field(default=None, description="DATABASE_URL.")

    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="URL Redis для счётчика rate limit.",
    )

    xai_api_key: str = Field(
        default="",
        description="Серверный ключ xAI.",
    )
    xai_base_url: str = Field(
        default="https://api.x.ai/v1",
        description="Базовый URL OpenAI-совместимого API xAI.",
    )
    xai_model: str = Field(
        default="grok-3-mini",
        description="Идентификатор модели Grok.",
    )
    http_timeout_seconds: float = Field(
        default=30.0,
        description="Таймаут HTTPX на весь запрос к LLM в секундах.",
        gt=0,
    )

    rate_limit_requests: int = Field(
        default=5,
        description="Максимум запросов пользователя за окно rate limit.",
        gt=0,
    )
    rate_limit_window_seconds: int = Field(
        default=60,
        description="Длина окна rate limit и TTL ключа Redis в секундах.",
        gt=0,
    )

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        """Приводит уровень логирования к верхнему регистру для модуля logging.
        Raises:
            ValueError: Если строка не является известным уровнем logging.
        """
        normalized = value.upper()
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if normalized not in allowed:
            allowed_list = ", ".join(sorted(allowed))
            raise ValueError(f"Недопустимый LOG_LEVEL={value!r}. Ожидается одно из: {allowed_list}.")
        return normalized

    def resolve_database_url(self) -> str:
        """Возвращает URL PostgreSQL для AsyncEngine.
        Если задан `database_url`, он нормализуется под asyncpg.
        Иначе URL собирается из `db_user`, `db_password`, `db_host`,`db_port` и `db_name`.
        Returns:
            Строка подключения вида `postgresql+asyncpg://user:pass@host:port/db`.
        """
        if self.database_url:
            return normalize_async_database_url(self.database_url)

        user = quote(self.db_user, safe="")
        password = quote(self.db_password, safe="")
        return f"postgresql+asyncpg://{user}:{password}@{self.db_host}:{self.db_port}/{self.db_name}"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Возвращает единственный экземпляр настроек на процесс."""
    return Settings()
