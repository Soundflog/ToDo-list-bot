import asyncio
import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.handler import handlers, task

load_dotenv()

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    dp = Dispatcher(storage=MemoryStorage())
    print(str(API_TOKEN))
    bot = Bot(token=str(API_TOKEN))
    dp.include_router(handlers.router)
    dp.include_router(task.router)
    # сюда импортируйте ваш собственный роутер для напитков
    # dp.message.middleware(ThrottlingMiddleware())
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except RuntimeError as e:
        print(e)


if __name__ == '__main__':
    asyncio.run(main())
