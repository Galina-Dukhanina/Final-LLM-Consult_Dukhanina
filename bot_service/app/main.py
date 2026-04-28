import asyncio

from app.bot.dispatcher import create_bot_and_dp
from app.bot.handlers import router as handlers_router


async def main() -> None:
    bot, dp = create_bot_and_dp()
    dp.include_router(handlers_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
