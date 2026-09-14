"""
User model — Supabase (PostgreSQL) backed via pg8000.
Falls back to SQLite for local development when DATABASE_URL is not set.
Roles: owner | incident_manager | viewer
"""
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE_URL = os.environ.get("DATABASE_URL", "")
_USE_PG = bool(DATABASE_URL)


# ── PostgreSQL helpers ────────────────────────────────────────────────────────

def _pg_conn():
    import pg8000.native, ssl
    from urllib.parse import urlparse, unquote
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    p = urlparse(DATABASE_URL)
    return pg8000.native.Connection(
        user=unquote(p.username or ""),
        password=unquote(p.password or ""),
        host=p.hostname or "",
        port=int(p.port or 6543),
        database=(p.path or "/postgres").lstrip("/"),
        ssl_context=ctx,
    )


def _pg_init():
    conn = _pg_conn()
    conn.run("""
        CREATE TABLE IF NOT EXISTS users (
            id       SERIAL PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            email    TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role     TEXT NOT NULL DEFAULT 'viewer',
            created  TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    conn.run("""
        CREATE TABLE IF NOT EXISTS incidents (
            id          SERIAL PRIMARY KEY,
            drafted_by  TEXT NOT NULL DEFAULT '',
            severity    TEXT NOT NULL DEFAULT 'Low',
            entries     TEXT NOT NULL,
            created     TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    conn.close()


def _pg_create_user(username, email, password, role):
    hashed = generate_password_hash(password)
    conn = _pg_conn()
    try:
        rows = conn.run(
            "INSERT INTO users (username, email, password, role) VALUES (:u, :e, :p, :r) RETURNING id",
            u=username.strip(), e=email.strip().lower(), p=hashed, r=role
        )
        conn.close()
        return {"id": rows[0][0], "username": username, "email": email, "role": role}
    except Exception as ex:
        conn.close()
        if "unique" in str(ex).lower():
            return None
        raise


def _pg_get_by_username(username):
    conn = _pg_conn()
    rows = conn.run(
        "SELECT id, username, email, password, role FROM users WHERE username = :u",
        u=username.strip()
    )
    conn.close()
    if not rows:
        return None
    r = rows[0]
    return {"id": r[0], "username": r[1], "email": r[2], "password": r[3], "role": r[4]}


def _pg_count_owners():
    conn = _pg_conn()
    rows = conn.run("SELECT COUNT(*) FROM users WHERE role = 'owner'")
    conn.close()
    return rows[0][0] if rows else 0


def _pg_get_all_users():
    conn = _pg_conn()
    rows = conn.run("SELECT id, username, email, role, created FROM users ORDER BY created ASC")
    conn.close()
    return [{"id": r[0], "username": r[1], "email": r[2], "role": r[3], "created": str(r[4])} for r in rows]


def _pg_update_role(user_id, role):
    conn = _pg_conn()
    conn.run("UPDATE users SET role = :r WHERE id = :uid", r=role, uid=user_id)
    conn.close()


def _pg_save_incident(drafted_by, severity, entries_json):
    conn = _pg_conn()
    conn.run(
        "INSERT INTO incidents (drafted_by, severity, entries) VALUES (:db, :sev, :ent)",
        db=drafted_by, sev=severity, ent=entries_json
    )
    conn.close()


def _pg_get_incidents(limit):
    conn = _pg_conn()
    rows = conn.run(
        "SELECT id, drafted_by, severity, entries, created FROM incidents ORDER BY created DESC LIMIT :lim",
        lim=limit
    )
    conn.close()
    return rows


# ── SQLite helpers ────────────────────────────────────────────────────────────

_SQLITE_PATH = os.path.join(os.path.dirname(__file__), "..", "users.db")


def _sqlite_conn():
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
                role     TEXT NOT NULL DEFAULT 'viewer',
                created  DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                drafted_by  TEXT NOT NULL DEFAULT '',
                severity    TEXT NOT NULL DEFAULT 'Low',
                entries     TEXT NOT NULL,
                created     DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def _sqlite_create_user(username, email, password, role):
    hashed = generate_password_hash(password)
    try:
        with _sqlite_conn() as conn:
            cur = conn.execute(
                "INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
                (username.strip(), email.strip().lower(), hashed, role)
            )
            conn.commit()
            return {"id": cur.lastrowid, "username": username, "email": email, "role": role}
    except sqlite3.IntegrityError:
        return None


def _sqlite_get_by_username(username):
    with _sqlite_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE username = ?", (username.strip(),)).fetchone()
    return dict(row) if row else None


def _sqlite_count_owners():
    with _sqlite_conn() as conn:
        row = conn.execute("SELECT COUNT(*) FROM users WHERE role = 'owner'").fetchone()
    return row[0] if row else 0


def _sqlite_get_all_users():
    with _sqlite_conn() as conn:
        rows = conn.execute("SELECT id, username, email, role, created FROM users ORDER BY created ASC").fetchall()
    return [dict(r) for r in rows]


def _sqlite_update_role(user_id, role):
    with _sqlite_conn() as conn:
        conn.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
        conn.commit()


def _sqlite_save_incident(drafted_by, severity, entries_json):
    with _sqlite_conn() as conn:
        conn.execute(
            "INSERT INTO incidents (drafted_by, severity, entries) VALUES (?, ?, ?)",
            (drafted_by, severity, entries_json)
        )
        conn.commit()


def _sqlite_get_incidents(limit):
    with _sqlite_conn() as conn:
        rows = conn.execute(
            "SELECT id, drafted_by, severity, entries, created FROM incidents ORDER BY created DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return [tuple(r) for r in rows]


# ── Public API ────────────────────────────────────────────────────────────────

def init_db():
    try:
        if _USE_PG:
            _pg_init()
        else:
            _sqlite_init()
    except Exception as e:
        print(f"[init_db] WARNING: {e}")


def count_owners() -> int:
    try:
        return _pg_count_owners() if _USE_PG else _sqlite_count_owners()
    except Exception:
        return 0


def create_user(username: str, email: str, password: str, role: str = "viewer"):
    if _USE_PG:
        return _pg_create_user(username, email, password, role)
    return _sqlite_create_user(username, email, password, role)


def get_user_by_username(username: str):
    if _USE_PG:
        return _pg_get_by_username(username)
    return _sqlite_get_by_username(username)


def get_all_users() -> list:
    try:
        return _pg_get_all_users() if _USE_PG else _sqlite_get_all_users()
    except Exception as e:
        print(f"[get_all_users] ERROR: {e}")
        return []


def update_user_role(user_id: int, role: str) -> bool:
    try:
        if _USE_PG:
            _pg_update_role(user_id, role)
        else:
            _sqlite_update_role(user_id, role)
        return True
    except Exception as e:
        print(f"[update_user_role] ERROR: {e}")
        return False


def verify_password(plain: str, hashed: str) -> bool:
    return check_password_hash(hashed, plain)


def save_incident(drafted_by: str, severity: str, entries: list) -> bool:
    import json
    entries_json = json.dumps(entries)
    try:
        if _USE_PG:
            _pg_save_incident(drafted_by, severity, entries_json)
        else:
            _sqlite_save_incident(drafted_by, severity, entries_json)
        return True
    except Exception as e:
        print(f"[save_incident] ERROR: {e}")
        return False


def delete_incident(incident_id: int) -> bool:
    try:
        if _USE_PG:
            conn = _pg_conn()
            conn.run("DELETE FROM incidents WHERE id = :id", id=incident_id)
            conn.close()
        else:
            with _sqlite_conn() as conn:
                conn.execute("DELETE FROM incidents WHERE id = ?", (incident_id,))
                conn.commit()
        return True
    except Exception as e:
        print(f"[delete_incident] ERROR: {e}")
        return False


def get_recent_incidents(limit: int = 5) -> list:    import json
    try:
        rows = _pg_get_incidents(limit) if _USE_PG else _sqlite_get_incidents(limit)
        return [
            {
                "id":         r[0],
                "drafted_by": r[1],
                "severity":   r[2],
                "entries":    json.loads(r[3]),
                "created":    str(r[4]),
            }
            for r in rows
        ]
    except Exception as e:
        print(f"[get_recent_incidents] ERROR: {e}")
        return []
