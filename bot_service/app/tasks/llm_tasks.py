import asyncio

from redis import Redis

from app.core.config import settings
from app.infra.celery_app import celery_app
from app.services.openrouter_client import OpenRouterError, chat_completion

_redis: Redis | None = None


def _get_redis_sync() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


@celery_app.task(name="app.tasks.llm_request", bind=True)
def llm_request(self, tg_chat_id: int, prompt: str) -> str:
    task_id = self.request.id
    redis = _get_redis_sync()

    result_key = f"result:{task_id}"

    try:
        text = asyncio.run(chat_completion(prompt))
        redis.set(result_key, text, ex=600)  # 10 минут
        return text
    except OpenRouterError as e:
        redis.set(result_key, f"Ошибка LLM: {e}", ex=600)
        raise
    except Exception as e:
        redis.set(result_key, f"Неожиданная ошибка: {e}", ex=600)
        raise
