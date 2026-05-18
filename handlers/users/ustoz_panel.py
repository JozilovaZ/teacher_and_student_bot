from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from keyboards.default.panels import (
    ustoz_menu, skip_keyboard, skip_deadline_keyboard,
    lessons_inline, lessons_delete_inline, assignments_inline, submissions_inline
)
from keyboards.default.menu import confirm_state
from loader import dp, bot
from states.panel import UstuzLessonState, UstuzAssignmentState, UstuzGradeState
from utils.db_api import database as db


# ──────────────────────────────────────────────
# MENYU
# ──────────────────────────────────────────────

@dp.message_handler(Text(equals="Ustoz paneli"), state=None)
async def show_ustoz_panel(message: types.Message):
    user = db.get_user(message.from_user.id)
    if not user or user['role'] != 'teacher':
        await message.answer("Bu panel faqat ustozlar uchun.")
        return
    await message.answer(
        f"Xush kelibsiz, <b>{user['full_name']}</b>!\nUstoz paneli:",
        reply_markup=ustoz_menu
    )


# ──────────────────────────────────────────────
# DARS QO'SHISH
# ──────────────────────────────────────────────

@dp.message_handler(Text(equals="Dars qo'shish"), state=None)
async def lesson_add_start(message: types.Message):
    user = db.get_user(message.from_user.id)
    if not user or user['role'] != 'teacher':
        await message.answer("Bu funksiya faqat ustozlar uchun.")
        return
    await message.answer("Dars nomini kiriting:")
    await UstuzLessonState.title.set()


@dp.message_handler(state=UstuzLessonState.title)
async def lesson_add_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await UstuzLessonState.description.set()
    await message.answer("Dars tavsifini kiriting:")


