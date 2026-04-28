from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.core.jwt import decode_and_validate
from app.infra.redis import get_redis
from app.tasks.llm_tasks import llm_request

router = Router()


def _token_key(tg_user_id: int) -> str:
    return f"token:{tg_user_id}"


@router.message(Command("token"))
async def set_token(message: Message) -> None:
    if not message.text:
        await message.answer("Использование: /token <jwt>")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Использование: /token <jwt>")
        return

    token = parts[1].strip()
    if not token:
        await message.answer("Использование: /token <jwt>")
        return

    try:
        decode_and_validate(token)
    except ValueError:
        await message.answer(
            "Токен неверный или истёк. Получите новый токен в Auth Service."
        )
        return

    redis = get_redis()
    await redis.set(_token_key(message.from_user.id), token)
    await message.answer("Токен сохранён. Теперь можно задавать вопросы.")


@router.message()
async def on_text(message: Message) -> None:
    if not message.text or not message.from_user:
        return

    redis = get_redis()
    token = await redis.get(_token_key(message.from_user.id))
    if not token:
        await message.answer(
            "Нет токена. Сначала отправьте: /token <jwt> (токен получите в Auth Service)."
        )
        return

    try:
        decode_and_validate(token)
    except ValueError:
        await message.answer(
            "Токен неверный или истёк. Получите новый токен в Auth Service и снова отправьте /token."
        )
        return

    llm_request.delay(message.chat.id, message.text)
    await message.answer("Запрос принят. Готовлю ответ…")
