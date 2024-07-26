from typing import Union

from aiogram import F
from aiogram import types, Router
from aiogram.enums import ParseMode

from bot.handler.usebale.back_to import back_to_group_list
from bot.handler.usebale.request import divide_event_request
from bot.handler.usebale.stringfy_printer import print_groups_list
from bot.state.Task import TaskStates

router = Router()


# Вызывается при edit group
@router.callback_query(lambda call: call.data.startswith('edit_group'), TaskStates.main)
async def main_edit_group_handler(event: Union[types.Message, types.CallbackQuery], state: TaskStates.main):
    await event.message.edit_reply_markup()
    await event.message.answer(
        parse_mode=ParseMode.HTML,
        text="Please provide a group name for the tasks.\n"
             "Example:\n"
             "Edit group name группа"
    )
    user_data_from_state_group = await state.get_data()
    group_id = user_data_from_state_group['group_id']
    await state.set_state(TaskStates.edit_group)
    await state.update_data({'group_id': group_id})


@router.message(TaskStates.edit_group, F.text)
@router.callback_query(lambda call: call.data.startswith('edit_group'), TaskStates.edit_group)
async def message_edit_group_handler(event: Union[types.Message, types.CallbackQuery], state: TaskStates.edit_group):
    group_name = event.text
    user_data_from_state_group = await state.get_data()
    group_id = user_data_from_state_group['group_id']
    json = {
        'group_id': group_id,
        'group_name': group_name,
        'telegram_id': event.from_user.id
    }
    response = await divide_event_request('edit_group', event, json)
    group_name_edited = response['group_name']
    await event.reply(
        f"Group <s>'{group_name_edited}'</s> edited!",
        parse_mode=ParseMode.HTML
    )
    # Back to group-list
    await back_to_group_list(event)
    await state.clear()

