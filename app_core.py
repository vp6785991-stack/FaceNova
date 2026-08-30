# app_core.py — FaceNova Core: Config, Helpers, Layout
from flask import Flask, request, send_file, redirect, url_for, session
import os, csv, base64, json, calendar as cal_mod
from datetime import datetime, timedelta
import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from styles import CSS

# ── Flask app ─────────────────────────────────────────
import secrets as _secrets
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or _secrets.token_hex(32)
app.permanent_session_lifetime = timedelta(days=7)

DATA_DIR     = "data"
GRAPH_DIR    = "graphs"
# sections file is now per-school (computed at runtime)
SECTIONS_FILE = os.path.join("data", "sections.json")  # legacy fallback
os.makedirs(DATA_DIR,  exist_ok=True)
os.makedirs(GRAPH_DIR, exist_ok=True)
ATT_FILE = os.path.join(DATA_DIR, "attendance.csv")

# ──────────────────────────────────────────────────────
#  SUBSCRIPTION MODULE CONSTANTS
# ──────────────────────────────────────────────────────
SUB_FILE       = os.path.join(DATA_DIR, "_subscription.json")
TRIAL_DAYS     = 10

PLANS = {
    "monthly": {"name": "Monthly Plan",   "price": 199,  "period": 30,   "label": "₹199 / month"},
    "yearly":  {"name": "Yearly Plan",    "price": 1499, "period": 365,  "label": "₹1,499 / year"},
    "5year":   {"name": "5-Year Plan",    "price": 3999, "period": 1825, "label": "₹3,999 / 5 years"},
}

# Free routes — accessible without login (auth.py enforces the rest)
FREE_ROUTES = {"/login", "/logout", "/upgrade", "/upgrade/activate"}

try:
    face_detector = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
except Exception:
    face_detector = None

# ══════════════════════════════════════════════════════
#  SUBSCRIPTION BANNER (uses db layer)
# ══════════════════════════════════════════════════════

def sub_banner():
    """Return HTML banner for the current school's subscription status."""
    from flask import session as _sess
    import db as _db
    role      = _sess.get("role")
    school_id = _sess.get("school_id")

    if role == "SUPER_ADMIN":
        return '''<div style="background:linear-gradient(90deg,rgba(139,92,246,0.18),rgba(59,130,246,0.1));border-bottom:1px solid rgba(139,92,246,0.25);padding:8px 24px;font-size:12.5px;display:flex;align-items:center;gap:10px">
          <span>👑</span>
          <strong style="color:var(--purple-l)">Super Admin Mode</strong>
          <span style="color:var(--text2)">· Full platform access</span>
          <a href="/superadmin" style="margin-left:auto;color:var(--purple-l);font-size:12px;font-weight:700">Admin Panel →</a>
        </div>'''

    if not school_id:
        return ""

    sub = _db.sub_get(school_id)
    if not sub:
        return ""

    if sub["is_expired"]:
        return '''<div style="background:rgba(239,68,68,0.12);border-bottom:1px solid rgba(239,68,68,0.25);padding:8px 24px;font-size:12.5px;display:flex;align-items:center;gap:10px">
          <span>🔒</span><strong style="color:var(--red-l)">Subscription Expired</strong>
          <span style="color:var(--text2)">· Upgrade to restore access</span>
          <a href="/upgrade" style="margin-left:auto;background:var(--red);color:white;padding:4px 14px;border-radius:20px;font-size:12px;font-weight:700;text-decoration:none">Upgrade Now</a>
        </div>'''
    if sub["warn"]:
        return f'''<div style="background:rgba(245,158,11,0.12);border-bottom:1px solid rgba(245,158,11,0.25);padding:8px 24px;font-size:12.5px;display:flex;align-items:center;gap:10px">
          <span>⚠️</span><strong style="color:var(--amber-l)">Trial expires in {sub["days_left"]} day{"s" if sub["days_left"]!=1 else ""}!</strong>
          <a href="/upgrade" style="margin-left:auto;background:var(--amber);color:#000;padding:4px 14px;border-radius:20px;font-size:12px;font-weight:700;text-decoration:none">Upgrade</a>
        </div>'''
    if sub["is_trial"]:
        return f'''<div style="background:rgba(59,130,246,0.08);border-bottom:1px solid rgba(59,130,246,0.15);padding:8px 24px;font-size:12.5px;display:flex;align-items:center;gap:10px">
          <span>🎉</span><strong style="color:var(--blue)">Free Trial Active</strong>
          <span style="color:var(--text2)">· {sub["days_left"]} day{"s" if sub["days_left"]!=1 else ""} remaining</span>
          <a href="/upgrade" style="margin-left:auto;color:var(--blue);font-size:12px;font-weight:600;text-decoration:none">View Plans →</a>
        </div>'''
    if sub["is_active"]:
        plan_label = sub.get("plan_name","").replace("_"," ").title()
        return f'''<div style="background:rgba(16,185,129,0.07);border-bottom:1px solid rgba(16,185,129,0.15);padding:7px 24px;font-size:12px;display:flex;align-items:center;gap:10px">
          <span>✅</span><strong style="color:var(--green-l)">{plan_label} Active</strong>
          <span style="color:var(--muted)">· All features unlocked</span>
        </div>'''
    return ""

