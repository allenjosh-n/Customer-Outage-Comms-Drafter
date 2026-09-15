"""
User + Workspace model — Supabase (PostgreSQL) backed via pg8000.
Falls back to SQLite for local development when DATABASE_URL is not set.
Roles: owner | incident_manager | viewer
"""
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE_URL = os.environ.get("DATABASE_URL", "")
_USE_PG = bool(DATABASE_URL)


# ── PostgreSQL connection ─────────────────────────────────────────────────────

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
    for sql in [
        """CREATE TABLE IF NOT EXISTS users (
            id       SERIAL PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            email    TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role     TEXT NOT NULL DEFAULT 'viewer',
            created  TIMESTAMPTZ DEFAULT NOW()
        )""",
        """CREATE TABLE IF NOT EXISTS incidents (
            id         SERIAL PRIMARY KEY,
            drafted_by TEXT NOT NULL DEFAULT '',
            severity   TEXT NOT NULL DEFAULT 'Low',
            entries    TEXT NOT NULL,
            created    TIMESTAMPTZ DEFAULT NOW()
        )""",
        """CREATE TABLE IF NOT EXISTS workspaces (
            id         SERIAL PRIMARY KEY,
            title      TEXT NOT NULL,
            severity   TEXT NOT NULL DEFAULT 'Medium',
            status     TEXT NOT NULL DEFAULT 'active',
            created_by TEXT NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )""",
        """CREATE TABLE IF NOT EXISTS workspace_members (
            id           SERIAL PRIMARY KEY,
            workspace_id INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
            user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            username     TEXT NOT NULL,
            joined_at    TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(workspace_id, user_id)
        )""",
        """CREATE TABLE IF NOT EXISTS workspace_updates (
            id               SERIAL PRIMARY KEY,
            workspace_id     INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
            created_by       TEXT NOT NULL,
            timeline         TEXT NOT NULL,
            phase            TEXT NOT NULL DEFAULT 'initial',
            customer_message TEXT NOT NULL DEFAULT '',
            summary_entry    TEXT NOT NULL DEFAULT '',
            created_at       TIMESTAMPTZ DEFAULT NOW()
        )""",
    ]:
        conn.run(sql)
    conn.close()


# ── SQLite connection ─────────────────────────────────────────────────────────

_SQLITE_PATH = os.path.join(os.path.dirname(__file__), "..", "users.db")


