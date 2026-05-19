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
            phone       TEXT,
            role        TEXT NOT NULL DEFAULT 'user',
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS ads (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            category    TEXT NOT NULL,
            fullname    TEXT NOT NULL,
            yosh        TEXT,
            texno       TEXT NOT NULL,
            aloqa       TEXT NOT NULL,
            hudud       TEXT NOT NULL,
            narx        TEXT,
            vaqt        TEXT,
            maqsad      TEXT,
            views       INTEGER DEFAULT 0,
            is_active   INTEGER DEFAULT 1,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)

    conn.commit()
    conn.close()
    logging.info("Jadvallar yaratildi.")


# ──────────────────────────────────────────────
# USERS
# ──────────────────────────────────────────────

def add_user(telegram_id: int, full_name: str, username: Optional[str]) -> bool:
    conn = get_connection()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO users (telegram_id, full_name, username) VALUES (?,?,?)",
            (telegram_id, full_name, username)
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


def set_user_phone(telegram_id: int, phone: str):
    conn = get_connection()
    try:
        conn.execute("UPDATE users SET phone = ? WHERE telegram_id = ?", (phone, telegram_id))
        conn.commit()
    finally:
        conn.close()


def set_user_role(telegram_id: int, role: str):
    conn = get_connection()
    try:
        conn.execute("UPDATE users SET role = ? WHERE telegram_id = ?", (role, telegram_id))
        conn.commit()
    finally:
        conn.close()


def block_user(telegram_id: int):
    conn = get_connection()
    try:
        conn.execute("UPDATE users SET role = 'blocked' WHERE telegram_id = ?", (telegram_id,))
        conn.commit()
    finally:
        conn.close()


def unblock_user(telegram_id: int):
    conn = get_connection()
    try:
        conn.execute("UPDATE users SET role = 'user' WHERE telegram_id = ?", (telegram_id,))
        conn.commit()
    finally:
        conn.close()


def get_all_users() -> List[sqlite3.Row]:
    conn = get_connection()
    try:
        return conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
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


def get_stats() -> dict:
    conn = get_connection()
    try:
        total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_ads   = conn.execute("SELECT COUNT(*) FROM ads WHERE is_active=1").fetchone()[0]
        cats = {}
        for cat in ('ustoz', 'shogird', 'hodim', 'ish_joyi', 'sherik'):
            cats[cat] = conn.execute(
                "SELECT COUNT(*) FROM ads WHERE category=? AND is_active=1", (cat,)
            ).fetchone()[0]
        return {
            "total_users": total_users,
            "total_ads": total_ads,
            "cats": cats,
        }
    finally:
        conn.close()


# ──────────────────────────────────────────────
# ADS
# ──────────────────────────────────────────────

def add_ad(user_telegram_id: int, category: str, fullname: str,
           yosh: str, texno: str, aloqa: str, hudud: str,
           narx: str, vaqt: str, maqsad: str) -> int:
    conn = get_connection()
    try:
        user = conn.execute(
            "SELECT id FROM users WHERE telegram_id = ?", (user_telegram_id,)
        ).fetchone()
        cursor = conn.execute("""
            INSERT INTO ads (user_id, category, fullname, yosh, texno, aloqa, hudud, narx, vaqt, maqsad)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (user['id'], category, fullname, yosh, texno, aloqa, hudud, narx, vaqt, maqsad))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_ads(category: str, offset: int = 0, limit: int = 5,
            hudud: Optional[str] = None, texno: Optional[str] = None) -> List[sqlite3.Row]:
    conn = get_connection()
    try:
        query = """
            SELECT a.*, u.telegram_id as user_telegram_id, u.username as user_username
            FROM ads a
            JOIN users u ON u.id = a.user_id
            WHERE a.category = ? AND a.is_active = 1
        """
        params = [category]
        if hudud:
            query += " AND LOWER(a.hudud) LIKE ?"
            params.append(f"%{hudud.lower()}%")
        if texno:
            query += " AND LOWER(a.texno) LIKE ?"
            params.append(f"%{texno.lower()}%")
        query += " ORDER BY a.created_at DESC LIMIT ? OFFSET ?"
        params += [limit, offset]
        return conn.execute(query, params).fetchall()
    finally:
        conn.close()


def count_ads(category: str, hudud: Optional[str] = None, texno: Optional[str] = None) -> int:
    conn = get_connection()
    try:
        query = "SELECT COUNT(*) FROM ads WHERE category = ? AND is_active = 1"
        params = [category]
        if hudud:
            query += " AND LOWER(hudud) LIKE ?"
            params.append(f"%{hudud.lower()}%")
        if texno:
            query += " AND LOWER(texno) LIKE ?"
            params.append(f"%{texno.lower()}%")
        return conn.execute(query, params).fetchone()[0]
    finally:
        conn.close()


def get_ad(ad_id: int) -> Optional[sqlite3.Row]:
    conn = get_connection()
    try:
        return conn.execute("""
            SELECT a.*, u.telegram_id as user_telegram_id, u.username as user_username, u.phone as user_phone
            FROM ads a
            JOIN users u ON u.id = a.user_id
            WHERE a.id = ?
        """, (ad_id,)).fetchone()
    finally:
        conn.close()


def increment_views(ad_id: int):
    conn = get_connection()
    try:
        conn.execute("UPDATE ads SET views = views + 1 WHERE id = ?", (ad_id,))
        conn.commit()
    finally:
        conn.close()


def get_my_ads(user_telegram_id: int) -> List[sqlite3.Row]:
    conn = get_connection()
    try:
        return conn.execute("""
            SELECT a.* FROM ads a
            JOIN users u ON u.id = a.user_id
            WHERE u.telegram_id = ?
            ORDER BY a.created_at DESC
        """, (user_telegram_id,)).fetchall()
    finally:
        conn.close()


def toggle_ad(ad_id: int, is_active: int):
    conn = get_connection()
    try:
        conn.execute("UPDATE ads SET is_active = ? WHERE id = ?", (is_active, ad_id))
        conn.commit()
    finally:
        conn.close()


def delete_ad(ad_id: int):
    conn = get_connection()
    try:
        conn.execute("DELETE FROM ads WHERE id = ?", (ad_id,))
        conn.commit()
    finally:
        conn.close()


def get_all_ads_admin() -> List[sqlite3.Row]:
    conn = get_connection()
    try:
        return conn.execute("""
            SELECT a.*, u.full_name as user_name, u.telegram_id as user_telegram_id
            FROM ads a
            JOIN users u ON u.id = a.user_id
            ORDER BY a.created_at DESC
        """).fetchall()
    finally:
        conn.close()
