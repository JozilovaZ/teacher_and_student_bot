from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 Ustoz kerak"), KeyboardButton(text="🎓 Shogird kerak")],
        [KeyboardButton(text="👔 Hodim kerak"), KeyboardButton(text="💼 Ish joyi kerak")],
        [KeyboardButton(text="🤝 Sherik kerak")],
        [KeyboardButton(text="📋 Ariza berish")],
        [KeyboardButton(text="📁 Mening arizalarim"), KeyboardButton(text="👤 Profilim")],
    ],
    resize_keyboard=True
)

confirm_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Ha, tasdiqlash"), KeyboardButton(text="❌ Bekor qilish")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

phone_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

skip_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="⏭ O'tkazib yuborish")]],
    resize_keyboard=True,
    one_time_keyboard=True
)

cancel_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🚫 Bekor qilish")]],
    resize_keyboard=True
)
