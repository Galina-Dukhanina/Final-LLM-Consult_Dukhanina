from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "bot_service",
    broker=settings.RABBITMQ_URL,
    backend=settings.REDIS_URL,
)

# Важно: явный импорт, чтобы задача точно зарегистрировалась
import app.tasks.llm_tasks  # noqa: F401