def _sqlite_conn():
    conn = sqlite3.connect(_SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _sqlite_init():
    with _sqlite_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email    TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role     TEXT NOT NULL DEFAULT 'viewer',
                created  DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS incidents (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                drafted_by TEXT NOT NULL DEFAULT '',
                severity   TEXT NOT NULL DEFAULT 'Low',
                entries    TEXT NOT NULL,
                created    DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS workspaces (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT NOT NULL,
                severity   TEXT NOT NULL DEFAULT 'Medium',
                status     TEXT NOT NULL DEFAULT 'active',
                created_by TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS workspace_members (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
                user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                username     TEXT NOT NULL,
                joined_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(workspace_id, user_id)
            );
            CREATE TABLE IF NOT EXISTS workspace_updates (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id     INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
                created_by       TEXT NOT NULL,
                timeline         TEXT NOT NULL,
                phase            TEXT NOT NULL DEFAULT 'initial',
                customer_message TEXT NOT NULL DEFAULT '',
                summary_entry    TEXT NOT NULL DEFAULT '',
                created_at       DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()


# ── User helpers ──────────────────────────────────────────────────────────────

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
        if _USE_PG:
            conn = _pg_conn()
            rows = conn.run("SELECT COUNT(*) FROM users WHERE role = 'owner'")
            conn.close()
            return rows[0][0] if rows else 0
        else:
            with _sqlite_conn() as conn:
                row = conn.execute("SELECT COUNT(*) FROM users WHERE role = 'owner'").fetchone()
            return row[0] if row else 0
    except Exception:
        return 0


def create_user(username: str, email: str, password: str, role: str = "viewer"):
    hashed = generate_password_hash(password)
    try:
        if _USE_PG:
            conn = _pg_conn()
            rows = conn.run(
                "INSERT INTO users (username, email, password, role) VALUES (:u, :e, :p, :r) RETURNING id",
                u=username.strip(), e=email.strip().lower(), p=hashed, r=role
            )
            conn.close()
            return {"id": rows[0][0], "username": username, "email": email, "role": role}
        else:
            with _sqlite_conn() as conn:
                cur = conn.execute(
                    "INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
                    (username.strip(), email.strip().lower(), hashed, role)
                )
                conn.commit()
                return {"id": cur.lastrowid, "username": username, "email": email, "role": role}
    except Exception as ex:
        if "unique" in str(ex).lower():
            return None
        raise


def get_user_by_username(username: str):
    try:
        if _USE_PG:
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
        else:
            with _sqlite_conn() as conn:
                row = conn.execute("SELECT * FROM users WHERE username = ?", (username.strip(),)).fetchone()
            return dict(row) if row else None
    except Exception as e:
        print(f"[get_user_by_username] ERROR: {e}")
        return None


def get_all_users() -> list:
    try:
        if _USE_PG:
            conn = _pg_conn()
            rows = conn.run("SELECT id, username, email, role, created FROM users ORDER BY created ASC")
            conn.close()
            return [{"id": r[0], "username": r[1], "email": r[2], "role": r[3], "created": str(r[4])} for r in rows]
        else:
            with _sqlite_conn() as conn:
                rows = conn.execute("SELECT id, username, email, role, created FROM users ORDER BY created ASC").fetchall()
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"[get_all_users] ERROR: {e}")
        return []


def update_user_role(user_id: int, role: str) -> bool:
    try:
        if _USE_PG:
            conn = _pg_conn()
            conn.run("UPDATE users SET role = :r WHERE id = :uid", r=role, uid=user_id)
            conn.close()
        else:
            with _sqlite_conn() as conn:
                conn.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
                conn.commit()
        return True
    except Exception as e:
        print(f"[update_user_role] ERROR: {e}")
        return False


def verify_password(plain: str, hashed: str) -> bool:
    return check_password_hash(hashed, plain)


# ── Incident history ──────────────────────────────────────────────────────────

def save_incident(drafted_by: str, severity: str, entries: list) -> bool:
    import json
    entries_json = json.dumps(entries)
    try:
        if _USE_PG:
            conn = _pg_conn()
            conn.run(
                "INSERT INTO incidents (drafted_by, severity, entries) VALUES (:db, :sev, :ent)",
                db=drafted_by, sev=severity, ent=entries_json
            )
            conn.close()
        else:
            with _sqlite_conn() as conn:
                conn.execute(
                    "INSERT INTO incidents (drafted_by, severity, entries) VALUES (?, ?, ?)",
                    (drafted_by, severity, entries_json)
                )
                conn.commit()
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


def get_recent_incidents(limit: int = 5) -> list:
    import json
    try:
        if _USE_PG:
            conn = _pg_conn()
            rows = conn.run(
                "SELECT id, drafted_by, severity, entries, created FROM incidents ORDER BY created DESC LIMIT :lim",
                lim=limit
            )
            conn.close()
            return [{"id": r[0], "drafted_by": r[1], "severity": r[2], "entries": json.loads(r[3]), "created": str(r[4])} for r in rows]
        else:
            with _sqlite_conn() as conn:
                rows = conn.execute(
                    "SELECT id, drafted_by, severity, entries, created FROM incidents ORDER BY created DESC LIMIT ?",
                    (limit,)
                ).fetchall()
            return [{"id": r["id"], "drafted_by": r["drafted_by"], "severity": r["severity"],
                     "entries": json.loads(r["entries"]), "created": r["created"]} for r in rows]
    except Exception as e:
        print(f"[get_recent_incidents] ERROR: {e}")
        return []


# ── Workspace functions ───────────────────────────────────────────────────────

def create_workspace(title: str, severity: str, created_by: str, user_id: int) -> dict:
    try:
        if _USE_PG:
            conn = _pg_conn()
            rows = conn.run(
                "INSERT INTO workspaces (title, severity, created_by) VALUES (:t, :s, :cb) RETURNING id",
                t=title, s=severity, cb=created_by
            )
            ws_id = rows[0][0]
            conn.run(
                "INSERT INTO workspace_members (workspace_id, user_id, username) VALUES (:wid, :uid, :un)",
                wid=ws_id, uid=user_id, un=created_by
            )
            conn.close()
        else:
            with _sqlite_conn() as conn:
                cur = conn.execute(
                    "INSERT INTO workspaces (title, severity, created_by) VALUES (?, ?, ?)",
                    (title, severity, created_by)
                )
                ws_id = cur.lastrowid
                conn.execute(
                    "INSERT INTO workspace_members (workspace_id, user_id, username) VALUES (?, ?, ?)",
                    (ws_id, user_id, created_by)
                )
                conn.commit()
        return {"id": ws_id, "title": title, "severity": severity, "status": "active", "created_by": created_by}
    except Exception as e:
        print(f"[create_workspace] ERROR: {e}")
        raise


def get_all_workspaces() -> list:
    try:
        if _USE_PG:
            conn = _pg_conn()
            rows = conn.run("""
                SELECT w.id, w.title, w.severity, w.status, w.created_by, w.created_at,
                       COUNT(wm.id) AS member_count
                FROM workspaces w
                LEFT JOIN workspace_members wm ON wm.workspace_id = w.id
                GROUP BY w.id, w.title, w.severity, w.status, w.created_by, w.created_at
                ORDER BY w.created_at DESC
            """)
            conn.close()
            return [{"id": r[0], "title": r[1], "severity": r[2], "status": r[3],
                     "created_by": r[4], "created_at": str(r[5]), "member_count": r[6]} for r in rows]
        else:
            with _sqlite_conn() as conn:
                rows = conn.execute("""
                    SELECT w.id, w.title, w.severity, w.status, w.created_by, w.created_at,
                           COUNT(wm.id) AS member_count
                    FROM workspaces w
                    LEFT JOIN workspace_members wm ON wm.workspace_id = w.id
                    GROUP BY w.id ORDER BY w.created_at DESC
                """).fetchall()
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"[get_all_workspaces] ERROR: {e}")
        return []


def get_workspace(workspace_id: int):
    try:
        if _USE_PG:
            conn = _pg_conn()
            ws_rows = conn.run(
                "SELECT id, title, severity, status, created_by, created_at FROM workspaces WHERE id = :id",
                id=workspace_id
            )
            if not ws_rows:
                conn.close()
                return None
            r = ws_rows[0]
            ws = {"id": r[0], "title": r[1], "severity": r[2], "status": r[3],
                  "created_by": r[4], "created_at": str(r[5])}
            mem_rows = conn.run(
                "SELECT id, user_id, username, joined_at FROM workspace_members WHERE workspace_id = :wid ORDER BY joined_at ASC",
                wid=workspace_id
            )
            ws["members"] = [{"id": m[0], "user_id": m[1], "username": m[2], "joined_at": str(m[3])} for m in mem_rows]
            upd_rows = conn.run(
                "SELECT id, created_by, timeline, phase, customer_message, summary_entry, created_at "
                "FROM workspace_updates WHERE workspace_id = :wid ORDER BY created_at ASC",
                wid=workspace_id
            )
            ws["updates"] = [{"id": u[0], "created_by": u[1], "timeline": u[2], "phase": u[3],
                               "customer_message": u[4], "summary_entry": u[5], "created_at": str(u[6])} for u in upd_rows]
            conn.close()
            return ws
        else:
            with _sqlite_conn() as conn:
                row = conn.execute(
                    "SELECT id, title, severity, status, created_by, created_at FROM workspaces WHERE id = ?",
                    (workspace_id,)
                ).fetchone()
                if not row:
                    return None
                ws = dict(row)
                ws["members"] = [dict(m) for m in conn.execute(
                    "SELECT id, user_id, username, joined_at FROM workspace_members WHERE workspace_id = ? ORDER BY joined_at ASC",
                    (workspace_id,)
                ).fetchall()]
                ws["updates"] = [dict(u) for u in conn.execute(
                    "SELECT id, created_by, timeline, phase, customer_message, summary_entry, created_at "
                    "FROM workspace_updates WHERE workspace_id = ? ORDER BY created_at ASC",
                    (workspace_id,)
                ).fetchall()]
            return ws
    except Exception as e:
        print(f"[get_workspace] ERROR: {e}")
        return None


def get_workspace_members(workspace_id: int) -> list:
    try:
        if _USE_PG:
            conn = _pg_conn()
            rows = conn.run(
                "SELECT id, user_id, username, joined_at FROM workspace_members WHERE workspace_id = :wid ORDER BY joined_at ASC",
                wid=workspace_id
            )
            conn.close()
            return [{"id": r[0], "user_id": r[1], "username": r[2], "joined_at": str(r[3])} for r in rows]
        else:
            with _sqlite_conn() as conn:
                rows = conn.execute(
                    "SELECT id, user_id, username, joined_at FROM workspace_members WHERE workspace_id = ? ORDER BY joined_at ASC",
                    (workspace_id,)
                ).fetchall()
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"[get_workspace_members] ERROR: {e}")
        return []


def add_workspace_member(workspace_id: int, user_id: int, username: str) -> bool:
    try:
        if _USE_PG:
            conn = _pg_conn()
            conn.run(
                "INSERT INTO workspace_members (workspace_id, user_id, username) VALUES (:wid, :uid, :un)",
                wid=workspace_id, uid=user_id, un=username
            )
            conn.close()
        else:
            with _sqlite_conn() as conn:
                conn.execute(
                    "INSERT INTO workspace_members (workspace_id, user_id, username) VALUES (?, ?, ?)",
                    (workspace_id, user_id, username)
                )
                conn.commit()
        return True
    except Exception as e:
        if "unique" in str(e).lower():
            return False
        print(f"[add_workspace_member] ERROR: {e}")
        return False


def remove_workspace_member(workspace_id: int, user_id: int) -> bool:
    try:
        if _USE_PG:
            conn = _pg_conn()
            conn.run(
                "DELETE FROM workspace_members WHERE workspace_id = :wid AND user_id = :uid",
                wid=workspace_id, uid=user_id
            )
            conn.close()
        else:
            with _sqlite_conn() as conn:
                conn.execute(
                    "DELETE FROM workspace_members WHERE workspace_id = ? AND user_id = ?",
                    (workspace_id, user_id)
                )
                conn.commit()
        return True
    except Exception as e:
        print(f"[remove_workspace_member] ERROR: {e}")
        return False


def add_workspace_update(workspace_id: int, created_by: str, timeline: str,
                          phase: str, customer_message: str, summary_entry: str) -> dict:
    try:
        if _USE_PG:
            conn = _pg_conn()
            rows = conn.run(
                "INSERT INTO workspace_updates (workspace_id, created_by, timeline, phase, customer_message, summary_entry) "
                "VALUES (:wid, :cb, :tl, :ph, :cm, :se) RETURNING id, created_at",
                wid=workspace_id, cb=created_by, tl=timeline, ph=phase, cm=customer_message, se=summary_entry
            )
            upd_id, created_at = rows[0][0], rows[0][1]
            conn.close()
        else:
            with _sqlite_conn() as conn:
                cur = conn.execute(
                    "INSERT INTO workspace_updates (workspace_id, created_by, timeline, phase, customer_message, summary_entry) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (workspace_id, created_by, timeline, phase, customer_message, summary_entry)
                )
                upd_id = cur.lastrowid
                conn.commit()
                row = conn.execute("SELECT created_at FROM workspace_updates WHERE id = ?", (upd_id,)).fetchone()
                created_at = row[0] if row else ""
        return {"id": upd_id, "workspace_id": workspace_id, "created_by": created_by,
                "timeline": timeline, "phase": phase, "customer_message": customer_message,
                "summary_entry": summary_entry, "created_at": str(created_at)}
    except Exception as e:
        print(f"[add_workspace_update] ERROR: {e}")
        raise


def close_workspace(workspace_id: int) -> bool:
    try:
        if _USE_PG:
            conn = _pg_conn()
            conn.run("UPDATE workspaces SET status = 'closed' WHERE id = :id", id=workspace_id)
            conn.close()
        else:
            with _sqlite_conn() as conn:
                conn.execute("UPDATE workspaces SET status = 'closed' WHERE id = ?", (workspace_id,))
                conn.commit()
        return True
    except Exception as e:
        print(f"[close_workspace] ERROR: {e}")
        return False
