from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

menu_start = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Sherik kerak"),
            KeyboardButton(text="Ish joyi kerak"),
        ],
        [
            KeyboardButton(text="Hodim kerak"),
            KeyboardButton(text="Ustoz kerak"),
        ],
        [
            KeyboardButton(text="Shogird kerak"),
        ],
    ],
    resize_keyboard=True
)

confirm_state = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Ha"),
            KeyboardButton(text="Yo`q"),
        ],
    ],
    resize_keyboard=True
)

phone_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Telefon raqamni yuborish", request_contact=True),
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)
