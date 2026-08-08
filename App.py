# app.py — FaceNova AI Attendance System
# Run this file to start the server: python app.py
#
# Project structure:
#   app.py       — app entry point (this file)
#   app_core.py  — config, constants, helpers, layout
#   routes.py    — all page/API route handlers
#   styles.py    — CSS styles
#
from app_core import app
import routes  # registers all routes with the app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
