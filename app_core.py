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


DATA_DIR     = "data"
GRAPH_DIR    = "graphs"
SECTIONS_FILE = os.path.join("data", "sections.json")
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

# Developer / hidden admin — always unlimited
DEV_CREDENTIALS = {
    "devadmin": "FaceNovaDev@2024"
}

FREE_ROUTES = {"/", "/login", "/upgrade", "/upgrade/activate",
               "/teacher/login", "/teacher/logout", "/dev/login",
               "/dev", "/dev/logout"}

face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# ══════════════════════════════════════════════════════
#  SUBSCRIPTION HELPERS
# ══════════════════════════════════════════════════════

def sub_load():
    """Load subscription record. Auto-create trial on first run."""
    if os.path.exists(SUB_FILE):
        try:
            return json.load(open(SUB_FILE))
        except:
            pass
    # First run — create 10-day trial
    now   = datetime.now()
    end   = now + timedelta(days=TRIAL_DAYS)
    rec   = {
        "status":          "trial",       # trial | active | expired
        "plan":            None,
        "trial_start":     now.strftime("%Y-%m-%d"),
        "trial_end":       end.strftime("%Y-%m-%d"),
        "premium_start":   None,
        "premium_end":     None,
        "payment_status":  None,
        "history":         [],
        "school_name":     "My School",
    }
    sub_save(rec)
    return rec

def sub_save(rec):
    os.makedirs(DATA_DIR, exist_ok=True)
    json.dump(rec, open(SUB_FILE, "w"), indent=2)

def sub_status():
    """
    Returns dict with computed status fields:
      status       : trial | active | expired
      days_left    : int  (trial days remaining, -1 if not trial)
      is_premium   : bool
      is_expired   : bool
      is_trial     : bool
      warn         : bool (3 days or less left)
      plan         : plan key or None
    """
    rec  = sub_load()
    now  = datetime.now().date()
    stat = rec.get("status", "trial")

    # Developer session always passes
    if session.get("dev_logged_in"):
        return {"status":"active","days_left":-1,"is_premium":True,
                "is_expired":False,"is_trial":False,"warn":False,
                "plan":"lifetime","rec":rec}

    days_left = -1
    if stat == "trial":
        try:
            end       = datetime.strptime(rec["trial_end"], "%Y-%m-%d").date()
            days_left = (end - now).days
        except:
            days_left = 0
        if days_left <= 0:
            # auto-expire
            rec["status"] = "expired"
            sub_save(rec)
            stat = "expired"

    elif stat == "active":
        # check premium expiry
        try:
            pend = datetime.strptime(rec["premium_end"], "%Y-%m-%d").date()
            if pend < now:
                rec["status"] = "expired"
                sub_save(rec)
                stat = "expired"
        except:
            pass

    return {
        "status":     stat,
        "days_left":  days_left,
        "is_premium": stat == "active",
        "is_expired": stat == "expired",
        "is_trial":   stat == "trial",
        "warn":       stat == "trial" and 0 < days_left <= 3,
        "plan":       rec.get("plan"),
        "rec":        rec,
    }

def sub_banner():
    """Return HTML banner string to inject into every page."""
    s = sub_status()
    if session.get("dev_logged_in"):
        return '''<div style="background:linear-gradient(90deg,rgba(139,92,246,0.18),rgba(59,130,246,0.1));border-bottom:1px solid rgba(139,92,246,0.25);padding:8px 24px;font-size:12.5px;display:flex;align-items:center;gap:10px">
          <span style="font-size:14px">👑</span>
          <strong style="color:var(--purple-l)">Developer Mode</strong>
          <span style="color:var(--text2)">· Lifetime Premium · All features unlocked</span>
          <a href="/dev" style="margin-left:auto;color:var(--purple-l);font-size:12px;font-weight:700">Dev Panel →</a>
        </div>'''
    if s["is_expired"]:
        return '''<div style="background:rgba(239,68,68,0.12);border-bottom:1px solid rgba(239,68,68,0.25);padding:8px 24px;font-size:12.5px;display:flex;align-items:center;gap:10px">
          <span>🔒</span>
          <strong style="color:var(--red-l)">Free Trial Expired</strong>
          <span style="color:var(--text2)">· Upgrade to continue using premium features</span>
          <a href="/upgrade" style="margin-left:auto;background:var(--red);color:white;padding:4px 14px;border-radius:20px;font-size:12px;font-weight:700;text-decoration:none">Upgrade Now</a>
        </div>'''
    if s["warn"]:
        return f'''<div style="background:rgba(245,158,11,0.12);border-bottom:1px solid rgba(245,158,11,0.25);padding:8px 24px;font-size:12.5px;display:flex;align-items:center;gap:10px">
          <span>⚠️</span>
          <strong style="color:var(--amber-l)">Trial expires in {s["days_left"]} day{"s" if s["days_left"]!=1 else ""}!</strong>
          <span style="color:var(--text2)">· Upgrade now to keep your data and features</span>
          <a href="/upgrade" style="margin-left:auto;background:var(--amber);color:#000;padding:4px 14px;border-radius:20px;font-size:12px;font-weight:700;text-decoration:none">Upgrade</a>
        </div>'''
    if s["is_trial"]:
        return f'''<div style="background:rgba(59,130,246,0.08);border-bottom:1px solid rgba(59,130,246,0.15);padding:8px 24px;font-size:12.5px;display:flex;align-items:center;gap:10px">
          <span>🎉</span>
          <strong style="color:var(--blue)">Free Trial Active</strong>
          <span style="color:var(--text2)">· {s["days_left"]} day{"s" if s["days_left"]!=1 else ""} remaining</span>
          <a href="/upgrade" style="margin-left:auto;color:var(--blue);font-size:12px;font-weight:600;text-decoration:none">View Plans →</a>
        </div>'''
    if s["is_premium"]:
        return '''<div style="background:rgba(16,185,129,0.07);border-bottom:1px solid rgba(16,185,129,0.15);padding:7px 24px;font-size:12px;display:flex;align-items:center;gap:10px">
          <span>✅</span>
          <strong style="color:var(--green-l)">Premium Active</strong>
          <span style="color:var(--muted)">· All features unlocked</span>
        </div>'''
    return ""

