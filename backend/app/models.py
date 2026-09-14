"""
User model — Supabase (PostgreSQL) backed via pg8000 (pure Python, no C extensions).
Falls back to SQLite for local development when DATABASE_URL is not set.
"""
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE_URL = os.environ.get("DATABASE_URL", "")
_USE_PG = bool(DATABASE_URL)


# ── PostgreSQL helpers (Supabase) ─────────────────────────────────────────────

def _pg_conn():
    import pg8000.native
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    # Parse URL but override password directly to avoid URL-encoding issues
    from urllib.parse import urlparse, unquote
    p = urlparse(DATABASE_URL)
    return pg8000.native.Connection(
        user=unquote(p.username or ""),
        password=unquote(p.password or ""),
        host=p.hostname or "",
        port=int(p.port or 6543),
        database=(p.path or "/postgres").lstrip("/"),
        ssl_context=ctx,
    )


def _pg_param(key: str) -> str:
    """Parse individual components from the DATABASE_URL."""
    from urllib.parse import urlparse
    p = urlparse(DATABASE_URL)
    return {
        "user":     p.username or "",
        "password": p.password or "",
        "host":     p.hostname or "",
        "port":     str(p.port or 5432),
        "database": (p.path or "/postgres").lstrip("/"),
    }[key]


def _pg_init():
    conn = _pg_conn()
    conn.run("""
        CREATE TABLE IF NOT EXISTS users (
            id       SERIAL PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            email    TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created  TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    conn.close()


def _pg_create_user(username, email, password):
    hashed = generate_password_hash(password)
    conn = _pg_conn()
    try:
        rows = conn.run(
            "INSERT INTO users (username, email, password) VALUES (:u, :e, :p) RETURNING id",
            u=username.strip(), e=email.strip().lower(), p=hashed
        )
        conn.close()
        return {"id": rows[0][0], "username": username, "email": email}
    except Exception as ex:
        conn.close()
        if "unique" in str(ex).lower():
            return None
        raise


def _pg_get_by_username(username):
    conn = _pg_conn()
    rows = conn.run(
        "SELECT id, username, email, password FROM users WHERE username = :u",
        u=username.strip()
    )
    conn.close()
    if not rows:
        return None
    r = rows[0]
    return {"id": r[0], "username": r[1], "email": r[2], "password": r[3]}


# ── SQLite helpers (local dev fallback) ───────────────────────────────────────

_SQLITE_PATH = os.path.join(os.path.dirname(__file__), "..", "users.db")


def _sqlite_conn():
    import sqlite3
    conn = sqlite3.connect(_SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _sqlite_init():
    with _sqlite_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email    TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                created  DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def _sqlite_create_user(username, email, password):
    hashed = generate_password_hash(password)
    try:
        with _sqlite_conn() as conn:
            cur = conn.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username.strip(), email.strip().lower(), hashed)
            )
            conn.commit()
            return {"id": cur.lastrowid, "username": username, "email": email}
    except sqlite3.IntegrityError:
        return None


def _sqlite_get_by_username(username):
    with _sqlite_conn() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username.strip(),)
        ).fetchone()
    return dict(row) if row else None


# ── Public API ────────────────────────────────────────────────────────────────

def init_db():
    try:
        if _USE_PG:
            _pg_init()
        else:
            _sqlite_init()
    except Exception as e:
        print(f"[init_db] WARNING: {e}")
        # Don't crash startup — tables may already exist


def create_user(username: str, email: str, password: str):
    if _USE_PG:
        return _pg_create_user(username, email, password)
    return _sqlite_create_user(username, email, password)


def get_user_by_username(username: str):
    if _USE_PG:
        return _pg_get_by_username(username)
    return _sqlite_get_by_username(username)


def verify_password(plain: str, hashed: str) -> bool:
    return check_password_hash(hashed, plain)
