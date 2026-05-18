from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher.filters import Text

from keyboards.default.menu import menu_start, phone_keyboard
from keyboards.default.panels import role_keyboard, ustoz_menu, shogird_menu
from loader import dp
from states.anketa import RegisterState
from states.panel import RoleSelectState
from utils.db_api import database as db


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    user = db.get_user(message.from_user.id)

    if user:
        if user['role'] == 'teacher':
            await message.answer(
                f"Xush kelibsiz, <b>{user['full_name']}</b>!\nUstoz paneli:",
                reply_markup=ustoz_menu
            )
        elif user['role'] == 'student':
            await message.answer(
                f"Xush kelibsiz, <b>{user['full_name']}</b>!\nShogird paneli:",
                reply_markup=shogird_menu
            )
        else:
            await message.answer(
                f"Xush kelibsiz, <b>{user['full_name']}</b>!\nMenyudan tanlang:",
                reply_markup=menu_start
            )
    else:
        await message.answer(
            f"Assalom alaykum, <b>{message.from_user.full_name}</b>!\n\n"
            "UstozShogird botiga xush kelibsiz!\n\n"
            "Ro'yxatdan o'tish uchun telefon raqamingizni yuboring:",
            reply_markup=phone_keyboard
        )
        await RegisterState.phone.set()


@dp.message_handler(content_types=types.ContentType.CONTACT, state=RegisterState.phone)
async def get_phone_contact(message: types.Message, state: FSMContext):
    db.add_user(
        telegram_id=message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username,
    )
    db.set_user_phone(message.from_user.id, message.contact.phone_number)
    await state.finish()

    await message.answer(
        "Ro'yxatdan o'tdingiz!\n\nRolingizni tanlang:",
        reply_markup=role_keyboard
    )
    await RoleSelectState.role.set()


@dp.message_handler(state=RegisterState.phone)
async def get_phone_wrong(message: types.Message):
    await message.answer(
        "Iltimos, \"Telefon raqamni yuborish\" tugmasini bosing.",
        reply_markup=phone_keyboard
    )


@dp.message_handler(Text(equals=["Ustoz", "Shogird"]), state=RoleSelectState.role)
async def choose_role(message: types.Message, state: FSMContext):
    role = "teacher" if message.text == "Ustoz" else "student"
    db.set_user_role(message.from_user.id, role)
    await state.finish()

    if role == "teacher":
        await message.answer(
            "Siz ustoz sifatida ro'yxatdan o'tdingiz!\nUstoz paneli:",
            reply_markup=ustoz_menu
        )
    else:
        await message.answer(
            "Siz shogird sifatida ro'yxatdan o'tdingiz!\nShogird paneli:",
            reply_markup=shogird_menu
        )


@dp.message_handler(state=RoleSelectState.role)
async def choose_role_wrong(message: types.Message):
    await message.answer(
        "Iltimos, Ustoz yoki Shogird deb tanlang.",
        reply_markup=role_keyboard
    )
