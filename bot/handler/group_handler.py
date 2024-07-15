import re
from typing import Union

from aiogram import F, Bot
from aiogram import types, Router
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from bot.handler.request import divide_event_request
from bot.handler.usebale_handler import print_groups_list
from bot.state.Task import TaskStates

router = Router()

# Вызывается при создании новой group
@router.message(F.in_("Создать группу"), StateFilter(None))
@router.callback_query(lambda call: call.data.startswith('add_group'))
async def main_add_group_handler(event: Union[types.Message, types.CallbackQuery], state: FSMContext):
    await event.message.edit_reply_markup()
    await event.message.answer(
        parse_mode=ParseMode.HTML,
        text="Please provide a group name for the tasks.\n"
             "Example:\n"
             "Group name группа"
    )
    await state.set_state(TaskStates.write_group)


@router.message(TaskStates.write_group, F.text)
@router.callback_query(lambda call: call.data.startswith('add_group'))
async def message_add_group_handler(event: Union[types.Message, types.CallbackQuery], state: TaskStates.write_group, bot: Bot):
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
        response2 = await divide_event_request('get_groups', message=event,
                                               json={'telegram_id': int(event.from_user.id)})
        groups = response2['groups']

        await print_groups_list(event, groups)
    else:
        await event.answer("Неправильно заданы данные")
    await state.clear()


# Вызывается при edit group
@router.message(F.in_("Редактировать группу"), StateFilter(TaskStates.main))
@router.callback_query(lambda call: call.data.startswith('edit_group'), TaskStates.main)
async def main_edit_group_handler(event: Union[types.Message, types.CallbackQuery], state: TaskStates.main):
    await event.message.edit_reply_markup()
    await event.message.answer(
        parse_mode=ParseMode.HTML,
        text="Please provide a group name for the tasks.\n"
             "Example:\n"
             "Edit group name группа"
    )
    await state.set_state(TaskStates.edit_group)

# Вызывается при delete group
