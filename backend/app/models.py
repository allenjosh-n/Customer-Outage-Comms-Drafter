"""
User model — SQLite-backed, no ORM required.
Uses werkzeug's built-in password hashing (pbkdf2) — no C extensions needed.
"""
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

# /tmp is the only writable directory on Vercel serverless
# Fall back to /tmp/users.db unless DB_PATH is explicitly set
_default_db = "/tmp/users.db" if os.path.exists("/tmp") else os.path.join(
    os.path.dirname(__file__), "..", "users.db"
)
DB_PATH = os.environ.get("DB_PATH", _default_db)


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the users table if it doesn't exist."""
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT    NOT NULL UNIQUE,
                email    TEXT    NOT NULL UNIQUE,
                password TEXT    NOT NULL,
                created  DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def create_user(username: str, email: str, password: str) -> dict | None:
    """Hash password and insert user. Returns the new user or None on duplicate."""
    hashed = generate_password_hash(password)
    try:
        with _get_conn() as conn:
            cursor = conn.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username.strip(), email.strip().lower(), hashed),
            )
            conn.commit()
            return {"id": cursor.lastrowid, "username": username, "email": email}
    except sqlite3.IntegrityError:
        return None  # username or email already taken


def get_user_by_username(username: str) -> sqlite3.Row | None:
    with _get_conn() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE username = ?", (username.strip(),)
        ).fetchone()


def get_user_by_email(email: str) -> sqlite3.Row | None:
    with _get_conn() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE email = ?", (email.strip().lower(),)
        ).fetchone()


def verify_password(plain: str, hashed: str) -> bool:
    return check_password_hash(hashed, plain)
