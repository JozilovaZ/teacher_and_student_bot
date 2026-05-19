from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from keyboards.default.menu import main_menu, cancel_kb, skip_kb
from keyboards.default.panels import (
    ads_list_kb, ad_detail_kb, contact_kb, PAGE_SIZE, CATEGORY_LABELS
)
from loader import dp
from states.anketa import FilterState
from utils.db_api import database as db

BUTTON_TO_CATEGORY = {
    "🔍 Ustoz kerak":   "ustoz",
    "🎓 Shogird kerak": "shogird",
    "👔 Hodim kerak":   "hodim",
    "💼 Ish joyi kerak": "ish_joyi",
    "🤝 Sherik kerak":  "sherik",
}


def _not_registered(user) -> bool:
    return not user or not user['phone']


def ad_text(ad) -> str:
    cat_label = CATEGORY_LABELS.get(ad['category'], ad['category'])
    lines = [f"<b>{cat_label}</b>\n"]
    lines.append(f"👤 Ism: <b>{ad['fullname']}</b>")
    if ad['yosh']:
        lines.append(f"🎂 Yosh: {ad['yosh']}")
    lines.append(f"💻 Texnologiya/Soha: {ad['texno']}")
    lines.append(f"📍 Hudud: {ad['hudud']}")
    if ad['narx']:
        lines.append(f"💰 Narx/Maosh: {ad['narx']}")
    if ad['vaqt']:
        lines.append(f"🕐 Vaqt: {ad['vaqt']}")
    if ad['maqsad']:
        lines.append(f"📝 Tavsif: {ad['maqsad']}")
    lines.append(f"\n👁 Ko'rishlar: {ad['views']}")
    return "\n".join(lines)


async def show_category(message_or_call, category: str, offset: int = 0,
                        hudud: str = '', texno: str = ''):
    total = db.count_ads(category, hudud or None, texno or None)
    ads = db.get_ads(category, offset, PAGE_SIZE, hudud or None, texno or None)

    cat_label = CATEGORY_LABELS.get(category, category)

    if total == 0:
        text = f"<b>{cat_label}</b>\n\nHozircha arizalar yo'q."
    else:
        filter_info = ""
        if hudud:
            filter_info += f" | 📍 {hudud}"
        if texno:
            filter_info += f" | 💻 {texno}"
        text = (
            f"<b>{cat_label}</b>{filter_info}\n"
            f"Jami: <b>{total}</b> ta ariza\n"
            f"Ko'rsatilmoqda: {offset+1}–{min(offset+PAGE_SIZE, total)}"
        )

    kb = ads_list_kb(ads, category, offset, total, hudud, texno)

    if isinstance(message_or_call, types.Message):
        await message_or_call.answer(text, reply_markup=kb)
    else:
        await message_or_call.message.answer(text, reply_markup=kb)
        await message_or_call.answer()


@dp.message_handler(Text(equals=list(BUTTON_TO_CATEGORY.keys())), state="*")
async def category_browse(message: types.Message, state: FSMContext):
    await state.finish()
    user = db.get_user(message.from_user.id)
    if _not_registered(user):
        await message.answer("Avval /start orqali ro'yxatdan o'ting.")
        return

    category = BUTTON_TO_CATEGORY[message.text]
    await show_category(message, category)


@dp.callback_query_handler(lambda c: c.data.startswith("browse_"))
async def browse_page(call: types.CallbackQuery):
    parts = call.data.split("_", 4)
    # browse_{category}_{offset}_{hudud}_{texno}
    category = parts[1]
    offset   = int(parts[2])
    hudud    = parts[3] if len(parts) > 3 else ''
    texno    = parts[4] if len(parts) > 4 else ''
    await show_category(call, category, offset, hudud, texno)


@dp.callback_query_handler(lambda c: c.data.startswith("ad_"))
async def view_ad(call: types.CallbackQuery):
    ad_id = int(call.data.split("_")[1])
    ad = db.get_ad(ad_id)
    if not ad:
        await call.answer("Ariza topilmadi.")
        return

    db.increment_views(ad_id)

    contact = ad['aloqa']
    username = ad['user_username']
    contact_display = f"@{username}" if username else contact

    await call.message.answer(
        ad_text(ad),
        reply_markup=ad_detail_kb(ad_id, contact_display)
    )
    await call.answer()


@dp.callback_query_handler(lambda c: c.data.startswith("contact_"))
async def show_contact(call: types.CallbackQuery):
    ad_id = int(call.data.split("_")[1])
    ad = db.get_ad(ad_id)
    if not ad:
        await call.answer("Ariza topilmadi.")
        return

    username = ad['user_username']
    phone = ad['aloqa']

    await call.message.answer(
        f"📞 <b>Aloqa ma'lumotlari:</b>\n\n"
        f"Telefon: <code>{phone}</code>\n"
        + (f"Telegram: @{username}" if username else ""),
        reply_markup=contact_kb(phone, username)
    )
    await call.answer()


@dp.callback_query_handler(lambda c: c.data == "noop")
async def noop(call: types.CallbackQuery):
    await call.answer()


# ──────────────────────────────────────────────
# FILTR
# ──────────────────────────────────────────────

@dp.callback_query_handler(lambda c: c.data.startswith("filter_"))
async def filter_start(call: types.CallbackQuery, state: FSMContext):
    category = call.data.split("_")[1]
    await state.update_data(filter_category=category)
    await FilterState.hudud.set()
    await call.message.answer(
        "📍 Hudud bo'yicha filtrlash (viloyat yoki shahar nomi).\n"
        "O'tkazib yuborish uchun tugmani bosing:",
        reply_markup=skip_kb
    )
    await call.answer()


@dp.message_handler(state=FilterState.hudud)
async def filter_hudud(message: types.Message, state: FSMContext):
    hudud = '' if message.text == "⏭ O'tkazib yuborish" else message.text.strip()
    await state.update_data(filter_hudud=hudud)
    await FilterState.texno.set()
    await message.answer(
        "💻 Texnologiya bo'yicha filtrlash (masalan: Python, Django).\n"
        "O'tkazib yuborish uchun tugmani bosing:",
        reply_markup=skip_kb
    )


@dp.message_handler(state=FilterState.texno)
async def filter_texno(message: types.Message, state: FSMContext):
    texno = '' if message.text == "⏭ O'tkazib yuborish" else message.text.strip()
    data = await state.get_data()
    await state.finish()

    category = data.get('filter_category', 'ustoz')
    hudud    = data.get('filter_hudud', '')
    await show_category(message, category, 0, hudud, texno)
