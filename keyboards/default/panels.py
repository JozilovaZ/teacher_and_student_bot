from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

# Rol tanlash klaviaturasi
role_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Ustoz"), KeyboardButton(text="Shogird")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Ustoz panel asosiy menyu
ustoz_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Dars qo'shish"), KeyboardButton(text="Mening darslarim")],
        [KeyboardButton(text="Topshiriq berish"), KeyboardButton(text="Javoblarni ko'rish")],
        [KeyboardButton(text="Shogirdlarim"), KeyboardButton(text="Darsni o'chirish")],
    ],
    resize_keyboard=True
)

# Shogird panel asosiy menyu
shogird_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Darslar"), KeyboardButton(text="Topshiriqlar")],
        [KeyboardButton(text="Baholarim")],
    ],
    resize_keyboard=True
)

# Fayl o'tkazib yuborish tugmasi
skip_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="O'tkazib yuborish")]],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Muddat o'tkazib yuborish
skip_deadline_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Muddat yo'q")]],
    resize_keyboard=True,
    one_time_keyboard=True
)


def lessons_inline(lessons, prefix="lesson") -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    for lesson in lessons:
        kb.add(InlineKeyboardButton(
            text=f"📚 {lesson['title']}",
            callback_data=f"{prefix}_{lesson['id']}"
        ))
    return kb


def assignments_inline(assignments, prefix="assign") -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    for a in assignments:
        kb.add(InlineKeyboardButton(
            text=f"📝 {a['title']}",
            callback_data=f"{prefix}_{a['id']}"
        ))
    return kb


def lessons_delete_inline(lessons) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    for lesson in lessons:
        kb.add(InlineKeyboardButton(
            text=f"🗑 {lesson['title']}",
            callback_data=f"dellesson_{lesson['id']}"
        ))
    return kb


def submissions_inline(submissions) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    for s in submissions:
        grade_text = f"✅ {s['grade']}/100" if s['grade'] is not None else "⏳ Baholanmagan"
        kb.add(InlineKeyboardButton(
            text=f"{s['student_name']} — {grade_text}",
            callback_data=f"sub_{s['id']}"
        ))
    return kb
