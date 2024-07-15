from typing import Union

from aiogram.types import InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def start_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        # InlineKeyboardButton(text="Open To-Do List", web_app=WebAppInfo(url=webapp_url))
        InlineKeyboardButton(text="Перейти", callback_data='groups_list'),
        InlineKeyboardButton(text="Coming soon...", callback_data='____'),
    )
    keyboard.adjust(1)
    # replyKeyboard = ReplyKeyboardBuilder()
    # replyKeyboard.add(
    #     KeyboardButton(text=f"Создать задачу"),
    #     KeyboardButton(text=f"Назад")
    # )
    return keyboard.as_markup()


def menu_reply_keyboard():
    replyKeyboard = ReplyKeyboardBuilder()
    replyKeyboard.row(
        KeyboardButton(text=f"Создать задачу"),
        KeyboardButton(text=f"Список предстоящих задач"),
    )
    return replyKeyboard.as_markup()


def groups_list_keyboard(groups_list: list):
    keyboard = InlineKeyboardBuilder()
    for group in groups_list:
        keyboard.add(
            InlineKeyboardButton(text=f"{group['name']}", callback_data=f"group_{group['id']}"),
        )
    keyboard.adjust(1)
    keyboard.add(
        InlineKeyboardButton(text=f"Добавить группу", callback_data=f"add_group")
    )
    return keyboard.as_markup()


def tasks_list_keyboard(tasks_list: list):
    keyboard = InlineKeyboardBuilder()
    for task in tasks_list:
        if bool(task['done']) is False:
            keyboard.add(
                InlineKeyboardButton(text=f"{task['task']}", callback_data=f"task_{task['id']}"),
            )
    keyboard.add(
        InlineKeyboardButton(text=f"Создать задачу", callback_data=f"add_task"),
        InlineKeyboardButton(text=f"Назад", callback_data=f"groups_list")).adjust(2)
    return keyboard.as_markup()


def tasks_menu_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text=f"Меню задач", callback_data=f"menu_tasks"),
        InlineKeyboardButton(text=f"Изменить группу", callback_data=f"edit_group"),
        InlineKeyboardButton(text=f"Удалить группу", callback_data=f"delete_group"),
        InlineKeyboardButton(text=f"Назад", callback_data=f"groups_list")
    )
    keyboard.adjust(2)
    return keyboard.as_markup()
