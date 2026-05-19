from aiogram.dispatcher.filters.state import State, StatesGroup


class RegisterState(StatesGroup):
    phone = State()


class AdCreateState(StatesGroup):
    category = State()
    fullname = State()
    yosh = State()
    texno = State()
    aloqa = State()
    hudud = State()
    narx = State()
    vaqt = State()
    maqsad = State()
    confirm = State()


class FilterState(StatesGroup):
    hudud = State()
    texno = State()