# ──────────────────────────────────────────────────────


DEFAULT_SECTIONS = ["6A","6B","7A","7B","8A","8B","8C","9A","9B","10A"]

def _sections_file(school_id=None):
    from flask import session as _sess
    sid = school_id or _sess.get("school_id") or "default"
    d   = os.path.join(DATA_DIR, sid)
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "sections.json")

def load_sections(school_id=None):
    """Return list of section names for this school."""
    sf = _sections_file(school_id)
    if os.path.exists(sf):
        try:
            return json.load(open(sf))
        except:
            pass
    return list(DEFAULT_SECTIONS)

def save_sections(sections, school_id=None):
    sf = _sections_file(school_id)
    os.makedirs(os.path.dirname(sf), exist_ok=True)
    json.dump(sections, open(sf,"w"))

def student_meta_file(name, school_id=None):
    sdir = school_data_dir(school_id)
    return os.path.join(sdir, name, "_meta.json")

def load_meta(name, school_id=None):
    """Load full meta dict for a student (school-scoped)."""
    mf = student_meta_file(name, school_id)
    if os.path.exists(mf):
        try: return json.load(open(mf))
        except: pass
    return {}

def save_meta(name, meta, school_id=None):
    mf = student_meta_file(name, school_id)
    os.makedirs(os.path.dirname(mf), exist_ok=True)
    json.dump(meta, open(mf,"w"))

def get_student_section(name, school_id=None):
    return load_meta(name, school_id).get("section","")

def set_student_section(name, section, school_id=None):
    meta = load_meta(name, school_id)
    meta["section"] = section
    save_meta(name, meta, school_id)

def get_profile_image(name, school_id=None):
    """Return URL for student profile image, school-scoped."""
    from flask import session as _sess
    sid      = school_id or _sess.get("school_id")
    user_dir = os.path.join(school_data_dir(sid), name)
    if not os.path.isdir(user_dir):
        return None
    for ext in ("jpg","jpeg","png","webp"):
        if os.path.exists(os.path.join(user_dir, f"_profile.{ext}")):
            return f"/profile-img/{name}"
    imgs = sorted([f for f in os.listdir(user_dir)
                   if f.lower().endswith((".jpg",".jpeg",".png"))
                   and not f.startswith("_")])
    return f"/img/{name}/{imgs[0]}" if imgs else None

def save_profile_image(name, file_storage, school_id=None):
    """Save uploaded file as square-cropped _profile.jpg, school-scoped."""
    from flask import session as _sess
    sid      = school_id or _sess.get("school_id")
    user_dir = os.path.join(school_data_dir(sid), name)
    os.makedirs(user_dir, exist_ok=True)
    for ext in ("jpg","jpeg","png","webp"):
        old = os.path.join(user_dir, f"_profile.{ext}")
        if os.path.exists(old):
            os.remove(old)
    dest = os.path.join(user_dir, "_profile.jpg")
    file_storage.save(dest)
    try:
        img = cv2.imread(dest)
        if img is not None:
            h, w   = img.shape[:2]
            side   = min(h, w)
            y0, x0 = (h-side)//2, (w-side)//2
            cv2.imwrite(dest, cv2.resize(img[y0:y0+side, x0:x0+side], (400,400)))
    except:
        pass

