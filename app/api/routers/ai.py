"""Эндпоинт проксирования prompt-а пользователя в AI модель."""

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, get_generation_service
from app.schemas.ai import GenerateRequest, GenerateResponse
from app.schemas.common import ErrorResponse
from app.services.auth import AuthenticatedUser
from app.services.generation import GenerationService

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])

_ERROR_RESPONSES = {
    401: {"model": ErrorResponse},
    403: {"model": ErrorResponse},
    422: {"model": ErrorResponse},
    429: {"model": ErrorResponse},
    502: {"model": ErrorResponse},
    503: {"model": ErrorResponse},
    504: {"model": ErrorResponse},
}


@router.post("/generate", response_model=GenerateResponse, responses=_ERROR_RESPONSES)
async def generate(
    body: GenerateRequest,
    user: AuthenticatedUser = Depends(get_current_user),
    generation: GenerationService = Depends(get_generation_service),
) -> GenerateResponse:
    """Проверяет ключ, лимит и отдаёт ответ модели."""
    result = await generation.generate(user.user_id, body.prompt)
    return GenerateResponse(response=result.text, model=result.model)
