from aiogram.fsm.state import StatesGroup, State


class GroupState(StatesGroup):
    group = State()
    write = State()