def students_in_section(section=""):
    """All students optionally filtered by section."""
    all_s = sorted([
        x for x in os.listdir(DATA_DIR)
        if os.path.isdir(os.path.join(DATA_DIR, x))
    ])
    if not section:
        return all_s
    return [s for s in all_s if get_student_section(s) == section]

# ══════════════════════════════════════════════════════
#  DATA HELPERS
# ══════════════════════════════════════════════════════

def att_file_for(school_id=None):
    """Return the correct attendance CSV path for a school."""
    if school_id:
        school_dir = os.path.join(DATA_DIR, school_id)
        os.makedirs(school_dir, exist_ok=True)
        return os.path.join(school_dir, "attendance.csv")
    # legacy fallback for single-school mode
    return ATT_FILE

def read_all_records(section="", school_id=None):
    """Return list of dicts: name, date, status, time, section.
       Always scoped to school_id (from session if not provided).
       Optionally further filter by section.
    """
    from flask import session as _sess
    sid  = school_id or _sess.get("school_id")
    path = att_file_for(sid)
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, newline="") as f:
        for r in csv.reader(f):
            if len(r) >= 3:
                rec = {
                    "name":    r[0],
                    "date":    r[1],
                    "status":  r[2],
                    "time":    r[3] if len(r) > 3 else "—",
                    "section": r[4] if len(r) > 4 else "",
                }
                if section and rec["section"] != section:
                    continue
                rows.append(rec)
    return rows

def write_att_record(row, school_id=None):
    """Append one attendance row to the correct school's CSV."""
    from flask import session as _sess
    sid  = school_id or _sess.get("school_id")
    path = att_file_for(sid)
    with open(path, "a", newline="") as f:
        csv.writer(f).writerow(row)

def school_data_dir(school_id=None):
    """Return and create the school-specific data directory."""
    from flask import session as _sess
    sid = school_id or _sess.get("school_id") or "default"
    d   = os.path.join(DATA_DIR, sid, "students")
    os.makedirs(d, exist_ok=True)
    return d

def enrolled_students(section="", school_id=None):
    """Return all students for this school, optionally filtered by section."""
    from flask import session as _sess
    sid  = school_id or _sess.get("school_id")
    sdir = school_data_dir(sid)
    all_s = sorted([
        x for x in os.listdir(sdir)
        if os.path.isdir(os.path.join(sdir, x))
    ])
    if not section:
        return all_s
    return [s for s in all_s if get_student_section(s, sid) == section]

def stats_for_student(name, records=None):
    if records is None:
        records = read_all_records()
    mine = [r for r in records if r["name"] == name]
    total   = len(mine)
    present = sum(1 for r in mine if r["status"] == "Present")
    absent  = total - present
    pct     = round((present / total * 100)) if total else 0
    # streak: consecutive present days ending today
    dates_present = sorted({r["date"] for r in mine if r["status"] == "Present"}, reverse=True)
    streak = 0
    check = datetime.now().date()
    for d in dates_present:
        if d == str(check):
            streak += 1
            check -= timedelta(days=1)
        else:
            break
    return {"total": total, "present": present, "absent": absent, "pct": pct, "streak": streak}

def daily_summary(date_str, records=None):
    if records is None:
        records = read_all_records()
    day_recs = [r for r in records if r["date"] == date_str]
    present = [r for r in day_recs if r["status"] == "Present"]
    absent  = [r for r in day_recs if r["status"] != "Present"]
    return present, absent

# ══════════════════════════════════════════════════════
#  SHARED LAYOUT
# ══════════════════════════════════════════════════════

from styles import CSS


def nav_icon(d):
    return f'<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="{d}"/></svg>'

