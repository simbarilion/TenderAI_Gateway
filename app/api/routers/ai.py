"""Эндпоинт проксирования prompt пользователя в AI модель."""

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, get_generation_service
from app.core.openapi import GENERATE_RESPONSES
from app.schemas.ai import GenerateRequest, GenerateResponse
from app.services.auth import AuthenticatedUser
from app.services.generation import GenerationService

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])


@router.post(
    "/generate",
    response_model=GenerateResponse,
    summary="Проксировать prompt в AI модель",
    description=(
        "Принимает описание IT-тендера или ТЗ, проверяет политики Gateway "
        "и пересылает prompt во внешнюю модель.\n\n"
        "**Что отправить**\n"
        "- Заголовок `Authorization: Bearer <api_key>` — ключ из `poetry run seed`\n"
        '- JSON `{"prompt": "..."}` — от 1 до 8000 символов, без системной инструкции\n\n'
        "**Что делает сервис**\n"
        "- Сверяет хеш ключа в PostgreSQL\n"
        "- Считает запросы пользователя в Redis: не больше 5 за 60 секунд\n"
        "- Добавляет системную инструкцию помощника тендерной площадки и вызывает xAI\n"
        "- Пишет технический лог (провайдер, модель, статус, latency) без текста prompt и ответа\n\n"
        "**Что вернётся**\n"
        "- `200` — `response` и `model`\n"
        "- `401` — нет или неизвестный ключ\n"
        "- `403` — ключ или пользователь отключены\n"
        "- `422` — пустой или слишком длинный prompt\n"
        "- `429` — лимит площадки, AI модель не вызвалась\n"
        "- `502` — ошибка или лимит xAI\n"
        "- `503` — серверный `XAI_API_KEY` отклонён провайдером\n"
        "- `504` — таймаут или сеть до xAI"
    ),
    responses=GENERATE_RESPONSES,
)
async def generate(
    body: GenerateRequest,
    user: AuthenticatedUser = Depends(get_current_user),
    generation: GenerationService = Depends(get_generation_service),
) -> GenerateResponse:
    """Проверяет ключ, лимит и отдаёт ответ модели."""
    result = await generation.generate(user.user_id, body.prompt)
    return GenerateResponse(response=result.text, model=result.model)
