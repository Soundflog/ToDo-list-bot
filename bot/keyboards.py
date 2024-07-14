from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.web_app_info import WebAppInfo


def start_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        # InlineKeyboardButton(text="Open To-Do List", web_app=WebAppInfo(url=webapp_url))
        InlineKeyboardButton(text="Перейти", callback_data='groups_list')
    )
    keyboard.adjust(1)
    return keyboard.as_markup()


def groups_list_keyboard(groups_list: list):
    keyboard = InlineKeyboardBuilder()
    for group in groups_list:
        keyboard.add(
            InlineKeyboardButton(text=f"{group['name']}", callback_data=f"group_{group['id']}"),
        )
    keyboard.adjust(1)
    keyboard.add(
        InlineKeyboardButton(text=f"Добавить", callback_data=f"group_add"),
    )
    return keyboard.as_markup()


def tasks_list_keyboard(tasks_list: list):
    keyboard = InlineKeyboardBuilder()
    # TODO: add more tasks pageable
    for task in tasks_list:
        if bool(task['done']) is False:
            keyboard.add(
                InlineKeyboardButton(text=f"{task['task']}", callback_data=f"task_{task['id']}"),
            )
    keyboard.add(
        InlineKeyboardButton(text=f"Создать", callback_data=f"task_add"),
    )
    keyboard.adjust(1)
    keyboard.add(
        InlineKeyboardButton(text=f"Назад", callback_data=f"groups_list"),
        InlineKeyboardButton(text=f"Меню", callback_data=f"group_menu"),
    ).adjust(2)
    return keyboard.as_markup()
