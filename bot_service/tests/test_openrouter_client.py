import pytest
import respx
from httpx import Response

from app.services.openrouter_client import chat_completion


@pytest.mark.asyncio
@respx.mock
async def test_chat_completion_success() -> None:
    route = respx.post("https://openrouter.ai/api/v1/chat/completions").mock(
        return_value=Response(
            200,
            json={"choices": [{"message": {"content": "Тестовый ответ от LLM"}}]},
        )
    )

    text = await chat_completion("Привет!")
    assert text == "Тестовый ответ от LLM"
    assert route.called
