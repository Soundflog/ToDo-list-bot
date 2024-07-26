from typing import Union
from aiogram import types

from bot.handler.usebale.request import divide_event_request
from bot.handler.usebale.stringfy_printer import print_groups_list, print_tasks_list


async def back_to_group_list(event: Union[types.Message, types.CallbackQuery]):
    await event.edit_reply_markup()
    response = await divide_event_request('get_groups', message=event, json={'telegram_id': event.from_user.id})
    groups = response['groups']
    await print_groups_list(event, groups)


async def back_to_task_list(event: Union[types.Message, types.CallbackQuery], group_id, is_edit_text=True):
    response = await divide_event_request('get_tasks', message=event, json={'group_id': int(group_id)})
    tasks = response['tasks']
    group = response['group']
    await print_tasks_list(event, tasks, group, is_edit_text)