def premium_required(f):
    """
    Decorator: if trial expired, redirect locked pages to /upgrade.
    Developer session always passes. Free routes always pass.
    """
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("dev_logged_in"):
            return f(*args, **kwargs)
        path = request.path
        # always allow free routes
        for fr in FREE_ROUTES:
            if path == fr or path.startswith(fr.rstrip("/")+"/"):
                return f(*args, **kwargs)
        s = sub_status()
        if s["is_expired"]:
            # allow dashboard and upgrade even when expired
            if path in ("/", "/upgrade", "/upgrade/activate"):
                return f(*args, **kwargs)
            return redirect("/upgrade?locked=1")
        return f(*args, **kwargs)
    return decorated

# ──────────────────────────────────────────────────────
#  SECTION HELPERS
# ──────────────────────────────────────────────────────

DEFAULT_SECTIONS = ["6A","6B","7A","7B","8A","8B","8C","9A","9B","10A"]

def load_sections():
    """Return list of section names."""
    if os.path.exists(SECTIONS_FILE):
        try:
            return json.load(open(SECTIONS_FILE))
        except:
            pass
    return list(DEFAULT_SECTIONS)

def save_sections(sections):
    os.makedirs(DATA_DIR, exist_ok=True)
    json.dump(sections, open(SECTIONS_FILE,"w"))

def student_meta_file(name):
    return os.path.join(DATA_DIR, name, "_meta.json")

def load_meta(name):
    """Load full meta dict for a student."""
    mf = student_meta_file(name)
    if os.path.exists(mf):
        try: return json.load(open(mf))
        except: pass
    return {}

def save_meta(name, meta):
    mf = student_meta_file(name)
    os.makedirs(os.path.dirname(mf), exist_ok=True)
    json.dump(meta, open(mf,"w"))

def get_student_section(name):
    return load_meta(name).get("section","")

def set_student_section(name, section):
    meta = load_meta(name)
    meta["section"] = section
    save_meta(name, meta)

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

def read_all_records(section=""):
    """Return list of dicts: name, date, status, time, section.
       Optionally filter by section."""
    rows = []
    if not os.path.exists(ATT_FILE):
        return rows
    with open(ATT_FILE, newline="") as f:
        for r in csv.reader(f):
            if len(r) >= 3:
                rec = {
                    "name":    r[0],
                    "date":    r[1],
                    "status":  r[2],
                    "time":    r[3] if len(r) > 3 else "—",
                    "section": r[4] if len(r) > 4 else get_student_section(r[0]),
                }
                if section and rec["section"] != section:
                    continue
                rows.append(rec)
    return rows

def enrolled_students(section=""):
    """Return all students, optionally filtered by section."""
    return students_in_section(section)

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
    _sub       = sub_status()
    _banner    = sub_banner()
    _exp_popup = ""
    if _sub["is_expired"] and not session.get("dev_logged_in"):
        _exp_popup = '''
        <div class="expired-overlay" id="expiredOverlay">
          <div class="expired-modal">
            <span class="lock-icon">🔒</span>
            <div class="expired-title">Free Trial Expired</div>
            <div class="expired-sub">
              Your 10-day free trial has ended.<br>
              Upgrade to <strong>Premium</strong> to continue using FaceNova AI.<br>
              <span style="color:var(--muted);font-size:12px">All your data is safe — nothing has been deleted.</span>
            </div>
            <a href="/upgrade" style="display:inline-block;width:100%;padding:14px;background:linear-gradient(135deg,#2563eb,#7c3aed);color:white;border-radius:12px;font-weight:700;font-size:15px;text-decoration:none;margin-bottom:12px">
              🚀 Upgrade to Premium
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

<script>
function tick(){{
  const n=new Date();
  document.getElementById('clock').textContent=
    n.toLocaleTimeString('en-US',{{hour:'2-digit',minute:'2-digit'}})+
    ' · '+n.toLocaleDateString('en-US',{{weekday:'short',month:'short',day:'numeric'}});
}}
tick();setInterval(tick,1000);
</script>


{_exp_popup}
</body></html>"""
