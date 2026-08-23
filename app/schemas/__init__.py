"""Pydantic-схемы HTTP-контракта."""

from app.schemas.ai import GenerateRequest, GenerateResponse
from app.schemas.common import ErrorResponse
from app.schemas.health import HealthResponse, ReadyResponse

__all__ = [
    "ErrorResponse",
    "GenerateRequest",
    "GenerateResponse",
    "HealthResponse",
    "ReadyResponse",
]
