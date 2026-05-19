from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart

from keyboards.default.menu import main_menu, phone_keyboard
from loader import dp
from states.anketa import RegisterState
from utils.db_api import database as db


@dp.message_handler(CommandStart(), state="*")
async def bot_start(message: types.Message, state: FSMContext):
    await state.finish()
    user = db.get_user(message.from_user.id)

    if user and user['role'] == 'blocked':
        await message.answer("Hisobingiz bloklangan. Admin bilan bog'laning.")
        return

    if user and user['phone']:
        await message.answer(
            f"Xush kelibsiz, <b>{user['full_name']}</b>! 👋\n\n"
            "Quyidagi bo'limlardan birini tanlang:",
            reply_markup=main_menu
        )
    else:
        db.add_user(
            telegram_id=message.from_user.id,
            full_name=message.from_user.full_name,
            username=message.from_user.username
        )
        await message.answer(
            f"Assalom alaykum, <b>{message.from_user.full_name}</b>! 👋\n\n"
            "<b>UstozShogird</b> — IT sohasida ustoz, shogird, hodim, ish joyi va sherik topish platformasi.\n\n"
            "Davom etish uchun telefon raqamingizni yuboring:",
            reply_markup=phone_keyboard
        )
        await RegisterState.phone.set()


@dp.message_handler(content_types=types.ContentType.CONTACT, state=RegisterState.phone)
async def get_phone(message: types.Message, state: FSMContext):
    db.set_user_phone(message.from_user.id, message.contact.phone_number)
    await state.finish()
    await message.answer(
        "✅ Ro'yxatdan o'tdingiz!\n\n"
        "Endi arizalar ko'rish yoki o'z arizangizni berish mumkin:",
        reply_markup=main_menu
    )


@dp.message_handler(state=RegisterState.phone)
async def get_phone_wrong(message: types.Message):
    await message.answer(
        "Iltimos, \"📱 Telefon raqamni yuborish\" tugmasini bosing.",
        reply_markup=phone_keyboard
    )
