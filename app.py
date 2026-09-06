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

# ── Always recreate SUPER_ADMIN from env vars on every startup ────
su_user = os.environ.get("SUPER_ADMIN_USERNAME", "").strip()
su_pass = os.environ.get("SUPER_ADMIN_PASSWORD", "").strip()

# Fallback default credentials if env vars not set
# CHANGE THESE after first login!
if not su_user:
    su_user = "superadmin"
if not su_pass:
    su_pass = "FaceNova@2024"

conn = db.get_conn()
existing = conn.execute(
    "SELECT id FROM users WHERE username=?", (su_user,)
).fetchone()
if existing:
    conn.execute(
        "UPDATE users SET password_hash=?, is_active=1, role='SUPER_ADMIN' WHERE username=?",
        (hash_password(su_pass), su_user)
    )
    print(f"[FaceNova] Super Admin '{su_user}' updated.")
else:
    conn.execute(
        """INSERT INTO users
           (school_id, role, username, password_hash, full_name, is_active, created_at)
           VALUES (NULL, 'SUPER_ADMIN', ?, ?, 'Super Administrator', 1, datetime('now'))""",
        (su_user, hash_password(su_pass))
    )
    print(f"[FaceNova] Super Admin '{su_user}' created.")
conn.commit()
conn.close()

# Import Flask app — must be named 'app' for gunicorn
from app_core import app

# Register all routes
import routes  # noqa: F401

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)




