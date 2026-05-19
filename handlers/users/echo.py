from aiogram import types

from keyboards.default.menu import main_menu
from loader import dp


@dp.message_handler(state=None)
async def bot_echo(message: types.Message):
    await message.answer(
        "Menyudan birini tanlang 👇",
        reply_markup=main_menu
    )
