from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from keyboards.default.menu import main_menu
from loader import dp
from utils.db_api import database as db


@dp.message_handler(Text(equals="👤 Profilim"), state="*")
async def show_profile(message: types.Message, state: FSMContext):
    await state.finish()
    user = db.get_user(message.from_user.id)
    if not user:
        await message.answer("Avval /start orqali ro'yxatdan o'ting.")
        return

    ads = db.get_my_ads(message.from_user.id)
    active_ads = [a for a in ads if a['is_active']]

    username = f"@{user['username']}" if user['username'] else "—"
    phone = user['phone'] or "—"

    await message.answer(
        f"👤 <b>Profilim</b>\n\n"
        f"Ism: <b>{user['full_name']}</b>\n"
        f"Telegram: {username}\n"
        f"Telefon: <code>{phone}</code>\n"
        f"Ro'yxatdan: {user['created_at']}\n\n"
        f"📋 Jami arizalar: <b>{len(ads)}</b> ta\n"
        f"✅ Faol arizalar: <b>{len(active_ads)}</b> ta",
        reply_markup=main_menu
    )
