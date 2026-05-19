import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from data.config import ADMINS
from keyboards.default.menu import main_menu
from keyboards.default.panels import admin_users_kb, admin_user_action_kb, CATEGORY_LABELS
from loader import dp, bot
from states.admin import BroadcastState
from utils.db_api import database as db


def is_admin(telegram_id: int) -> bool:
    return str(telegram_id) in ADMINS


# ──────────────────────────────────────────────
# KIRISH
# ──────────────────────────────────────────────

@dp.message_handler(commands=["admin"], state="*")
async def admin_panel(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("Sizda ruxsat yo'q.")
        return
    await state.finish()
    from keyboards.default.admin_menu import admin_menu
    await message.answer("Admin panel:", reply_markup=admin_menu)


# ──────────────────────────────────────────────
# STATISTIKA
# ──────────────────────────────────────────────

@dp.message_handler(Text(equals="Statistika"), state=None)
async def admin_stats(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    s = db.get_stats()
    cats = s['cats']
    cat_lines = "\n".join(
        f"   {CATEGORY_LABELS.get(k, k)}: <b>{v}</b>"
        for k, v in cats.items()
    )
    text = (
        "<b>Bot statistikasi</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{s['total_users']}</b>\n\n"
        f"📋 Faol arizalar: <b>{s['total_ads']}</b>\n"
        f"{cat_lines}"
    )
    await message.answer(text)


# ──────────────────────────────────────────────
# FOYDALANUVCHILAR
# ──────────────────────────────────────────────

@dp.message_handler(Text(equals="Foydalanuvchilar"), state=None)
async def admin_users(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    users = db.get_all_users()
    if not users:
        await message.answer("Foydalanuvchilar yo'q.")
        return
    await message.answer(
        f"Jami {len(users)} ta foydalanuvchi:",
        reply_markup=admin_users_kb(users)
    )


@dp.callback_query_handler(lambda c: c.data.startswith("auser_"))
async def admin_user_detail(call: types.CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("Ruxsat yo'q.")
        return
    try:
        telegram_id = int(call.data.split("_")[1])
    except (IndexError, ValueError):
        return

    user = db.get_user(telegram_id)
    if not user:
        await call.answer("Foydalanuvchi topilmadi.")
        return

    username = f"@{user['username']}" if user['username'] else "—"
    phone = user['phone'] or "—"
    ads = db.get_my_ads(telegram_id)
    status = "🚫 Bloklangan" if user['role'] == 'blocked' else "✅ Faol"

    text = (
        f"👤 <b>{user['full_name']}</b>\n\n"
        f"ID: <code>{user['telegram_id']}</code>\n"
        f"Username: {username}\n"
        f"Telefon: {phone}\n"
        f"Holat: {status}\n"
        f"Arizalar: {len(ads)} ta\n"
        f"Ro'yxatdan: {user['created_at']}"
    )
    await call.message.answer(
        text,
        reply_markup=admin_user_action_kb(telegram_id, user['role'])
    )
    await call.answer()


@dp.callback_query_handler(lambda c: c.data.startswith("ablock_"))
async def admin_block_user(call: types.CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("Ruxsat yo'q.")
        return
    telegram_id = int(call.data.split("_")[1])
    db.block_user(telegram_id)
    await call.message.edit_reply_markup()
    await call.message.answer("🚫 Foydalanuvchi bloklandi.")
    try:
        await bot.send_message(telegram_id, "Hisobingiz bloklandi. Admin bilan bog'laning.")
    except Exception:
        pass
    await call.answer()


@dp.callback_query_handler(lambda c: c.data.startswith("aunblock_"))
async def admin_unblock_user(call: types.CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("Ruxsat yo'q.")
        return
    telegram_id = int(call.data.split("_")[1])
    db.unblock_user(telegram_id)
    await call.message.edit_reply_markup()
    await call.message.answer("✅ Foydalanuvchi blokdan chiqarildi.")
    try:
        await bot.send_message(telegram_id, "Hisobingiz tiklandi!", reply_markup=main_menu)
    except Exception:
        pass
    await call.answer()


# ──────────────────────────────────────────────
# ARIZALAR (ADMIN)
# ──────────────────────────────────────────────

@dp.message_handler(Text(equals="Arizalar (admin)"), state=None)
async def admin_ads(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    ads = db.get_all_ads_admin()
    if not ads:
        await message.answer("Hozircha arizalar yo'q.")
        return

    lines = [f"<b>Barcha arizalar ({len(ads)} ta):</b>\n"]
    for ad in ads[:30]:
        cat = CATEGORY_LABELS.get(ad['category'], ad['category'])
        status = "✅" if ad['is_active'] else "⏸"
        lines.append(f"{status} [{cat}] {ad['fullname']} | {ad['user_name']} | 👁{ad['views']}")

    if len(ads) > 30:
        lines.append(f"\n... va yana {len(ads)-30} ta")

    await message.answer("\n".join(lines))


# ──────────────────────────────────────────────
# BROADCAST
# ──────────────────────────────────────────────

@dp.message_handler(Text(equals="Broadcast"), state=None)
async def broadcast_start(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    user_ids = db.get_all_users_telegram_ids()
    await message.answer(
        f"Barcha foydalanuvchilarga ({len(user_ids)} ta) xabar yuborasiz.\n\n"
        "Xabar yozing (matn, rasm, hujjat — barchasi qabul qilinadi):"
    )
    await BroadcastState.message.set()


@dp.message_handler(content_types=types.ContentType.ANY, state=BroadcastState.message)
async def broadcast_preview(message: types.Message, state: FSMContext):
    await state.update_data(msg_id=message.message_id, chat_id=message.chat.id)
    await BroadcastState.confirm.set()

    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Ha"), KeyboardButton(text="Yo`q")]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await message.answer("Xabar ko'rinishi yuqorida. Yuborishni tasdiqlaysizmi?", reply_markup=kb)


@dp.message_handler(Text(equals="Ha"), state=BroadcastState.confirm)
async def broadcast_send(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.finish()

    user_ids = db.get_all_users_telegram_ids()
    sent, failed = 0, 0
    from keyboards.default.admin_menu import admin_menu
    status_msg = await message.answer(f"Yuborilmoqda... 0/{len(user_ids)}", reply_markup=admin_menu)

    for i, uid in enumerate(user_ids, 1):
        try:
            await bot.copy_message(chat_id=uid, from_chat_id=data['chat_id'], message_id=data['msg_id'])
            sent += 1
        except Exception:
            failed += 1
        if i % 20 == 0:
            try:
                await status_msg.edit_text(f"Yuborilmoqda... {i}/{len(user_ids)}")
            except Exception:
                pass
        await asyncio.sleep(0.05)

    try:
        await status_msg.edit_text(f"✅ Broadcast yakunlandi!\n\nYuborildi: {sent}\nXato: {failed}")
    except Exception:
        await message.answer(f"✅ Broadcast yakunlandi!\n\nYuborildi: {sent}\nXato: {failed}")


@dp.message_handler(Text(equals="Yo`q"), state=BroadcastState.confirm)
async def broadcast_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    from keyboards.default.admin_menu import admin_menu
    await message.answer("Broadcast bekor qilindi.", reply_markup=admin_menu)
