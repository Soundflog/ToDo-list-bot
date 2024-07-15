from typing import Union

from aiogram import types
from aiogram.enums import ParseMode

from bot.handler.request import divide_event_request
from bot.keyboards import groups_list_keyboard, tasks_list_keyboard, tasks_menu_keyboard


async def back_to_task_list(event: Union[types.Message, types.CallbackQuery], group_id, is_edit_text=True):
    response = await divide_event_request('get_tasks', message=event, json={'group_id': int(group_id)})
    tasks = response['tasks']
    group = response['group']
    await print_tasks_list(event, tasks, group, is_edit_text)


async def print_groups_list(event: Union[types.Message, types.CallbackQuery], groups):
    if groups:
        answer_response_text = stringfy_groups_response_text(groups[:5])
        response_text = "<b>Группы Задач</b>\n"
        response_text += stringfy_groups_response_text(groups)
        response_text += ("\n\n <em>Для того чтобы перейти к группе, нажмите кнопку ниже, соответствующую названии "
                          "группы</em>")
        if type(event) is types.CallbackQuery:
            await event.answer(answer_response_text)
            await event.message.answer(
                parse_mode=ParseMode.HTML,
                text=response_text,
                reply_markup=groups_list_keyboard(groups)
            )
        else:
            await event.answer(
                parse_mode=ParseMode.HTML,
                text=response_text,
                reply_markup=groups_list_keyboard(groups)
            )
    else:
        await event.answer("No groups found.")


async def print_tasks_list(event: Union[types.Message, types.CallbackQuery], tasks, group, is_edit_text=True):
    if tasks:
        answer_response_text = stringfy_tasks_response_text(tasks[:2])
        response_text = (f"<b>{group['name']}</b>\n\n"
                         f"<b>Задачи</b>:\n")
        response_text += stringfy_tasks_response_text(tasks)
        await event.answer(text=answer_response_text)
        if is_edit_text:
            await event.message.edit_text(
                inline_message_id=event.inline_message_id,
                parse_mode=ParseMode.HTML,
                text=response_text,
                reply_markup=tasks_menu_keyboard()
            )
        else:
            await event.answer(
                parse_mode=ParseMode.HTML,
                text=response_text, reply_markup=tasks_menu_keyboard()
            )
    else:
        await event.answer("No tasks found.")


def stringfy_groups_response_text(groups):
    return '\n'.join([f"{group['id']}. {group['name']}" for group in groups])


def stringfy_tasks_response_text(tasks):
    response_lines = [
        f"Task: {task['task']}\nStatus: {task['custom_status']}\nEnd Time: {task['end_time']}\n"
        for task in tasks
    ]
    return "\n".join(response_lines)