NAV = [
    ("dashboard", "/",          "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6", "Dashboard"),
    ("scan",      "/scan",      "M15 10l4.553-2.069A1 1 0 0121 8.82V15a1 1 0 01-1.447.894L15 14M3 8a2 2 0 012-2h8a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2V8z", "Face Scan"),
    ("enroll",    "/enroll",    "M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z", "Enroll"),
    ("students",  "/students",  "M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z", "Students"),
    ("sections",  "/sections",  "M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10", "Sections"),
    ("calendar",  "/calendar",  "M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z", "Calendar"),
    ("daily",     "/daily",     "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01", "Daily Log"),
    ("gallery",   "/gallery",   "M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z", "Gallery"),
    ("analytics", "/graph",     "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z", "Analytics"),
    ("teacher",   "/teacher",   "M12 14l9-5-9-5-9 5 9 5z M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z", "Teacher"),
    ("upgrade",    "/upgrade",  "M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z", "⭐ Premium"),
    ("admin",     "/admin",     "M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z", "Admin"),
]

def layout(page_title, content, active="dashboard"):
    nav_html = ""
    for key, href, path_d, label in NAV:
        cls = "nav-active" if key == active else ""
        # settings icon needs two paths
        if "M15 12" in path_d or key == "admin":
            icon = f'''<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8"
                d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>''' if key == "admin" else nav_icon(path_d)
        else:
            icon = nav_icon(path_d)
        nav_html += f'<a href="{href}" class="nav-item {cls}">{icon}<span>{label}</span></a>'

    today_str  = datetime.now().strftime("%Y-%m-%d")
    # Build drawer nav for mobile
    drawer_nav = ""
    for key, href, path_d, label in NAV:
        is_act  = key == active
        act_cls = "drawer-active" if is_act else ""
        icon_svg = f'<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="{path_d}"/></svg>'
        drawer_nav += f'<a href="{href}" class="drawer-item {act_cls}">{icon_svg}<span>{label}</span></a>'
    # Resolve subscription state using the new db layer
    import db as _db
    _school_id = session.get("school_id")
    _role      = session.get("role","")
    _sub       = _db.sub_get(_school_id) if _school_id else None
    _banner    = sub_banner()
    _exp_popup = ""
    # Show expired popup when subscription is expired, except for SUPER_ADMIN
    if _sub and _sub.get("is_expired") and _role != "SUPER_ADMIN":
        _exp_popup = '''
        <div class="expired-overlay" id="expiredOverlay">
          <div class="expired-modal">
            <span class="lock-icon">🔒</span>
            <div class="expired-title">Subscription Expired</div>
            <div class="expired-sub">
              Your subscription has expired.<br>
              Upgrade to <strong>Premium</strong> to continue using FaceNova AI.<br>
              <span style="color:var(--muted);font-size:12px">All your data is safe — nothing has been deleted.</span>
            </div>
            <a href="/upgrade" style="display:inline-block;width:100%;padding:14px;background:linear-gradient(135deg,#2563eb,#7c3aed);color:white;border-radius:12px;font-weight:700;font-size:15px;text-decoration:none;margin-bottom:12px">
              🚀 View Upgrade Plans
            </a>
            <a href="/" style="font-size:13px;color:var(--text2);text-decoration:none">
              View Dashboard →
            </a>
          </div>
        </div>'''
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{page_title} — FaceNova AI</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🧠</text></svg>">
{CSS}
</head>
<body>

<!-- ── SIDEBAR ─────────────────────────── -->
<aside class="sidebar">
  <div class="sidebar-logo">
    <div class="logo-mark">
      <div class="logo-icon">🧠</div>
      <div>
        <div class="logo-text">Face<span>Nova</span></div>
        <div class="logo-tag">AI Attendance</div>
      </div>
    </div>
  </div>
  <div class="sidebar-section">Menu</div>
  <nav>{nav_html}</nav>
  <div class="sidebar-footer">
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
      <div style="width:28px;height:28px;border-radius:8px;background:linear-gradient(135deg,var(--blue),var(--purple));display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700">FN</div>
      <div>
        <div style="font-size:12px;font-weight:600;color:var(--text)">FaceNova</div>
        <div style="font-size:10.5px;color:var(--muted)">v4.0 · AI Active</div>
      </div>
    </div>
    <div style="font-size:11.5px;color:var(--text2);display:flex;align-items:center">
      <span class="status-dot"></span>All systems online
    </div>
  </div>
