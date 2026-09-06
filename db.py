# db.py — FaceNova Database Layer
# SQLite via Python built-in sqlite3. No extra installs needed.

import sqlite3, os
from datetime import datetime, timedelta

# On Render: use /tmp (survives restarts within same session)
# Locally: use data/ folder
if os.environ.get("RENDER"):
    DB_PATH = "/tmp/facenova.db"
else:
    os.makedirs("data", exist_ok=True)
    DB_PATH = os.path.join("data", "facenova.db")

# ── Feature permission map per plan ──────────────────────────────────────
PLAN_FEATURES = {
    "FREE_TRIAL": {
        "label":            "Free Trial",
        "max_students":     50,
        "max_teachers":     2,
        "face_auth":        True,
        "basic_attendance": True,
        "basic_dashboard":  True,
        "reports":          False,
        "advanced_analytics": False,
        "multi_teacher":    False,
        "sections":         False,
        "csv_export":       False,
        "api_access":       False,
    },
    "BASIC": {
        "label":            "Basic",
        "max_students":     200,
        "max_teachers":     5,
        "face_auth":        True,
        "basic_attendance": True,
        "basic_dashboard":  True,
        "reports":          True,
        "advanced_analytics": False,
        "multi_teacher":    True,
        "sections":         True,
        "csv_export":       True,
        "api_access":       False,
    },
    "PROFESSIONAL": {
        "label":            "Professional",
        "max_students":     1000,
        "max_teachers":     20,
        "face_auth":        True,
        "basic_attendance": True,
        "basic_dashboard":  True,
        "reports":          True,
        "advanced_analytics": True,
        "multi_teacher":    True,
        "sections":         True,
        "csv_export":       True,
        "api_access":       False,
    },
    "ENTERPRISE": {
        "label":            "Enterprise",
        "max_students":     999999,
        "max_teachers":     999999,
        "face_auth":        True,
        "basic_attendance": True,
        "basic_dashboard":  True,
        "reports":          True,
        "advanced_analytics": True,
        "multi_teacher":    True,
        "sections":         True,
        "csv_export":       True,
        "api_access":       True,
    },
}

TRIAL_DAYS = 10


def get_conn():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create all tables if they don't exist. Safe to call on every startup."""
    conn = get_conn()
    c = conn.cursor()

    # ── schools ──────────────────────────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS schools (
        id          TEXT PRIMARY KEY,          -- slug: 'delhi-public-school'
        name        TEXT NOT NULL,
        address     TEXT DEFAULT '',
        email       TEXT DEFAULT '',
        phone       TEXT DEFAULT '',
        created_at  TEXT NOT NULL,
        is_active   INTEGER DEFAULT 1
    )""")

    # ── users ─────────────────────────────────────────────
    # roles: SUPER_ADMIN | SCHOOL_ADMIN | TEACHER
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        school_id     TEXT REFERENCES schools(id),  -- NULL for SUPER_ADMIN
        role          TEXT NOT NULL,
        username      TEXT NOT NULL UNIQUE,
        email         TEXT DEFAULT '',
        password_hash TEXT NOT NULL,
        full_name     TEXT DEFAULT '',
        teacher_id    TEXT DEFAULT '',
        assigned_sections TEXT DEFAULT '[]',        -- JSON list of section names
        is_active     INTEGER DEFAULT 1,
        created_at    TEXT NOT NULL,
        last_login    TEXT DEFAULT NULL
    )""")

    # ── subscriptions ─────────────────────────────────────
    # status: TRIAL | ACTIVE | EXPIRED | CANCELLED
    c.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
        id                 INTEGER PRIMARY KEY AUTOINCREMENT,
        school_id          TEXT NOT NULL REFERENCES schools(id),
        status             TEXT NOT NULL DEFAULT 'TRIAL',
        plan_name          TEXT NOT NULL DEFAULT 'FREE_TRIAL',
        trial_start        TEXT,
        trial_end          TEXT,
        subscription_start TEXT DEFAULT NULL,
        subscription_end   TEXT DEFAULT NULL,
        payment_status     TEXT DEFAULT 'NONE',    -- NONE | MOCK_PAID | CANCELLED
        updated_at         TEXT NOT NULL
    )""")

    # ── subscription history (never deleted) ─────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS sub_history (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        school_id  TEXT NOT NULL,
        event      TEXT NOT NULL,   -- TRIAL_STARTED | PLAN_CHANGED | EXPIRED | CANCELLED
        plan_name  TEXT,
        note       TEXT DEFAULT '',
        created_at TEXT NOT NULL
    )""")

    conn.commit()
    conn.close()


