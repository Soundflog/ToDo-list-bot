from typing import Union
from aiogram import types
from aiogram.enums import ParseMode

from bot.keyboards import groups_list_keyboard, empty_group_list, tasks_menu_keyboard


async def print_groups_list(event: Union[types.Message, types.CallbackQuery], groups):
    if groups:
        answer_response_text = stringfy_groups_response_text(groups[:5])
        response_text = "📚<b>Группы Задач</b>📚\n"
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
        await event.answer("Групп задач не найдено\nПожалуйста, создайте новую группу",
                           reply_markup=empty_group_list())


async def print_tasks_list(event: Union[types.Message, types.CallbackQuery], tasks, group, is_edit_text=True):
    response_text = f"📚<b>{group['name']}</b>📚\n\n"
    if tasks:
        response_text += f"📋<b>Задачи</b>📋\n\n"
        answer_response_text = stringfy_tasks_response_text(tasks[:2])
        response_text += stringfy_tasks_response_text(tasks)
    else:
        answer_response_text = "Нет задач"
        response_text += "Нет задач"
        response_text += "\n\n<i>Меню задач --> Создать задачу</i>"

    if is_edit_text:
        await event.answer(text=answer_response_text)
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
    await event.answer("No tasks found.")


def stringfy_groups_response_text(groups):
    return '\n'.join([f"📕 {group['name']}" for group in groups])


def stringfy_tasks_response_text(tasks):
    if len(tasks) > 0:
        response_lines = [
            (f"📜 {task['task']}\n"
             f"⭐ {task['custom_status'] if task['custom_status'] is not None else 'Не указано'}\n"
             f"📌 {task['end_time']}\n")
            for task in tasks
        ]
        return "\n".join(response_lines)
    return "\n Нет задач"
