from datetime import datetime
import re
from typing import Union

from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from aiogram import types, Router
from aiogram.filters import Command, StateFilter
from aiogram import F

from bot.handler.request import divide_event_request
from bot.keyboards import start_keyboard, groups_list_keyboard, tasks_list_keyboard
from bot.state.Task import TaskStates

router = Router()


@router.message(F.in_("Создать задачу"), StateFilter(None))
@router.callback_query(lambda call: call.data.startswith('task_add'))
async def main_add_task_handler(event: Union[types.Message, types.CallbackQuery], state: TaskStates.group):
    await event.message.edit_reply_markup()
    await event.message.answer(
        parse_mode=ParseMode.HTML,
        text="Please provide a task description and time.\n"
             "Example:\n"
             "New_task, 02.20 15:00, status"
    )
    user_data_from_state_group = await state.get_data()
    group_id = user_data_from_state_group['group_id']
    await state.set_state(TaskStates.write)
    await state.update_data({'group_id': group_id})


@router.message(TaskStates.write)
async def message_add_task_handler(message: types.Message, state: TaskStates.write):
    if message.text:
        msg = message.text
        pattern = r'^(?P<task>.+?), (?P<date>\d{2}\.\d{2}) (?P<time>\d{2}:\d{2}), (?P<status>.+?)$'
        match = re.match(pattern, msg.strip())
        if match:
            task_name = match.group('task')
            date = match.group('date')
            time = match.group('time')
            status = match.group('status')

            day, month = map(int, date.split('.'))
            hour, minute = map(int, time.split(':'))
            current_year = datetime.now().year
            end_time = datetime(current_year, month, day, hour, minute, 0)
            if end_time < datetime.now():
                return await message.answer("The task is in the past. Please try again.")
            user_data_from_state_group = await state.get_data()
            group_id = user_data_from_state_group['group_id']

            json = {
                'group_id': group_id,
                'telegram_id': message.from_user.id,
                'task': task_name,
                'end_time': end_time.isoformat(),
                'status': status,
                # TODO: start_time
            }
            response = await divide_event_request('add_task', message, json)
            task_name_added = response['task']
            await message.reply(
                f"Task '{task_name_added}' added!",
                parse_mode=ParseMode.HTML
            )
            # Back to task-list
            response2 = await divide_event_request('get_tasks', message=message, json={'group_id': int(group_id)})
            tasks = response2['tasks']
            group = response2['group']
            if tasks:
                response_text = f"Ваши задачи в группе {group['name']}:\n"
                response_text += '\n'.join(
                    [f"{task['task']} -- {task['done']} -- {task['end_time']}" for task in tasks])
                await message.answer(
                    parse_mode=ParseMode.HTML,
                    text=response_text,
                    reply_markup=tasks_list_keyboard(tasks)
                )
                await state.set_state(TaskStates.group)
                update_data_state = {'group_id': group_id}
                await state.update_data(update_data_state)
            else:
                await message.answer("No tasks found.")
        else:
            await message.answer("Неправильно заданы данные")
    else:
        await message.answer("Please provide a task description.")
    await state.clear()