# ── School helpers ────────────────────────────────────────────────────────

def school_create(school_id, name, email="", phone="", address=""):
    conn = get_conn()
    now  = datetime.now().isoformat()
    try:
        conn.execute(
            "INSERT INTO schools (id,name,email,phone,address,created_at) VALUES (?,?,?,?,?,?)",
            (school_id, name, email, phone, address, now)
        )
        # auto-create 10-day trial subscription
        trial_end = (datetime.now() + timedelta(days=TRIAL_DAYS)).strftime("%Y-%m-%d")
        conn.execute(
            """INSERT INTO subscriptions
               (school_id,status,plan_name,trial_start,trial_end,updated_at)
               VALUES (?,?,?,?,?,?)""",
            (school_id, "TRIAL", "FREE_TRIAL", datetime.now().strftime("%Y-%m-%d"),
             trial_end, now)
        )
        conn.execute(
            "INSERT INTO sub_history (school_id,event,plan_name,note,created_at) VALUES (?,?,?,?,?)",
            (school_id, "TRIAL_STARTED", "FREE_TRIAL", "Auto 10-day trial on school creation", now)
        )
        conn.commit()
        return True, None
    except sqlite3.IntegrityError as e:
        return False, str(e)
    finally:
        conn.close()

def school_get(school_id):
    conn = get_conn()
    row  = conn.execute("SELECT * FROM schools WHERE id=?", (school_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def school_list():
    conn  = get_conn()
    rows  = conn.execute("SELECT * FROM schools ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── User helpers ──────────────────────────────────────────────────────────

def user_create(school_id, role, username, password_hash,
                full_name="", email="", teacher_id="", sections=None):
    conn = get_conn()
    now  = datetime.now().isoformat()
    try:
        conn.execute(
            """INSERT INTO users
               (school_id,role,username,email,password_hash,full_name,
                teacher_id,assigned_sections,created_at)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (school_id, role, username, email, password_hash,
             full_name, teacher_id,
             __import__('json').dumps(sections or []), now)
        )
        conn.commit()
        return True, None
    except sqlite3.IntegrityError as e:
        return False, str(e)
    finally:
        conn.close()

def user_get_by_username(username):
    conn = get_conn()
    row  = conn.execute(
        "SELECT * FROM users WHERE username=? AND is_active=1", (username,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None

def user_get_by_id(user_id):
    conn = get_conn()
    row  = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def users_by_school(school_id, role=None):
    conn  = get_conn()
    q     = "SELECT * FROM users WHERE school_id=?"
    args  = [school_id]
    if role:
        q    += " AND role=?"
        args.append(role)
    rows = conn.execute(q + " ORDER BY full_name", args).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def user_update(user_id, **fields):
    conn  = get_conn()
    sets  = ", ".join(f"{k}=?" for k in fields)
    vals  = list(fields.values()) + [user_id]
    conn.execute(f"UPDATE users SET {sets} WHERE id=?", vals)
    conn.commit()
    conn.close()

def user_set_last_login(user_id):
    conn = get_conn()
    conn.execute("UPDATE users SET last_login=? WHERE id=?",
                 (datetime.now().isoformat(), user_id))
    conn.commit()
    conn.close()


# ── Subscription helpers ──────────────────────────────────────────────────

def sub_get(school_id):
    """Return subscription row for school, computing live status."""
    conn = get_conn()
    row  = conn.execute(
        "SELECT * FROM subscriptions WHERE school_id=? ORDER BY id DESC LIMIT 1",
        (school_id,)
    ).fetchone()
    conn.close()
    if not row:
        return None
    rec   = dict(row)
    now   = datetime.now().date()
    stat  = rec["status"]

    if stat == "TRIAL":
        try:
            end       = datetime.strptime(rec["trial_end"], "%Y-%m-%d").date()
            days_left = (end - now).days
        except:
            days_left = 0
        if days_left <= 0:
            sub_expire(school_id)
            stat, days_left = "EXPIRED", 0
        rec["days_left"] = days_left
    elif stat == "ACTIVE":
        try:
            pend = datetime.strptime(rec["subscription_end"], "%Y-%m-%d").date()
            if pend < now:
                sub_expire(school_id)
                stat = "EXPIRED"
        except:
            pass
        rec["days_left"] = -1
    else:
        rec["days_left"] = 0

    rec["status"]       = stat
    rec["is_trial"]     = stat == "TRIAL"
    rec["is_active"]    = stat == "ACTIVE"
    rec["is_expired"]   = stat in ("EXPIRED","CANCELLED")
    rec["warn"]         = stat == "TRIAL" and 0 < rec.get("days_left",0) <= 3
    rec["features"]     = PLAN_FEATURES.get(rec["plan_name"], PLAN_FEATURES["FREE_TRIAL"])
    return rec

def sub_activate(school_id, plan_name, period_days):
    conn  = get_conn()
    now   = datetime.now()
    start = now.strftime("%Y-%m-%d")
    end   = (now + timedelta(days=period_days)).strftime("%Y-%m-%d")
    conn.execute(
        """UPDATE subscriptions
           SET status='ACTIVE', plan_name=?, subscription_start=?,
               subscription_end=?, payment_status='MOCK_PAID', updated_at=?
           WHERE school_id=?""",
        (plan_name, start, end, now.isoformat(), school_id)
    )
    conn.execute(
        "INSERT INTO sub_history (school_id,event,plan_name,note,created_at) VALUES (?,?,?,?,?)",
        (school_id, "PLAN_CHANGED", plan_name, f"Mock activated for {period_days} days", now.isoformat())
    )
    conn.commit()
    conn.close()

def sub_expire(school_id):
    conn = get_conn()
    now  = datetime.now().isoformat()
    conn.execute(
        "UPDATE subscriptions SET status='EXPIRED', updated_at=? WHERE school_id=?",
        (now, school_id)
    )
    conn.execute(
        "INSERT INTO sub_history (school_id,event,plan_name,note,created_at) VALUES (?,?,?,?,?)",
        (school_id, "EXPIRED", None, "Auto-expired", now)
    )
    conn.commit()
    conn.close()

def sub_cancel(school_id):
    conn = get_conn()
    now  = datetime.now().isoformat()
    conn.execute(
        "UPDATE subscriptions SET status='CANCELLED', updated_at=? WHERE school_id=?",
        (now, school_id)
    )
    conn.execute(
        "INSERT INTO sub_history (school_id,event,plan_name,note,created_at) VALUES (?,?,?,?,?)",
        (school_id, "CANCELLED", None, "Admin cancelled", now)
    )
    conn.commit()
    conn.close()

def sub_extend_trial(school_id, days):
    conn = get_conn()
    row  = conn.execute(
        "SELECT trial_end, status FROM subscriptions WHERE school_id=?", (school_id,)
    ).fetchone()
    if not row:
        conn.close()
        return
    now = datetime.now()
    try:
        base = datetime.strptime(row["trial_end"], "%Y-%m-%d")
        base = max(base, now)
    except:
        base = now
    new_end = (base + timedelta(days=days)).strftime("%Y-%m-%d")
    conn.execute(
        "UPDATE subscriptions SET trial_end=?, status='TRIAL', updated_at=? WHERE school_id=?",
        (new_end, now.isoformat(), school_id)
    )
    conn.execute(
        "INSERT INTO sub_history (school_id,event,plan_name,note,created_at) VALUES (?,?,?,?,?)",
        (school_id, "TRIAL_EXTENDED", "FREE_TRIAL", f"Extended by {days} days → {new_end}", now.isoformat())
    )
    conn.commit()
    conn.close()

def sub_history_get(school_id):
    conn  = get_conn()
    rows  = conn.execute(
        "SELECT * FROM sub_history WHERE school_id=? ORDER BY id DESC",
        (school_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def super_admin_exists():
    conn = get_conn()
    row  = conn.execute("SELECT id FROM users WHERE role='SUPER_ADMIN' LIMIT 1").fetchone()
    conn.close()
    return row is not None

