from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from keyboards.default.panels import shogird_menu, skip_keyboard, assignments_inline
from loader import dp
from states.panel import ShogirdSubmitState
from utils.db_api import database as db


# ──────────────────────────────────────────────
# MENYU
# ──────────────────────────────────────────────

@dp.message_handler(Text(equals="Shogird paneli"), state=None)
async def show_shogird_panel(message: types.Message):
    user = db.get_user(message.from_user.id)
    if not user or user['role'] != 'student':
        await message.answer("Bu panel faqat shogirdlar uchun.")
        return
    await message.answer(
        f"Xush kelibsiz, <b>{user['full_name']}</b>!\nShogird paneli:",
        reply_markup=shogird_menu
    )


# ──────────────────────────────────────────────
# DARSLAR
# ──────────────────────────────────────────────

@dp.message_handler(Text(equals="Darslar"), state=None)
async def view_all_lessons(message: types.Message):
    user = db.get_user(message.from_user.id)
    if not user or user['role'] != 'student':
        await message.answer("Bu funksiya faqat shogirdlar uchun.")
        return

    lessons = db.get_all_lessons()
    if not lessons:
        await message.answer("Hozircha darslar yo'q.")
        return

    lines = [f"Mavjud darslar ({len(lessons)} ta):\n"]
    for i, lesson in enumerate(lessons, 1):
        lines.append(
            f"{i}. 📚 <b>{lesson['title']}</b>\n"
            f"   👨‍🏫 Ustoz: {lesson['teacher_name']}"
        )
    await message.answer("\n".join(lines))

    from keyboards.default.panels import lessons_inline
    await message.answer("Darsni tanlang:", reply_markup=lessons_inline(lessons, prefix="slesson"))


@dp.callback_query_handler(lambda c: c.data.startswith("slesson_"))
async def shogird_lesson_detail(call: types.CallbackQuery):
    lesson_id = int(call.data.split("_")[1])
    lesson = db.get_lesson(lesson_id)
    if not lesson:
        await call.answer("Dars topilmadi.")
        return

    text = f"📚 <b>{lesson['title']}</b>\n\n{lesson['description'] or ''}"
    await call.message.answer(text)

    if lesson['file_id']:
        if lesson['file_type'] == 'document':
            await call.message.answer_document(lesson['file_id'], caption="Dars materiali")
        elif lesson['file_type'] == 'video':
            await call.message.answer_video(lesson['file_id'], caption="Dars materiali")
        elif lesson['file_type'] == 'photo':
            await call.message.answer_photo(lesson['file_id'], caption="Dars materiali")

    await call.answer()


# ──────────────────────────────────────────────
# TOPSHIRIQLAR
# ──────────────────────────────────────────────

@dp.message_handler(Text(equals="Topshiriqlar"), state=None)
async def view_assignments(message: types.Message):
    user = db.get_user(message.from_user.id)
    if not user or user['role'] != 'student':
        await message.answer("Bu funksiya faqat shogirdlar uchun.")
        return

    lessons = db.get_all_lessons()
    if not lessons:
        await message.answer("Hozircha topshiriqlar yo'q.")
        return

    all_assignments = []
    for lesson in lessons:
        assignments = db.get_assignments_by_lesson(lesson['id'])
        for a in assignments:
            all_assignments.append(a)

    if not all_assignments:
        await message.answer("Hozircha topshiriqlar yo'q.")
        return

    lines = [f"Topshiriqlar ({len(all_assignments)} ta):\n"]
    for i, a in enumerate(all_assignments, 1):
        deadline = f" | 📅 {a['deadline']}" if a['deadline'] else ""
        lines.append(f"{i}. 📝 <b>{a['title']}</b>{deadline}")

    await message.answer("\n".join(lines))
    await message.answer(
        "Javob yuborish uchun tanlang:",
        reply_markup=assignments_inline(all_assignments, prefix="submit")
    )


