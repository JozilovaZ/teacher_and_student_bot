from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from keyboards.default.menu import main_menu, confirm_kb, cancel_kb, skip_kb
from keyboards.default.panels import category_select_kb, CATEGORY_LABELS
from loader import dp
from states.anketa import AdCreateState
from utils.db_api import database as db

CATEGORY_QUESTIONS = {
    'ustoz': {
        'texno': "Qaysi texnologiyalarni o'rganmoqchisiz?\nMasalan: Python, Django, SQL",
        'narx':  "To'lov qilasizmi? Narxni kiriting yoki \"Tekin\" deb yozing:",
        'maqsad': "Maqsadingizni qisqacha yozib bering (nima o'rganmoqchisiz, nima uchun):",
    },
    'shogird': {
        'texno': "Qaysi texnologiyalardan dars bera olasiz?\nMasalan: Python, Django, SQL",
        'narx':  "Dars narxi? (masalan: 300 000 so'm/oy yoki Tekin):",
        'maqsad': "O'zingiz haqingizda qisqacha yozing (tajriba, usul):",
    },
    'hodim': {
        'texno': "Qanday mutaxassis kerak? (masalan: Python developer, Frontend):",
        'narx':  "Oylik maosh? (masalan: 3 000 000 so'm yoki Kelishiladi):",
        'maqsad': "Kompaniya va vazifa haqida qisqacha:",
    },
    'ish_joyi': {
        'texno': "Qaysi texnologiyalarni bilasiz? Qaysi sohadagi ish izlayapsiz?",
        'narx':  "Kutilayotgan maosh? (yoki \"Kelishiladi\"):",
        'maqsad': "O'zingiz haqingizda va maqsadingiz haqida qisqacha:",
    },
    'sherik': {
        'texno': "Qaysi soha/texnologiyalar bo'yicha sherik izlayapsiz?",
        'narx':  "Moliyaviy shart-sharoit haqida (ixtiyoriy, o'tkazib yuborishingiz mumkin):",
        'maqsad': "Loyiha/g'oya haqida qisqacha yozing:",
    },
}


def ad_preview(data: dict) -> str:
    cat = data['category']
    cat_label = CATEGORY_LABELS.get(cat, cat)
    lines = [f"<b>{cat_label} — ariza ko'rinishi:</b>\n"]
    lines.append(f"👤 Ism: <b>{data['fullname']}</b>")
    if data.get('yosh'):
        lines.append(f"🎂 Yosh: {data['yosh']}")
    lines.append(f"💻 Texnologiya/Soha: {data['texno']}")
    lines.append(f"📞 Aloqa: {data['aloqa']}")
    lines.append(f"📍 Hudud: {data['hudud']}")
    if data.get('narx'):
        lines.append(f"💰 Narx/Maosh: {data['narx']}")
    if data.get('vaqt'):
        lines.append(f"🕐 Murojaat vaqti: {data['vaqt']}")
    if data.get('maqsad'):
        lines.append(f"📝 Tavsif: {data['maqsad']}")
    return "\n".join(lines)


@dp.message_handler(Text(equals="📋 Ariza berish"), state="*")
async def ad_create_start(message: types.Message, state: FSMContext):
    await state.finish()
    user = db.get_user(message.from_user.id)
    if not user or not user['phone']:
        await message.answer("Avval /start orqali ro'yxatdan o'ting.")
        return

    await message.answer(
        "Qaysi kategoriyada ariza berasiz?",
        reply_markup=category_select_kb()
    )
    await AdCreateState.category.set()


@dp.callback_query_handler(lambda c: c.data.startswith("newad_"), state=AdCreateState.category)
async def ad_choose_category(call: types.CallbackQuery, state: FSMContext):
    category = call.data.split("_")[1]
    await state.update_data(category=category)
    await AdCreateState.fullname.set()
    await call.message.answer(
        "Ism familiyangizni kiriting:",
        reply_markup=cancel_kb
    )
    await call.answer()


@dp.message_handler(Text(equals="🚫 Bekor qilish"), state="*")
async def ad_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Bekor qilindi.", reply_markup=main_menu)


