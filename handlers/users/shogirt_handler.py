from aiogram import types
from aiogram.dispatcher import FSMContext

from data.config import ADMINS
from keyboards.default.menu import confirm_state, menu_start
from loader import dp, bot
from states.anketa import shogirtkkState
from utils.validators import (
    validate_fullname, validate_yosh, validate_texno, validate_aloqa,
    validate_hudud, validate_narx, validate_kasb, validate_vaqt, validate_maqsad
)


@dp.message_handler(text="Ustoz kerak")
async def shogirt_handler(message: types.Message):
    await message.answer(
        "Shogird topish uchun ariza berish\n\n"
        "Hozir sizga bir necha savollar beriladi.\n"
        "Har biriga javob bering.\n"
        "Oxirida to'g'ri bo'lsa <b>Ha</b> tugmasini bosing."
    )
    await message.answer("Ism familiyangizni kiriting:")
    await shogirtkkState.fullname.set()


@dp.message_handler(state=shogirtkkState.fullname)
async def shogirt_fullname(message: types.Message, state: FSMContext):
    ok, err = validate_fullname(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(fullname=message.text.strip())
    await shogirtkkState.yosh.set()
    await message.answer("Yoshingizni kiriting?\nMasalan: 25")


@dp.message_handler(state=shogirtkkState.yosh)
async def shogirt_yosh(message: types.Message, state: FSMContext):
    ok, err = validate_yosh(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(yosh=message.text.strip())
    await shogirtkkState.texno.set()
    await message.answer(
        "Qaysi texnologiyalardan dars berasiz?\n"
        "Vergul bilan ajrating. Masalan: Python, Django, SQL"
    )


@dp.message_handler(state=shogirtkkState.texno)
async def shogirt_texno(message: types.Message, state: FSMContext):
    ok, err = validate_texno(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(texno=message.text.strip())
    await shogirtkkState.aloqa.set()
    await message.answer("Aloqa uchun telefon raqamingiz:\nMasalan: +998 90 123 45 67")


@dp.message_handler(state=shogirtkkState.aloqa)
async def shogirt_aloqa(message: types.Message, state: FSMContext):
    ok, err = validate_aloqa(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(aloqa=message.text.strip())
    await shogirtkkState.hudud.set()
    await message.answer("Qaysi hududdansiz?\nViloyat yoki shahar nomini kiriting.")


@dp.message_handler(state=shogirtkkState.hudud)
async def shogirt_hudud(message: types.Message, state: FSMContext):
    ok, err = validate_hudud(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(hudud=message.text.strip())
    await shogirtkkState.narx.set()
    await message.answer("Dars narxi qancha?\nMasalan: 300 000 so'm / oy yoki Tekin")


@dp.message_handler(state=shogirtkkState.narx)
async def shogirt_narx(message: types.Message, state: FSMContext):
    ok, err = validate_narx(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(narx=message.text.strip())
    await shogirtkkState.kasb.set()
    await message.answer("Kasbingiz nima?\nMasalan: Dasturchi, Freelancer")


@dp.message_handler(state=shogirtkkState.kasb)
async def shogirt_kasb(message: types.Message, state: FSMContext):
    ok, err = validate_kasb(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(kasb=message.text.strip())
    await shogirtkkState.vaqt.set()
    await message.answer("Qaysi vaqtda dars o'tishingiz mumkin?\nMasalan: 9:00 - 18:00")


@dp.message_handler(state=shogirtkkState.vaqt)
async def shogirt_vaqt(message: types.Message, state: FSMContext):
    ok, err = validate_vaqt(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(vaqt=message.text.strip())
    await shogirtkkState.maqsad.set()
    await message.answer("Shogirdga nima o'rgatmoqchisiz? Qisqacha yozib bering:")


@dp.message_handler(state=shogirtkkState.maqsad)
async def shogirt_maqsad(message: types.Message, state: FSMContext):
    ok, err = validate_maqsad(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(maqsad=message.text.strip())

    data = await state.get_data()
    text = (
        "<b>Shogird kerak — ariza:</b>\n\n"
        f"🎓 Ism familiya: {data['fullname']}\n"
        f"🕑 Yosh: {data['yosh']}\n"
        f"📚 Texnologiya: {data['texno']}\n"
        f"📞 Aloqa: {data['aloqa']}\n"
        f"🌐 Hudud: {data['hudud']}\n"
        f"💰 Narx: {data['narx']}\n"
        f"👨‍💻 Kasb: {data['kasb']}\n"
        f"🕰 Dars vaqti: {data['vaqt']}\n"
        f"🔎 Maqsad: {data['maqsad']}\n"
    )
    await message.answer(text)
    await message.answer("Barcha ma'lumotlar to'g'rimi?", reply_markup=confirm_state)
    await shogirtkkState.confirm.set()


@dp.message_handler(state=shogirtkkState.confirm)
async def shogirt_confirm(message: types.Message, state: FSMContext):
    javob = message.text.lower()

    if javob == "ha":
        data = await state.get_data()
        text = (
            "<b>Shogird kerak — yangi ariza:</b>\n\n"
            f"🎓 Ism familiya: {data['fullname']}\n"
            f"🕑 Yosh: {data['yosh']}\n"
            f"📚 Texnologiya: {data['texno']}\n"
            f"📞 Aloqa: {data['aloqa']}\n"
            f"🌐 Hudud: {data['hudud']}\n"
            f"💰 Narx: {data['narx']}\n"
            f"👨‍💻 Kasb: {data['kasb']}\n"
            f"🕰 Dars vaqti: {data['vaqt']}\n"
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
