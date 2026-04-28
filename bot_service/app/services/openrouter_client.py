from typing import Any

import httpx

from app.core.config import settings


class OpenRouterError(RuntimeError):
    pass


async def chat_completion(prompt: str) -> str:
    if not settings.OPENROUTER_API_KEY:
        raise OpenRouterError("OPENROUTER_API_KEY is empty")

    url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    if settings.OPENROUTER_SITE_URL:
        headers["HTTP-Referer"] = settings.OPENROUTER_SITE_URL
    if settings.OPENROUTER_APP_NAME:
        headers["X-Title"] = settings.OPENROUTER_APP_NAME

    payload: dict[str, Any] = {
        "model": settings.OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
    }

    timeout = httpx.Timeout(60.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            resp = await client.post(url, json=payload, headers=headers)
        except httpx.RequestError as e:
            raise OpenRouterError(f"Network error: {e}") from e

    if resp.status_code != 200:
        raise OpenRouterError(f"OpenRouter error {resp.status_code}: {resp.text}")

    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        raise OpenRouterError(f"Unexpected response format: {data}") from e
