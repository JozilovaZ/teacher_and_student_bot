import asyncio
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from data.config import ADMINS
from keyboards.default.admin_menu import (
    admin_menu, users_filter_kb,
    user_detail_kb, admin_lessons_kb, confirm_delete_kb
)
from keyboards.default.panels import ustoz_menu, shogird_menu
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
    await message.answer("Admin panel:", reply_markup=admin_menu)


# ──────────────────────────────────────────────
# STATISTIKA
# ──────────────────────────────────────────────

@dp.message_handler(Text(equals="Statistika"), state=None)
async def admin_stats(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    s = db.get_stats()
    text = (
        "<b>Bot statistikasi</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{s['total_users']}</b>\n"
        f"   👨‍🏫 Ustozlar: <b>{s['teachers']}</b>\n"
        f"   🎓 Shogirdlar: <b>{s['students']}</b>\n\n"
        f"📚 Darslar: <b>{s['lessons']}</b>\n"
        f"📝 Topshiriqlar: <b>{s['assignments']}</b>\n"
        f"📨 Yuborilgan javoblar: <b>{s['submissions']}</b>\n"
        f"✅ Baholangan javoblar: <b>{s['graded']}</b>"
    )
    await message.answer(text)


# ──────────────────────────────────────────────
# FOYDALANUVCHILAR
# ──────────────────────────────────────────────

@dp.message_handler(Text(equals="Foydalanuvchilar"), state=None)
async def admin_users(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Qaysi guruhni ko'rmoqchisiz?", reply_markup=users_filter_kb)


@dp.callback_query_handler(lambda c: c.data.startswith("afilter_"))
async def admin_users_filter(call: types.CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("Ruxsat yo'q.")
        return

    filt = call.data.split("_")[1]
    users = db.get_all_users()

    if filt == "teacher":
        users = [u for u in users if u["role"] == "teacher"]
        title = "Ustozlar"
    elif filt == "student":
        users = [u for u in users if u["role"] == "student"]
        title = "Shogirdlar"
    else:
        title = "Barcha foydalanuvchilar"

    if not users:
        await call.message.answer("Hozircha foydalanuvchilar yo'q.")
        await call.answer()
        return

    # 30 tadan ko'p bo'lsa qisqartirish
    shown = users[:30]
    lines = [f"<b>{title}</b> ({len(users)} ta):\n"]
    for u in shown:
        username = f"@{u['username']}" if u['username'] else "—"
        role_icon = {"teacher": "👨‍🏫", "student": "🎓", "blocked": "🚫"}.get(u["role"], "👤")
        lines.append(f"{role_icon} <b>{u['full_name']}</b> | {username} | /auser_{u['telegram_id']}")

    if len(users) > 30:
        lines.append(f"\n... va yana {len(users) - 30} ta")

    await call.message.answer("\n".join(lines))
    await call.answer()


@dp.message_handler(lambda m: m.text and m.text.startswith("/auser_"), state=None)
async def admin_user_detail(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    try:
        telegram_id = int(message.text.split("_")[1])
    except (IndexError, ValueError):
        return

    user = db.get_user(telegram_id)
    if not user:
        await message.answer("Foydalanuvchi topilmadi.")
        return

    role_names = {"teacher": "Ustoz", "student": "Shogird", "blocked": "Bloklangan"}
    role_text = role_names.get(user["role"], user["role"])
    username = f"@{user['username']}" if user['username'] else "—"
    phone = user['phone'] or "—"

    text = (
        f"👤 <b>{user['full_name']}</b>\n\n"
        f"Telegram ID: <code>{user['telegram_id']}</code>\n"
        f"Username: {username}\n"
        f"Telefon: {phone}\n"
        f"Rol: {role_text}\n"
        f"Ro'yxatdan: {user['created_at']}"
    )
    await message.answer(text, reply_markup=user_detail_kb(telegram_id, user["role"]))


@dp.callback_query_handler(lambda c: c.data.startswith("aset_") or
                                      c.data.startswith("ablock_") or
                                      c.data.startswith("aunblock_"))
async def admin_user_action(call: types.CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("Ruxsat yo'q.")
        return

    parts = call.data.split("_")
    action = parts[0]

    if action == "aset":
        new_role = parts[1]
        telegram_id = int(parts[2])
        db.set_user_role(telegram_id, new_role)
        role_name = "Ustoz" if new_role == "teacher" else "Shogird"
        await call.message.edit_reply_markup()
        await call.message.answer(f"Rol o'zgartirildi: {role_name}")

        # Foydalanuvchiga xabar
        try:
            menu = ustoz_menu if new_role == "teacher" else shogird_menu
            label = "ustoz" if new_role == "teacher" else "shogird"
            await bot.send_message(
                telegram_id,
                f"Sizning rolingiz <b>{label}</b> ga o'zgartirildi.",
                reply_markup=menu
            )
        except Exception:
            pass

    elif action == "ablock":
        telegram_id = int(parts[1])
        db.block_user(telegram_id)
        await call.message.edit_reply_markup()
        await call.message.answer("Foydalanuvchi bloklandi.")
        try:
            await bot.send_message(telegram_id, "Hisobingiz bloklandi. Admin bilan bog'laning.")
        except Exception:
            pass

    elif action == "aunblock":
        role = parts[1]
        telegram_id = int(parts[2])
        db.unblock_user(telegram_id, role)
        await call.message.edit_reply_markup()
        await call.message.answer("Foydalanuvchi blokdan chiqarildi.")
        try:
            await bot.send_message(telegram_id, "Hisobingiz tiklandi!")
        except Exception:
            pass

    await call.answer()


# ──────────────────────────────────────────────
# DARSLAR (ADMIN)
# ──────────────────────────────────────────────

@dp.message_handler(Text(equals="Darslar (admin)"), state=None)
async def admin_lessons(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    lessons = db.get_all_lessons()
    if not lessons:
        await message.answer("Hozircha darslar yo'q.")
        return
    await message.answer(
        f"Barcha darslar ({len(lessons)} ta).\nO'chirish uchun tanlang:",
        reply_markup=admin_lessons_kb(lessons)
    )


@dp.callback_query_handler(lambda c: c.data.startswith("adlesson_"))
async def admin_lesson_detail(call: types.CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("Ruxsat yo'q.")
        return

    lesson_id = int(call.data.split("_")[1])
    lesson = db.get_lesson(lesson_id)
    if not lesson:
        await call.answer("Dars topilmadi.")
        return

    assignments = db.get_assignments_by_lesson(lesson_id)
    text = (
        f"📚 <b>{lesson['title']}</b>\n\n"
        f"{lesson['description'] or ''}\n\n"
        f"Topshiriqlar: {len(assignments)} ta\n"
        f"Dars ID: {lesson_id}"
    )
    await call.message.answer(text, reply_markup=confirm_delete_kb(lesson_id))
    await call.answer()


@dp.callback_query_handler(lambda c: c.data.startswith("adel_"))
async def admin_lesson_delete(call: types.CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("Ruxsat yo'q.")
        return

    if call.data == "adel_cancel":
        await call.message.edit_reply_markup()
        await call.answer("Bekor qilindi.")
        return

    lesson_id = int(call.data.split("_")[2])
    db.delete_lesson(lesson_id)
    await call.message.edit_reply_markup()
    await call.message.answer("Dars o'chirildi.")
    await call.answer()


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
        "Xabar matnini yozing (matn, rasm, hujjat — barchasi qabul qilinadi):"
    )
    await BroadcastState.message.set()


@dp.message_handler(
    content_types=types.ContentType.ANY,
    state=BroadcastState.message
)
async def broadcast_preview(message: types.Message, state: FSMContext):
    await state.update_data(
        msg_id=message.message_id,
        chat_id=message.chat.id
    )
    await BroadcastState.confirm.set()

    from keyboards.default.menu import confirm_state
    await message.answer(
        "Xabar ko'rinishi yuqorida. Yuborishni tasdiqlaysizmi?",
        reply_markup=confirm_state
    )


@dp.message_handler(Text(equals="Ha"), state=BroadcastState.confirm)
async def broadcast_send(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.finish()

    user_ids = db.get_all_users_telegram_ids()
    sent = 0
    failed = 0

    status_msg = await message.answer(f"Yuborilmoqda... 0/{len(user_ids)}", reply_markup=admin_menu)

    for i, uid in enumerate(user_ids, 1):
        try:
            await bot.copy_message(
                chat_id=uid,
                from_chat_id=data['chat_id'],
                message_id=data['msg_id']
            )
            sent += 1
        except Exception:
            failed += 1

        if i % 20 == 0:
            try:
                await status_msg.edit_text(f"Yuborilmoqda... {i}/{len(user_ids)}")
            except Exception:
                pass

        await asyncio.sleep(0.05)

    result_text = (
        f"Broadcast yakunlandi!\n\n"
        f"✅ Yuborildi: {sent}\n"
        f"❌ Xato: {failed}"
    )
    try:
        await status_msg.edit_text(result_text)
    except Exception:
        await message.answer(result_text, reply_markup=admin_menu)


@dp.message_handler(Text(equals="Yo`q"), state=BroadcastState.confirm)
async def broadcast_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Broadcast bekor qilindi.", reply_markup=admin_menu)
