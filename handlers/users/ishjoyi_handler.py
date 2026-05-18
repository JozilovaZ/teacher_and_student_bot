from aiogram import types
from aiogram.dispatcher import FSMContext

from data.config import ADMINS
from keyboards.default.menu import confirm_state, menu_start
from loader import dp, bot
from states.anketa import Ishjoyikerak
from utils.validators import (
    validate_fullname, validate_yosh, validate_texno, validate_aloqa,
    validate_hudud, validate_maosh, validate_kasb, validate_vaqt, validate_maqsad
)


@dp.message_handler(text="Ish joyi kerak")
async def ishjoyi_handler(message: types.Message):
    await message.answer(
        "Ish joyi topish uchun ariza berish\n\n"
        "Hozir sizga bir necha savollar beriladi.\n"
        "Har biriga javob bering.\n"
        "Oxirida to'g'ri bo'lsa <b>Ha</b> tugmasini bosing."
    )
    await message.answer("Ism familiyangizni kiriting:")
    await Ishjoyikerak.full_name.set()


@dp.message_handler(state=Ishjoyikerak.full_name)
async def ishjoyi_full_name(message: types.Message, state: FSMContext):
    ok, err = validate_fullname(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(fullname=message.text.strip())
    await Ishjoyikerak.yosh.set()
    await message.answer("Yoshingizni kiriting:\nMasalan: 22")


@dp.message_handler(state=Ishjoyikerak.yosh)
async def ishjoyi_yosh(message: types.Message, state: FSMContext):
    ok, err = validate_yosh(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(yosh=message.text.strip())
    await Ishjoyikerak.texno.set()
    await message.answer(
        "Qaysi texnologiyalarni bilasiz?\n"
        "Vergul bilan ajrating. Masalan: Python, Django, SQL"
    )


@dp.message_handler(state=Ishjoyikerak.texno)
async def ishjoyi_texno(message: types.Message, state: FSMContext):
    ok, err = validate_texno(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(texnologiya=message.text.strip())
    await Ishjoyikerak.aloqa.set()
    await message.answer("Aloqa uchun telefon raqamingiz:\nMasalan: +998 90 123 45 67")


@dp.message_handler(state=Ishjoyikerak.aloqa)
async def ishjoyi_aloqa(message: types.Message, state: FSMContext):
    ok, err = validate_aloqa(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(aloqa=message.text.strip())
    await Ishjoyikerak.hudud.set()
    await message.answer("Qaysi hududdansiz?\nViloyat yoki shahar nomini kiriting.")


@dp.message_handler(state=Ishjoyikerak.hudud)
async def ishjoyi_hudud(message: types.Message, state: FSMContext):
    ok, err = validate_hudud(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(hudud=message.text.strip())
    await Ishjoyikerak.narx.set()
    await message.answer("Kutilayotgan maosh:\nMasalan: 3 000 000 so'm / oy yoki Kelishamiz")


@dp.message_handler(state=Ishjoyikerak.narx)
async def ishjoyi_narx(message: types.Message, state: FSMContext):
    ok, err = validate_maosh(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(narx=message.text.strip())
    await Ishjoyikerak.kasb.set()
    await message.answer("Kasbingiz yoki lavozimingiz:\nMasalan: Backend dasturchi, Talaba")


@dp.message_handler(state=Ishjoyikerak.kasb)
async def ishjoyi_kasb(message: types.Message, state: FSMContext):
    ok, err = validate_kasb(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(kasb=message.text.strip())
    await Ishjoyikerak.vaqt.set()
    await message.answer("Qaysi vaqtda ishlashingiz mumkin?\nMasalan: 9:00 - 18:00, To'liq kun")


@dp.message_handler(state=Ishjoyikerak.vaqt)
async def ishjoyi_vaqt(message: types.Message, state: FSMContext):
    ok, err = validate_vaqt(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(vaqt=message.text.strip())
    await Ishjoyikerak.maqsad.set()
    await message.answer("Maqsadingizni qisqacha yozib bering:")


@dp.message_handler(state=Ishjoyikerak.maqsad)
async def ishjoyi_maqsad(message: types.Message, state: FSMContext):
    ok, err = validate_maqsad(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(maqsad=message.text.strip())

    data = await state.get_data()
    text = (
        "<b>Ish joyi kerak — ariza:</b>\n\n"
        f"👤 Ism familiya: {data['fullname']}\n"
        f"🕑 Yosh: {data['yosh']}\n"
        f"📚 Texnologiya: {data['texnologiya']}\n"
        f"📞 Aloqa: {data['aloqa']}\n"
        f"🌐 Hudud: {data['hudud']}\n"
        f"💰 Kutilayotgan maosh: {data['narx']}\n"
        f"👨‍💻 Kasb: {data['kasb']}\n"
        f"🕰 Ish vaqti: {data['vaqt']}\n"
        f"🔎 Maqsad: {data['maqsad']}\n"
    )
    await message.answer(text)
    await message.answer("Barcha ma'lumotlar to'g'rimi?", reply_markup=confirm_state)
    await Ishjoyikerak.confirm.set()


@dp.message_handler(state=Ishjoyikerak.confirm)
async def ishjoyi_confirm(message: types.Message, state: FSMContext):
    javob = message.text.lower()

    if javob == "ha":
        data = await state.get_data()
        text = (
            "<b>Ish joyi kerak — yangi ariza:</b>\n\n"
            f"👤 Ism familiya: {data['fullname']}\n"
            f"🕑 Yosh: {data['yosh']}\n"
            f"📚 Texnologiya: {data['texnologiya']}\n"
            f"📞 Aloqa: {data['aloqa']}\n"
            f"🌐 Hudud: {data['hudud']}\n"
            f"💰 Kutilayotgan maosh: {data['narx']}\n"
            f"👨‍💻 Kasb: {data['kasb']}\n"
            f"🕰 Ish vaqti: {data['vaqt']}\n"
            f"🔎 Maqsad: {data['maqsad']}\n"
        )
        for admin_id in ADMINS:
            try:
                await bot.send_message(admin_id, text)
            except Exception:
                pass
        await state.finish()
        await message.answer("Arizangiz adminga yuborildi!", reply_markup=menu_start)

    elif javob == "yo`q":
        await state.finish()
        await message.answer("Ariza bekor qilindi.", reply_markup=menu_start)
    else:
        await message.answer("Iltimos, Ha yoki Yo`q deb javob bering.")
