from types import SimpleNamespace

import pytest

from app.bot import handlers


class DummyMessage:
    def __init__(self, text: str, user_id: int = 1, chat_id: int = 1):
        self.text = text
        self.from_user = SimpleNamespace(id=user_id)
        self.chat = SimpleNamespace(id=chat_id)
        self.answers: list[str] = []
        self.bot = SimpleNamespace(send_chat_action=self._fake_chat_action)

    async def answer(self, text: str) -> None:
        self.answers.append(text)

    async def _fake_chat_action(self, **kwargs):
        return None


@pytest.mark.asyncio
async def test_set_token_saves_token(monkeypatch, fake_redis) -> None:
    monkeypatch.setattr(handlers, "get_redis", lambda: fake_redis)
    monkeypatch.setattr(
        handlers, "decode_and_validate", lambda token: {"sub": "1", "role": "user"}
    )

    message = DummyMessage("/token test.jwt.token", user_id=42, chat_id=42)
    await handlers.set_token(message)

    saved = await fake_redis.get("token:42")
    assert saved == "test.jwt.token"
    assert any("Токен сохранён" in x for x in message.answers)


@pytest.mark.asyncio
async def test_on_text_without_token_refuses(monkeypatch, fake_redis, mocker) -> None:
    monkeypatch.setattr(handlers, "get_redis", lambda: fake_redis)
    delay_mock = mocker.patch("app.bot.handlers.llm_request.delay")

    message = DummyMessage("Привет", user_id=7, chat_id=7)
    await handlers.on_text(message)

    delay_mock.assert_not_called()
    assert any("Нет токена" in x for x in message.answers)


@pytest.mark.asyncio
async def test_on_text_with_token_calls_celery(monkeypatch, fake_redis, mocker) -> None:
    monkeypatch.setattr(handlers, "get_redis", lambda: fake_redis)
    monkeypatch.setattr(
        handlers, "decode_and_validate", lambda token: {"sub": "7", "role": "user"}
    )

    await fake_redis.set("token:7", "ok.jwt.token")

    fake_async_result = SimpleNamespace(id="task-123")
    delay_mock = mocker.patch(
        "app.bot.handlers.llm_request.delay", return_value=fake_async_result
    )

    scheduled = {"coro": None}

    def _fake_create_task(coro):
        scheduled["coro"] = coro
        return SimpleNamespace()

    create_task_mock = mocker.patch(
        "app.bot.handlers.asyncio.create_task", side_effect=_fake_create_task
    )

    message = DummyMessage("Что такое JWT?", user_id=7, chat_id=777)
    await handlers.on_text(message)

    delay_mock.assert_called_once_with(777, "Что такое JWT?")
    create_task_mock.assert_called_once()
    assert any("Запрос принят" in x for x in message.answers)

    task_id = await fake_redis.get("task:777")
    assert task_id == "task-123"

    # закрываем корутину, чтобы не было warning "coroutine was never awaited"
    assert scheduled["coro"] is not None
    scheduled["coro"].close()