@dp.message_handler(state=AdCreateState.fullname)
async def ad_fullname(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if len(text) < 3:
        return await message.answer("Ism familiya kamida 3 ta harf bo'lishi kerak. Qaytadan kiriting:")
    await state.update_data(fullname=text)
    await AdCreateState.yosh.set()
    await message.answer(
        "Yoshingizni kiriting (masalan: 22).\nO'tkazib yuborish mumkin:",
        reply_markup=skip_kb
    )


@dp.message_handler(state=AdCreateState.yosh)
async def ad_yosh(message: types.Message, state: FSMContext):
    yosh = ''
    if message.text != "⏭ O'tkazib yuborish":
        yosh = message.text.strip()
        if not yosh.isdigit() or not (10 <= int(yosh) <= 80):
            return await message.answer("Yosh 10 dan 80 gacha bo'lishi kerak. Qaytadan:")
    await state.update_data(yosh=yosh)
    data = await state.get_data()
    cat = data['category']
    question = CATEGORY_QUESTIONS[cat]['texno']
    await AdCreateState.texno.set()
    await message.answer(question, reply_markup=cancel_kb)


@dp.message_handler(state=AdCreateState.texno)
async def ad_texno(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if len(text) < 2:
        return await message.answer("Kamida 2 ta belgi kiriting:")
    await state.update_data(texno=text)
    await AdCreateState.aloqa.set()
    await message.answer(
        "📞 Aloqa uchun telefon raqamingiz:\nMasalan: +998 90 123 45 67",
        reply_markup=cancel_kb
    )


@dp.message_handler(state=AdCreateState.aloqa)
async def ad_aloqa(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if len(text) < 7:
        return await message.answer("To'g'ri telefon raqam kiriting:")
    await state.update_data(aloqa=text)
    await AdCreateState.hudud.set()
    await message.answer(
        "📍 Qaysi hududdansiz? (viloyat yoki shahar nomi):",
        reply_markup=cancel_kb
    )


@dp.message_handler(state=AdCreateState.hudud)
async def ad_hudud(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if len(text) < 2:
        return await message.answer("Hudud nomini kiriting:")
    await state.update_data(hudud=text)
    data = await state.get_data()
    cat = data['category']
    question = CATEGORY_QUESTIONS[cat]['narx']
    await AdCreateState.narx.set()
    await message.answer(question, reply_markup=skip_kb)


@dp.message_handler(state=AdCreateState.narx)
async def ad_narx(message: types.Message, state: FSMContext):
    narx = ''
    if message.text != "⏭ O'tkazib yuborish":
        narx = message.text.strip()
    await state.update_data(narx=narx)
    await AdCreateState.vaqt.set()
    await message.answer(
        "🕐 Murojaat qilish uchun qulay vaqt?\nMasalan: 09:00–18:00 yoki istalgan vaqt.",
        reply_markup=skip_kb
    )


@dp.message_handler(state=AdCreateState.vaqt)
async def ad_vaqt(message: types.Message, state: FSMContext):
    vaqt = ''
    if message.text != "⏭ O'tkazib yuborish":
        vaqt = message.text.strip()
    await state.update_data(vaqt=vaqt)
    data = await state.get_data()
    cat = data['category']
    question = CATEGORY_QUESTIONS[cat]['maqsad']
    await AdCreateState.maqsad.set()
    await message.answer(question, reply_markup=skip_kb)


@dp.message_handler(state=AdCreateState.maqsad)
async def ad_maqsad(message: types.Message, state: FSMContext):
    maqsad = ''
    if message.text != "⏭ O'tkazib yuborish":
        maqsad = message.text.strip()
    await state.update_data(maqsad=maqsad)

    data = await state.get_data()
    await AdCreateState.confirm.set()
    await message.answer(
        ad_preview(data) + "\n\n<b>Yuborishasizmi?</b>",
        reply_markup=confirm_kb
    )


@dp.message_handler(Text(equals="✅ Ha, tasdiqlash"), state=AdCreateState.confirm)
async def ad_confirm_yes(message: types.Message, state: FSMContext):
    data = await state.get_data()
    ad_id = db.add_ad(
        user_telegram_id=message.from_user.id,
        category=data['category'],
        fullname=data['fullname'],
        yosh=data.get('yosh', ''),
        texno=data['texno'],
        aloqa=data['aloqa'],
        hudud=data['hudud'],
        narx=data.get('narx', ''),
        vaqt=data.get('vaqt', ''),
        maqsad=data.get('maqsad', '')
    )
    await state.finish()
    cat_label = CATEGORY_LABELS.get(data['category'])
    await message.answer(
        f"✅ Arizangiz joylandi!\n\n"
        f"Kategoriya: <b>{cat_label}</b>\n"
        f"Ariza ID: #{ad_id}\n\n"
        "Boshqalar endi sizni ko'rishi mumkin.",
        reply_markup=main_menu
    )


@dp.message_handler(Text(equals="❌ Bekor qilish"), state=AdCreateState.confirm)
async def ad_confirm_no(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Ariza bekor qilindi.", reply_markup=main_menu)
