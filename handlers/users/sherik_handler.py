from aiogram import types
from aiogram.dispatcher import FSMContext

from data.config import ADMINS
from keyboards.default.menu import confirm_state, menu_start
from loader import dp, bot
from states.anketa import SherikState
from utils.validators import (
    validate_fullname, validate_texno, validate_aloqa, validate_hudud,
    validate_narx, validate_kasb, validate_murojat, validate_maqsad
)


@dp.message_handler(text="Sherik kerak")
async def sherik_handler(message: types.Message):
    await message.answer(
        "Sherik topish uchun ariza berish\n\n"
        "Hozir sizga bir necha savollar beriladi.\n"
        "Har biriga javob bering.\n"
        "Oxirida to'g'ri bo'lsa <b>Ha</b> tugmasini bosing."
    )
    await message.answer("Ism familiyangizni kiriting:")
    await SherikState.full_name.set()


@dp.message_handler(state=SherikState.full_name)
async def sherik_full_name(message: types.Message, state: FSMContext):
    ok, err = validate_fullname(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(fullname=message.text.strip())
    await SherikState.texno.set()
    await message.answer(
        "Qaysi texnologiyalarda sherik qidiryapsiz?\n"
        "Vergul bilan ajrating. Masalan: Python, Django, SQL"
    )


@dp.message_handler(state=SherikState.texno)
async def sherik_texno(message: types.Message, state: FSMContext):
    ok, err = validate_texno(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(texnologiya=message.text.strip())
    await SherikState.aloqa.set()
    await message.answer("Aloqa uchun telefon raqamingiz:\nMasalan: +998 90 123 45 67")


@dp.message_handler(state=SherikState.aloqa)
async def sherik_aloqa(message: types.Message, state: FSMContext):
    ok, err = validate_aloqa(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(aloqa=message.text.strip())
    await SherikState.hudud.set()
    await message.answer("Qaysi hududdansiz?\nViloyat yoki shahar nomini kiriting.")


@dp.message_handler(state=SherikState.hudud)
async def sherik_hudud(message: types.Message, state: FSMContext):
    ok, err = validate_hudud(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(hudud=message.text.strip())
    await SherikState.narx.set()
    await message.answer("To'lov qilasizmi yoki tekinmi?\nKerak bo'lsa summani kiriting.")


@dp.message_handler(state=SherikState.narx)
async def sherik_narx(message: types.Message, state: FSMContext):
    ok, err = validate_narx(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(narx=message.text.strip())
    await SherikState.kasb.set()
    await message.answer("Kasbingiz nima?\nMasalan: Talaba, Dasturchi")


@dp.message_handler(state=SherikState.kasb)
async def sherik_kasb(message: types.Message, state: FSMContext):
    ok, err = validate_kasb(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(kasb=message.text.strip())
    await SherikState.murojat.set()
    await message.answer("Qaysi vaqtda murojaat qilish mumkin?\nMasalan: 9:00 - 18:00")


@dp.message_handler(state=SherikState.murojat)
async def sherik_murojat(message: types.Message, state: FSMContext):
    ok, err = validate_murojat(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(murojat=message.text.strip())
    await SherikState.maqsad.set()
    await message.answer("Maqsadingizni qisqacha yozib bering:")


@dp.message_handler(state=SherikState.maqsad)
async def sherik_maqsad(message: types.Message, state: FSMContext):
    ok, err = validate_maqsad(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(maqsad=message.text.strip())

    data = await state.get_data()
    text = (
        "<b>Sherik kerak — ariza:</b>\n\n"
        f"🏅 Ism familiya: {data['fullname']}\n"
        f"📚 Texnologiya: {data['texnologiya']}\n"
        f"📞 Aloqa: {data['aloqa']}\n"
        f"🌐 Hudud: {data['hudud']}\n"
        f"💰 Narx: {data['narx']}\n"
        f"👨‍💻 Kasb: {data['kasb']}\n"
        f"🕰 Murojaat vaqti: {data['murojat']}\n"
        f"🔎 Maqsad: {data['maqsad']}\n"
    )
    await message.answer(text)
    await message.answer("Barcha ma'lumotlar to'g'rimi?", reply_markup=confirm_state)
    await SherikState.confirm.set()


@dp.message_handler(state=SherikState.confirm)
async def sherik_confirm(message: types.Message, state: FSMContext):
    javob = message.text.lower()

    if javob == "ha":
        data = await state.get_data()
        text = (
            "<b>Sherik kerak — yangi ariza:</b>\n\n"
            f"🏅 Ism familiya: {data['fullname']}\n"
            f"📚 Texnologiya: {data['texnologiya']}\n"
            f"📞 Aloqa: {data['aloqa']}\n"
            f"🌐 Hudud: {data['hudud']}\n"
            f"💰 Narx: {data['narx']}\n"
            f"👨‍💻 Kasb: {data['kasb']}\n"
            f"🕰 Murojaat vaqti: {data['murojat']}\n"
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
