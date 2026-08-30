# app.py — FaceNova AI Attendance System
# Run: python app.py
# First time? Go to http://localhost:5000/setup in your browser.
#
# Files needed in same folder:
#   app.py, app_core.py, routes.py, db.py, auth.py, styles.py
#
# Optional .env file for configuration (see .env.example)

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

# Initialise database tables
db.init_db()

# Create SUPER_ADMIN from env vars if set and no admin exists yet
# OR visit /setup in your browser for a guided setup wizard
if os.environ.get("SUPER_ADMIN_PASSWORD"):
    auth.bootstrap_super_admin()

from app_core import app
import routes  # registers all routes with the app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
