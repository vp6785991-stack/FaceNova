# app.py — FaceNova AI Attendance System
# Gunicorn start: gunicorn app:app

import os

# Load .env file if present
if os.path.exists(".env"):
    for line in open(".env"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

import db
import auth

# Initialise database
db.init_db()

# Create SUPER_ADMIN from env vars if set
if os.environ.get("SUPER_ADMIN_PASSWORD"):
    auth.bootstrap_super_admin()

# Import Flask app object — must be named 'app' for gunicorn
from app_core import app

# Register all routes
import routes  # noqa: F401

# Gunicorn needs 'app' at module level — it is already imported above

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

