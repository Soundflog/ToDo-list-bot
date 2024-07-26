from aiogram import types
from aiogram.enums import ParseMode

from bot.handler.usebale.request import divide_event_request
from bot.handler.usebale.stringfy_printer import stringfy_tasks_response_text


async def list_upcoming_tasks(message: types.Message):
    telegram_id = message.from_user.id
    response = await divide_event_request(f'upcoming_tasks/{telegram_id}', message, {}, method='GET')
    if response:
        response_text = 'Задачи \n\n'
        response_text += stringfy_tasks_response_text(response)
    else:
        response_text = "Все задачи выполнены! \n\n <i>Нажмите кнопку <b>'Создать новую задачу'</b></i>"
    await message.answer(response_text, parse_mode=ParseMode.HTML)
