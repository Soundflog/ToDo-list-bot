import re
from typing import Union

from aiogram import F
from aiogram import types, Router
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from bot.handler.usebale.back_to import back_to_group_list
from bot.handler.usebale.request import divide_event_request
from bot.keyboards import cancel_keyboard
from bot.state.Task import TaskStates

router = Router()


# Вызывается при создании новой group
@router.message(F.in_("Создать группу"), StateFilter(None))
@router.callback_query(lambda call: call.data.startswith('add_group'))
async def main_add_group_handler(event: Union[types.Message, types.CallbackQuery], state: FSMContext):
    await event.message.edit_reply_markup()
    await event.message.answer(
        parse_mode=ParseMode.HTML,
        text="Пожалуйста, напишите название группы для задач.\n"
             "<i>Пример:\nГруппа задач</i>",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(TaskStates.write_group)


@router.message(TaskStates.write_group, F.text)
@router.callback_query(lambda call: call.data.startswith('add_group'))
async def message_add_group_handler(event: Union[types.Message, types.CallbackQuery], state: TaskStates.write_group):
    msg = event.text
    pattern = r'^(?P<group>.+?)$'
    match = re.match(pattern, msg.strip())
    if match:
        group_name = match.group('group')
        json = {
            'group_name': group_name,
            'telegram_id': event.from_user.id
        }
        response = await divide_event_request('add_group', event, json)
        group_name_added = response['group_name']
        await event.reply(
            f"Group '{group_name_added}' added!",
            parse_mode=ParseMode.HTML
        )
        # Back to group-list
        await back_to_group_list(event)
    else:
        await event.answer("Неправильно заданы данные")
    await state.clear()


@router.callback_query(lambda call: call.data.startswith('cancel'), TaskStates.write_group)
async def cancel_handler(event: types.CallbackQuery, state: TaskStates.write_group):
    await event.message.edit_reply_markup()
    await event.message.answer('Отменить')
    # Back to group-list
    await back_to_group_list(event)
    await state.set_state(TaskStates.main)
