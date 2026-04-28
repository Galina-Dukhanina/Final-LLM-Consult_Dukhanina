from aiogram import Bot, Dispatcher

from app.core.config import settings


def create_bot_and_dp() -> tuple[Bot, Dispatcher]:
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()
    return bot, dp
