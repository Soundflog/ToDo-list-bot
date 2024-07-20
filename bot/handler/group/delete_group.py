from aiogram import types, Router

from bot.handler.request import divide_event_request
from bot.state.Task import TaskStates

router = Router()


@router.callback_query(lambda call: call.data.startswith('delete_group'), TaskStates.main)
async def delete_group_handler(event:  types.CallbackQuery, state: TaskStates.main):
    user_data_from_state_group = await state.get_data()
    group_id = user_data_from_state_group['group_id']

    json = {'telegram_id': event.from_user.id, 'group_id': group_id}
    response_status = await divide_event_request('delete_group', event, json=json)
    if response_status['success']:
        await event.answer(f"Успешно удалена группа")
        await back_
    else:
        await event.answer(f"Ошибка удаления группы")
