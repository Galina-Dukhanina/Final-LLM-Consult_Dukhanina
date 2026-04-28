import asyncio

from app.infra.celery_app import celery_app
from app.services.openrouter_client import chat_completion


@celery_app.task(name="app.tasks.llm_request")
def llm_request(tg_chat_id: int, prompt: str) -> str:
    # Celery task синхронная, а httpx-клиент у нас async — запускаем через asyncio.run
    return asyncio.run(chat_completion(prompt))
