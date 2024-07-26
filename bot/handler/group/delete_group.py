from aiogram import types, Router
from aiogram.enums import ParseMode

from bot.handler.usebale.back_to import back_to_group_list
from bot.handler.usebale.request import divide_event_request
from bot.keyboards import confirm_delete_keyboard
from bot.state.Task import TaskStates

router = Router()


@router.callback_query(lambda call: call.data.startswith('delete_group'), TaskStates.main)
async def confirm_delete_group_handler(event: types.CallbackQuery, state: TaskStates.main):
    await event.message.edit_reply_markup()

    user_data_from_state_group = await state.get_data()
    group_id = user_data_from_state_group['group_id']

    json = {'group_id': group_id}
    group = await divide_event_request('get_group_by_id', event, json)

    if group['success'] is False:
        await event.answer(f"Ошибка удаления группы")
        return
    await event.message.edit_text(
        f"Вы уверены что хотите удалить группу <b>{group.name}</b>?",
        parse_mode=ParseMode.HTML,
        reply_markup=confirm_delete_keyboard()
    )


@router.callback_query(lambda call: call.data.startswith('confirm_delete_group'), TaskStates.main)
async def delete_group_handler(event: types.CallbackQuery, state: TaskStates.main):
    user_data_from_state_group = await state.get_data()
    group_id = user_data_from_state_group['group_id']

    json = {'telegram_id': event.from_user.id, 'group_id': group_id}
    response_status = await divide_event_request('delete_group', event, json=json)
    if response_status['success']:
        await event.answer(f"Успешно удалена группа")
        await back_to_group_list(event)
    else:
        await event.answer(f"Ошибка удаления группы")
