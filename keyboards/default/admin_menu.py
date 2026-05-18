from aiogram.types import (
    KeyboardButton, ReplyKeyboardMarkup,
    InlineKeyboardMarkup, InlineKeyboardButton
)

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Statistika"), KeyboardButton(text="Foydalanuvchilar")],
        [KeyboardButton(text="Darslar (admin)"), KeyboardButton(text="Broadcast")],
    ],
    resize_keyboard=True
)

# Foydalanuvchilar filter
users_filter_kb = InlineKeyboardMarkup(row_width=3).add(
    InlineKeyboardButton("Hammasi", callback_data="afilter_all"),
    InlineKeyboardButton("Ustozlar", callback_data="afilter_teacher"),
    InlineKeyboardButton("Shogirdlar", callback_data="afilter_student"),
)


def user_detail_kb(telegram_id: int, role: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    if role == "blocked":
        kb.add(InlineKeyboardButton("Blokdan chiqarish (Shogird)", callback_data=f"aunblock_student_{telegram_id}"))
        kb.add(InlineKeyboardButton("Blokdan chiqarish (Ustoz)", callback_data=f"aunblock_teacher_{telegram_id}"))
    else:
        if role != "teacher":
            kb.add(InlineKeyboardButton("Ustoz qilish", callback_data=f"aset_teacher_{telegram_id}"))
        if role != "student":
            kb.add(InlineKeyboardButton("Shogird qilish", callback_data=f"aset_student_{telegram_id}"))
        kb.add(InlineKeyboardButton("Bloklash", callback_data=f"ablock_{telegram_id}"))
    return kb


def admin_lessons_kb(lessons) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    for lesson in lessons:
        kb.add(InlineKeyboardButton(
            text=f"📚 {lesson['title']} — {lesson['teacher_name']}",
            callback_data=f"adlesson_{lesson['id']}"
        ))
    return kb


def confirm_delete_kb(lesson_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("Ha, o'chir", callback_data=f"adel_confirm_{lesson_id}"),
        InlineKeyboardButton("Bekor", callback_data="adel_cancel"),
    )
