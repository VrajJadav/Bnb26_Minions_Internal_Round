import re
import secrets
import sqlite3
import string
from datetime import datetime

DB_FILE = "relearn.db"


def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)


def make_initials(name):
    parts = [p for p in re.split(r"\s+", name.strip()) if p]

    if len(parts) >= 2:
        initials = (parts[0][0] + parts[-1][0]).upper()
    elif parts:
        initials = parts[0][:2].upper()
    else:
        initials = "RL"

    return initials[:2]


def make_user_id(initials):
    alphabet = string.ascii_uppercase + string.digits

    while True:
        suffix = "".join(secrets.choice(alphabet) for _ in range(4))
        user_id = f"RL-{initials}-{suffix}"

        conn = get_connection()
        exists = conn.execute(
            "SELECT 1 FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        conn.close()

        if not exists:
            return user_id


def init_database():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            initials TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # Upgrade an older Re:Learn database automatically.
    columns = {
        row[1]
        for row in conn.execute("PRAGMA table_info(users)").fetchall()
    }

    if "initials" not in columns:
        conn.execute("ALTER TABLE users ADD COLUMN initials TEXT")

        rows = conn.execute(
            "SELECT id, name FROM users"
        ).fetchall()

        for user_id, name in rows:
            conn.execute(
                "UPDATE users SET initials = ? WHERE id = ?",
                (make_initials(name), user_id),
            )

    conn.execute("""
        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            question TEXT NOT NULL,
            user_answer TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            misconception TEXT,
            confidence REAL,
            is_correct INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS resolutions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            misconception TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def create_or_get_user(name):
    name = name.strip()

    conn = get_connection()

    existing = conn.execute("""
        SELECT id, name, initials
        FROM users
        WHERE LOWER(name) = LOWER(?)
        LIMIT 1
    """, (name,)).fetchone()

    if existing:
        conn.close()
        return {
            "id": existing[0],
            "name": existing[1],
            "initials": existing[2] or make_initials(existing[1]),
        }

    initials = make_initials(name)
    user_id = make_user_id(initials)

    conn.execute("""
        INSERT INTO users (id, name, initials, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        user_id,
        name,
        initials,
        datetime.now().isoformat(timespec="seconds"),
    ))

    conn.commit()
    conn.close()

    return {
        "id": user_id,
        "name": name,
        "initials": initials,
    }


def get_user_by_id(user_id):
    conn = get_connection()

    row = conn.execute("""
        SELECT id, name, initials
        FROM users
        WHERE id = ?
    """, (user_id,)).fetchone()

    conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "name": row[1],
        "initials": row[2] or make_initials(row[1]),
    }


def save_attempt(
    user_id,
    question,
    user_answer,
    correct_answer,
    misconception,
    confidence,
    is_correct,
):
    conn = get_connection()

    conn.execute("""
        INSERT INTO attempts (
            user_id,
            question,
            user_answer,
            correct_answer,
            misconception,
            confidence,
            is_correct,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        question,
        user_answer,
        correct_answer,
        misconception,
        confidence,
        int(is_correct),
        datetime.now().isoformat(timespec="seconds"),
    ))

    conn.commit()
    conn.close()


def save_resolution(user_id, misconception):
    conn = get_connection()

    conn.execute("""
        INSERT INTO resolutions (
            user_id,
            misconception,
            created_at
        )
        VALUES (?, ?, ?)
    """, (
        user_id,
        misconception,
        datetime.now().isoformat(timespec="seconds"),
    ))

    conn.commit()
    conn.close()


def get_user_stats(user_id):
    conn = get_connection()

    total = conn.execute("""
        SELECT COUNT(*)
        FROM attempts
        WHERE user_id = ?
    """, (user_id,)).fetchone()[0]

    correct = conn.execute("""
        SELECT COUNT(*)
        FROM attempts
        WHERE user_id = ?
        AND is_correct = 1
    """, (user_id,)).fetchone()[0]

    resolved = conn.execute("""
        SELECT COUNT(*)
        FROM resolutions
        WHERE user_id = ?
    """, (user_id,)).fetchone()[0]

    accuracy = round(correct / total * 100) if total else 0

    rows = conn.execute("""
        SELECT is_correct
        FROM attempts
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,)).fetchall()

    streak = 0
    for row in rows:
        if row[0] == 1:
            streak += 1
        else:
            break

    conn.close()

    return {
        "total": total,
        "correct": correct,
        "accuracy": accuracy,
        "resolved": resolved,
        "streak": streak,
    }


def get_misconception_stats(user_id):
    conn = get_connection()

    rows = conn.execute("""
        SELECT misconception, COUNT(*) AS attempts
        FROM attempts
        WHERE user_id = ?
        AND misconception IS NOT NULL
        GROUP BY misconception
        ORDER BY attempts DESC
    """, (user_id,)).fetchall()

    result = []

    for label, attempts in rows:
        resolved = conn.execute("""
            SELECT COUNT(*)
            FROM resolutions
            WHERE user_id = ?
            AND misconception = ?
        """, (user_id, label)).fetchone()[0]

        resolution_rate = round(
            min(resolved / attempts * 100, 100)
        ) if attempts else 0

        result.append({
            "label": label,
            "attempts": attempts,
            "resolved": resolved,
            "resolution_rate": resolution_rate,
        })

    conn.close()
    return result
