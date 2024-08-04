import re
from datetime import datetime

import requests
from aiogram import F
from aiogram import types, Router
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter

from bot.handler.usebale.back_to import back_to_task_list
from bot.handler.usebale.request import divide_event_request
from bot.handler.usebale.stringfy_printer import stringfy_tasks_response_text
from bot.handler.usebale.usebale_handler import list_upcoming_tasks
from bot.keyboards import tasks_list_keyboard, cancel_keyboard, tasks_change_keyboard
from bot.state.Task import TaskStates

router = Router()


# Message "Add Task"
@router.message(F.text.lower() == "💡создать задачу", StateFilter(None))
async def main_msg_add_task_handler(event: types.Message, state: TaskStates.main):
    await event.answer(
        parse_mode=ParseMode.HTML,
        text="Пожалуйста, напишите название и время задачи. Можно указать статус.\n"
             "Пример:\n"
             "Новая задача, 20.08 10:15, статус"
    )
    user_data_from_state_group = await state.get_data()
    if user_data_from_state_group.get('group_id') is not None and user_data_from_state_group['group_id'] is not None:
        group_id = user_data_from_state_group['group_id']
    else:
        group_id = 0
    await state.set_state(TaskStates.write_task)
    await state.update_data({'group_id': group_id})


# Callback Add Task
@router.callback_query(lambda call: call.data.startswith('add_task'))
async def main_add_task_handler(event: types.CallbackQuery, state: TaskStates.main):
    await event.message.edit_reply_markup()
    await event.message.answer(
        parse_mode=ParseMode.HTML,
        text="Пожалуйста, напишите название и время задачи. Можно указать статус.\n"
             "Пример:\n"
             "Новая задача, 20.08 10:15, статус",
        reply_markup=cancel_keyboard()
    )
    user_data_from_state_group = await state.get_data()
    group_id = user_data_from_state_group['group_id']
    await state.set_state(TaskStates.write_task)
    await state.update_data({'group_id': group_id})


@router.message(TaskStates.write_task, F.text)
async def message_add_task_handler(message: types.Message, state: TaskStates.write_task):
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
        end_time = datetime(year=current_year, month=month, day=day, hour=hour, minute=minute, second=0)
        if end_time < datetime.now():
            return await message.answer("The task is in the past. Please try again.")
        user_data_from_state_group = await state.get_data()
        group_id = user_data_from_state_group['group_id']

        json = {
            'group_id': group_id,
            'telegram_id': message.from_user.id,
            'task': task_name,
            'end_time': end_time.isoformat(),
            'custom_status': status,
            # TODO: start_time
        }
        response = await divide_event_request('add_task', message, json)
        task_name_added = response['task']
        group_name = response['group']['name']
        group_id = response['group']['id']
        await message.reply(
            f"Task '{task_name_added}' added!\n\n"
            f"<i>Группа {group_name}</i>",
            parse_mode=ParseMode.HTML
        )
        # Back to task-list
        group = await back_to_task_list(message, group_id, False)

        await state.set_state(TaskStates.main)
        update_data_state = {'group_id': group_id, 'group_name': group['name']}
        await state.update_data(update_data_state)
    else:
        await message.answer("Неправильно заданы данные")


# Cancel Task
@router.callback_query(lambda call: call.data.startswith('cancel'), TaskStates.write_task)
async def cancel_handler(event: types.CallbackQuery, state: TaskStates.write_task):
    await event.message.edit_reply_markup()
    await event.message.answer('Отменить')
    # Back to task-list
    user_data_from_state_group = await state.get_data()
    group_id = user_data_from_state_group['group_id']
    group = await back_to_task_list(event, group_id, True)

    await state.set_state(TaskStates.main)
    update_data_state = {'group_id': group_id, 'group_name': group['name']}
    await state.update_data(update_data_state)


# ------------------- Menu Tasks -------------------
@router.message(F.text.lower() == '🎯список предстоящих задач')
async def upcoming_tasks_handler(message: types.Message):
    await list_upcoming_tasks(message)


# @router.callback_query(lambda call: call.data.startswith('menu_tasks'))
# async def menu_tasks_handler(event: types.CallbackQuery, state: TaskStates.main):
#     user_data_from_state_group = await state.get_data()
#     group_id = user_data_from_state_group['group_id']
#     response = await divide_event_request('get_tasks', message=event, json={'group_id': int(group_id)})
#     tasks = response['tasks']
#     await event.message.edit_reply_markup(
#         reply_markup=tasks_list_keyboard(tasks)
#     )

@router.callback_query(lambda call: call.data.startswith('menu_tasks'))
async def menu_tasks_handler(event: types.CallbackQuery, state: TaskStates.main):
    status_list = ["upcoming", "all", "completed"]
    status_text = {"upcoming": "Предстоящие", "all": "Все", "completed": "Выполнены"}
    status_index = 0

    status = status_list[status_index]
    await event.message.edit_reply_markup(
        reply_markup=tasks_change_keyboard(status_index, status_text[status])
    )


async def list_tasks(event: types.CallbackQuery, group_name: str, status_index: int = 0):
    status_list = ["upcoming", "all", "completed"]
    status_text = {"upcoming": "Предстоящие", "all": "Все", "completed": "Выполнены"}

    telegram_id = event.from_user.id
    status = status_list[status_index]
    response = await divide_event_request(f'tasks_status/{telegram_id}/{status}', method='GET', message=event)
    response_text = f"📚<b>{group_name}</b>📚\n\n"
    if response:
        response_text += f"📋<b>Задачи</b>📋\n\n"
        response_text += stringfy_tasks_response_text(response)
    else:
        response_text = "No tasks found."

    await event.message.edit_text(
        parse_mode=ParseMode.HTML, text=response_text,
        reply_markup=tasks_change_keyboard(status_index, status_text[status]))


@router.callback_query(lambda c: c.data.startswith("prev_") or c.data.startswith("next_"))
async def navigate_tasks(callback_query: types.CallbackQuery, state: TaskStates.main):
    status_list = ["upcoming", "all", "completed"]
    status_text = {"upcoming": "Предстоящие", "all": "Все", "completed": "Выполнены"}
    user_data_from_state_group = await state.get_data()
    group_name = user_data_from_state_group['group_name']

    current_index = int(callback_query.data.split('_')[1])
    if "prev" in callback_query.data:
        new_index = (current_index - 1) % len(status_list)
    else:
        new_index = (current_index + 1) % len(status_list)

    await list_tasks(callback_query, group_name, new_index)