@dp.message_handler(state=UstuzLessonState.description)
async def lesson_add_desc(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await UstuzLessonState.file.set()
    await message.answer(
        "Dars materialini yuboring (hujjat, video yoki rasm).\n"
        "Fayl bo'lmasa — o'tkazib yuboring:",
        reply_markup=skip_keyboard
    )


@dp.message_handler(Text(equals="O'tkazib yuborish"), state=UstuzLessonState.file)
async def lesson_add_no_file(message: types.Message, state: FSMContext):
    await _save_lesson(message, state, file_id=None, file_type=None)


@dp.message_handler(content_types=types.ContentType.DOCUMENT, state=UstuzLessonState.file)
async def lesson_add_doc(message: types.Message, state: FSMContext):
    await _save_lesson(message, state, file_id=message.document.file_id, file_type="document")


@dp.message_handler(content_types=types.ContentType.VIDEO, state=UstuzLessonState.file)
async def lesson_add_video(message: types.Message, state: FSMContext):
    await _save_lesson(message, state, file_id=message.video.file_id, file_type="video")


@dp.message_handler(content_types=types.ContentType.PHOTO, state=UstuzLessonState.file)
async def lesson_add_photo(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await _save_lesson(message, state, file_id=file_id, file_type="photo")


async def _save_lesson(message: types.Message, state: FSMContext, file_id, file_type):
    data = await state.get_data()
    user = db.get_user(message.from_user.id)

    lesson_id = db.add_lesson(
        title=data['title'],
        description=data['description'],
        teacher_id=user['id'],
        file_id=file_id,
        file_type=file_type
    )
    await state.finish()
    await message.answer(
        f"Dars qo'shildi!\n\n"
        f"📚 <b>{data['title']}</b>\n"
        f"ID: {lesson_id}",
        reply_markup=ustoz_menu
    )


# ──────────────────────────────────────────────
# MENING DARSLARIM
# ──────────────────────────────────────────────

@dp.message_handler(Text(equals="Mening darslarim"), state=None)
async def my_lessons(message: types.Message):
    lessons = db.get_lessons_by_teacher(message.from_user.id)
    if not lessons:
        await message.answer("Siz hali dars qo'shmagansiz.")
        return
    await message.answer(
        f"Jami {len(lessons)} ta dars:",
        reply_markup=lessons_inline(lessons, prefix="mylesson")
    )


@dp.callback_query_handler(lambda c: c.data.startswith("mylesson_"))
async def lesson_detail(call: types.CallbackQuery):
    lesson_id = int(call.data.split("_")[1])
    lesson = db.get_lesson(lesson_id)
    if not lesson:
        await call.answer("Dars topilmadi.")
        return

    assignments = db.get_assignments_by_lesson(lesson_id)
    text = (
        f"📚 <b>{lesson['title']}</b>\n\n"
        f"{lesson['description'] or ''}\n\n"
        f"Topshiriqlar soni: {len(assignments)}"
    )
    await call.message.answer(text)

    if lesson['file_id']:
        if lesson['file_type'] == 'document':
            await call.message.answer_document(lesson['file_id'])
        elif lesson['file_type'] == 'video':
            await call.message.answer_video(lesson['file_id'])
        elif lesson['file_type'] == 'photo':
            await call.message.answer_photo(lesson['file_id'])

    await call.answer()


# ──────────────────────────────────────────────
# DARSNI O'CHIRISH
# ──────────────────────────────────────────────

@dp.message_handler(Text(equals="Darsni o'chirish"), state=None)
async def delete_lesson_start(message: types.Message):
    user = db.get_user(message.from_user.id)
    if not user or user['role'] != 'teacher':
        await message.answer("Bu funksiya faqat ustozlar uchun.")
        return
    lessons = db.get_lessons_by_teacher(message.from_user.id)
    if not lessons:
        await message.answer("Siz hali dars qo'shmagansiz.", reply_markup=ustoz_menu)
        return
    await message.answer(
        "Qaysi darsni o'chirmoqchisiz?\n⚠️ Dars va unga tegishli topshiriqlar ham o'chadi!",
        reply_markup=lessons_delete_inline(lessons)
    )


@dp.callback_query_handler(lambda c: c.data.startswith("dellesson_"))
async def delete_lesson_confirm(call: types.CallbackQuery):
    lesson_id = int(call.data.split("_")[1])
    lesson = db.get_lesson(lesson_id)
    if not lesson:
        await call.answer("Dars topilmadi.")
        return

    # Faqat o'z darsini o'chira oladi
    user = db.get_user(call.from_user.id)
    if lesson['teacher_id'] != user['id']:
        await call.answer("Bu sizning darsningiz emas.")
        return

    db.delete_lesson(lesson_id)
    await call.message.answer(
        f"✅ <b>{lesson['title']}</b> darsi o'chirildi.",
        reply_markup=ustoz_menu
    )
    await call.answer()


# ──────────────────────────────────────────────
# TOPSHIRIQ BERISH
# ──────────────────────────────────────────────

@dp.message_handler(Text(equals="Topshiriq berish"), state=None)
async def assignment_start(message: types.Message):
    lessons = db.get_lessons_by_teacher(message.from_user.id)
    if not lessons:
        await message.answer("Avval dars qo'shishingiz kerak.")
        return
    await message.answer(
        "Qaysi darsga topshiriq bermoqchisiz?",
        reply_markup=lessons_inline(lessons, prefix="addassign")
    )
    await UstuzAssignmentState.lesson_id.set()


@dp.callback_query_handler(lambda c: c.data.startswith("addassign_"), state=UstuzAssignmentState.lesson_id)
async def assignment_choose_lesson(call: types.CallbackQuery, state: FSMContext):
    lesson_id = int(call.data.split("_")[1])
    await state.update_data(lesson_id=lesson_id)
    await UstuzAssignmentState.title.set()
    await call.message.answer("Topshiriq nomini kiriting:")
    await call.answer()


@dp.message_handler(state=UstuzAssignmentState.title)
async def assignment_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await UstuzAssignmentState.description.set()
    await message.answer("Topshiriq matnini kiriting:")


@dp.message_handler(state=UstuzAssignmentState.description)
async def assignment_desc(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await UstuzAssignmentState.deadline.set()
    await message.answer(
        "Topshiriq muddatini kiriting (Masalan: 2024-12-31).\n"
        "Muddat bo'lmasa:",
        reply_markup=skip_deadline_keyboard
    )


@dp.message_handler(Text(equals="Muddat yo'q"), state=UstuzAssignmentState.deadline)
async def assignment_no_deadline(message: types.Message, state: FSMContext):
    await _save_assignment(message, state, deadline=None)


@dp.message_handler(state=UstuzAssignmentState.deadline)
async def assignment_deadline(message: types.Message, state: FSMContext):
    await _save_assignment(message, state, deadline=message.text)


async def _save_assignment(message: types.Message, state: FSMContext, deadline):
    data = await state.get_data()
    assignment_id = db.add_assignment(
        lesson_id=data['lesson_id'],
        title=data['title'],
        description=data['description'],
        deadline=deadline
    )
    await state.finish()
    deadline_text = deadline if deadline else "Muddat yo'q"
    await message.answer(
        f"Topshiriq qo'shildi!\n\n"
        f"📝 <b>{data['title']}</b>\n"
        f"📅 Muddat: {deadline_text}\n"
        f"ID: {assignment_id}",
        reply_markup=ustoz_menu
    )


# ──────────────────────────────────────────────
# JAVOBLARNI KO'RISH VA BAHOLASH
# ──────────────────────────────────────────────

@dp.message_handler(Text(equals="Javoblarni ko'rish"), state=None)
async def view_submissions_start(message: types.Message):
    lessons = db.get_lessons_by_teacher(message.from_user.id)
    if not lessons:
        await message.answer("Siz hali dars qo'shmagansiz.")
        return
    await message.answer(
        "Qaysi darsning topshiriqlarini ko'rmoqchisiz?",
        reply_markup=lessons_inline(lessons, prefix="viewlesson")
    )


@dp.callback_query_handler(lambda c: c.data.startswith("viewlesson_"))
async def view_lesson_assignments(call: types.CallbackQuery):
    lesson_id = int(call.data.split("_")[1])
    assignments = db.get_assignments_by_lesson(lesson_id)
    if not assignments:
        await call.message.answer("Bu darsdagi topshiriqlar yo'q.")
        await call.answer()
        return
    await call.message.answer(
        "Topshiriqni tanlang:",
        reply_markup=assignments_inline(assignments, prefix="view_assign")
    )
    await call.answer()


@dp.callback_query_handler(lambda c: c.data.startswith("view_assign_"))
async def view_assignment_submissions(call: types.CallbackQuery):
    assignment_id = int(call.data.split("_")[2])
    submissions = db.get_submissions_by_assignment(assignment_id)
    if not submissions:
        await call.message.answer("Hali hech qanday javob yuborilmagan.")
        await call.answer()
        return
    await call.message.answer(
        f"Javoblar ({len(submissions)} ta). Baholash uchun tanlang:",
        reply_markup=submissions_inline(submissions)
    )
    await call.answer()


@dp.callback_query_handler(lambda c: c.data.startswith("sub_"))
async def view_submission_detail(call: types.CallbackQuery, state: FSMContext):
    submission_id = int(call.data.split("_")[1])

    conn = db.get_connection()
    sub = conn.execute("""
        SELECT s.*, u.full_name as student_name, a.title as assignment_title
        FROM submissions s
        JOIN users u ON u.id = s.student_id
        JOIN assignments a ON a.id = s.assignment_id
        WHERE s.id = ?
    """, (submission_id,)).fetchone()
    conn.close()

    if not sub:
        await call.answer("Javob topilmadi.")
        return

    grade_text = f"{sub['grade']}/100" if sub['grade'] is not None else "Baholanmagan"
    text = (
        f"👤 Shogird: <b>{sub['student_name']}</b>\n"
        f"📝 Topshiriq: {sub['assignment_title']}\n"
        f"💬 Javob: {sub['answer_text'] or '—'}\n"
        f"📊 Baho: {grade_text}\n"
        f"💭 Izoh: {sub['feedback'] or '—'}"
    )
    await call.message.answer(text)

    if sub['file_id']:
        await call.message.answer_document(sub['file_id'], caption="Shogird yuborgan fayl")

    if sub['grade'] is None:
        await state.update_data(submission_id=submission_id)
        await UstuzGradeState.grade.set()
        await call.message.answer("Baho kiriting (0 dan 100 gacha):")

    await call.answer()


@dp.message_handler(state=UstuzGradeState.grade)
async def grade_enter_score(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or not (0 <= int(message.text) <= 100):
        await message.answer("Iltimos, 0 dan 100 gacha son kiriting.")
        return
    await state.update_data(grade=int(message.text))
    await UstuzGradeState.feedback.set()
    await message.answer("Izoh yozing (ixtiyoriy). O'tkazish uchun — \"O'tkazib yuborish\" deb yozing:")


@dp.message_handler(state=UstuzGradeState.feedback)
async def grade_enter_feedback(message: types.Message, state: FSMContext):
    data = await state.get_data()
    feedback = "" if message.text == "O'tkazib yuborish" else message.text

    db.grade_submission(
        submission_id=data['submission_id'],
        grade=data['grade'],
        feedback=feedback
    )

    # Shogirdga xabar yuborish
    conn = db.get_connection()
    sub = conn.execute("""
        SELECT s.*, u.telegram_id as student_telegram_id, a.title as assignment_title
        FROM submissions s
        JOIN users u ON u.id = s.student_id
        JOIN assignments a ON a.id = s.assignment_id
        WHERE s.id = ?
    """, (data['submission_id'],)).fetchone()
    conn.close()

    if sub:
        try:
            feedback_text = f"\n💭 Izoh: {feedback}" if feedback else ""
            await bot.send_message(
                sub['student_telegram_id'],
                f"📊 Baholandi!\n\n"
                f"📝 Topshiriq: <b>{sub['assignment_title']}</b>\n"
                f"✅ Baho: <b>{data['grade']}/100</b>{feedback_text}"
            )
        except Exception:
            pass

    await state.finish()
    await message.answer(
        f"Baho saqlandi: {data['grade']}/100",
        reply_markup=ustoz_menu
    )


# ──────────────────────────────────────────────
# SHOGIRDLARIM
# ──────────────────────────────────────────────

@dp.message_handler(Text(equals="Shogirdlarim"), state=None)
async def my_students(message: types.Message):
    students = db.get_students_of_teacher(message.from_user.id)
    if not students:
        await message.answer(
            "Hali birorta shogird yo'q.\n"
            "Shogirdlar ro'yxatdan o'tib, sizga ulanganda bu yerda ko'rinadi."
        )
        return

    lines = [f"Shogirdlarim ({len(students)} ta):\n"]
    for i, s in enumerate(students, 1):
        username = f"@{s['username']}" if s['username'] else "username yo'q"
        lines.append(f"{i}. <b>{s['full_name']}</b> — {username}")

    await message.answer("\n".join(lines))