@dp.callback_query_handler(lambda c: c.data.startswith("submit_"))
async def submit_choose_assignment(call: types.CallbackQuery, state: FSMContext):
    assignment_id = int(call.data.split("_")[1])
    assignment = db.get_assignment(assignment_id)
    if not assignment:
        await call.answer("Topshiriq topilmadi.")
        return

    # Allaqachon javob berganmi?
    user = db.get_user(call.from_user.id)
    conn = db.get_connection()
    existing = conn.execute(
        "SELECT * FROM submissions WHERE assignment_id=? AND student_id=?",
        (assignment_id, user['id'])
    ).fetchone()
    conn.close()

    if existing:
        grade = f"{existing['grade']}/100" if existing['grade'] is not None else "Baholanmagan"
        await call.message.answer(
            f"Bu topshiriqqa allaqachon javob bergansiz.\n"
            f"📊 Baho: {grade}"
        )
        await call.answer()
        return

    await state.update_data(assignment_id=assignment_id)
    await ShogirdSubmitState.answer.set()
    await call.message.answer(
        f"📝 <b>{assignment['title']}</b>\n\n"
        f"{assignment['description'] or ''}\n\n"
        "Javobingizni yozing yoki fayl yuboring:",
        reply_markup=skip_keyboard
    )
    await call.answer()


@dp.message_handler(Text(equals="O'tkazib yuborish"), state=ShogirdSubmitState.answer)
async def submit_skip(message: types.Message, state: FSMContext):
    await message.answer("Topshiriq bekor qilindi.", reply_markup=shogird_menu)
    await state.finish()


@dp.message_handler(content_types=types.ContentType.TEXT, state=ShogirdSubmitState.answer)
async def submit_text_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    success = db.submit_assignment(
        assignment_id=data['assignment_id'],
        student_telegram_id=message.from_user.id,
        answer_text=message.text
    )
    await state.finish()
    if success:
        await message.answer("Javobingiz yuborildi!", reply_markup=shogird_menu)
    else:
        await message.answer("Xatolik yuz berdi. Qaytadan urining.", reply_markup=shogird_menu)


@dp.message_handler(content_types=types.ContentType.DOCUMENT, state=ShogirdSubmitState.answer)
async def submit_file_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    success = db.submit_assignment(
        assignment_id=data['assignment_id'],
        student_telegram_id=message.from_user.id,
        answer_text=message.caption or "",
        file_id=message.document.file_id
    )
    await state.finish()
    if success:
        await message.answer("Javobingiz yuborildi!", reply_markup=shogird_menu)
    else:
        await message.answer("Xatolik yuz berdi. Qaytadan urining.", reply_markup=shogird_menu)


# ──────────────────────────────────────────────
# BAHOLARIM
# ──────────────────────────────────────────────

@dp.message_handler(Text(equals="Baholarim"), state=None)
async def my_grades(message: types.Message):
    user = db.get_user(message.from_user.id)
    if not user or user['role'] != 'student':
        await message.answer("Bu funksiya faqat shogirdlar uchun.")
        return

    submissions = db.get_student_submissions(message.from_user.id)
    if not submissions:
        await message.answer("Siz hali birorta topshiriq yubormadingiz.")
        return

    lines = [f"Baholarim ({len(submissions)} ta):\n"]
    total = 0
    graded = 0
    for s in submissions:
        if s['grade'] is not None:
            grade_text = f"✅ {s['grade']}/100"
            total += s['grade']
            graded += 1
        else:
            grade_text = "⏳ Kutilmoqda"
        lines.append(
            f"📝 <b>{s['assignment_title']}</b>\n"
            f"   📚 {s['lesson_title']} | {grade_text}"
        )

    if graded > 0:
        avg = total // graded
        lines.append(f"\n📊 O'rtacha baho: <b>{avg}/100</b>")

    await message.answer("\n".join(lines))
