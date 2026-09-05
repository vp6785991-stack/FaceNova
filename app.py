# app.py — FaceNova AI Attendance System
# gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 1

import os

# Load .env file if present
if os.path.exists(".env"):
    for line in open(".env"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

import db
from auth import hash_password

# Initialise database tables every startup
db.init_db()

# ── Always recreate SUPER_ADMIN from env vars on every startup ────
# This fixes Render free plan resetting the database
su_user = os.environ.get("SUPER_ADMIN_USERNAME", "")
su_pass = os.environ.get("SUPER_ADMIN_PASSWORD", "")

if su_user and su_pass:
    import sqlite3
    conn = db.get_conn()
    existing = conn.execute(
        "SELECT id FROM users WHERE username=?", (su_user,)
    ).fetchone()
    if existing:
        # Update password hash in case it changed
        conn.execute(
            "UPDATE users SET password_hash=?, is_active=1 WHERE username=?",
            (hash_password(su_pass), su_user)
        )
    else:
        # Create fresh super admin
        conn.execute(
            """INSERT INTO users
               (school_id, role, username, password_hash, full_name, is_active, created_at)
               VALUES (NULL, 'SUPER_ADMIN', ?, ?, 'Super Administrator', 1, datetime('now'))""",
            (su_user, hash_password(su_pass))
        )
    conn.commit()
    conn.close()
    print(f"[FaceNova] Super Admin '{su_user}' ready.")
else:
    print("[FaceNova] WARNING: Set SUPER_ADMIN_USERNAME and SUPER_ADMIN_PASSWORD in environment variables!")

# Import Flask app — must be named 'app' for gunicorn
from app_core import app

# Register all routes
import routes  # noqa: F401

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)


