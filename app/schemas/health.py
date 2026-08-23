"""Схемы проверки работоспособности."""

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    """Liveness: процесс жив. PostgreSQL и Redis здесь не проверяются."""

    model_config = ConfigDict(json_schema_extra={"examples": [{"status": "ok"}]})

    status: str = Field(default="ok", description="Всегда `ok`, если эндпоинт ответил.")


class ReadyResponse(BaseModel):
    """Readiness: доступность PostgreSQL и Redis по отдельности."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"status": "ok", "postgres": "ok", "redis": "ok"},
                {"status": "unavailable", "postgres": "ok", "redis": "unavailable"},
            ]
        }
    )

    status: str = Field(description="`ok`, если обе зависимости доступны, иначе `unavailable`.")
    postgres: str = Field(description="`ok` или `unavailable`.")
    redis: str = Field(description="`ok` или `unavailable`.")
