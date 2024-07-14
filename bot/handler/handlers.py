import os
from typing import Union

import requests
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from dotenv import load_dotenv
from aiogram import types, Router
from aiogram.filters import Command

from bot.handler.request import divide_event_request
from bot.keyboards import start_keyboard, groups_list_keyboard, tasks_list_keyboard
from bot.state.Task import TaskStates

load_dotenv()
WEBAPP_URL = os.getenv("WEBAPP_URL")
FLASK_URL = os.getenv("FLASK_URL")

router = Router()


@router.message(Command('start'))
@router.callback_query(lambda call: call.data.startswith('start_menu'))
async def send_welcome(message: types.Message):
    await message.reply(
        "Hi! I'm your To-Do List bot. Use me to manage your tasks.",
        reply_markup=start_keyboard()
    )


@router.message(Command('list'))
@router.callback_query(lambda call: call.data.startswith('groups_list'))
async def list_groups(event: Union[types.Message, types.CallbackQuery]):
    response = await divide_event_request('get_groups', message=event, json={'telegram_id': int(event.from_user.id)})
    groups = response['groups']
    if groups:
        answer_response_text = '\n'.join([f"{group['name']}" for group in groups[:5]])
        response_text = "Ваши группы задач:\n"
        response_text += '\n'.join([f"{group['id']}. {group['name']}" for group in groups])
        await event.answer(answer_response_text)
        await event.message.answer(
            parse_mode=ParseMode.HTML,
            text=response_text,
            reply_markup=groups_list_keyboard(groups)
        )
    else:
        await event.answer("No groups found.")


@router.callback_query(lambda call: call.data.startswith('group_'))
async def list_task(event: types.CallbackQuery, state: FSMContext):
    split_callback_data = event.data.split('_')
    group_id = split_callback_data[1]
    response = await divide_event_request('get_tasks', message=event, json={'group_id': int(group_id)})
    tasks = response['tasks']
    group = response['group']
    if tasks:
        answer_response_text = '\n'.join([f"{task['task']}" for task in tasks[:5]])
        response_text = f"Ваши задачи в группе {group['name']}:\n"
        response_text += '\n'.join([f"{task['task']} -- {task['done']} -- {task['end_time']}" for task in tasks])
        await event.answer(text=answer_response_text)
        await event.message.edit_text(
            inline_message_id=event.inline_message_id,
            parse_mode=ParseMode.HTML,
            text=response_text,
            reply_markup=tasks_list_keyboard(tasks)
        )
        await state.set_state(TaskStates.group)
        update_data_state = {'group_id': group_id}
        await state.update_data(update_data_state)
    else:
        await event.answer("No tasks found.")


@router.message(Command('done'))
async def mark_done(message: types.Message):
    task_id = message.get_args()
    if task_id.isdigit():
        response = requests.post(f'{FLASK_URL}/update_task',
                                 json={'telegram_id': message.from_user.id, 'task_id': int(task_id), 'done': True})
        if response.status_code == 200:
            await message.reply(f"Task {task_id} marked as done!")
        else:
            await message.reply("Error updating task.")
    else:
        await message.reply("Please provide a valid task ID.")


@router.message(Command('delete'))
async def delete_task_handler(message: types.Message):
    task_id = message.get_args()
    if task_id.isdigit():
        response = requests.post(f'{FLASK_URL}/delete_task',
                                 json={'telegram_id': message.from_user.id, 'task_id': int(task_id)})
        if response.status_code == 200:
            await message.reply(f"Task {task_id} deleted!")
        else:
            await message.reply("Error deleting task.")
    else:
        await message.reply("Please provide a valid task ID.")
