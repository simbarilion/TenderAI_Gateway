"""Перечисления, которые хранятся в PostgreSQL как строки."""

from enum import StrEnum


class AIRequestStatus(StrEnum):
    """Статус обращения к внешнему LLM."""

    SUCCESS = "success"
    UPSTREAM_ERROR = "upstream_error"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
