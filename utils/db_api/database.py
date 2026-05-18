import sqlite3
import os
import logging
from typing import Optional, List

DB_PATH = os.path.join(os.path.dirname(__file__), "ustoz_shogirt.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            full_name   TEXT NOT NULL,
            username    TEXT,
            role        TEXT NOT NULL DEFAULT 'student',  -- 'student' yoki 'teacher'
            phone       TEXT,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS lessons (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            description TEXT,
            teacher_id  INTEGER NOT NULL,
            file_id     TEXT,            -- Telegram file_id (hujjat yoki video)
            file_type   TEXT,            -- 'document', 'video', 'photo'
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS assignments (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson_id    INTEGER NOT NULL,
            title        TEXT NOT NULL,
            description  TEXT,
            deadline     DATETIME,
            created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lesson_id) REFERENCES lessons(id)
        );

        CREATE TABLE IF NOT EXISTS submissions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            assignment_id   INTEGER NOT NULL,
            student_id      INTEGER NOT NULL,
            answer_text     TEXT,
            file_id         TEXT,
            grade           INTEGER,       -- 0-100
            feedback        TEXT,
            submitted_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
            graded_at       DATETIME,
            FOREIGN KEY (assignment_id) REFERENCES assignments(id),
            FOREIGN KEY (student_id)    REFERENCES users(id),
            UNIQUE (assignment_id, student_id)
        );

        CREATE TABLE IF NOT EXISTS enrollments (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id  INTEGER NOT NULL,
            teacher_id  INTEGER NOT NULL,
            joined_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users(id),
            FOREIGN KEY (teacher_id) REFERENCES users(id),
            UNIQUE (student_id, teacher_id)
        );
    """)

    conn.commit()
    conn.close()
    logging.info("Ma'lumotlar bazasi jadvallari yaratildi.")


# ──────────────────────────────────────────────
# USERS
# ──────────────────────────────────────────────

def add_user(telegram_id: int, full_name: str, username: Optional[str], role: str = "student") -> bool:
    conn = get_connection()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO users (telegram_id, full_name, username, role) VALUES (?,?,?,?)",
            (telegram_id, full_name, username, role)
        )
        conn.commit()
        return conn.total_changes > 0
    finally:
        conn.close()


def get_user(telegram_id: int) -> Optional[sqlite3.Row]:
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        ).fetchone()
    finally:
        conn.close()


def set_user_role(telegram_id: int, role: str):
    conn = get_connection()
    try:
        conn.execute("UPDATE users SET role = ? WHERE telegram_id = ?", (role, telegram_id))
        conn.commit()
    finally:
        conn.close()


def set_user_phone(telegram_id: int, phone: str):
    conn = get_connection()
    try:
        conn.execute("UPDATE users SET phone = ? WHERE telegram_id = ?", (phone, telegram_id))
        conn.commit()
    finally:
        conn.close()


def get_all_students() -> List[sqlite3.Row]:
    conn = get_connection()
    try:
        return conn.execute("SELECT * FROM users WHERE role = 'student'").fetchall()
    finally:
        conn.close()


def get_all_teachers() -> List[sqlite3.Row]:
    conn = get_connection()
    try:
        return conn.execute("SELECT * FROM users WHERE role = 'teacher'").fetchall()
    finally:
        conn.close()


# ──────────────────────────────────────────────
# LESSONS
# ──────────────────────────────────────────────

def add_lesson(title: str, description: str, teacher_id: int,
               file_id: Optional[str] = None, file_type: Optional[str] = None) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO lessons (title, description, teacher_id, file_id, file_type) VALUES (?,?,?,?,?)",
            (title, description, teacher_id, file_id, file_type)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_lessons_by_teacher(teacher_telegram_id: int) -> List[sqlite3.Row]:
    conn = get_connection()
    try:
        return conn.execute("""
            SELECT l.* FROM lessons l
            JOIN users u ON u.id = l.teacher_id
            WHERE u.telegram_id = ?
            ORDER BY l.created_at DESC
        """, (teacher_telegram_id,)).fetchall()
    finally:
        conn.close()


def get_lesson(lesson_id: int) -> Optional[sqlite3.Row]:
    conn = get_connection()
    try:
        return conn.execute("SELECT * FROM lessons WHERE id = ?", (lesson_id,)).fetchone()
    finally:
        conn.close()


def get_all_lessons() -> List[sqlite3.Row]:
    conn = get_connection()
    try:
        return conn.execute("""
            SELECT l.*, u.full_name as teacher_name
            FROM lessons l
            JOIN users u ON u.id = l.teacher_id
            ORDER BY l.created_at DESC
        """).fetchall()
    finally:
        conn.close()


# ──────────────────────────────────────────────
# ASSIGNMENTS
# ──────────────────────────────────────────────

def add_assignment(lesson_id: int, title: str, description: str,
                   deadline: Optional[str] = None) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO assignments (lesson_id, title, description, deadline) VALUES (?,?,?,?)",
            (lesson_id, title, description, deadline)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_assignments_by_lesson(lesson_id: int) -> List[sqlite3.Row]:
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM assignments WHERE lesson_id = ? ORDER BY created_at DESC",
            (lesson_id,)
        ).fetchall()
    finally:
        conn.close()


def get_assignment(assignment_id: int) -> Optional[sqlite3.Row]:
    conn = get_connection()
    try:
        return conn.execute("SELECT * FROM assignments WHERE id = ?", (assignment_id,)).fetchone()
    finally:
        conn.close()


# ──────────────────────────────────────────────
# SUBMISSIONS
# ──────────────────────────────────────────────

def submit_assignment(assignment_id: int, student_telegram_id: int,
                      answer_text: Optional[str] = None,
                      file_id: Optional[str] = None) -> bool:
    conn = get_connection()
    try:
        student = conn.execute(
            "SELECT id FROM users WHERE telegram_id = ?", (student_telegram_id,)
        ).fetchone()
        if not student:
            return False
        conn.execute("""
            INSERT OR REPLACE INTO submissions (assignment_id, student_id, answer_text, file_id)
            VALUES (?,?,?,?)
        """, (assignment_id, student["id"], answer_text, file_id))
        conn.commit()
        return True
    finally:
        conn.close()


def grade_submission(submission_id: int, grade: int, feedback: str = ""):
    conn = get_connection()
    try:
        conn.execute("""
            UPDATE submissions
            SET grade = ?, feedback = ?, graded_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (grade, feedback, submission_id))
        conn.commit()
    finally:
        conn.close()


