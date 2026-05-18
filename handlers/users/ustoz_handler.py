from aiogram import types
from aiogram.dispatcher import FSMContext

from data.config import ADMINS
from keyboards.default.menu import confirm_state, menu_start
from loader import dp, bot
from states.anketa import ustozState
from utils.validators import (
    validate_fullname, validate_yosh, validate_texno, validate_aloqa,
    validate_hudud, validate_narx, validate_kasb, validate_vaqt, validate_maqsad
)


@dp.message_handler(text="Shogird kerak")
async def ustoz_handler(message: types.Message):
    await message.answer(
        "Ustoz topish uchun ariza berish\n\n"
        "Hozir sizga bir necha savollar beriladi.\n"
        "Har biriga javob bering.\n"
        "Oxirida to'g'ri bo'lsa <b>Ha</b> tugmasini bosing."
    )
    await message.answer("Ism familiyangizni kiriting:")
    await ustozState.fullname.set()


@dp.message_handler(state=ustozState.fullname)
async def ustoz_fullname(message: types.Message, state: FSMContext):
    ok, err = validate_fullname(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(fullname=message.text.strip())
    await ustozState.yosh.set()
    await message.answer("Yoshingizni kiriting?\nMasalan: 19")


@dp.message_handler(state=ustozState.yosh)
async def ustoz_yosh(message: types.Message, state: FSMContext):
    ok, err = validate_yosh(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(yosh=message.text.strip())
    await ustozState.texno.set()
    await message.answer(
        "Qaysi texnologiyalarni o'rganmoqchisiz?\n"
        "Vergul bilan ajrating. Masalan: Python, Django, SQL"
    )


@dp.message_handler(state=ustozState.texno)
async def ustoz_texno(message: types.Message, state: FSMContext):
    ok, err = validate_texno(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(texno=message.text.strip())
    await ustozState.aloqa.set()
    await message.answer("Aloqa uchun telefon raqamingiz:\nMasalan: +998 90 123 45 67")


@dp.message_handler(state=ustozState.aloqa)
async def ustoz_aloqa(message: types.Message, state: FSMContext):
    ok, err = validate_aloqa(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(aloqa=message.text.strip())
    await ustozState.hudud.set()
    await message.answer("Qaysi hududdansiz?\nViloyat yoki shahar nomini kiriting.")


@dp.message_handler(state=ustozState.hudud)
async def ustoz_hudud(message: types.Message, state: FSMContext):
    ok, err = validate_hudud(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(hudud=message.text.strip())
    await ustozState.narx.set()
    await message.answer("To'lov qilasizmi yoki tekinmi?\nKerak bo'lsa summasini kiriting.")


@dp.message_handler(state=ustozState.narx)
async def ustoz_narx(message: types.Message, state: FSMContext):
    ok, err = validate_narx(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(narx=message.text.strip())
    await ustozState.kasb.set()
    await message.answer("Ishlaysizmi yoki o'qiysizmi?\nMasalan: Talaba")


@dp.message_handler(state=ustozState.kasb)
async def ustoz_kasb(message: types.Message, state: FSMContext):
    ok, err = validate_kasb(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(kasb=message.text.strip())
    await ustozState.vaqt.set()
    await message.answer("Qaysi vaqtda murojaat qilish mumkin?\nMasalan: 9:00 - 18:00")


@dp.message_handler(state=ustozState.vaqt)
async def ustoz_vaqt(message: types.Message, state: FSMContext):
    ok, err = validate_vaqt(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(vaqt=message.text.strip())
    await ustozState.maqsad.set()
    await message.answer("Maqsadingizni qisqacha yozib bering:")


@dp.message_handler(state=ustozState.maqsad)
async def ustoz_maqsad(message: types.Message, state: FSMContext):
    ok, err = validate_maqsad(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(maqsad=message.text.strip())

    data = await state.get_data()
    text = (
        "<b>Ustoz kerak — ariza:</b>\n\n"
        f"🎓 Ism familiya: {data['fullname']}\n"
        f"🕑 Yosh: {data['yosh']}\n"
        f"📚 Texnologiya: {data['texno']}\n"
        f"📞 Aloqa: {data['aloqa']}\n"
        f"🌐 Hudud: {data['hudud']}\n"
        f"💰 Narx: {data['narx']}\n"
        f"👨‍💻 Kasb: {data['kasb']}\n"
        f"🕰 Murojaat vaqti: {data['vaqt']}\n"
        f"🔎 Maqsad: {data['maqsad']}\n"
    )
    await message.answer(text)
    await message.answer("Barcha ma'lumotlar to'g'rimi?", reply_markup=confirm_state)
    await ustozState.confirm.set()


@dp.message_handler(state=ustozState.confirm)
async def ustoz_confirm(message: types.Message, state: FSMContext):
    javob = message.text.lower()

    if javob == "ha":
        data = await state.get_data()
        text = (
            "<b>Ustoz kerak — yangi ariza:</b>\n\n"
            f"🎓 Ism familiya: {data['fullname']}\n"
            f"🕑 Yosh: {data['yosh']}\n"
            f"📚 Texnologiya: {data['texno']}\n"
            f"📞 Aloqa: {data['aloqa']}\n"
            f"🌐 Hudud: {data['hudud']}\n"
            f"💰 Narx: {data['narx']}\n"
            f"👨‍💻 Kasb: {data['kasb']}\n"
            f"🕰 Murojaat vaqti: {data['vaqt']}\n"
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
