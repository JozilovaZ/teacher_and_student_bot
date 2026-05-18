from aiogram import types
from aiogram.dispatcher import FSMContext

from data.config import ADMINS
from keyboards.default.menu import confirm_state, menu_start
from loader import dp, bot
from states.anketa import hodimkkState
from utils.validators import (
    validate_fullname, validate_texno, validate_aloqa, validate_hudud,
    validate_idora, validate_murojat, validate_vaqt, validate_maosh, validate_maqsad
)


@dp.message_handler(text="Hodim kerak")
async def hodim_handler(message: types.Message):
    await message.answer(
        "Hodim topish uchun ariza berish\n\n"
        "Hozir sizga bir necha savollar beriladi.\n"
        "Har biriga javob bering.\n"
        "Oxirida to'g'ri bo'lsa <b>Ha</b> tugmasini bosing."
    )
    await message.answer("Idora (kompaniya) nomini kiriting:")
    await hodimkkState.idora.set()


@dp.message_handler(state=hodimkkState.idora)
async def hodim_idora(message: types.Message, state: FSMContext):
    ok, err = validate_idora(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(idora=message.text.strip())
    await hodimkkState.texno.set()
    await message.answer(
        "Talab qilinadigan texnologiyalarni kiriting.\n"
        "Vergul bilan ajrating. Masalan: Python, Django, SQL"
    )


@dp.message_handler(state=hodimkkState.texno)
async def hodim_texno(message: types.Message, state: FSMContext):
    ok, err = validate_texno(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(texno=message.text.strip())
    await hodimkkState.aloqa.set()
    await message.answer("Bog'lanish uchun telefon raqam:\nMasalan: +998 90 123 45 67")


@dp.message_handler(state=hodimkkState.aloqa)
async def hodim_aloqa(message: types.Message, state: FSMContext):
    ok, err = validate_aloqa(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(aloqa=message.text.strip())
    await hodimkkState.hudud.set()
    await message.answer("Idora qaysi hududda joylashgan?\nViloyat yoki shahar nomini kiriting.")


@dp.message_handler(state=hodimkkState.hudud)
async def hodim_hudud(message: types.Message, state: FSMContext):
    ok, err = validate_hudud(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(hudud=message.text.strip())
    await hodimkkState.full_name.set()
    await message.answer("Mas'ul shaxsning ism sharifi:")


@dp.message_handler(state=hodimkkState.full_name)
async def hodim_full_name(message: types.Message, state: FSMContext):
    ok, err = validate_fullname(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(fullname=message.text.strip())
    await hodimkkState.murojat.set()
    await message.answer("Murojaat qilish vaqti:\nMasalan: 9:00 - 18:00")


@dp.message_handler(state=hodimkkState.murojat)
async def hodim_murojat(message: types.Message, state: FSMContext):
    ok, err = validate_murojat(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(murojat=message.text.strip())
    await hodimkkState.ish_vaqti.set()
    await message.answer("Ish vaqtini kiriting:\nMasalan: 9:00 - 18:00, Dushanba-Juma")


@dp.message_handler(state=hodimkkState.ish_vaqti)
async def hodim_ish_vaqti(message: types.Message, state: FSMContext):
    ok, err = validate_vaqt(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(ish_vaqti=message.text.strip())
    await hodimkkState.maosh.set()
    await message.answer("Taklif etilayotgan maosh:\nMasalan: 3 000 000 so'm / oy")


@dp.message_handler(state=hodimkkState.maosh)
async def hodim_maosh(message: types.Message, state: FSMContext):
    ok, err = validate_maosh(message.text)
    if not ok:
        return await message.answer(f"❌ {err}\n\nQaytadan kiriting:")
    await state.update_data(maosh=message.text.strip())
    await hodimkkState.qoshimcha_malumot.set()
    await message.answer("Qo'shimcha ma'lumotlar (ixtiyoriy):\nYo'q bo'lsa — \"Yo'q\" deb yozing.")


@dp.message_handler(state=hodimkkState.qoshimcha_malumot)
async def hodim_qoshimcha(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if len(text) < 1:
        return await message.answer("❌ Kamida biror narsa yozing yoki \"Yo'q\" deb yozing.")
    await state.update_data(qoshimcha_malumot=text)

    data = await state.get_data()
    text = (
        "<b>Hodim kerak — ariza:</b>\n\n"
        f"🏢 Idora: {data['idora']}\n"
        f"📚 Texnologiya: {data['texno']}\n"
        f"📞 Aloqa: {data['aloqa']}\n"
        f"🌐 Hudud: {data['hudud']}\n"
        f"✍️ Mas'ul: {data['fullname']}\n"
        f"🕰 Murojaat vaqti: {data['murojat']}\n"
        f"🕰 Ish vaqti: {data['ish_vaqti']}\n"
        f"💰 Maosh: {data['maosh']}\n"
        f"‼️ Qo'shimcha: {data['qoshimcha_malumot']}\n"
    )
    await message.answer(text)
    await message.answer("Barcha ma'lumotlar to'g'rimi?", reply_markup=confirm_state)
    await hodimkkState.confirm.set()


@dp.message_handler(state=hodimkkState.confirm)
async def hodim_confirm(message: types.Message, state: FSMContext):
    javob = message.text.lower()

    if javob == "ha":
        data = await state.get_data()
        text = (
            "<b>Hodim kerak — yangi ariza:</b>\n\n"
            f"🏢 Idora: {data['idora']}\n"
            f"📚 Texnologiya: {data['texno']}\n"
            f"📞 Aloqa: {data['aloqa']}\n"
            f"🌐 Hudud: {data['hudud']}\n"
            f"✍️ Mas'ul: {data['fullname']}\n"
            f"🕰 Murojaat vaqti: {data['murojat']}\n"
            f"🕰 Ish vaqti: {data['ish_vaqti']}\n"
            f"💰 Maosh: {data['maosh']}\n"
            f"‼️ Qo'shimcha: {data['qoshimcha_malumot']}\n"
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
