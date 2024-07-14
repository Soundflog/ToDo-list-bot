from datetime import datetime
import re

from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from aiogram import types, Router
from aiogram.filters import Command, StateFilter
from aiogram import F

from bot.handler.request import divide_event_request
from bot.keyboards import start_keyboard, groups_list_keyboard, tasks_list_keyboard
from bot.state.Task import TaskStates

router = Router()


@router.message(Command('add_task'), StateFilter(None))
@router.callback_query(lambda call: call.data.startswith('task_add'))
async def main_add_task_handler(message: types.Message, state: FSMContext):
    await message.answer(
        parse_mode=ParseMode.HTML,
        text="Please provide a task description and time.\n"
             "Example:\n"
             "New_task, 02.20 15:00, status"
    )
    await state.set_state(TaskStates.write)


@router.message(TaskStates.write, F.regex(r'^(?P<task>.+?), (?P<date>\d{2}\.\d{2}) (?P<time>\d{2}:\d{2}), '
                                          r'(?P<status>.+)$'))
async def message_add_task_handler(message: types.Message, state: TaskStates.write):
    if message.text:
        msg = message.text
        pattern = r'^(?P<task>.+?), (?P<date>\d{2}\.\d{2}) (?P<time>\d{2}:\d{2}), (?P<status>.+)$'
        match = re.match(pattern, msg)
        if match:
            task_name = match.group('task')
            date = match.group('date')
            time = match.group('time')
            status = match.group('status')

            day, month = map(int, date.split('.'))
            hour, minute = map(int, time.split(':'))
            current_year = datetime.now().year
            end_time = datetime(current_year, month, day, hour, minute, 0)

            json = {
                'telegram_id': message.from_user.id,
                'task': task_name,
                'end_time': end_time,
                'status': status,
                # TODO: start_time
            }
            response = await divide_event_request('add_task', message, json)
            await message.reply(f"Task '{response['name']}' added!")
        else:
            await message.answer("Неправильно заданы данные")
    else:
        await message.answer("Please provide a task description.")
    await state.clear()
