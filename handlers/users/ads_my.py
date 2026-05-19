from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from keyboards.default.menu import main_menu
from keyboards.default.panels import my_ads_kb, my_ad_manage_kb, CATEGORY_LABELS
from loader import dp
from utils.db_api import database as db


@dp.message_handler(Text(equals="📁 Mening arizalarim"), state="*")
async def my_ads(message: types.Message, state: FSMContext):
    await state.finish()
    user = db.get_user(message.from_user.id)
    if not user or not user['phone']:
        await message.answer("Avval /start orqali ro'yxatdan o'ting.")
        return

    ads = db.get_my_ads(message.from_user.id)
    if not ads:
        await message.answer(
            "Sizda hali ariza yo'q.\n\n"
            "Ariza berish uchun \"📋 Ariza berish\" tugmasini bosing.",
            reply_markup=main_menu
        )
        return

    await message.answer(
        f"Sizning arizalaringiz (<b>{len(ads)}</b> ta).\n"
        "Boshqarish uchun tanlang:",
        reply_markup=my_ads_kb(ads)
    )


@dp.callback_query_handler(lambda c: c.data.startswith("myad_") and
                            not c.data.startswith("myad_off_") and
                            not c.data.startswith("myad_on_") and
                            not c.data.startswith("myad_del_") and
                            c.data != "myad_back")
async def my_ad_detail(call: types.CallbackQuery):
    ad_id = int(call.data.split("_")[1])
    ad = db.get_ad(ad_id)
    if not ad:
        await call.answer("Ariza topilmadi.")
        return

    cat_label = CATEGORY_LABELS.get(ad['category'], ad['category'])
    status = "✅ Faol" if ad['is_active'] else "⏸ To'xtatilgan"
    text = (
        f"<b>{cat_label}</b>\n\n"
        f"👤 {ad['fullname']}\n"
        f"💻 {ad['texno']}\n"
        f"📍 {ad['hudud']}\n"
        f"📞 {ad['aloqa']}\n"
        f"👁 Ko'rishlar: {ad['views']}\n"
        f"Holat: {status}"
    )
    await call.message.answer(text, reply_markup=my_ad_manage_kb(ad_id, ad['is_active']))
    await call.answer()


@dp.callback_query_handler(lambda c: c.data.startswith("myad_off_"))
async def my_ad_deactivate(call: types.CallbackQuery):
    ad_id = int(call.data.split("_")[2])
    db.toggle_ad(ad_id, 0)
    await call.message.edit_reply_markup()
    await call.message.answer("⏸ Ariza to'xtatildi. Yana faollashtirish mumkin.")
    await call.answer()


@dp.callback_query_handler(lambda c: c.data.startswith("myad_on_"))
async def my_ad_activate(call: types.CallbackQuery):
    ad_id = int(call.data.split("_")[2])
    db.toggle_ad(ad_id, 1)
    await call.message.edit_reply_markup()
    await call.message.answer("▶️ Ariza faollashtirildi!")
    await call.answer()


@dp.callback_query_handler(lambda c: c.data.startswith("myad_del_"))
async def my_ad_delete(call: types.CallbackQuery):
    ad_id = int(call.data.split("_")[2])
    db.delete_ad(ad_id)
    await call.message.edit_reply_markup()
    await call.message.answer("🗑 Ariza o'chirildi.")
    await call.answer()


@dp.callback_query_handler(lambda c: c.data == "myad_back")
async def my_ad_back(call: types.CallbackQuery):
    ads = db.get_my_ads(call.from_user.id)
    if not ads:
        await call.message.answer("Arizalar yo'q.", reply_markup=main_menu)
    else:
        await call.message.answer(
            f"Sizning arizalaringiz (<b>{len(ads)}</b> ta):",
            reply_markup=my_ads_kb(ads)
        )
    await call.answer()
