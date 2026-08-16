# app.py — FaceNova AI Attendance System
# Run: python app.py
#
# Required env vars (set in .env or shell):
#   FLASK_SECRET_KEY      — random string for session signing
#   SUPER_ADMIN_USERNAME  — superadmin username (default: superadmin)
#   SUPER_ADMIN_PASSWORD  — superadmin password (auto-generated if not set)
#   SUPER_ADMIN_EMAIL     — optional email

import os

# Load .env file if present (no extra package needed)
if os.path.exists(".env"):
    for line in open(".env"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

import db
import auth

# Initialise database + create SUPER_ADMIN on first run
db.init_db()
auth.bootstrap_super_admin()

from app_core import app
import routes  # registers all routes

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

