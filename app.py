
from flask import Flask, request, send_file, redirect, url_for
import os, csv, base64, json, calendar as cal_mod
from datetime import datetime, timedelta
import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

app = Flask(__name__)

DATA_DIR  = "data"
GRAPH_DIR = "graphs"
os.makedirs(DATA_DIR,  exist_ok=True)
os.makedirs(GRAPH_DIR, exist_ok=True)
ATT_FILE = os.path.join(DATA_DIR, "attendance.csv")

face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# ══════════════════════════════════════════════════════
#  DATA HELPERS
# ══════════════════════════════════════════════════════

def read_all_records():
    """Return list of dicts: name, date, status, time"""
    rows = []
    if not os.path.exists(ATT_FILE):
        return rows
    with open(ATT_FILE, newline="") as f:
        for r in csv.reader(f):
            if len(r) >= 3:
                rows.append({
                    "name":   r[0],
                    "date":   r[1],
                    "status": r[2],
                    "time":   r[3] if len(r) > 3 else "—"
                })
    return rows

def enrolled_students():
    return sorted([
        x for x in os.listdir(DATA_DIR)
        if os.path.isdir(os.path.join(DATA_DIR, x))
    ])

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

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}

:root{
  --bg:#07090f; --surface:#0d1117; --card:#111827;
  --border:rgba(255,255,255,0.07);
  --blue:#3b82f6; --cyan:#06b6d4; --green:#10b981;
  --red:#ef4444; --amber:#f59e0b; --purple:#8b5cf6;
  --text:#f1f5f9; --muted:#64748b; --sidebar-w:248px;
}
body{font-family:'Inter',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;display:flex;}

/* ── SIDEBAR ── */
.sidebar{width:var(--sidebar-w);background:var(--surface);border-right:1px solid var(--border);
  display:flex;flex-direction:column;position:fixed;top:0;bottom:0;left:0;z-index:100;padding:0 0 20px;}
.sidebar-logo{padding:24px 20px 18px;border-bottom:1px solid var(--border);}
.logo-mark{display:flex;align-items:center;gap:10px;}
.logo-icon{width:36px;height:36px;background:linear-gradient(135deg,var(--blue),var(--cyan));
  border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:17px;}
.logo-text{font-family:'Space Grotesk',sans-serif;font-size:19px;font-weight:700;letter-spacing:-0.3px;}
.logo-text span{color:var(--cyan);}
.sidebar-section{font-size:10px;font-weight:700;letter-spacing:1.8px;color:var(--muted);
  text-transform:uppercase;padding:18px 20px 6px;}
.nav-item{display:flex;align-items:center;gap:11px;padding:10px 20px;color:var(--muted);
  text-decoration:none;font-size:13.5px;font-weight:500;transition:all 0.15s;
  border-left:3px solid transparent;margin:1px 0;}
.nav-item svg{width:17px;height:17px;flex-shrink:0;}
.nav-item:hover{color:var(--text);background:rgba(255,255,255,0.04);}
.nav-active{color:var(--blue)!important;background:rgba(59,130,246,0.09)!important;border-left-color:var(--blue)!important;}
.sidebar-footer{margin-top:auto;padding:16px 20px 0;border-top:1px solid var(--border);}
.status-dot{display:inline-block;width:7px;height:7px;background:var(--green);border-radius:50%;
  margin-right:7px;animation:blink 2s infinite;}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0.3}}

/* ── MAIN ── */
.main{margin-left:var(--sidebar-w);flex:1;display:flex;flex-direction:column;min-height:100vh;}
.topbar{background:var(--surface);border-bottom:1px solid var(--border);padding:0 28px;height:62px;
  display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:50;}
.topbar-title{font-family:'Space Grotesk',sans-serif;font-size:16px;font-weight:600;}
.topbar-right{display:flex;align-items:center;gap:14px;}
.tbadge{background:rgba(59,130,246,0.14);color:var(--blue);padding:4px 11px;
  border-radius:20px;font-size:12px;font-weight:600;}
.page{padding:28px;flex:1;}

