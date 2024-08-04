import os
from typing import Union

import requests
from aiogram import types, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

from bot.handler.usebale.back_to import back_to_group_list, back_to_task_list
from bot.keyboards import start_keyboard, menu_reply_keyboard
from bot.state.Task import TaskStates

load_dotenv()
WEBAPP_URL = os.getenv("WEBAPP_URL")
FLASK_URL = os.getenv("FLASK_URL")

router = Router()


@router.message(Command('start'))
@router.callback_query(lambda call: call.data.startswith('start_menu'))
async def send_welcome(message: types.Message):
    await message.reply(
        text=f"Привет, {message.from_user.first_name}!\nДобро пожаловать в самый крутой проект.\n"
             f"<b>ToDo List Список задач</b>\n",
        parse_mode=ParseMode.HTML,
        reply_markup=menu_reply_keyboard()
    )
    await message.answer(
        "Доступные функции:\n",
        reply_markup=start_keyboard()
    )


@router.message(Command('list'))
@router.callback_query(lambda call: call.data.startswith('groups_list'))
async def list_groups(event: Union[types.Message, types.CallbackQuery]):
    await back_to_group_list(event)


@router.callback_query(lambda call: call.data.startswith('group_'))
async def list_task(event: types.CallbackQuery, state: FSMContext):
    split_callback_data = event.data.split('_')
    group_id = split_callback_data[1]
    group = await back_to_task_list(event, group_id)

    await state.set_state(TaskStates.main)
    update_data_state = {'group_id': group_id, 'group_name': group['name']}
    await state.update_data(update_data_state)


# TODO: LATER
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


