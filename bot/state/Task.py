from aiogram.fsm.state import StatesGroup, State


class TaskStates(StatesGroup):
    main = State()
    edit_group = State()
    write_group = State()
    write_task = State()

    async def clear(self) -> None:
        await self.set_state(state=None)
        await self.set_data({})