</aside>

<!-- ── MAIN ──────────────────────────────── -->
<div class="main">
  {_banner}
  <div class="topbar">
    <div style="display:flex;align-items:center;gap:12px">
      <div class="topbar-title">{page_title}</div>
      <div style="height:16px;width:1px;background:var(--border)"></div>
      <div style="font-size:11.5px;color:var(--muted)">{today_str}</div>
    </div>
    <div class="topbar-right">
      <span id="clock" style="font-size:12px;color:var(--text2)"></span>
      <div style="width:1px;height:16px;background:var(--border)"></div>
      <span class="tbadge">🟢 AI Online</span>
      <a href="/teacher" style="width:30px;height:30px;border-radius:8px;background:rgba(255,255,255,0.06);border:1px solid var(--border);display:flex;align-items:center;justify-content:center;text-decoration:none;font-size:14px;transition:background 0.15s" title="Teacher Portal">👨‍🏫</a>
    </div>
  </div>

  <div class="page">{content}</div>
</div>

<!-- ── MOBILE TOPBAR ──────────────────────── -->
<div class="mobile-topbar">
  <div class="mobile-logo">
    <div class="logo-icon" style="width:30px;height:30px;font-size:14px">🧠</div>
    Face<span>Nova</span>
  </div>
  <button class="hamburger-btn" onclick="openDrawer()" aria-label="Menu">
    <span></span><span></span><span></span>
  </button>
</div>

<!-- ── MOBILE DRAWER ─────────────────────── -->
<div class="drawer-overlay" id="drawerOverlay" onclick="closeDrawer()"></div>
<div class="drawer" id="drawer">
  <div class="drawer-header">
    <div style="font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:15px">Menu</div>
    <button class="drawer-close" onclick="closeDrawer()">✕</button>
  </div>
  {drawer_nav}
  <div style="margin-top:auto;padding:16px 20px;border-top:1px solid var(--border)">
    <a href="/logout" style="display:flex;align-items:center;gap:10px;color:var(--red-l);font-size:14px;font-weight:600;text-decoration:none;padding:10px 0">
      <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
      Sign Out
    </a>
  </div>
</div>

<!-- ── MOBILE BOTTOM NAV ─────────────────── -->
<nav class="mobile-nav">
  <div class="mobile-nav-inner">
    <a href="/" class="mnav-item {'mnav-active' if active=='dashboard' else ''}">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
      Home
    </a>
    <a href="/scan" class="mnav-item {'mnav-active' if active=='scan' else ''}">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M15 10l4.553-2.069A1 1 0 0121 8.82V15a1 1 0 01-1.447.894L15 14M3 8a2 2 0 012-2h8a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2V8z"/></svg>
      Scan
    </a>
    <a href="/students" class="mnav-item {'mnav-active' if active=='students' else ''}">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
      Students
    </a>
    <a href="/upgrade" class="mnav-item mnav-premium {'mnav-active' if active=='upgrade' else ''}">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"/></svg>
      Premium
    </a>
    <a href="/teacher" class="mnav-item {'mnav-active' if active=='teacher' else ''}">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z"/></svg>
      Dashboard
    </a>
  </div>
</nav>

<script>
function tick(){{
  const n=new Date();
  const el=document.getElementById('clock');
  if(el) el.textContent=
    n.toLocaleTimeString('en-US',{{hour:'2-digit',minute:'2-digit'}})+
    ' · '+n.toLocaleDateString('en-US',{{weekday:'short',month:'short',day:'numeric'}});
}}
tick();setInterval(tick,1000);

function openDrawer(){{
  document.getElementById('drawer').classList.add('open');
  document.getElementById('drawerOverlay').style.display='block';
  document.body.style.overflow='hidden';
}}
function closeDrawer(){{
  document.getElementById('drawer').classList.remove('open');
  document.getElementById('drawerOverlay').style.display='none';
  document.body.style.overflow='';
}}
</script>

{_exp_popup}
</body></html>"""