def get_submissions_by_assignment(assignment_id: int) -> List[sqlite3.Row]:
    conn = get_connection()
    try:
        return conn.execute("""
            SELECT s.*, u.full_name as student_name, u.telegram_id as student_telegram_id
            FROM submissions s
            JOIN users u ON u.id = s.student_id
            WHERE s.assignment_id = ?
            ORDER BY s.submitted_at DESC
        """, (assignment_id,)).fetchall()
    finally:
        conn.close()


def get_student_submissions(student_telegram_id: int) -> List[sqlite3.Row]:
    conn = get_connection()
    try:
        return conn.execute("""
            SELECT s.*, a.title as assignment_title, l.title as lesson_title
            FROM submissions s
            JOIN assignments a ON a.id = s.assignment_id
            JOIN lessons l ON l.id = a.lesson_id
            JOIN users u ON u.id = s.student_id
            WHERE u.telegram_id = ?
            ORDER BY s.submitted_at DESC
        """, (student_telegram_id,)).fetchall()
    finally:
        conn.close()


# ──────────────────────────────────────────────
# ENROLLMENTS
# ──────────────────────────────────────────────

def enroll_student(student_telegram_id: int, teacher_telegram_id: int) -> bool:
    conn = get_connection()
    try:
        student = conn.execute(
            "SELECT id FROM users WHERE telegram_id = ?", (student_telegram_id,)
        ).fetchone()
        teacher = conn.execute(
            "SELECT id FROM users WHERE telegram_id = ?", (teacher_telegram_id,)
        ).fetchone()
        if not student or not teacher:
            return False
        conn.execute(
            "INSERT OR IGNORE INTO enrollments (student_id, teacher_id) VALUES (?,?)",
            (student["id"], teacher["id"])
        )
        conn.commit()
        return conn.total_changes > 0
    finally:
        conn.close()


def get_students_of_teacher(teacher_telegram_id: int) -> List[sqlite3.Row]:
    conn = get_connection()
    try:
        return conn.execute("""
            SELECT u.*
            FROM enrollments e
            JOIN users u ON u.id = e.student_id
            JOIN users t ON t.id = e.teacher_id
            WHERE t.telegram_id = ?
        """, (teacher_telegram_id,)).fetchall()
    finally:
        conn.close()


def get_teachers_of_student(student_telegram_id: int) -> List[sqlite3.Row]:
    conn = get_connection()
    try:
        return conn.execute("""
            SELECT u.*
            FROM enrollments e
            JOIN users u ON u.id = e.teacher_id
            JOIN users s ON s.id = e.student_id
            WHERE s.telegram_id = ?
        """, (student_telegram_id,)).fetchall()
    finally:
        conn.close()


# ──────────────────────────────────────────────
# ADMIN
# ──────────────────────────────────────────────

def get_stats() -> dict:
    conn = get_connection()
    try:
        total_users    = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_teachers = conn.execute("SELECT COUNT(*) FROM users WHERE role='teacher'").fetchone()[0]
        total_students = conn.execute("SELECT COUNT(*) FROM users WHERE role='student'").fetchone()[0]
        total_lessons  = conn.execute("SELECT COUNT(*) FROM lessons").fetchone()[0]
        total_assigns  = conn.execute("SELECT COUNT(*) FROM assignments").fetchone()[0]
        total_subs     = conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0]
        graded_subs    = conn.execute("SELECT COUNT(*) FROM submissions WHERE grade IS NOT NULL").fetchone()[0]
        return {
            "total_users": total_users,
            "teachers": total_teachers,
            "students": total_students,
            "lessons": total_lessons,
            "assignments": total_assigns,
            "submissions": total_subs,
            "graded": graded_subs,
        }
    finally:
        conn.close()


def get_all_users() -> List[sqlite3.Row]:
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM users ORDER BY created_at DESC"
        ).fetchall()
    finally:
        conn.close()


def get_user_by_id(user_id: int) -> Optional[sqlite3.Row]:
    conn = get_connection()
    try:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    finally:
        conn.close()


def block_user(telegram_id: int):
    conn = get_connection()
    try:
        conn.execute("UPDATE users SET role = 'blocked' WHERE telegram_id = ?", (telegram_id,))
        conn.commit()
    finally:
        conn.close()


def unblock_user(telegram_id: int, role: str = "student"):
    conn = get_connection()
    try:
        conn.execute("UPDATE users SET role = ? WHERE telegram_id = ?", (role, telegram_id))
        conn.commit()
    finally:
        conn.close()


def delete_lesson(lesson_id: int):
    conn = get_connection()
    try:
        conn.execute("DELETE FROM assignments WHERE lesson_id = ?", (lesson_id,))
        conn.execute("DELETE FROM lessons WHERE id = ?", (lesson_id,))
        conn.commit()
    finally:
        conn.close()


def get_all_users_telegram_ids() -> List[int]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT telegram_id FROM users WHERE role != 'blocked'"
        ).fetchall()
        return [r[0] for r in rows]
    finally:
        conn.close()