/* ── STAT CARDS ── */
.stats-row{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px;}
.stat{background:var(--card);border:1px solid var(--border);border-radius:15px;padding:20px;position:relative;overflow:hidden;}
.stat::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;}
.s-blue::before{background:linear-gradient(90deg,var(--blue),var(--cyan));}
.s-green::before{background:linear-gradient(90deg,var(--green),#34d399);}
.s-red::before{background:linear-gradient(90deg,var(--red),#f87171);}
.s-amber::before{background:linear-gradient(90deg,var(--amber),#fcd34d);}
.s-purple::before{background:linear-gradient(90deg,var(--purple),#a78bfa);}
.stat-ico{width:38px;height:38px;border-radius:10px;display:flex;align-items:center;justify-content:center;
  font-size:17px;margin-bottom:12px;}
.stat-val{font-family:'Space Grotesk',sans-serif;font-size:30px;font-weight:700;line-height:1;margin-bottom:3px;}
.stat-lbl{font-size:12px;color:var(--muted);font-weight:500;}

/* ── PROGRESS BAR ── */
.pbar-wrap{background:rgba(255,255,255,0.06);border-radius:20px;height:8px;overflow:hidden;margin-top:8px;}
.pbar{height:100%;border-radius:20px;transition:width 0.6s ease;}
.pbar-green{background:linear-gradient(90deg,var(--green),#34d399);}
.pbar-amber{background:linear-gradient(90deg,var(--amber),#fcd34d);}
.pbar-red{background:linear-gradient(90deg,var(--red),#f87171);}

/* ── CARDS ── */
.card{background:var(--card);border:1px solid var(--border);border-radius:15px;padding:22px;}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:18px;}
.grid-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:18px;}
.sec-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px;}
.sec-title{font-family:'Space Grotesk',sans-serif;font-size:16px;font-weight:700;}
.sec-sub{font-size:12px;color:var(--muted);margin-top:2px;}

/* ── TABLE ── */
.tbl-wrap{overflow-x:auto;}
table{width:100%;border-collapse:collapse;font-size:13.5px;}
thead th{background:rgba(255,255,255,0.04);padding:11px 14px;text-align:left;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  color:var(--muted);border-bottom:1px solid var(--border);}
tbody td{padding:13px 14px;border-bottom:1px solid var(--border);}
tbody tr:hover{background:rgba(255,255,255,0.02);}
tbody tr:last-child td{border-bottom:none;}

/* ── PILLS ── */
.pill{display:inline-flex;align-items:center;gap:5px;padding:4px 11px;border-radius:20px;font-size:12px;font-weight:600;}
.pill-green{background:rgba(16,185,129,0.13);color:#34d399;}
.pill-red{background:rgba(239,68,68,0.13);color:#f87171;}
.pill-amber{background:rgba(245,158,11,0.13);color:var(--amber);}
.pill-blue{background:rgba(59,130,246,0.13);color:var(--blue);}

/* ── BUTTONS ── */
.btn{display:inline-flex;align-items:center;gap:7px;padding:9px 18px;border:none;border-radius:9px;
  font-size:13.5px;font-weight:600;cursor:pointer;transition:all 0.15s;text-decoration:none;font-family:'Inter',sans-serif;}
.btn-primary{background:linear-gradient(135deg,var(--blue),#2563eb);color:white;}
.btn-primary:hover{transform:translateY(-1px);box-shadow:0 4px 18px rgba(59,130,246,0.38);}
.btn-cyan{background:linear-gradient(135deg,var(--cyan),#0891b2);color:white;}
.btn-cyan:hover{transform:translateY(-1px);box-shadow:0 4px 18px rgba(6,182,212,0.38);}
.btn-ghost{background:rgba(255,255,255,0.06);color:var(--text);border:1px solid var(--border);}
.btn-ghost:hover{background:rgba(255,255,255,0.1);}
.btn-red{background:rgba(239,68,68,0.14);color:var(--red);border:1px solid rgba(239,68,68,0.28);}
.btn-red:hover{background:rgba(239,68,68,0.24);}
.btn-sm{padding:6px 13px;font-size:12.5px;}

/* ── FORMS ── */
.form-group{margin-bottom:16px;}
label{display:block;font-size:12.5px;font-weight:600;color:var(--muted);margin-bottom:7px;letter-spacing:0.3px;}
input[type=text],select,textarea{width:100%;background:rgba(255,255,255,0.05);border:1px solid var(--border);
  border-radius:9px;padding:10px 13px;color:var(--text);font-size:13.5px;font-family:'Inter',sans-serif;
  transition:border 0.15s;outline:none;}
input[type=text]:focus,select:focus{border-color:var(--blue);background:rgba(59,130,246,0.06);}
select option{background:#1e293b;}
input[type=file]{width:100%;background:rgba(255,255,255,0.04);border:1px dashed var(--border);
  border-radius:9px;padding:10px 13px;color:var(--muted);font-size:13px;font-family:'Inter',sans-serif;}

/* ── ALERTS ── */
.alert{padding:13px 16px;border-radius:11px;font-size:13.5px;margin-bottom:18px;
  display:flex;align-items:center;gap:9px;}
.alert-success{background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.25);color:#34d399;}
.alert-error{background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.25);color:#f87171;}
.alert-info{background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.25);color:var(--blue);}
.alert-warn{background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.25);color:var(--amber);}

/* ══ CALENDAR SPECIFIC ══ */
.cal-nav{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;}
.cal-month{font-family:'Space Grotesk',sans-serif;font-size:20px;font-weight:700;}
.cal-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:6px;}
.cal-dow{text-align:center;font-size:11px;font-weight:700;color:var(--muted);padding:6px 0;
  letter-spacing:0.8px;text-transform:uppercase;}
.cal-cell{border-radius:10px;padding:10px 6px;text-align:center;min-height:62px;
  border:1px solid var(--border);background:rgba(255,255,255,0.02);cursor:pointer;transition:all 0.15s;}
.cal-cell:hover{background:rgba(255,255,255,0.06);}
.cal-cell.empty{opacity:0;pointer-events:none;}
.cal-cell.today{border-color:var(--blue);background:rgba(59,130,246,0.08);}
.cal-cell.c-present{background:rgba(16,185,129,0.1);border-color:rgba(16,185,129,0.3);}
.cal-cell.c-absent{background:rgba(239,68,68,0.1);border-color:rgba(239,68,68,0.3);}
.cal-cell.c-partial{background:rgba(245,158,11,0.1);border-color:rgba(245,158,11,0.3);}
.cal-day-num{font-size:14px;font-weight:600;margin-bottom:4px;}
.cal-dots{display:flex;gap:3px;justify-content:center;flex-wrap:wrap;}
.dot{width:6px;height:6px;border-radius:50%;}
.dot-g{background:var(--green);}
.dot-r{background:var(--red);}
.cal-legend{display:flex;gap:18px;align-items:center;margin-top:14px;font-size:12px;color:var(--muted);}
.leg-dot{width:10px;height:10px;border-radius:50%;display:inline-block;margin-right:5px;}

/* ── DAILY LOG ── */
.log-item{display:flex;align-items:center;gap:14px;padding:13px 0;border-bottom:1px solid var(--border);}
.log-item:last-child{border-bottom:none;}
.log-avatar{width:38px;height:38px;border-radius:10px;background:linear-gradient(135deg,var(--blue),var(--purple));
  display:flex;align-items:center;justify-content:center;font-weight:700;font-size:15px;flex-shrink:0;}
.log-info{flex:1;}
.log-name{font-weight:600;font-size:14px;}
.log-time{font-size:12px;color:var(--muted);margin-top:1px;}

/* ── STUDENT PROFILE CARD ── */
.student-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:14px;}
.student-card{background:var(--card);border:1px solid var(--border);border-radius:14px;
  padding:18px;text-align:center;transition:transform 0.15s;}
.student-card:hover{transform:translateY(-3px);}
.s-avatar{width:64px;height:64px;border-radius:50%;object-fit:cover;margin:0 auto 10px;
  border:2px solid var(--border);}
.s-avatar-placeholder{width:64px;height:64px;border-radius:50%;background:linear-gradient(135deg,var(--blue),var(--purple));
  display:flex;align-items:center;justify-content:center;font-size:22px;margin:0 auto 10px;
  border:2px solid var(--border);}
.s-name{font-weight:700;font-size:14px;margin-bottom:4px;}
.s-pct{font-size:22px;font-weight:700;font-family:'Space Grotesk',sans-serif;}

/* ── STREAK BADGE ── */
.streak{display:inline-flex;align-items:center;gap:4px;background:rgba(245,158,11,0.15);
  color:var(--amber);border-radius:20px;padding:3px 10px;font-size:12px;font-weight:700;}

/* ── SCAN RING ── */
.scan-wrap{position:relative;display:inline-block;}
.scan-ring{position:absolute;inset:-14px;border-radius:50%;border:2px solid var(--cyan);
  opacity:0;animation:ring 2.5s ease-in-out infinite;}
.scan-ring:nth-child(2){animation-delay:0.8s;}
.scan-ring:nth-child(3){animation-delay:1.6s;}
@keyframes ring{0%{transform:scale(0.85);opacity:0.8}100%{transform:scale(1.15);opacity:0}}
video{border-radius:14px;display:block;}

/* ── GALLERY ── */
.gallery-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:14px;}
.gallery-item{background:var(--card);border:1px solid var(--border);border-radius:13px;overflow:hidden;transition:transform 0.15s;}
.gallery-item:hover{transform:translateY(-3px);}
.gallery-item img{width:100%;height:150px;object-fit:cover;display:block;}
.gallery-item-info{padding:11px;}
.gallery-item-name{font-size:13.5px;font-weight:600;}
.gallery-item-stat{font-size:11.5px;color:var(--muted);margin-top:2px;}

/* ── PAGE HERO ── */
.hero{background:linear-gradient(135deg,rgba(59,130,246,0.1),rgba(6,182,212,0.06));
  border:1px solid rgba(59,130,246,0.2);border-radius:18px;padding:24px 28px;
  margin-bottom:24px;display:flex;align-items:center;justify-content:space-between;}
.hero h1{font-family:'Space Grotesk',sans-serif;font-size:23px;font-weight:700;margin-bottom:5px;}
.hero p{color:var(--muted);font-size:13.5px;}

/* ── RESPONSIVE ── */
@media(max-width:900px){
  .sidebar{display:none;}
  .main{margin-left:0;}
  .stats-row{grid-template-columns:1fr 1fr;}
  .grid-2,.grid-3{grid-template-columns:1fr;}
}
@media(max-width:560px){
  .page{padding:16px;}
  .stats-row{grid-template-columns:1fr 1fr;}
  .hero{flex-direction:column;gap:14px;}
}
</style>
"""

def nav_icon(d):
    return f'<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="{d}"/></svg>'

NAV = [
    ("dashboard", "/",          "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6", "Dashboard"),
    ("scan",      "/scan",      "M15 10l4.553-2.069A1 1 0 0121 8.82V15a1 1 0 01-1.447.894L15 14M3 8a2 2 0 012-2h8a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2V8z", "Face Scan"),
    ("enroll",    "/enroll",    "M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z", "Enroll"),
    ("students",  "/students",  "M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z", "Students"),
    ("calendar",  "/calendar",  "M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z", "Calendar"),
    ("daily",     "/daily",     "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01", "Daily Log"),
    ("gallery",   "/gallery",   "M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z", "Gallery"),
    ("analytics", "/graph",     "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z", "Analytics"),
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

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{page_title} — FaceNova</title>
{CSS}
</head>
<body>
<aside class="sidebar">
  <div class="sidebar-logo">
    <div class="logo-mark">
      <div class="logo-icon">🧠</div>
      <div class="logo-text">Face<span>Nova</span></div>
    </div>
  </div>
  <div class="sidebar-section">Navigation</div>
  <nav>{nav_html}</nav>
  <div class="sidebar-footer">
    <div style="font-size:12.5px;color:var(--muted)"><span class="status-dot"></span>System Online</div>
    <div style="font-size:11px;color:var(--muted);margin-top:5px">AI Attendance v3.0</div>
  </div>
</aside>
<div class="main">
  <div class="topbar">
    <div class="topbar-title">{page_title}</div>
    <div class="topbar-right">
      <span id="clock" style="font-size:12.5px;color:var(--muted)"></span>
      <span class="tbadge">AI Active</span>
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
</body></html>"""

# ══════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════

@app.route("/")
def home():
    records   = read_all_records()
    students  = enrolled_students()
    today_str = datetime.now().strftime("%Y-%m-%d")
    present_t, absent_t = daily_summary(today_str, records)

    total_att = len(records)
    pct_today = round(len(present_t)/(len(present_t)+len(absent_t))*100) if (present_t or absent_t) else 0
    pbar_cls  = "pbar-green" if pct_today>=75 else ("pbar-amber" if pct_today>=50 else "pbar-red")

    # recent 8
    recent_html = ""
    for r in reversed(records[-8:]):
        pill = "pill-green" if r["status"]=="Present" else "pill-red"
        icon = "✅" if r["status"]=="Present" else "❌"
        recent_html += f"""<tr>
          <td><strong>{r['name']}</strong></td>
          <td>{r['date']}</td>
          <td>{r['time']}</td>
          <td><span class="pill {pill}">{icon} {r['status']}</span></td>
        </tr>"""

    # absent today list
    absent_names = "".join(f'<span class="pill pill-red" style="margin:3px">{r["name"]}</span>' for r in absent_t) or '<span style="color:var(--muted);font-size:13px">None recorded yet</span>'

    content = f"""
    <div class="hero">
      <div>
        <h1>👋 Welcome to FaceNova</h1>
        <p>AI-powered face recognition attendance — real-time, smart, effortless.</p>
      </div>
      <a href="/scan" class="btn btn-cyan">🎥 &nbsp;Start Face Scan</a>
    </div>

    <div class="stats-row">
      <div class="stat s-blue">
        <div class="stat-ico" style="background:rgba(59,130,246,0.15)">👥</div>
        <div class="stat-val">{len(students)}</div>
        <div class="stat-lbl">Enrolled Students</div>
      </div>
      <div class="stat s-green">
        <div class="stat-ico" style="background:rgba(16,185,129,0.15)">✅</div>
        <div class="stat-val">{len(present_t)}</div>
        <div class="stat-lbl">Present Today</div>
      </div>
      <div class="stat s-red">
        <div class="stat-ico" style="background:rgba(239,68,68,0.15)">❌</div>
        <div class="stat-val">{len(absent_t)}</div>
        <div class="stat-lbl">Absent Today</div>
      </div>
      <div class="stat s-amber">
        <div class="stat-ico" style="background:rgba(245,158,11,0.15)">📊</div>
        <div class="stat-val">{total_att}</div>
        <div class="stat-lbl">Total Records</div>
      </div>
    </div>

    <div class="grid-2" style="margin-bottom:18px">
      <div class="card">
        <div class="sec-head">
          <div><div class="sec-title">Today's Attendance Rate</div>
          <div class="sec-sub">{today_str}</div></div>
          <span style="font-family:'Space Grotesk',sans-serif;font-size:26px;font-weight:700">{pct_today}%</span>
        </div>
        <div class="pbar-wrap"><div class="pbar {pbar_cls}" style="width:{pct_today}%"></div></div>
        <div style="display:flex;justify-content:space-between;margin-top:10px;font-size:12px;color:var(--muted)">
          <span>0%</span><span>Target: 75%</span><span>100%</span>
        </div>
        <div style="margin-top:16px">
          <div style="font-size:12px;font-weight:600;color:var(--muted);margin-bottom:8px">ABSENT TODAY</div>
          <div style="display:flex;flex-wrap:wrap;gap:4px">{absent_names}</div>
        </div>
      </div>

      <div class="card">
        <div class="sec-head">
          <div><div class="sec-title">Recent Activity</div>
          <div class="sec-sub">Last scans recorded</div></div>
          <a href="/daily" class="btn btn-ghost btn-sm">View All</a>
        </div>
        <div class="tbl-wrap">
          <table>
            <thead><tr><th>Name</th><th>Date</th><th>Time</th><th>Status</th></tr></thead>
            <tbody>{recent_html or '<tr><td colspan="4" style="text-align:center;color:var(--muted);padding:20px">No records yet</td></tr>'}</tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="grid-3">
      <div class="card" style="text-align:center">
        <div style="font-size:40px;margin-bottom:10px">📅</div>
        <div class="sec-title">Smart Calendar</div>
        <div style="font-size:13px;color:var(--muted);margin:8px 0 16px">Monthly attendance heatmap</div>
        <a href="/calendar" class="btn btn-ghost" style="width:100%;justify-content:center">Open Calendar</a>
      </div>
      <div class="card" style="text-align:center">
        <div style="font-size:40px;margin-bottom:10px">👤</div>
        <div class="sec-title">Student Profiles</div>
        <div style="font-size:13px;color:var(--muted);margin:8px 0 16px">Per-student stats & tracking</div>
        <a href="/students" class="btn btn-ghost" style="width:100%;justify-content:center">View Students</a>
      </div>
      <div class="card" style="text-align:center">
        <div style="font-size:40px;margin-bottom:10px">📋</div>
        <div class="sec-title">Daily Log</div>
        <div style="font-size:13px;color:var(--muted);margin:8px 0 16px">Full record of today's scans</div>
        <a href="/daily" class="btn btn-ghost" style="width:100%;justify-content:center">View Today</a>
      </div>
    </div>
    """
    return layout("Dashboard", content, "dashboard")

# ══════════════════════════════════════════════════════
#  SMART CALENDAR
# ══════════════════════════════════════════════════════

@app.route("/calendar")
def calendar():
    # which month/year to show
    now = datetime.now()
    year  = int(request.args.get("year",  now.year))
    month = int(request.args.get("month", now.month))

    records   = read_all_records()
    today_str = now.strftime("%Y-%m-%d")

    # build day → {present, absent} count map
    day_map = {}
    for r in records:
        try:
            d = datetime.strptime(r["date"], "%Y-%m-%d")
            if d.year == year and d.month == month:
                key = d.day
                if key not in day_map:
                    day_map[key] = {"present": 0, "absent": 0}
                if r["status"] == "Present":
                    day_map[key]["present"] += 1
                else:
                    day_map[key]["absent"] += 1
        except:
            pass

    # prev / next
    if month == 1:
        prev_y, prev_m = year-1, 12
    else:
        prev_y, prev_m = year, month-1
    if month == 12:
        next_y, next_m = year+1, 1
    else:
        next_y, next_m = year, month+1

    month_name = datetime(year, month, 1).strftime("%B %Y")
    first_dow  = datetime(year, month, 1).weekday()  # Mon=0
    first_dow  = (first_dow + 1) % 7                 # shift so Sun=0
    days_in    = cal_mod.monthrange(year, month)[1]

    # day-of-week headers
    dows = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]
    dow_html = "".join(f'<div class="cal-dow">{d}</div>' for d in dows)

    cells = ""
    # empty leading cells
    for _ in range(first_dow):
        cells += '<div class="cal-cell empty"></div>'

    for day in range(1, days_in+1):
        date_str = f"{year:04d}-{month:02d}-{day:02d}"
        extra = ""
        info  = day_map.get(day)
        if info:
            p, a = info["present"], info["absent"]
            total = p + a
            if a == 0:
                extra = "c-present"
            elif p == 0:
                extra = "c-absent"
            else:
                extra = "c-partial"
            dots = "".join('<div class="dot dot-g"></div>' for _ in range(min(p,5)))
            dots += "".join('<div class="dot dot-r"></div>' for _ in range(min(a,5)))
            dot_html = f'<div class="cal-dots">{dots}</div>'
            count_html = f'<div style="font-size:10px;color:var(--muted);margin-top:3px">{p}P / {a}A</div>'
        else:
            dot_html = ""
            count_html = ""

        today_cls = "today" if date_str == today_str else ""
        cells += f"""
        <div class="cal-cell {extra} {today_cls}" onclick="window.location='/daily?date={date_str}'">
          <div class="cal-day-num">{day}</div>
          {dot_html}
          {count_html}
        </div>"""

    # month stats
    month_records = [r for r in records if r["date"].startswith(f"{year:04d}-{month:02d}-")]
    m_present = sum(1 for r in month_records if r["status"]=="Present")
    m_absent  = len(month_records) - m_present
    m_total   = len(month_records)
    m_pct     = round(m_present/m_total*100) if m_total else 0
    pbar_cls  = "pbar-green" if m_pct>=75 else ("pbar-amber" if m_pct>=50 else "pbar-red")

    content = f"""
    <div class="sec-head" style="margin-bottom:20px">
      <div><div class="sec-title" style="font-size:20px">📅 Attendance Calendar</div>
      <div class="sec-sub">Click any day to see who was present or absent</div></div>
      <a href="/daily" class="btn btn-primary">Today's Log</a>
    </div>

    <div class="grid-2" style="margin-bottom:20px">
      <div class="card" style="padding:18px 22px">
        <div style="font-size:12px;font-weight:700;color:var(--muted);letter-spacing:0.8px;margin-bottom:4px">MONTH OVERVIEW — {month_name.upper()}</div>
        <div style="display:flex;align-items:baseline;gap:10px;margin-top:8px">
          <span style="font-family:'Space Grotesk',sans-serif;font-size:36px;font-weight:700">{m_pct}%</span>
          <span style="color:var(--muted);font-size:13px">attendance rate</span>
        </div>
        <div class="pbar-wrap" style="margin-top:10px"><div class="pbar {pbar_cls}" style="width:{m_pct}%"></div></div>
        <div style="display:flex;gap:20px;margin-top:12px;font-size:13px">
          <span>✅ <strong>{m_present}</strong> Present</span>
          <span>❌ <strong>{m_absent}</strong> Absent</span>
          <span>📊 <strong>{m_total}</strong> Total</span>
        </div>
      </div>
      <div class="card" style="padding:18px 22px">
        <div style="font-size:12px;font-weight:700;color:var(--muted);letter-spacing:0.8px;margin-bottom:12px">CALENDAR LEGEND</div>
        <div class="cal-legend">
          <div><span class="leg-dot" style="background:rgba(16,185,129,0.6)"></span>All Present</div>
          <div><span class="leg-dot" style="background:rgba(239,68,68,0.6)"></span>All Absent</div>
          <div><span class="leg-dot" style="background:rgba(245,158,11,0.6)"></span>Mixed Day</div>
          <div><span class="leg-dot" style="background:rgba(59,130,246,0.6)"></span>Today</div>
        </div>
        <div style="margin-top:14px;font-size:13px;color:var(--muted)">
          🟢 Green dots = Present &nbsp;|&nbsp; 🔴 Red dots = Absent
        </div>
      </div>
    </div>

    <div class="card">
      <div class="cal-nav">
        <a href="/calendar?year={prev_y}&month={prev_m}" class="btn btn-ghost btn-sm">← Prev</a>
        <div class="cal-month">{month_name}</div>
        <a href="/calendar?year={next_y}&month={next_m}" class="btn btn-ghost btn-sm">Next →</a>
      </div>
      <div class="cal-grid">
        {dow_html}
        {cells}
      </div>
    </div>
    """
    return layout("Calendar", content, "calendar")

# ══════════════════════════════════════════════════════
#  DAILY LOG
# ══════════════════════════════════════════════════════

@app.route("/daily")
def daily():
    date_str  = request.args.get("date", datetime.now().strftime("%Y-%m-%d"))
    records   = read_all_records()
    present, absent = daily_summary(date_str, records)
    students  = enrolled_students()

    # figure out who has NO record today at all
    scanned_names = {r["name"] for r in records if r["date"] == date_str}
    not_recorded  = [s for s in students if s not in scanned_names]

    def log_row(r, status):
        pill = "pill-green" if status=="Present" else "pill-red"
        icon = "✅" if status=="Present" else "❌"
        init = r["name"][0].upper()
        return f"""<div class="log-item">
          <div class="log-avatar">{init}</div>
          <div class="log-info">
            <div class="log-name">{r['name']}</div>
            <div class="log-time">⏰ {r['time']}</div>
          </div>
          <span class="pill {pill}">{icon} {status}</span>
        </div>"""

    present_log = "".join(log_row(r, "Present") for r in present) or \
        '<div style="padding:20px;text-align:center;color:var(--muted)">No one marked present</div>'
    absent_log  = "".join(log_row(r, "Absent") for r in absent) or \
        '<div style="padding:20px;text-align:center;color:var(--muted)">No absentees recorded</div>'

    not_rec_html = "".join(
        f'<span class="pill pill-amber" style="margin:3px">{s}</span>'
        for s in not_recorded
    ) or '<span style="color:var(--muted);font-size:13px">All students scanned</span>'

    total_day = len(present)+len(absent)
    pct_day   = round(len(present)/total_day*100) if total_day else 0
    pbar_cls  = "pbar-green" if pct_day>=75 else ("pbar-amber" if pct_day>=50 else "pbar-red")

    # date nav
    try:
        d_obj  = datetime.strptime(date_str, "%Y-%m-%d")
        prev_d = (d_obj - timedelta(days=1)).strftime("%Y-%m-%d")
        next_d = (d_obj + timedelta(days=1)).strftime("%Y-%m-%d")
    except:
        prev_d = next_d = date_str

    content = f"""
    <div class="sec-head" style="margin-bottom:20px">
      <div>
        <div class="sec-title" style="font-size:20px">📋 Daily Attendance Log</div>
        <div class="sec-sub">Detailed record for {date_str}</div>
      </div>
      <div style="display:flex;gap:8px">
        <a href="/daily?date={prev_d}" class="btn btn-ghost btn-sm">← Prev Day</a>
        <a href="/daily" class="btn btn-primary btn-sm">Today</a>
        <a href="/daily?date={next_d}" class="btn btn-ghost btn-sm">Next Day →</a>
      </div>
    </div>

    <div class="stats-row" style="grid-template-columns:repeat(4,1fr);margin-bottom:20px">
      <div class="stat s-blue">
        <div class="stat-ico" style="background:rgba(59,130,246,0.15)">👥</div>
        <div class="stat-val">{len(students)}</div>
        <div class="stat-lbl">Total Students</div>
      </div>
      <div class="stat s-green">
        <div class="stat-ico" style="background:rgba(16,185,129,0.15)">✅</div>
        <div class="stat-val">{len(present)}</div>
        <div class="stat-lbl">Present</div>
      </div>
      <div class="stat s-red">
        <div class="stat-ico" style="background:rgba(239,68,68,0.15)">❌</div>
        <div class="stat-val">{len(absent)}</div>
        <div class="stat-lbl">Absent</div>
      </div>
      <div class="stat s-amber">
        <div class="stat-ico" style="background:rgba(245,158,11,0.15)">📊</div>
        <div class="stat-val">{pct_day}%</div>
        <div class="stat-lbl">Rate</div>
      </div>
    </div>

    <div class="card" style="margin-bottom:18px;padding:18px 22px">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
        <div style="font-size:13px;font-weight:600;color:var(--muted)">ATTENDANCE RATE</div>
        <span style="font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:18px">{pct_day}%</span>
      </div>
      <div class="pbar-wrap"><div class="pbar {pbar_cls}" style="width:{pct_day}%"></div></div>
    </div>

    <div class="grid-2" style="margin-bottom:18px">
      <div class="card">
        <div class="sec-head">
          <div><div class="sec-title">✅ Present ({len(present)})</div></div>
        </div>
        {present_log}
      </div>
      <div class="card">
        <div class="sec-head">
          <div><div class="sec-title">❌ Absent ({len(absent)})</div></div>
        </div>
        {absent_log}
      </div>
    </div>

    <div class="card">
      <div class="sec-head">
        <div><div class="sec-title">⚠️ Not Yet Scanned</div>
        <div class="sec-sub">Enrolled students with no record today</div></div>
      </div>
      <div style="display:flex;flex-wrap:wrap;gap:6px">{not_rec_html}</div>
    </div>
    """
    return layout(f"Daily Log — {date_str}", content, "daily")

# ══════════════════════════════════════════════════════
#  STUDENT PROFILES
# ══════════════════════════════════════════════════════

@app.route("/students")
def students():
    all_students = enrolled_students()
    records      = read_all_records()

    if not all_students:
        content = """<div class="card" style="text-align:center;padding:60px">
          <div style="font-size:50px;margin-bottom:14px">👥</div>
          <div class="sec-title">No Students Enrolled</div>
          <div style="color:var(--muted);margin-top:8px;margin-bottom:20px">Enroll students to see their profiles here.</div>
          <a href="/enroll" class="btn btn-primary">+ Enroll First Student</a>
        </div>"""
        return layout("Students", content, "students")

    cards = ""
    for name in all_students:
        s = stats_for_student(name, records)
        pct_color = "var(--green)" if s["pct"]>=75 else ("var(--amber)" if s["pct"]>=50 else "var(--red)")
        pbar_cls  = "pbar-green" if s["pct"]>=75 else ("pbar-amber" if s["pct"]>=50 else "pbar-red")

        # profile pic
        user_dir = os.path.join(DATA_DIR, name)
        img_tag  = ""
        if os.path.isdir(user_dir):
            imgs = [f for f in os.listdir(user_dir) if f.lower().endswith((".jpg",".jpeg",".png"))]
            if imgs:
                img_tag = f'<img src="/img/{name}/{imgs[0]}" class="s-avatar">'
        if not img_tag:
            img_tag = f'<div class="s-avatar-placeholder">{name[0].upper()}</div>'

        streak_html = f'<div class="streak">🔥 {s["streak"]}d streak</div>' if s["streak"]>0 else ""

        cards += f"""
        <div class="student-card">
          <a href="/student/{name}" style="text-decoration:none;color:inherit">
            {img_tag}
            <div class="s-name">{name}</div>
            <div class="s-pct" style="color:{pct_color}">{s['pct']}%</div>
            <div style="font-size:11.5px;color:var(--muted);margin-bottom:8px">{s['present']}P / {s['absent']}A of {s['total']}</div>
            <div class="pbar-wrap"><div class="pbar {pbar_cls}" style="width:{s['pct']}%"></div></div>
            <div style="margin-top:8px">{streak_html}</div>
          </a>
        </div>"""

    content = f"""
    <div class="sec-head" style="margin-bottom:20px">
      <div><div class="sec-title" style="font-size:20px">👥 Student Profiles</div>
      <div class="sec-sub">Click a student to view their full attendance history</div></div>
      <a href="/enroll" class="btn btn-primary">+ Enroll New</a>
    </div>
    <div class="student-grid">{cards}</div>
    """
    return layout("Students", content, "students")

# ══════════════════════════════════════════════════════
#  SINGLE STUDENT DETAIL
# ══════════════════════════════════════════════════════

@app.route("/student/<name>")
def student_detail(name):
    records = read_all_records()
    mine    = [r for r in records if r["name"] == name]
    s       = stats_for_student(name, records)

    pbar_cls  = "pbar-green" if s["pct"]>=75 else ("pbar-amber" if s["pct"]>=50 else "pbar-red")
    status_msg = "🟢 Good Standing" if s["pct"]>=75 else ("🟡 Needs Improvement" if s["pct"]>=50 else "🔴 Low Attendance — At Risk")

    rows = "".join(f"""<tr>
      <td>{r['date']}</td><td>{r['time']}</td>
      <td><span class="pill {'pill-green' if r['status']=='Present' else 'pill-red'}">{r['status']}</span></td>
    </tr>""" for r in reversed(mine)) or \
    '<tr><td colspan="3" style="text-align:center;color:var(--muted);padding:20px">No records</td></tr>'

    # profile pic
    user_dir = os.path.join(DATA_DIR, name)
    img_tag  = ""
    if os.path.isdir(user_dir):
        imgs = [f for f in os.listdir(user_dir) if f.lower().endswith((".jpg",".jpeg",".png"))]
        if imgs:
            img_tag = f'<img src="/img/{name}/{imgs[0]}" style="width:80px;height:80px;border-radius:50%;object-fit:cover;border:2px solid var(--border);margin-bottom:12px">'
    if not img_tag:
        img_tag = f'<div style="width:80px;height:80px;border-radius:50%;background:linear-gradient(135deg,var(--blue),var(--purple));display:flex;align-items:center;justify-content:center;font-size:30px;margin:0 auto 12px">{name[0].upper()}</div>'

    content = f"""
    <a href="/students" class="btn btn-ghost btn-sm" style="margin-bottom:18px">← Back to Students</a>
    <div class="grid-2" style="align-items:start">
      <div class="card" style="text-align:center">
        {img_tag}
        <div style="font-family:'Space Grotesk',sans-serif;font-size:22px;font-weight:700;margin-bottom:4px">{name}</div>
        <div style="margin-bottom:14px">{status_msg}</div>
        <div style="font-family:'Space Grotesk',sans-serif;font-size:42px;font-weight:700;margin-bottom:4px">{s['pct']}%</div>
        <div style="color:var(--muted);font-size:13px;margin-bottom:14px">Attendance Rate</div>
        <div class="pbar-wrap" style="margin-bottom:16px"><div class="pbar {pbar_cls}" style="width:{s['pct']}%"></div></div>
        <div style="display:flex;justify-content:space-around;font-size:13px">
          <div><div style="font-weight:700;font-size:20px;color:var(--green)">{s['present']}</div><div style="color:var(--muted)">Present</div></div>
          <div><div style="font-weight:700;font-size:20px;color:var(--red)">{s['absent']}</div><div style="color:var(--muted)">Absent</div></div>
          <div><div style="font-weight:700;font-size:20px;color:var(--amber)">{s['streak']}</div><div style="color:var(--muted)">Streak</div></div>
        </div>
      </div>
      <div class="card">
        <div class="sec-title" style="margin-bottom:16px">📋 Attendance History</div>
        <div class="tbl-wrap">
          <table>
            <thead><tr><th>Date</th><th>Time</th><th>Status</th></tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </div>
      </div>
    </div>
    """
    return layout(name, content, "students")

# ══════════════════════════════════════════════════════
#  ENROLL
# ══════════════════════════════════════════════════════

@app.route("/enroll")
def enroll_page():
    content = """
    <div class="sec-head" style="margin-bottom:20px">
      <div><div class="sec-title" style="font-size:20px">📸 Enroll New Student</div>
      <div class="sec-sub">Upload face photos to register in the system</div></div>
    </div>
    <div class="grid-2">
      <div class="card">
        <div class="sec-title" style="margin-bottom:18px">Upload Face Photos</div>
        <form action='/upload' method='POST' enctype='multipart/form-data'>
          <div class="form-group">
            <label>Full Name</label>
            <input type='text' name='name' placeholder='e.g. Rahul Sharma' required>
          </div>
          <div class="form-group">
            <label>Face Photos (3–5 recommended)</label>
            <input type='file' name='photos' multiple accept='image/*' required>
          </div>
          <button type='submit' class='btn btn-primary' style='width:100%;justify-content:center;padding:12px'>
            ✅ &nbsp;Upload & Enroll
          </button>
        </form>
      </div>
      <div class="card" style="display:flex;flex-direction:column;gap:14px">
        <div class="sec-title">📌 Enrollment Tips</div>
        <div class="alert alert-info">Use 3–5 clear, well-lit photos for best recognition accuracy.</div>
        <div style="display:flex;flex-direction:column;gap:10px;font-size:13.5px">
          <div>✅ Front-facing, eyes open</div>
          <div>✅ Good lighting, no shadows</div>
          <div>✅ No sunglasses or masks</div>
          <div>✅ Different angles improve accuracy</div>
          <div>❌ Avoid blurry or dark images</div>
        </div>
      </div>
    </div>"""
    return layout("Enroll", content, "enroll")

@app.route("/upload", methods=["POST"])
def upload():
    try:
        name  = request.form["name"].strip()
        files = request.files.getlist("photos")
        os.makedirs(os.path.join(DATA_DIR, name), exist_ok=True)
        saved = 0
        for f in files:
            f.save(os.path.join(DATA_DIR, name, f"{datetime.now().timestamp()}.jpg"))
            saved += 1
        content = f"""
        <div class="alert alert-success">✅ {name} enrolled with {saved} photo(s).</div>
        <div class="card" style="text-align:center;padding:40px">
          <div style="font-size:56px;margin-bottom:14px">🎉</div>
          <div class="sec-title" style="font-size:20px;margin-bottom:6px">{name} Enrolled!</div>
          <div style="color:var(--muted);margin-bottom:22px">{saved} face photo(s) saved.</div>
          <div style="display:flex;gap:10px;justify-content:center">
            <a href="/enroll" class="btn btn-primary">Enroll Another</a>
            <a href="/students" class="btn btn-ghost">View Students</a>
            <a href="/" class="btn btn-ghost">Dashboard</a>
          </div>
        </div>"""
        return layout("Enrolled", content, "enroll")
    except Exception as e:
        content = f'<div class="alert alert-error">❌ {str(e)}</div><a href="/enroll" class="btn btn-ghost">Go Back</a>'
        return layout("Error", content, "enroll")

# ══════════════════════════════════════════════════════
#  FACE SCAN
# ══════════════════════════════════════════════════════

@app.route("/scan")
def scan_page():
    content = """
    <div class="sec-head" style="margin-bottom:20px">
      <div><div class="sec-title" style="font-size:20px">🎥 Live Face Scan</div>
      <div class="sec-sub">Position face in frame and tap Scan</div></div>
    </div>
    <div class="grid-2" style="align-items:start">
      <div class="card" style="display:flex;flex-direction:column;align-items:center;gap:18px">
        <div class="scan-wrap" style="border-radius:14px;overflow:visible">
          <video id='cam' width='380' autoplay playsinline></video>
          <div class="scan-ring"></div>
          <div class="scan-ring"></div>
          <div class="scan-ring"></div>
        </div>
        <button class='btn btn-cyan' onclick='snap()' style="width:100%;justify-content:center;padding:13px;font-size:15px">
          📷 &nbsp;Scan Face Now
        </button>
        <canvas id='canvas' style='display:none'></canvas>
        <form id='camForm' action='/camera' method='POST'>
          <input type='hidden' name='img' id='imgdata'>
        </form>
      </div>
      <div class="card">
        <div class="sec-title" style="margin-bottom:16px">How It Works</div>
        <div style="display:flex;flex-direction:column;gap:16px">
          <div style="display:flex;gap:12px;align-items:flex-start">
            <div style="background:rgba(59,130,246,0.15);color:var(--blue);border-radius:8px;width:30px;height:30px;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0;font-size:13px">1</div>
            <div><div style="font-weight:600;margin-bottom:2px">Allow Camera</div>
            <div style="color:var(--muted);font-size:13px">Grant browser camera permission when prompted</div></div>
          </div>
          <div style="display:flex;gap:12px;align-items:flex-start">
            <div style="background:rgba(6,182,212,0.15);color:var(--cyan);border-radius:8px;width:30px;height:30px;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0;font-size:13px">2</div>
            <div><div style="font-weight:600;margin-bottom:2px">Center Your Face</div>
            <div style="color:var(--muted);font-size:13px">Make sure face is clearly visible in frame</div></div>
          </div>
          <div style="display:flex;gap:12px;align-items:flex-start">
            <div style="background:rgba(16,185,129,0.15);color:var(--green);border-radius:8px;width:30px;height:30px;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0;font-size:13px">3</div>
            <div><div style="font-weight:600;margin-bottom:2px">Tap Scan</div>
            <div style="color:var(--muted);font-size:13px">AI detects and logs attendance instantly</div></div>
          </div>
        </div>
        <div class="alert alert-warn" style="margin-top:20px">⚠️ Enroll first before scanning for accurate records.</div>
      </div>
    </div>
    <script>
    navigator.mediaDevices.getUserMedia({video:true})
      .then(s=>{document.getElementById('cam').srcObject=s;})
      .catch(()=>{alert("Camera access denied.");});
    function snap(){
      let v=document.getElementById("cam"),c=document.getElementById("canvas");
      c.width=v.videoWidth;c.height=v.videoHeight;
      c.getContext("2d").drawImage(v,0,0);
      document.getElementById("imgdata").value=c.toDataURL("image/jpeg",0.85);
      document.getElementById("camForm").submit();
    }
    </script>"""
    return layout("Face Scan", content, "scan")

def get_face_encoding(image_path):
    """Extract face region as a small normalized grayscale array for comparison."""
    img = cv2.imread(image_path)
    if img is None:
        return None
    gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    if len(faces) == 0:
        return None
    # Take the largest face
    x, y, w, h = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)[0]
    face_crop = gray[y:y+h, x:x+w]
    # Resize to fixed 64x64 for comparison
    face_resized = cv2.resize(face_crop, (64, 64))
    return face_resized.flatten().astype("float32")

def match_face(scan_path):
    """
    Compare scanned face against all enrolled student photos.
    Returns (matched_name, confidence_pct) or (None, 0) if no face found.
    confidence_pct is 0–100, higher = better match.
    """
    scan_enc = get_face_encoding(scan_path)
    if scan_enc is None:
        return None, 0  # no face detected at all

    best_name  = None
    best_score = float("inf")  # lower distance = better

    for student in enrolled_students():
        student_dir = os.path.join(DATA_DIR, student)
        if not os.path.isdir(student_dir):
            continue
        imgs = [f for f in os.listdir(student_dir)
                if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        for img_file in imgs:
            enc = get_face_encoding(os.path.join(student_dir, img_file))
            if enc is None:
                continue
            # Normalised correlation distance
            a = scan_enc / (np.linalg.norm(scan_enc) + 1e-6)
            b = enc       / (np.linalg.norm(enc)       + 1e-6)
            dist = float(np.linalg.norm(a - b))
            if dist < best_score:
                best_score = dist
                best_name  = student

    # Threshold: distance < 0.85 is considered a match
    THRESHOLD = 0.85
    if best_name and best_score < THRESHOLD:
        confidence = max(0, round((1 - best_score / THRESHOLD) * 100))
        return best_name, confidence
    return "Unknown", 0

@app.route("/camera", methods=["POST"])
def camera():
    try:
        data = request.form.get("img","")
        _, encoded = data.split(",", 1)
        img_bytes  = base64.b64decode(encoded)
        filename   = f"camera_{datetime.now().timestamp()}.jpg"
        full_path  = os.path.join(DATA_DIR, filename)
        with open(full_path, "wb") as f:
            f.write(img_bytes)

        person, confidence = match_face(full_path)

        # person = actual student name, or "Unknown", or None (no face at all)
        if person is None:
            # No face detected in frame
            status    = "Absent"
            person    = "No Face Detected"
            conf_html = ""
        elif person == "Unknown":
            # Face found but doesn't match any enrolled student
            status    = "Absent"
            conf_html = '<div class="alert alert-warn" style="margin-top:12px">⚠️ Face not recognised — not enrolled in system.</div>'
        else:
            # Matched a real student!
            status    = "Present"
            conf_html = f'<div style="margin-top:8px"><span class="pill pill-blue">🎯 {confidence}% match confidence</span></div>'

        today    = datetime.now().strftime("%Y-%m-%d")
        time_str = datetime.now().strftime("%H:%M:%S")

        with open(ATT_FILE, "a", newline="") as f:
            csv.writer(f).writerow([person, today, status, time_str])

        pill_cls  = "pill-green" if status == "Present" else "pill-red"
        alert_cls = "alert-success" if status == "Present" else "alert-error"
        icon      = "✅" if status == "Present" else "❌"

        # Profile picture of matched student (if known)
        profile_img = ""
        if status == "Present":
            user_dir = os.path.join(DATA_DIR, person)
            if os.path.isdir(user_dir):
                imgs = [f for f in os.listdir(user_dir)
                        if f.lower().endswith((".jpg",".jpeg",".png"))]
                if imgs:
                    profile_img = f'<img src="/img/{person}/{imgs[0]}" style="width:60px;height:60px;border-radius:50%;object-fit:cover;border:2px solid var(--green);margin-bottom:8px">'

        content = f"""
        <div class="alert {alert_cls}">{icon} Scan complete — <strong>{status}</strong>{' · ' + person if status == 'Present' else ''}</div>
        <div class="grid-2" style="align-items:start">
          <div class="card" style="text-align:center">
            <img src='/cam/{filename}' style='width:100%;max-width:360px;border-radius:12px;border:1px solid var(--border)'>
          </div>
          <div class="card">
            <div class="sec-title" style="margin-bottom:18px">Scan Result</div>
            <div style="text-align:center;margin-bottom:16px">
              {profile_img}
              <div style="font-family:'Space Grotesk',sans-serif;font-size:22px;font-weight:700">{person}</div>
              {conf_html}
            </div>
            <table style="font-size:14px">
              <tbody>
                <tr><td style="color:var(--muted);padding:10px 0;border:none;width:100px">Name</td><td style="font-weight:600;border:none">{person}</td></tr>
                <tr><td style="color:var(--muted);padding:10px 0;border:none">Status</td><td style="border:none"><span class="pill {pill_cls}">{icon} {status}</span></td></tr>
                <tr><td style="color:var(--muted);padding:10px 0;border:none">Date</td><td style="border:none">{today}</td></tr>
                <tr><td style="color:var(--muted);padding:10px 0;border:none">Time</td><td style="border:none">{time_str}</td></tr>
              </tbody>
            </table>
            <div style="margin-top:22px;display:flex;flex-direction:column;gap:10px">
              <a href="/scan" class="btn btn-primary" style="justify-content:center">Scan Again</a>
              <a href="/daily" class="btn btn-ghost" style="justify-content:center">View Today's Log</a>
              <a href="/" class="btn btn-ghost" style="justify-content:center">Dashboard</a>
            </div>
          </div>
        </div>"""
        return layout("Scan Result", content, "scan")
    except Exception as e:
        content = f'<div class="alert alert-error">❌ {str(e)}</div><a href="/scan" class="btn btn-ghost">Go Back</a>'
        return layout("Error", content, "scan")

@app.route("/cam/<file>")
def cam(file):
    return send_file(os.path.join(DATA_DIR, file))

@app.route("/img/<user>/<file>")
def img(user, file):
    return send_file(os.path.join(DATA_DIR, user, file))

# ══════════════════════════════════════════════════════
#  GALLERY
# ══════════════════════════════════════════════════════

@app.route("/gallery")
def gallery():
    records  = read_all_records()
    students = enrolled_students()
    cards    = ""
    for name in students:
        user_dir = os.path.join(DATA_DIR, name)
        if not os.path.isdir(user_dir):
            continue
        imgs = [f for f in os.listdir(user_dir) if f.lower().endswith((".jpg",".jpeg",".png"))]
        if not imgs:
            continue
        s = stats_for_student(name, records)
        pbar_cls = "pbar-green" if s["pct"]>=75 else ("pbar-amber" if s["pct"]>=50 else "pbar-red")
        cards += f"""
        <a href="/student/{name}" style="text-decoration:none">
          <div class="gallery-item">
            <img src='/img/{name}/{imgs[0]}' alt='{name}'>
            <div class="gallery-item-info">
              <div class="gallery-item-name">{name}</div>
              <div class="gallery-item-stat">{s['pct']}% attendance · {s['present']}P / {s['absent']}A</div>
              <div class="pbar-wrap" style="margin-top:6px"><div class="pbar {pbar_cls}" style="width:{s['pct']}%"></div></div>
            </div>
          </div>
        </a>"""

    empty = '<div style="grid-column:1/-1;text-align:center;padding:60px;color:var(--muted)">No faces enrolled yet. <a href="/enroll" style="color:var(--blue)">Enroll someone</a></div>' if not cards else ""

    content = f"""
    <div class="sec-head" style="margin-bottom:20px">
      <div><div class="sec-title" style="font-size:20px">🖼 Face Gallery</div>
      <div class="sec-sub">All enrolled students with attendance stats</div></div>
      <a href="/enroll" class="btn btn-primary">+ Enroll New</a>
    </div>
    <div class="gallery-grid">{cards or empty}</div>"""
    return layout("Gallery", content, "gallery")

# ══════════════════════════════════════════════════════
#  ANALYTICS ENGINE
# ══════════════════════════════════════════════════════

CHART_BG   = "#07090f"
CARD_BG    = "#0d1117"
PANEL_BG   = "#111827"
GRID_COL   = "#1a2234"
TEXT_COL   = "#f1f5f9"
MUTED_COL  = "#475569"
GREEN_COL  = "#10b981"
GREEN2_COL = "#34d399"
RED_COL    = "#ef4444"
RED2_COL   = "#f87171"
BLUE_COL   = "#3b82f6"
CYAN_COL   = "#06b6d4"
AMBER_COL  = "#f59e0b"
PURPLE_COL = "#8b5cf6"

plt.rcParams.update({
    "font.family":      "DejaVu Sans",
    "axes.labelcolor":  MUTED_COL,
    "xtick.color":      MUTED_COL,
    "ytick.color":      MUTED_COL,
    "figure.facecolor": CHART_BG,
    "axes.facecolor":   CARD_BG,
})

def style_ax(ax, xgrid=False):
    ax.set_facecolor(PANEL_BG)
    ax.tick_params(colors=MUTED_COL, labelsize=9, length=3)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.yaxis.grid(True, color=GRID_COL, linewidth=0.7, linestyle="--", zorder=0)
    ax.xaxis.grid(xgrid, color=GRID_COL, linewidth=0.5, linestyle="--", zorder=0)
    ax.set_axisbelow(True)

def save_graph(fig, name):
    fig.patch.set_facecolor(CHART_BG)
    path = os.path.join(GRAPH_DIR, name)
    plt.savefig(path, dpi=130, bbox_inches="tight",
                facecolor=CHART_BG, edgecolor="none")
    plt.close("all")
    return path

# ── DATA AGGREGATORS ─────────────────────────────────

def get_daily_counts(records, days=30):
    result = []
    for i in range(days-1, -1, -1):
        d = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        p = sum(1 for r in records if r["date"]==d and r["status"]=="Present")
        a = sum(1 for r in records if r["date"]==d and r["status"]!="Present")
        result.append((d, p, a))
    return result

def get_weekly_counts(records, weeks=8):
    result = []
    today = datetime.now().date()
    for i in range(weeks-1, -1, -1):
        ws  = today - timedelta(days=today.weekday() + 7*i)
        we  = ws + timedelta(days=6)
        lbl = ws.strftime("%d %b")
        p = sum(1 for r in records if ws.strftime("%Y-%m-%d") <= r["date"] <= we.strftime("%Y-%m-%d") and r["status"]=="Present")
        a = sum(1 for r in records if ws.strftime("%Y-%m-%d") <= r["date"] <= we.strftime("%Y-%m-%d") and r["status"]!="Present")
        result.append((lbl, p, a))
    return result

def get_monthly_counts(records, months=6):
    result = []
    now = datetime.now()
    for i in range(months-1, -1, -1):
        m = now.month - i; y = now.year
        while m <= 0: m += 12; y -= 1
        lbl    = datetime(y, m, 1).strftime("%b %Y")
        prefix = f"{y:04d}-{m:02d}-"
        p = sum(1 for r in records if r["date"].startswith(prefix) and r["status"]=="Present")
        a = sum(1 for r in records if r["date"].startswith(prefix) and r["status"]!="Present")
        result.append((lbl, p, a))
    return result

# ── CHART 1 · DUAL LINE (30-day trend) ───────────────

def render_line(records):
    data   = get_daily_counts(records, 30)
    labels = [d[0][-5:] for d in data]
    p_vals = np.array([d[1] for d in data], dtype=float)
    a_vals = np.array([d[2] for d in data], dtype=float)
    x      = np.arange(30)

    # smooth with rolling average
    def smooth(arr, w=3):
        return np.convolve(arr, np.ones(w)/w, mode="same")

    fig, ax = plt.subplots(figsize=(14, 5))
    style_ax(ax)

    # shaded fill first
    ax.fill_between(x, smooth(p_vals), alpha=0.15, color=GREEN_COL, zorder=1)
    ax.fill_between(x, smooth(a_vals), alpha=0.12, color=RED_COL,   zorder=1)

    # raw dots (faint)
    ax.scatter(x, p_vals, s=18, color=GREEN_COL, alpha=0.4, zorder=2)
    ax.scatter(x, a_vals, s=18, color=RED_COL,   alpha=0.4, zorder=2)

    # smooth lines (bold)
    ax.plot(x, smooth(p_vals), color=GREEN_COL, linewidth=2.8, zorder=3, label="Present")
    ax.plot(x, smooth(a_vals), color=RED_COL,   linewidth=2.8, zorder=3, label="Absent")

    # target line
    max_p = int(p_vals.max()) if p_vals.max() > 0 else 1
    ax.axhline(max_p * 0.75, color=AMBER_COL, linewidth=1, linestyle=":", alpha=0.7, label="75% Target")

    ax.set_xticks(list(x)[::3])
    ax.set_xticklabels(labels[::3], rotation=30, ha="right", fontsize=8.5)
    ax.set_title("Daily Attendance Trend  ·  Last 30 Days",
                 color=TEXT_COL, fontsize=14, fontweight="bold", pad=16, loc="left")
    ax.legend(facecolor=PANEL_BG, labelcolor=TEXT_COL, framealpha=0.95,
              fontsize=10, edgecolor=GRID_COL)

    # annotate peak
    peak_day = int(np.argmax(p_vals))
    if p_vals[peak_day] > 0:
        ax.annotate(f"Peak\n{int(p_vals[peak_day])}",
                    xy=(peak_day, p_vals[peak_day]),
                    xytext=(peak_day+1, p_vals[peak_day]+0.6),
                    color=GREEN2_COL, fontsize=8, fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color=GREEN2_COL, lw=1.2))
    return save_graph(fig, "graph_line.png")

# ── CHART 2 · CANDLESTICK (weekly) ───────────────────

def render_candle(records):
    """
    Real-style candlestick: each candle = one week.
    Open  = Mon attendance count
    Close = Fri attendance count
    High  = best single day in week
    Low   = worst single day in week
    Green candle = Close >= Open (improving week)
    Red candle   = Close <  Open (declining week)
    """
    N     = 12
    today = datetime.now().date()
    candles = []
    for i in range(N-1, -1, -1):
        ws   = today - timedelta(days=today.weekday() + 7*i)
        days = []
        for d in range(7):
            day = ws + timedelta(days=d)
            ds  = day.strftime("%Y-%m-%d")
            p   = sum(1 for r in records if r["date"]==ds and r["status"]=="Present")
            days.append(p)
        open_  = float(days[0])          # Mon
        close_ = float(days[4])          # Fri
        high_  = float(max(days))
        low_   = float(min(days))
        label  = ws.strftime("%d %b")
        candles.append((label, open_, close_, high_, low_))

    fig, ax = plt.subplots(figsize=(14, 6))
    style_ax(ax)

    for i, (lbl, op, cl, hi, lo) in enumerate(candles):
        bullish    = cl >= op
        body_col   = GREEN_COL if bullish else RED_COL
        wick_col   = GREEN2_COL if bullish else RED2_COL
        body_bot   = min(op, cl)
        body_h     = max(abs(cl - op), 0.15)

        # Upper wick
        ax.plot([i, i], [max(op, cl), hi], color=wick_col, linewidth=1.6, zorder=2, solid_capstyle="round")
        # Lower wick
        ax.plot([i, i], [lo, body_bot],    color=wick_col, linewidth=1.6, zorder=2, solid_capstyle="round")

        # Body rectangle with glow border
        body = plt.Rectangle((i-0.32, body_bot), 0.64, body_h,
                              facecolor=body_col, alpha=0.85, zorder=3,
                              linewidth=1.2, edgecolor=wick_col)
        ax.add_patch(body)

        # Open / close dots
        ax.scatter([i], [op], color=MUTED_COL, s=22, zorder=4)
        ax.scatter([i], [cl], color=TEXT_COL,  s=22, zorder=4)

        # Close label
        ax.text(i, hi + 0.18, f"{int(cl)}", ha="center", va="bottom",
                color=wick_col, fontsize=7.5, fontweight="bold")

    ax.set_xlim(-0.7, N - 0.3)
    ax.set_xticks(range(N))
    ax.set_xticklabels([c[0] for c in candles], rotation=30, ha="right", fontsize=8.5)
    ax.set_ylabel("Students Present", color=MUTED_COL, fontsize=9)
    ax.set_title("Weekly Attendance Candlestick  ·  Mon Open / Fri Close",
                 color=TEXT_COL, fontsize=14, fontweight="bold", pad=16, loc="left")

    bull = plt.Rectangle((0,0),1,1, facecolor=GREEN_COL, alpha=0.85, edgecolor=GREEN2_COL)
    bear = plt.Rectangle((0,0),1,1, facecolor=RED_COL,   alpha=0.85, edgecolor=RED2_COL)
    ax.legend([bull, bear], ["📈 Bull Week (Fri ≥ Mon)", "📉 Bear Week (Fri < Mon)"],
              facecolor=PANEL_BG, labelcolor=TEXT_COL, framealpha=0.95,
              fontsize=10, edgecolor=GRID_COL)

    # Volume-style bar strip at bottom
    ax2 = ax.twinx()
    ax2.set_facecolor("none")
    totals = [(c[2]+c[1]) for c in candles]
    ax2.bar(range(N), totals, width=0.64, color=BLUE_COL, alpha=0.08, zorder=0)
    ax2.set_ylim(0, max(totals)*8 if totals else 1)
    ax2.tick_params(left=False, right=False, labelleft=False, labelright=False)
    for sp in ax2.spines.values(): sp.set_visible(False)

    return save_graph(fig, "graph_candle.png")

# ── CHART 3 · STUDENT BAR ────────────────────────────

def render_bar(records):
    att = {}
    for r in records:
        n = r["name"]
        if n not in att: att[n] = {"p":0,"a":0}
        if r["status"]=="Present": att[n]["p"] += 1
        else:                       att[n]["a"] += 1

    names  = list(att.keys())
    p_vals = [att[n]["p"] for n in names]
    a_vals = [att[n]["a"] for n in names]
    pcts   = [round(p/(p+a)*100) if (p+a) else 0 for p,a in zip(p_vals, a_vals)]
    x, w   = np.arange(len(names)), 0.34

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), gridspec_kw={"width_ratios":[2,1]})
    style_ax(axes[0]); style_ax(axes[1])

    # Grouped bars with gradient effect
    bar_colors_p = [GREEN_COL if pct>=75 else (AMBER_COL if pct>=50 else RED_COL) for pct in pcts]
    bars_p = axes[0].bar(x - w/2, p_vals, w, label="Present", color=bar_colors_p, alpha=0.88, zorder=3)
    bars_a = axes[0].bar(x + w/2, a_vals, w, label="Absent",  color=RED2_COL,    alpha=0.55, zorder=3)

    for bar, val in zip(bars_p, p_vals):
        if val: axes[0].text(bar.get_x()+bar.get_width()/2, val+0.08,
                             str(val), ha="center", color=TEXT_COL, fontsize=8, fontweight="bold")
    for bar, val in zip(bars_a, a_vals):
        if val: axes[0].text(bar.get_x()+bar.get_width()/2, val+0.08,
                             str(val), ha="center", color=MUTED_COL, fontsize=8)

    axes[0].set_xticks(x)
    axes[0].set_xticklabels(names, rotation=22, ha="right", fontsize=9)
    axes[0].set_title("Attendance by Student", color=TEXT_COL, fontsize=13, fontweight="bold", pad=12, loc="left")
    axes[0].legend(facecolor=PANEL_BG, labelcolor=TEXT_COL, framealpha=0.95, edgecolor=GRID_COL)

    # Horizontal rate bars (right panel)
    sorted_idx = np.argsort(pcts)
    s_names = [names[i] for i in sorted_idx]
    s_pcts  = [pcts[i]  for i in sorted_idx]
    s_colors = [GREEN_COL if p>=75 else (AMBER_COL if p>=50 else RED_COL) for p in s_pcts]
    y_pos = np.arange(len(s_names))
    axes[1].barh(y_pos, s_pcts, color=s_colors, alpha=0.85, height=0.55, zorder=3)
    axes[1].set_yticks(y_pos)
    axes[1].set_yticklabels(s_names, fontsize=9)
    axes[1].set_xlim(0, 110)
    axes[1].axvline(75, color=AMBER_COL, linewidth=1.2, linestyle="--", alpha=0.8)
    axes[1].set_title("Attendance Rate %", color=TEXT_COL, fontsize=13, fontweight="bold", pad=12, loc="left")
    for i, pct in enumerate(s_pcts):
        axes[1].text(pct+1.5, i, f"{pct}%", va="center", color=TEXT_COL, fontsize=8.5, fontweight="bold")

    return save_graph(fig, "graph_bar.png")

# ── CHART 4 · WEEKLY STACKED + RATE ─────────────────

def render_weekly(records):
    data   = get_weekly_counts(records, 8)
    labels = [d[0] for d in data]
    p_vals = np.array([d[1] for d in data], dtype=float)
    a_vals = np.array([d[2] for d in data], dtype=float)
    rates  = np.array([round(p/(p+a)*100) if (p+a) else 0 for p, a in zip(p_vals, a_vals)], dtype=float)
    x      = np.arange(8)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    style_ax(axes[0]); style_ax(axes[1])

    # Stacked bar with value labels
    bars_p = axes[0].bar(x, p_vals, 0.55, label="Present", color=GREEN_COL, alpha=0.88, zorder=3)
    bars_a = axes[0].bar(x, a_vals, 0.55, bottom=p_vals, label="Absent",   color=RED_COL, alpha=0.7, zorder=3)
    for i, (p, a) in enumerate(zip(p_vals, a_vals)):
        total = p + a
        if total: axes[0].text(i, total+0.1, str(int(total)),
                               ha="center", color=TEXT_COL, fontsize=8, fontweight="bold")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(labels, rotation=30, ha="right", fontsize=8.5)
    axes[0].set_title("Weekly Stacked Attendance", color=TEXT_COL, fontsize=13, fontweight="bold", pad=12, loc="left")
    axes[0].legend(facecolor=PANEL_BG, labelcolor=TEXT_COL, framealpha=0.95, edgecolor=GRID_COL)

    # Rate line with area + diamond markers
    axes[1].fill_between(x, rates, alpha=0.14, color=BLUE_COL, zorder=1)
    axes[1].plot(x, rates, color=BLUE_COL, linewidth=2.8, zorder=3, marker="D",
                 markersize=7, markerfacecolor=CYAN_COL, markeredgecolor=BLUE_COL, markeredgewidth=1.5)
    axes[1].axhline(75, color=AMBER_COL, linewidth=1.3, linestyle="--", alpha=0.85, label="75% Target", zorder=2)
    axes[1].set_ylim(0, 115)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels, rotation=30, ha="right", fontsize=8.5)
    for i, r in enumerate(rates):
        axes[1].text(i, r + (4 if r < 105 else -8), f"{int(r)}%",
                     ha="center", color=CYAN_COL, fontsize=8.5, fontweight="bold")
    axes[1].set_title("Weekly Attendance Rate %", color=TEXT_COL, fontsize=13, fontweight="bold", pad=12, loc="left")
    axes[1].legend(facecolor=PANEL_BG, labelcolor=TEXT_COL, framealpha=0.95, edgecolor=GRID_COL)

    return save_graph(fig, "graph_weekly.png")

# ── CHART 5 · MONTHLY OVERVIEW ───────────────────────

def render_monthly(records):
    data   = get_monthly_counts(records, 6)
    labels = [d[0] for d in data]
    p_vals = [d[1] for d in data]
    a_vals = [d[2] for d in data]
    rates  = [round(p/(p+a)*100) if (p+a) else 0 for p, a in zip(p_vals, a_vals)]
    x      = np.arange(6)

    fig = plt.figure(figsize=(14, 10))
    gs  = fig.add_gridspec(2, 3, hspace=0.45, wspace=0.35)
    ax1 = fig.add_subplot(gs[0, :2])  # top-left wide: grouped bar
    ax2 = fig.add_subplot(gs[0, 2])   # top-right: donut
    ax3 = fig.add_subplot(gs[1, :])   # bottom full: rate area line

    for ax in [ax1, ax2, ax3]: style_ax(ax)

    # Grouped bar
    w = 0.30
    ax1.bar(x - w/2, p_vals, w, label="Present", color=GREEN_COL, alpha=0.88, zorder=3)
    ax1.bar(x + w/2, a_vals, w, label="Absent",  color=RED_COL,   alpha=0.82, zorder=3)
    for i, (p, a) in enumerate(zip(p_vals, a_vals)):
        if p: ax1.text(i-w/2, p+0.06, str(p), ha="center", color=GREEN2_COL, fontsize=8, fontweight="bold")
        if a: ax1.text(i+w/2, a+0.06, str(a), ha="center", color=RED2_COL,   fontsize=8, fontweight="bold")
    ax1.set_xticks(x); ax1.set_xticklabels(labels, rotation=15, ha="right", fontsize=9)
    ax1.set_title("Monthly Present vs Absent", color=TEXT_COL, fontsize=13, fontweight="bold", pad=12, loc="left")
    ax1.legend(facecolor=PANEL_BG, labelcolor=TEXT_COL, framealpha=0.95, edgecolor=GRID_COL)

    # Donut — current month
    ax2.set_facecolor(PANEL_BG)
    lp, la = p_vals[-1], a_vals[-1]
    if lp + la > 0:
        wedge_props = dict(width=0.52, edgecolor=CHART_BG, linewidth=2.5)
        ax2.pie([lp, la], colors=[GREEN_COL, RED_COL], startangle=90,
                wedgeprops=wedge_props, counterclock=False)
        pct = round(lp/(lp+la)*100)
        col = GREEN_COL if pct>=75 else (AMBER_COL if pct>=50 else RED_COL)
        ax2.text(0,  0.12,  f"{pct}%",      ha="center", va="center",
                 color=col, fontsize=26, fontweight="bold")
        ax2.text(0, -0.18, "This Month",    ha="center", va="center",
                 color=MUTED_COL, fontsize=9)
        ax2.text(0, -0.38, f"✅{lp}  ❌{la}", ha="center", va="center",
                 color=MUTED_COL, fontsize=8)
    ax2.set_title(labels[-1] if labels else "", color=TEXT_COL, fontsize=12, fontweight="bold", pad=10)

    # 6-month rate area
    x6 = np.arange(6)
    ax3.fill_between(x6, rates, alpha=0.16, color=PURPLE_COL, zorder=1)
    ax3.plot(x6, rates, color=PURPLE_COL, linewidth=3, zorder=3,
             marker="o", markersize=8, markerfacecolor=BLUE_COL,
             markeredgecolor=PURPLE_COL, markeredgewidth=2)
    ax3.axhline(75, color=AMBER_COL, linewidth=1.2, linestyle="--", alpha=0.8, label="75% Goal")
    ax3.set_ylim(0, 115)
    ax3.set_xticks(x6); ax3.set_xticklabels(labels, fontsize=9)
    for i, r in enumerate(rates):
        col = GREEN_COL if r>=75 else (AMBER_COL if r>=50 else RED_COL)
        ax3.text(i, r+3.5, f"{r}%", ha="center", color=col, fontsize=9, fontweight="bold")
    ax3.set_title("6-Month Attendance Rate Trend", color=TEXT_COL, fontsize=13, fontweight="bold", pad=12, loc="left")
    ax3.legend(facecolor=PANEL_BG, labelcolor=TEXT_COL, framealpha=0.95, edgecolor=GRID_COL)

    return save_graph(fig, "graph_monthly.png")

# ── CHART 6 · 30-DAY HEATMAP ────────────────────────

def render_heatmap(records):
    """
    GitHub-style contribution heatmap — 7 rows (days of week) × 5 cols (weeks).
    Color intensity = number of students present that day.
    """
    today = datetime.now().date()
    days  = 35  # 5 weeks
    matrix = np.zeros((7, 5))   # rows=weekday, cols=week
    col_labels = []

    for col in range(4, -1, -1):
        week_start = today - timedelta(days=today.weekday() + 7*col)
        col_labels.append(week_start.strftime("%d %b"))
        for row in range(7):
            day = week_start + timedelta(days=row)
            ds  = day.strftime("%Y-%m-%d")
            p   = sum(1 for r in records if r["date"]==ds and r["status"]=="Present")
            matrix[row, 4-col] = p

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.set_facecolor(PANEL_BG)

    # custom green colormap
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list(
        "fn_green", [PANEL_BG, "#134e2a", GREEN_COL, GREEN2_COL], N=256)

    im = ax.imshow(matrix, cmap=cmap, aspect="auto",
                   vmin=0, vmax=max(matrix.max(), 1))

    # cell value labels
    for r in range(7):
        for c in range(5):
            val = int(matrix[r, c])
            txt_col = TEXT_COL if val > 0 else GRID_COL
            ax.text(c, r, str(val) if val > 0 else "·",
                    ha="center", va="center", fontsize=10,
                    fontweight="bold", color=txt_col)

    dow = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    ax.set_yticks(range(7)); ax.set_yticklabels(dow, fontsize=9, color=MUTED_COL)
    ax.set_xticks(range(5)); ax.set_xticklabels(col_labels, fontsize=9, color=MUTED_COL)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(length=0)

    cbar = plt.colorbar(im, ax=ax, shrink=0.85, pad=0.02)
    cbar.ax.tick_params(colors=MUTED_COL, labelsize=8)
    cbar.outline.set_visible(False)
    cbar.set_label("Students Present", color=MUTED_COL, fontsize=9)

    ax.set_title("5-Week Attendance Heatmap  ·  Darker = More Students",
                 color=TEXT_COL, fontsize=13, fontweight="bold", pad=14, loc="left")
    fig.patch.set_facecolor(CHART_BG)
    return save_graph(fig, "graph_heatmap.png")

# ── MAIN ANALYTICS ROUTE ─────────────────────────────

@app.route("/graph")
def graph():
    records    = read_all_records()
    chart_type = request.args.get("type", "line")

    if not records:
        content = """
        <div class="card" style="text-align:center;padding:70px">
          <div style="font-size:56px;margin-bottom:16px">📊</div>
          <div class="sec-title" style="font-size:20px">No Data Yet</div>
          <div style="color:var(--muted);margin-top:8px;margin-bottom:22px">
            Start scanning faces to build your analytics dashboard.
          </div>
          <a href="/scan" class="btn btn-primary">🎥 Start Scanning</a>
        </div>"""
        return layout("Analytics", content, "analytics")

    ts = str(datetime.now().timestamp())

    CHART_META = {
        "line":    ("render_line",    "graph_line.png",    "📉 Line Chart",        "30-day daily present/absent trend with smoothing"),
        "candle":  ("render_candle",  "graph_candle.png",  "🕯 Candlestick Chart", "Weekly open/close/high/low · green = improving week"),
        "bar":     ("render_bar",     "graph_bar.png",     "📊 Student Bar Chart", "Per-student present vs absent + attendance rate ranking"),
        "weekly":  ("render_weekly",  "graph_weekly.png",  "📅 Weekly Overview",   "8-week stacked attendance + rate trend line"),
        "monthly": ("render_monthly", "graph_monthly.png", "🗓 Monthly Dashboard", "6-month grouped bar, donut gauge + trend line"),
        "heatmap": ("render_heatmap", "graph_heatmap.png", "🔥 Heatmap",           "GitHub-style 5-week attendance intensity grid"),
    }

    if chart_type not in CHART_META:
        chart_type = "line"

    fn_name, img_file, chart_title, chart_sub = CHART_META[chart_type]
    RENDERERS = {
        "line":    render_line,
        "candle":  render_candle,
        "bar":     render_bar,
        "weekly":  render_weekly,
        "monthly": render_monthly,
        "heatmap": render_heatmap,
    }
    RENDERERS[chart_type](records)

    img_url = f"/graph-image/{img_file}?t={ts}"

    # ── KPI summary row
    all_p     = sum(1 for r in records if r["status"]=="Present")
    all_a     = len(records) - all_p
    all_total = len(records)
    all_pct   = round(all_p/all_total*100) if all_total else 0
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_p   = sum(1 for r in records if r["date"]==today_str and r["status"]=="Present")
    students  = enrolled_students()

    pbar_cls = "pbar-green" if all_pct>=75 else ("pbar-amber" if all_pct>=50 else "pbar-red")

    kpi_html = f"""
    <div class="stats-row" style="margin-bottom:22px">
      <div class="stat s-blue">
        <div class="stat-ico" style="background:rgba(59,130,246,0.15)">👥</div>
        <div class="stat-val">{len(students)}</div>
        <div class="stat-lbl">Enrolled</div>
      </div>
      <div class="stat s-green">
        <div class="stat-ico" style="background:rgba(16,185,129,0.15)">✅</div>
        <div class="stat-val">{all_p}</div>
        <div class="stat-lbl">Total Present</div>
      </div>
      <div class="stat s-red">
        <div class="stat-ico" style="background:rgba(239,68,68,0.15)">❌</div>
        <div class="stat-val">{all_a}</div>
        <div class="stat-lbl">Total Absent</div>
      </div>
      <div class="stat s-amber">
        <div class="stat-ico" style="background:rgba(245,158,11,0.15)">📊</div>
        <div class="stat-val">{all_pct}%</div>
        <div class="stat-lbl">Overall Rate</div>
      </div>
    </div>
    <div class="card" style="padding:16px 20px;margin-bottom:22px">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
        <span style="font-size:12.5px;font-weight:700;color:var(--muted)">OVERALL ATTENDANCE RATE</span>
        <span style="font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:17px">{all_pct}%  ·  {all_p} of {all_total} records</span>
      </div>
      <div class="pbar-wrap"><div class="pbar {pbar_cls}" style="width:{all_pct}%"></div></div>
    </div>"""

    # ── Chart type tab bar
    TABS = [
        ("line",    "📉", "Line",    "30-day trend"),
        ("candle",  "🕯", "Candle",  "Weekly OHLC"),
        ("bar",     "📊", "Bar",     "Per student"),
        ("weekly",  "📅", "Weekly",  "8-week view"),
        ("monthly", "🗓", "Monthly", "6-month view"),
        ("heatmap", "🔥", "Heatmap", "5-week grid"),
    ]
    tab_btns = ""
    for t, emoji, lbl, hint in TABS:
        if t == chart_type:
            style = ("background:linear-gradient(135deg,var(--blue),#2563eb);color:white;"
                     "border-color:transparent;box-shadow:0 4px 14px rgba(59,130,246,0.35);")
        else:
            style = ""
        tab_btns += f"""
        <a href="/graph?type={t}" class="btn btn-ghost"
           style="flex-direction:column;gap:2px;padding:10px 16px;{style}font-size:13px"
           title="{hint}">
          <span style="font-size:17px">{emoji}</span>
          <span style="font-size:11px;font-weight:700">{lbl}</span>
        </a>"""

    # ── Monthly mini-cards
    monthly  = get_monthly_counts(records, 6)
    m_cards  = ""
    for lbl, p, a in monthly:
        total = p + a
        pct   = round(p/total*100) if total else 0
        pbar  = "pbar-green" if pct>=75 else ("pbar-amber" if pct>=50 else "pbar-red")
        m_cards += f"""
        <div style="background:var(--card);border:1px solid var(--border);border-radius:12px;padding:14px">
          <div style="font-size:10px;font-weight:700;color:var(--muted);letter-spacing:0.8px;margin-bottom:6px">{lbl.upper()}</div>
          <div style="font-family:'Space Grotesk',sans-serif;font-size:22px;font-weight:700;margin-bottom:2px">{pct}%</div>
          <div style="font-size:11px;color:var(--muted);margin-bottom:7px">✅{p} &nbsp;❌{a}</div>
          <div class="pbar-wrap"><div class="pbar {pbar}" style="width:{pct}%"></div></div>
        </div>"""

    # ── Weekly table
    weekly_data = get_weekly_counts(records, 6)
    w_rows = ""
    for lbl, p, a in weekly_data:
        total = p + a
        pct   = round(p/total*100) if total else 0
        pill  = "pill-green" if pct>=75 else ("pill-amber" if pct>=50 else "pill-red")
        trend = "↑" if pct>=75 else ("→" if pct>=50 else "↓")
        trend_col = "var(--green)" if pct>=75 else ("var(--amber)" if pct>=50 else "var(--red)")
        w_rows += f"""<tr>
          <td><strong>{lbl}</strong></td>
          <td style="color:var(--green);font-weight:600">{p}</td>
          <td style="color:var(--red);font-weight:600">{a}</td>
          <td>{total}</td>
          <td><span class="pill {pill}">{pct}%</span></td>
          <td style="color:{trend_col};font-size:16px;font-weight:700">{trend}</td>
        </tr>"""

    content = f"""
    <div class="sec-head" style="margin-bottom:6px">
      <div>
        <div class="sec-title" style="font-size:20px">📊 Advanced Analytics</div>
        <div class="sec-sub">Professional attendance intelligence — 6 chart types</div>
      </div>
      <div style="display:flex;gap:8px">
        <a href="/download" class="btn btn-ghost">⬇ Export CSV</a>
      </div>
    </div>

    {kpi_html}

    <!-- Tab selector -->
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px;
                background:var(--card);border:1px solid var(--border);
                border-radius:14px;padding:10px 12px;align-items:center">
      <span style="font-size:11px;font-weight:700;color:var(--muted);
                   letter-spacing:1px;margin-right:4px">CHART TYPE</span>
      {tab_btns}
    </div>

    <!-- Main chart -->
    <div class="card" style="margin-bottom:22px;padding:20px">
      <div class="sec-head" style="margin-bottom:14px">
        <div>
          <div class="sec-title" style="font-size:17px">{chart_title}</div>
          <div class="sec-sub">{chart_sub}</div>
        </div>
        <span class="pill pill-blue" style="font-size:11px">Live Data</span>
      </div>
      <img src="{img_url}" style="width:100%;border-radius:10px;border:1px solid var(--border)">
    </div>

    <!-- Monthly mini-cards -->
    <div class="sec-head" style="margin-bottom:14px">
      <div><div class="sec-title">🗓 Monthly Breakdown</div>
      <div class="sec-sub">Last 6 months at a glance</div></div>
    </div>
    <div style="display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin-bottom:24px">
      {m_cards}
    </div>

    <!-- Weekly table -->
    <div class="card">
      <div class="sec-head" style="margin-bottom:14px">
        <div><div class="sec-title">📅 Weekly Summary Table</div>
        <div class="sec-sub">Last 6 weeks — trend indicator included</div></div>
      </div>
      <div class="tbl-wrap">
        <table>
          <thead>
            <tr><th>Week Starting</th><th>Present</th><th>Absent</th><th>Total</th><th>Rate</th><th>Trend</th></tr>
          </thead>
          <tbody>{w_rows or '<tr><td colspan="6" style="text-align:center;color:var(--muted);padding:20px">No weekly data yet</td></tr>'}</tbody>
        </table>
      </div>
    </div>"""

    return layout("Analytics", content, "analytics")

@app.route("/graph-image/<filename>")
def graph_image(filename):
    allowed = {
        "graph_line.png","graph_candle.png","graph_bar.png",
        "graph_weekly.png","graph_monthly.png","graph_heatmap.png","graph.png"
    }
    if filename not in allowed:
        return "Not found", 404
    p = os.path.join(GRAPH_DIR, filename)
    return send_file(p) if os.path.exists(p) else ("Not found", 404)

# ══════════════════════════════════════════════════════
#  ADMIN
# ══════════════════════════════════════════════════════

@app.route("/admin")
def admin():
    records = read_all_records()
    rows = "".join(f"""<tr>
      <td><strong>{r['name']}</strong></td><td>{r['date']}</td><td>{r['time']}</td>
      <td><span class="pill {'pill-green' if r['status']=='Present' else 'pill-red'}">{r['status']}</span></td>
    </tr>""" for r in reversed(records)) or \
    '<tr><td colspan="4" style="text-align:center;color:var(--muted);padding:24px">No records</td></tr>'

    content = f"""
    <div class="sec-head" style="margin-bottom:20px">
      <div><div class="sec-title" style="font-size:20px">⚙ Admin Panel</div>
      <div class="sec-sub">Full attendance log and data management</div></div>
      <div style="display:flex;gap:10px">
        <a href="/download" class="btn btn-primary">⬇ Export CSV</a>
        <a href="/delete" class="btn btn-red" onclick="return confirm('Delete ALL data permanently?')">🗑 Clear All</a>
      </div>
    </div>
    <div class="card">
      <div class="tbl-wrap">
        <table>
          <thead><tr><th>Name</th><th>Date</th><th>Time</th><th>Status</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </div>"""
    return layout("Admin", content, "admin")

@app.route("/download")
def download():
    return send_file(ATT_FILE, as_attachment=True) if os.path.exists(ATT_FILE) else ("No data", 404)

@app.route("/delete")
def delete():
    try:
        if os.path.exists(ATT_FILE):
            os.remove(ATT_FILE)
        for root, _, files in os.walk(DATA_DIR):
            for f in files:
                if f.endswith((".jpg",".png")):
                    try: os.remove(os.path.join(root,f))
                    except: pass
        content = '<div class="alert alert-success">✅ All data cleared.</div><a href="/admin" class="btn btn-ghost">← Admin</a>'
        return layout("Cleared", content, "admin")
    except Exception as e:
        return layout("Error", f'<div class="alert alert-error">❌ {str(e)}</div>', "admin")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


