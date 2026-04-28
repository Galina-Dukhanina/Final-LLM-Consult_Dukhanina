import asyncio

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.core.jwt import decode_and_validate
from app.infra.redis import get_redis
from app.tasks.llm_tasks import llm_request

router = Router()


def _token_key(tg_user_id: int) -> str:
    return f"token:{tg_user_id}"


def _task_key(chat_id: int) -> str:
    return f"task:{chat_id}"


def _result_key(task_id: str) -> str:
    return f"result:{task_id}"


def _split_telegram(text: str, limit: int = 4000) -> list[str]:
    text = text or ""
    chunks: list[str] = []
    while text:
        chunks.append(text[:limit])
        text = text[limit:]
    return chunks or [""]


async def _wait_and_send_result(
    message: Message, *, task_id: str, chat_id: int
) -> None:
    redis = get_redis()
    key = _result_key(task_id)

    # ждём до 90 секунд
    for _ in range(90):
        value = await redis.get(key)
        if value:
            await redis.delete(key)
            await redis.delete(_task_key(chat_id))
            for part in _split_telegram(value):
                await message.answer(part)
            return
        await asyncio.sleep(1)

    await message.answer("Ответ задерживается. Попробуйте ещё раз через минуту.")


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

    async_result = llm_request.delay(message.chat.id, message.text)
    task_id = async_result.id

    await redis.set(_task_key(message.chat.id), task_id, ex=600)

    asyncio.create_task(
        _wait_and_send_result(message, task_id=task_id, chat_id=message.chat.id)
    )
    await message.answer("Запрос принят. Готовлю ответ…")
