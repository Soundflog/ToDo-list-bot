from aiogram.fsm.state import StatesGroup, State


class TaskStates(StatesGroup):
    write = State()

    async def clear(self) -> None:
        await self.set_state(state=None)
        await self.set_data({})