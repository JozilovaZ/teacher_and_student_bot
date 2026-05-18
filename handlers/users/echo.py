from aiogram import types
from aiogram.dispatcher.filters import Text

from keyboards.default.menu import menu_start
from loader import dp

MENU_TEXTS = {"Sherik kerak", "Ish joyi kerak", "Hodim kerak", "Ustoz kerak", "Shogird kerak"}


@dp.message_handler(state=None)
async def bot_echo(message: types.Message):
    if message.text in MENU_TEXTS:
        await message.answer("Iltimos, ro'yxatdan o'ting. /start buyrug'ini bosing.")
        return
    await message.answer(
        "Tushunmadim. Iltimos, menyudan tanlang:",
        reply_markup=menu_start
    )
