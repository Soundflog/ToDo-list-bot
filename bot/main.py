import asyncio
import logging
import os
import requests

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from bot.handler import handlers, task_handler
from bot.handler.group import group_handler, delete_group, edit_group

load_dotenv()
FLASK_URL = os.getenv("FLASK_URL")
API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")


async def check_and_notify(bot: Bot):
    response = requests.get(f'{FLASK_URL}/tasks_due')
    if response.status_code == 200:
        tasks_due = response.json()
        if len(tasks_due) > 0:
            for task in tasks_due:
                user_id = task['user_id']
                task_description = task['description']
                task_id = task['task_id']
                await bot.send_message(user_id, f"📢🔔Task '{task_description}' is due!✅")
                # Mark the task as done
                requests.post(f'{FLASK_URL}/update_task', json={'task_id': task_id, 'done': True})


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    dp = Dispatcher(storage=MemoryStorage())
    print(str(API_TOKEN))
    bot = Bot(token=str(API_TOKEN))
    scheduler = AsyncIOScheduler()
    dp.include_router(handlers.router)
    dp.include_router(task_handler.router)
    dp.include_router(group_handler.router)
    dp.include_router(edit_group.router)
    dp.include_router(delete_group.router)
    # сюда импортируйте ваш собственный роутер
    # dp.message.middleware(ThrottlingMiddleware())
    try:
        # Настройка триггера для проверки задач каждые 5 минут
        scheduler.add_job(check_and_notify, IntervalTrigger(minutes=1), kwargs={"bot": bot})
        scheduler.start()
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except RuntimeError as e:
        print(e)


if __name__ == '__main__':
    asyncio.run(main())
