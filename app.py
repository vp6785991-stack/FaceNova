from flask import Flask, request, send_file, redirect, url_for
import os
import csv
import base64
from datetime import datetime
import cv2
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

app = Flask(__name__)

DATA_DIR = "data"
GRAPH_DIR = "graphs"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(GRAPH_DIR, exist_ok=True)
ATT_FILE = os.path.join(DATA_DIR, "attendance.csv")

face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# ─────────────────────────────────────────────
#  SHARED LAYOUT
# ─────────────────────────────────────────────

def layout(page_title, content, active="dashboard"):
    nav_items = [
        ("dashboard", "/",         "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6", "Dashboard"),
        ("scan",      "/scan",     "M15 10l4.553-2.069A1 1 0 0121 8.82V15a1 1 0 01-1.447.894L15 14M3 8a2 2 0 012-2h8a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2V8z", "Face Scan"),
        ("upload",    "/enroll",   "M12 4v16m8-8H4", "Enroll"),
        ("gallery",   "/gallery",  "M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z", "Gallery"),
        ("analytics", "/graph",    "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z", "Analytics"),
        ("calendar",  "/calendar", "M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z", "Calendar"),
        ("admin",     "/admin",    "M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z", "Admin"),
    ]

    nav_html = ""
    for key, href, path_d, label in nav_items:
        is_active = key == active
        active_cls = "nav-active" if is_active else ""
        # Handle multi-path SVGs
        if "M15 12" in path_d:
            icon = f'<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>'
        else:
            icon = f'<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="{path_d}"/></svg>'
        nav_html += f'<a href="{href}" class="nav-item {active_cls}">{icon}<span>{label}</span></a>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{page_title} — FaceNova</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}

:root{{
  --bg:       #07090f;
  --surface:  #0d1117;
  --card:     #111827;
  --border:   rgba(255,255,255,0.07);
  --blue:     #3b82f6;
  --cyan:     #06b6d4;
  --green:    #10b981;
  --red:      #ef4444;
  --amber:    #f59e0b;
  --text:     #f1f5f9;
  --muted:    #64748b;
  --sidebar-w:240px;
}}

body{{
  font-family:'Inter',sans-serif;
  background:var(--bg);
  color:var(--text);
  min-height:100vh;
  display:flex;
}}

/* ── SIDEBAR ── */
.sidebar{{
  width:var(--sidebar-w);
  background:var(--surface);
  border-right:1px solid var(--border);
  display:flex;
  flex-direction:column;
  position:fixed;
  top:0;bottom:0;left:0;
  z-index:100;
  padding:0 0 24px;
}}

.sidebar-logo{{
  padding:28px 24px 20px;
  border-bottom:1px solid var(--border);
}}

.logo-mark{{
  display:flex;
  align-items:center;
  gap:12px;
}}

.logo-icon{{
  width:38px;height:38px;
  background:linear-gradient(135deg,var(--blue),var(--cyan));
  border-radius:10px;
  display:flex;align-items:center;justify-content:center;
  font-size:18px;
}}

.logo-text{{
  font-family:'Space Grotesk',sans-serif;
  font-size:20px;
  font-weight:700;
  letter-spacing:-0.3px;
}}

.logo-text span{{color:var(--cyan)}}

.sidebar-label{{
  font-size:10px;
  font-weight:600;
  letter-spacing:1.5px;
  color:var(--muted);
  text-transform:uppercase;
  padding:20px 24px 8px;
}}

.nav-item{{
  display:flex;
  align-items:center;
  gap:12px;
  padding:11px 24px;
  color:var(--muted);
  text-decoration:none;
  font-size:14px;
  font-weight:500;
  transition:all 0.15s;
  border-left:3px solid transparent;
  margin:1px 0;
}}

.nav-item svg{{
  width:18px;height:18px;
  flex-shrink:0;
}}

.nav-item:hover{{
  color:var(--text);
  background:rgba(255,255,255,0.04);
}}

.nav-active{{
  color:var(--blue) !important;
  background:rgba(59,130,246,0.08) !important;
  border-left-color:var(--blue) !important;
}}

.sidebar-footer{{
  margin-top:auto;
  padding:20px 24px 0;
  border-top:1px solid var(--border);
}}

.status-dot{{
  display:inline-block;
  width:8px;height:8px;
  background:var(--green);
  border-radius:50%;
  margin-right:8px;
  animation:pulse 2s infinite;
}}

@keyframes pulse{{
  0%,100%{{opacity:1}}
  50%{{opacity:0.4}}
}}

/* ── MAIN ── */
.main{{
  margin-left:var(--sidebar-w);
  flex:1;
  display:flex;
  flex-direction:column;
  min-height:100vh;
}}

.topbar{{
  background:var(--surface);
  border-bottom:1px solid var(--border);
  padding:0 32px;
  height:64px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  position:sticky;
  top:0;
  z-index:50;
}}

.topbar-title{{
  font-family:'Space Grotesk',sans-serif;
  font-size:17px;
  font-weight:600;
}}

.topbar-meta{{
  display:flex;
  align-items:center;
  gap:16px;
  font-size:13px;
  color:var(--muted);
}}

.badge{{
  background:rgba(59,130,246,0.15);
  color:var(--blue);
  padding:4px 10px;
  border-radius:20px;
  font-size:12px;
  font-weight:600;
}}

.page{{
  padding:32px;
  flex:1;
}}

/* ── CARDS ── */
.card{{
  background:var(--card);
  border:1px solid var(--border);
  border-radius:16px;
  padding:24px;
}}

.card-sm{{
  padding:20px;
}}

.grid-4{{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}}
.grid-3{{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}}
.grid-2{{display:grid;grid-template-columns:repeat(2,1fr);gap:20px}}

.stat-card{{
  background:var(--card);
  border:1px solid var(--border);
  border-radius:16px;
  padding:22px;
  position:relative;
  overflow:hidden;
}}

.stat-card::before{{
  content:'';
  position:absolute;
  top:0;left:0;right:0;
  height:2px;
}}

.stat-blue::before{{background:linear-gradient(90deg,var(--blue),var(--cyan))}}
.stat-green::before{{background:linear-gradient(90deg,var(--green),#34d399)}}
.stat-amber::before{{background:linear-gradient(90deg,var(--amber),#fcd34d)}}
.stat-red::before{{background:linear-gradient(90deg,var(--red),#f87171)}}

.stat-icon{{
  width:40px;height:40px;
  border-radius:10px;
  display:flex;align-items:center;justify-content:center;
  font-size:18px;
  margin-bottom:14px;
}}

.stat-value{{
  font-family:'Space Grotesk',sans-serif;
  font-size:32px;
  font-weight:700;
  line-height:1;
  margin-bottom:4px;
}}

.stat-label{{
  font-size:13px;
  color:var(--muted);
  font-weight:500;
}}

/* ── BUTTONS ── */
.btn{{
  display:inline-flex;
  align-items:center;
  gap:8px;
  padding:10px 20px;
  border:none;
  border-radius:10px;
  font-size:14px;
  font-weight:600;
  cursor:pointer;
  transition:all 0.15s;
  text-decoration:none;
  font-family:'Inter',sans-serif;
}}

.btn-primary{{
  background:linear-gradient(135deg,var(--blue),#2563eb);
  color:white;
}}

.btn-primary:hover{{
  transform:translateY(-1px);
  box-shadow:0 4px 20px rgba(59,130,246,0.4);
}}

.btn-cyan{{
  background:linear-gradient(135deg,var(--cyan),#0891b2);
  color:white;
}}

.btn-cyan:hover{{transform:translateY(-1px);box-shadow:0 4px 20px rgba(6,182,212,0.4)}}

.btn-ghost{{
  background:rgba(255,255,255,0.06);
  color:var(--text);
  border:1px solid var(--border);
}}

.btn-ghost:hover{{background:rgba(255,255,255,0.1)}}

.btn-red{{background:rgba(239,68,68,0.15);color:var(--red);border:1px solid rgba(239,68,68,0.3)}}
.btn-red:hover{{background:rgba(239,68,68,0.25)}}

.btn-green{{background:var(--green);color:white}}
.btn-green:hover{{transform:translateY(-1px);box-shadow:0 4px 20px rgba(16,185,129,0.4)}}

/* ── FORM ── */
.form-group{{margin-bottom:18px}}

label{{
  display:block;
  font-size:13px;
  font-weight:600;
  color:var(--muted);
  margin-bottom:8px;
  letter-spacing:0.3px;
}}

input[type=text],
input[type=file]{{
  width:100%;
  background:rgba(255,255,255,0.05);
  border:1px solid var(--border);
  border-radius:10px;
  padding:11px 14px;
  color:var(--text);
  font-size:14px;
  font-family:'Inter',sans-serif;
  transition:border 0.15s;
  outline:none;
}}

input[type=text]:focus{{
  border-color:var(--blue);
  background:rgba(59,130,246,0.05);
}}

input[type=file]{{padding:10px 14px;color:var(--muted)}}

/* ── TABLE ── */
.table-wrap{{overflow-x:auto}}

table{{
  width:100%;
  border-collapse:collapse;
  font-size:14px;
}}

thead th{{
  background:rgba(255,255,255,0.04);
  padding:12px 16px;
  text-align:left;
  font-size:11px;
  font-weight:700;
  letter-spacing:1px;
  text-transform:uppercase;
  color:var(--muted);
  border-bottom:1px solid var(--border);
}}

tbody td{{
  padding:14px 16px;
  border-bottom:1px solid var(--border);
  font-size:14px;
}}

tbody tr:hover{{background:rgba(255,255,255,0.02)}}
tbody tr:last-child td{{border-bottom:none}}

/* ── PILL STATUS ── */
.pill{{
  display:inline-block;
  padding:4px 12px;
  border-radius:20px;
  font-size:12px;
  font-weight:600;
}}

.pill-green{{background:rgba(16,185,129,0.12);color:#34d399}}
.pill-red{{background:rgba(239,68,68,0.12);color:#f87171}}

/* ── SCAN RING ── */
.scan-wrap{{
  position:relative;
  display:inline-block;
}}

.scan-ring{{
  position:absolute;
  inset:-16px;
  border-radius:50%;
  border:2px solid var(--cyan);
  opacity:0;
  animation:ring 2.5s ease-in-out infinite;
}}

.scan-ring:nth-child(2){{animation-delay:0.8s}}
.scan-ring:nth-child(3){{animation-delay:1.6s}}

@keyframes ring{{
  0%{{transform:scale(0.85);opacity:0.8}}
  100%{{transform:scale(1.15);opacity:0}}
}}

video{{border-radius:16px;display:block}}

/* ── SECTION HEADING ── */
.section-head{{
  display:flex;
  align-items:center;
  justify-content:space-between;
  margin-bottom:20px;
}}

.section-title{{
  font-family:'Space Grotesk',sans-serif;
  font-size:18px;
  font-weight:700;
}}

.section-sub{{
  font-size:13px;
  color:var(--muted);
  margin-top:3px;
}}

/* ── PAGE HERO ── */
.page-hero{{
  background:linear-gradient(135deg,rgba(59,130,246,0.1),rgba(6,182,212,0.06));
  border:1px solid rgba(59,130,246,0.2);
  border-radius:20px;
  padding:28px 32px;
  margin-bottom:28px;
  display:flex;
  align-items:center;
  justify-content:space-between;
}}

.hero-text h1{{
  font-family:'Space Grotesk',sans-serif;
  font-size:26px;
  font-weight:700;
  margin-bottom:6px;
}}

.hero-text p{{
  color:var(--muted);
  font-size:14px;
}}

/* ── GALLERY ── */
.gallery-grid{{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(200px,1fr));
  gap:16px;
}}

.gallery-item{{
  background:var(--card);
  border:1px solid var(--border);
  border-radius:14px;
  overflow:hidden;
  transition:transform 0.15s;
}}

.gallery-item:hover{{transform:translateY(-3px)}}

.gallery-item img{{
  width:100%;
  height:160px;
  object-fit:cover;
  display:block;
}}

.gallery-item-info{{
  padding:12px;
}}

.gallery-item-name{{
  font-size:14px;
  font-weight:600;
}}

/* ── CALENDAR ── */
.cal-grid{{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(140px,1fr));
  gap:12px;
}}

.cal-day{{
  border-radius:12px;
  padding:16px;
  border:1px solid var(--border);
}}

.cal-day-date{{
  font-size:12px;
  color:var(--muted);
  margin-bottom:6px;
}}

.cal-day-status{{
  font-size:14px;
  font-weight:700;
}}

.cal-present{{
  background:rgba(16,185,129,0.08);
  border-color:rgba(16,185,129,0.25);
}}

.cal-present .cal-day-status{{color:var(--green)}}

.cal-absent{{
  background:rgba(239,68,68,0.08);
  border-color:rgba(239,68,68,0.25);
}}

.cal-absent .cal-day-status{{color:var(--red)}}

/* ── ALERT ── */
.alert{{
  padding:14px 18px;
  border-radius:12px;
  font-size:14px;
  margin-bottom:20px;
  display:flex;
  align-items:center;
  gap:10px;
}}

.alert-success{{background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.25);color:#34d399}}
.alert-error{{background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.25);color:#f87171}}
.alert-info{{background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.25);color:var(--blue)}}

/* ── RESPONSIVE ── */
@media(max-width:900px){{
  .sidebar{{display:none}}
  .main{{margin-left:0}}
  .grid-4{{grid-template-columns:repeat(2,1fr)}}
  .grid-3{{grid-template-columns:1fr}}
  .grid-2{{grid-template-columns:1fr}}
}}

@media(max-width:600px){{
  .page{{padding:20px}}
  .grid-4{{grid-template-columns:1fr 1fr}}
  .page-hero{{flex-direction:column;gap:16px}}
}}
</style>
</head>
<body>

<aside class="sidebar">
  <div class="sidebar-logo">
    <div class="logo-mark">
      <div class="logo-icon">🧠</div>
      <div class="logo-text">Face<span>Nova</span></div>
    </div>
  </div>
  <div class="sidebar-label">Main Menu</div>
  <nav>{nav_html}</nav>
  <div class="sidebar-footer">
    <div style="font-size:13px;color:var(--muted)">
      <span class="status-dot"></span>System Online
    </div>
    <div style="font-size:11px;color:var(--muted);margin-top:6px">AI Face Recognition v2.0</div>
  </div>
</aside>

<div class="main">
  <div class="topbar">
    <div class="topbar-title">{page_title}</div>
    <div class="topbar-meta">
      <span id="clock" style="font-size:13px"></span>
      <span class="badge">AI Active</span>
    </div>
  </div>
  <div class="page">
    {content}
  </div>
</div>

<script>
function tick(){{
  const now = new Date();
  document.getElementById('clock').textContent =
    now.toLocaleTimeString('en-US',{{hour:'2-digit',minute:'2-digit'}}) +
    ' · ' + now.toLocaleDateString('en-US',{{month:'short',day:'numeric'}});
}}
tick(); setInterval(tick,1000);
</script>
</body>
</html>"""


# ─────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────

@app.route("/")
def home():
    students = [x for x in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, x))]
    total_students = len(students)

    total_att = present_today = absent_today = 0
    today_str = datetime.now().strftime("%Y-%m-%d")

    if os.path.exists(ATT_FILE):
        with open(ATT_FILE) as f:
            rows = list(csv.reader(f))
        total_att = len(rows)
        for r in rows:
            if len(r) >= 3 and r[1] == today_str:
                if r[2] == "Present":
                    present_today += 1
                else:
                    absent_today += 1

    recent_rows = ""
    if os.path.exists(ATT_FILE):
        with open(ATT_FILE) as f:
            all_rows = list(csv.reader(f))
        for r in reversed(all_rows[-8:]):
            if len(r) >= 3:
                pill_cls = "pill-green" if r[2] == "Present" else "pill-red"
                recent_rows += f"""
                <tr>
                  <td><strong>{r[0]}</strong></td>
                  <td>{r[1]}</td>
                  <td><span class="pill {pill_cls}">{r[2]}</span></td>
                </tr>"""

    content = f"""
    <div class="page-hero">
      <div class="hero-text">
        <h1>👋 Welcome to FaceNova</h1>
        <p>AI-powered face recognition for offices, schools & colleges. Real-time attendance tracking.</p>
      </div>
      <a href="/scan" class="btn btn-cyan">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.069A1 1 0 0121 8.82V15a1 1 0 01-1.447.894L15 14M3 8a2 2 0 012-2h8a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2V8z"/></svg>
        Start Face Scan
      </a>
    </div>

    <div class="grid-4" style="margin-bottom:28px">
      <div class="stat-card stat-blue">
        <div class="stat-icon" style="background:rgba(59,130,246,0.15)">👤</div>
        <div class="stat-value">{total_students}</div>
        <div class="stat-label">Enrolled Users</div>
      </div>
      <div class="stat-card stat-green">
        <div class="stat-icon" style="background:rgba(16,185,129,0.15)">✅</div>
        <div class="stat-value">{present_today}</div>
        <div class="stat-label">Present Today</div>
      </div>
      <div class="stat-card stat-red">
        <div class="stat-icon" style="background:rgba(239,68,68,0.15)">❌</div>
        <div class="stat-value">{absent_today}</div>
        <div class="stat-label">Absent Today</div>
      </div>
      <div class="stat-card stat-amber">
        <div class="stat-icon" style="background:rgba(245,158,11,0.15)">📊</div>
        <div class="stat-value">{total_att}</div>
        <div class="stat-label">Total Records</div>
      </div>
    </div>

    <div class="grid-2">
      <div class="card">
        <div class="section-head">
          <div>
            <div class="section-title">Recent Activity</div>
            <div class="section-sub">Latest attendance records</div>
          </div>
          <a href="/admin" class="btn btn-ghost" style="font-size:13px;padding:8px 14px">View All</a>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Name</th><th>Date</th><th>Status</th></tr></thead>
            <tbody>{''.join(recent_rows) if recent_rows else '<tr><td colspan="3" style="text-align:center;color:var(--muted);padding:24px">No records yet</td></tr>'}</tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <div class="section-head">
          <div>
            <div class="section-title">Quick Actions</div>
            <div class="section-sub">Jump to any module</div>
          </div>
        </div>
        <div style="display:flex;flex-direction:column;gap:12px">
          <a href="/scan" class="btn btn-primary" style="justify-content:center">🎥 &nbsp;Live Face Scan</a>
          <a href="/enroll" class="btn btn-cyan" style="justify-content:center">📸 &nbsp;Enroll New User</a>
          <a href="/gallery" class="btn btn-ghost" style="justify-content:center">🖼 &nbsp;View Gallery</a>
          <a href="/graph" class="btn btn-ghost" style="justify-content:center">📊 &nbsp;Analytics</a>
          <a href="/download" class="btn btn-ghost" style="justify-content:center">⬇ &nbsp;Export CSV</a>
        </div>
      </div>
    </div>
    """
    return layout("Dashboard", content, "dashboard")


# ─────────────────────────────────────────────
#  ENROLL
# ─────────────────────────────────────────────

@app.route("/enroll")
def enroll_page():
    content = """
    <div class="section-head">
      <div>
        <div class="section-title">Enroll New User</div>
        <div class="section-sub">Upload face photos to register a student or employee</div>
      </div>
    </div>

    <div class="grid-2">
      <div class="card">
        <div class="section-title" style="margin-bottom:20px">📸 Upload Face Photos</div>
        <form action='/upload' method='POST' enctype='multipart/form-data'>
          <div class="form-group">
            <label>Full Name</label>
            <input type='text' name='name' placeholder='e.g. John Smith' required>
          </div>
          <div class="form-group">
            <label>Face Photos (multiple allowed)</label>
            <input type='file' name='photos' multiple accept='image/*' required>
          </div>
          <button type='submit' class='btn btn-primary' style='width:100%;justify-content:center;padding:13px'>
            Upload & Enroll
          </button>
        </form>
      </div>

      <div class="card" style="display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:16px">
        <div style="font-size:56px">📋</div>
        <div class="section-title">Enrollment Tips</div>
        <div style="color:var(--muted);font-size:14px;line-height:1.7">
          ✅ Use clear, well-lit photos<br>
          ✅ Front-facing photos work best<br>
          ✅ Upload 3–5 photos per person<br>
          ✅ Avoid sunglasses or masks<br>
          ✅ Different angles improve accuracy
        </div>
      </div>
    </div>
    """
    return layout("Enroll User", content, "upload")


@app.route("/upload", methods=["POST"])
def upload():
    try:
        name = request.form["name"]
        files = request.files.getlist("photos")
        user_dir = os.path.join(DATA_DIR, name)
        os.makedirs(user_dir, exist_ok=True)
        saved = 0
        for f in files:
            filename = f"{datetime.now().timestamp()}.jpg"
            f.save(os.path.join(user_dir, filename))
            saved += 1

        content = f"""
        <div class="alert alert-success">✅ Successfully enrolled <strong>{name}</strong> with {saved} photo(s).</div>
        <div class="card" style="text-align:center;padding:40px">
          <div style="font-size:64px;margin-bottom:16px">🎉</div>
          <div class="section-title" style="margin-bottom:8px">{name} Enrolled!</div>
          <div style="color:var(--muted);margin-bottom:24px">{saved} face photo(s) uploaded successfully.</div>
          <div style="display:flex;gap:12px;justify-content:center">
            <a href="/enroll" class="btn btn-primary">Enroll Another</a>
            <a href="/gallery" class="btn btn-ghost">View Gallery</a>
            <a href="/" class="btn btn-ghost">Dashboard</a>
          </div>
        </div>
        """
        return layout("Enrolled", content, "upload")
    except Exception as e:
        content = f'<div class="alert alert-error">❌ Upload failed: {str(e)}</div><a href="/enroll" class="btn btn-ghost">Go Back</a>'
        return layout("Error", content, "upload")


# ─────────────────────────────────────────────
#  SCAN PAGE
# ─────────────────────────────────────────────

@app.route("/scan")
def scan_page():
    content = """
    <div class="section-head">
      <div>
        <div class="section-title">Live Face Scan</div>
        <div class="section-sub">Point the camera at a face and tap Scan</div>
      </div>
    </div>

    <div class="grid-2" style="align-items:start">
      <div class="card" style="display:flex;flex-direction:column;align-items:center;gap:20px">
        <div class="scan-wrap" id="scanWrap" style="border-radius:16px;overflow:hidden">
          <video id='cam' width='380' autoplay playsinline></video>
          <div class="scan-ring" id="r1"></div>
          <div class="scan-ring" id="r2"></div>
          <div class="scan-ring" id="r3"></div>
        </div>
        <button class='btn btn-cyan' onclick='snap()' style="width:100%;justify-content:center;padding:14px;font-size:16px">
          📷 &nbsp;Scan Face Now
        </button>
        <canvas id='canvas' style='display:none;'></canvas>
        <form id='camForm' action='/camera' method='POST'>
          <input type='hidden' name='img' id='imgdata'>
        </form>
      </div>

      <div class="card">
        <div class="section-title" style="margin-bottom:16px">How it works</div>
        <div style="display:flex;flex-direction:column;gap:16px">
          <div style="display:flex;gap:14px;align-items:flex-start">
            <div style="background:rgba(59,130,246,0.15);color:var(--blue);border-radius:8px;width:32px;height:32px;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0">1</div>
            <div>
              <div style="font-weight:600;margin-bottom:2px">Allow Camera</div>
              <div style="color:var(--muted);font-size:13px">Grant camera access when prompted by the browser</div>
            </div>
          </div>
          <div style="display:flex;gap:14px;align-items:flex-start">
            <div style="background:rgba(6,182,212,0.15);color:var(--cyan);border-radius:8px;width:32px;height:32px;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0">2</div>
            <div>
              <div style="font-weight:600;margin-bottom:2px">Position Face</div>
              <div style="color:var(--muted);font-size:13px">Ensure your face is centered in the camera frame</div>
            </div>
          </div>
          <div style="display:flex;gap:14px;align-items:flex-start">
            <div style="background:rgba(16,185,129,0.15);color:var(--green);border-radius:8px;width:32px;height:32px;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0">3</div>
            <div>
              <div style="font-weight:600;margin-bottom:2px">Tap Scan</div>
              <div style="color:var(--muted);font-size:13px">The AI will detect and log your attendance instantly</div>
            </div>
          </div>
        </div>
        <div class="alert alert-info" style="margin-top:24px">
          💡 Make sure you are enrolled first via the Enroll page before scanning.
        </div>
      </div>
    </div>

    <script>
    navigator.mediaDevices.getUserMedia({video:true})
      .then(s=>{ document.getElementById('cam').srcObject=s; })
      .catch(()=>{ alert("Camera access denied. Please allow camera in your browser settings."); });

    function snap(){
      let v=document.getElementById("cam"),c=document.getElementById("canvas");
      c.width=v.videoWidth; c.height=v.videoHeight;
      c.getContext("2d").drawImage(v,0,0);
      document.getElementById("imgdata").value=c.toDataURL("image/jpeg",0.85);
      document.getElementById("camForm").submit();
    }
    </script>
    """
    return layout("Face Scan", content, "scan")


# ─────────────────────────────────────────────
#  CAMERA PROCESS
# ─────────────────────────────────────────────

def detect_face(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return False
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    return len(faces) > 0

@app.route("/camera", methods=["POST"])
def camera():
    try:
        data = request.form.get("img")
        if not data:
            return "No image received"
        header, encoded = data.split(",", 1)
        img_bytes = base64.b64decode(encoded)
        filename = f"camera_{datetime.now().timestamp()}.jpg"
        full_path = os.path.join(DATA_DIR, filename)
        with open(full_path, "wb") as f:
            f.write(img_bytes)

        has_face = detect_face(full_path)
        person = "Face Detected" if has_face else "Unknown"
        status = "Present" if has_face else "Absent"
        today = datetime.now().strftime("%Y-%m-%d")
        time_str = datetime.now().strftime("%H:%M:%S")

        with open(ATT_FILE, "a", newline="") as f:
            csv.writer(f).writerow([person, today, status])

        icon = "✅" if has_face else "❌"
        pill_cls = "pill-green" if has_face else "pill-red"
        alert_cls = "alert-success" if has_face else "alert-error"

        content = f"""
        <div class="alert {alert_cls}">{icon} Scan complete — <strong>{status}</strong></div>
        <div class="grid-2" style="align-items:start">
          <div class="card" style="text-align:center">
            <img src='/cam/{filename}' style='width:100%;max-width:360px;border-radius:12px;border:1px solid var(--border)'>
          </div>
          <div class="card">
            <div class="section-title" style="margin-bottom:20px">Scan Result</div>
            <table style="font-size:14px">
              <tbody>
                <tr><td style="color:var(--muted);padding:10px 0;border:none">Person</td><td style="font-weight:600;border:none">{person}</td></tr>
                <tr><td style="color:var(--muted);padding:10px 0;border:none">Status</td><td style="border:none"><span class="pill {pill_cls}">{status}</span></td></tr>
                <tr><td style="color:var(--muted);padding:10px 0;border:none">Date</td><td style="border:none">{today}</td></tr>
                <tr><td style="color:var(--muted);padding:10px 0;border:none">Time</td><td style="border:none">{time_str}</td></tr>
              </tbody>
            </table>
            <div style="margin-top:24px;display:flex;flex-direction:column;gap:10px">
              <a href="/scan" class="btn btn-primary" style="justify-content:center">Scan Again</a>
              <a href="/" class="btn btn-ghost" style="justify-content:center">Dashboard</a>
            </div>
          </div>
        </div>
        """
        return layout("Scan Result", content, "scan")
    except Exception as e:
        content = f'<div class="alert alert-error">❌ Camera error: {str(e)}</div><a href="/scan" class="btn btn-ghost">Go Back</a>'
        return layout("Error", content, "scan")

@app.route("/cam/<file>")
def cam(file):
    return send_file(os.path.join(DATA_DIR, file))

@app.route("/img/<user>/<file>")
def img(user, file):
    return send_file(os.path.join(DATA_DIR, user, file))


# ─────────────────────────────────────────────
#  GALLERY
# ─────────────────────────────────────────────

@app.route("/gallery")
def gallery():
    gallery_html = ""
    for user in os.listdir(DATA_DIR):
        user_dir = os.path.join(DATA_DIR, user)
        if not os.path.isdir(user_dir):
            continue
        for img_file in os.listdir(user_dir):
            if img_file.lower().endswith(('.jpg','.jpeg','.png')):
                gallery_html += f"""
                <div class="gallery-item">
                  <img src='/img/{user}/{img_file}' alt='{user}'>
                  <div class="gallery-item-info">
                    <div class="gallery-item-name">👤 {user}</div>
                  </div>
                </div>"""

    empty = '<div style="grid-column:1/-1;text-align:center;padding:60px;color:var(--muted)">No enrolled users yet. <a href="/enroll" style="color:var(--blue)">Enroll someone</a></div>' if not gallery_html else ""

    content = f"""
    <div class="section-head">
      <div>
        <div class="section-title">Face Gallery</div>
        <div class="section-sub">All enrolled faces in the system</div>
      </div>
      <a href="/enroll" class="btn btn-primary">+ Enroll New</a>
    </div>
    <div class="gallery-grid">{gallery_html or empty}</div>
    """
    return layout("Gallery", content, "gallery")


# ─────────────────────────────────────────────
#  ANALYTICS
# ─────────────────────────────────────────────

@app.route("/graph")
def graph():
    attendance = {}
    if os.path.exists(ATT_FILE):
        with open(ATT_FILE) as f:
            for row in csv.reader(f):
                if len(row) >= 3:
                    attendance[row[0]] = attendance.get(row[0], 0) + 1

    if not attendance:
        content = """
        <div class="card" style="text-align:center;padding:60px">
          <div style="font-size:56px;margin-bottom:16px">📊</div>
          <div class="section-title">No Data Yet</div>
          <div style="color:var(--muted);margin-top:8px">Start scanning faces to see analytics here.</div>
        </div>"""
        return layout("Analytics", content, "analytics")

    plt.close("all")
    fig, ax = plt.subplots(figsize=(9, 5))
    fig.patch.set_facecolor("#111827")
    ax.set_facecolor("#111827")
    colors = ["#3b82f6","#06b6d4","#10b981","#f59e0b","#8b5cf6"]
    bars = ax.bar(list(attendance.keys()), list(attendance.values()),
                  color=[colors[i % len(colors)] for i in range(len(attendance))],
                  width=0.5, zorder=3)
    ax.tick_params(colors="#94a3b8")
    ax.spines[:].set_visible(False)
    ax.set_title("Attendance by Person", color="#f1f5f9", fontsize=14, fontweight='bold', pad=16)
    ax.set_ylabel("Records", color="#94a3b8")
    ax.yaxis.grid(True, color="rgba(255,255,255,0.06)", zorder=0)
    ax.set_axisbelow(True)
    for bar, val in zip(bars, attendance.values()):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                str(val), ha='center', color='#f1f5f9', fontsize=11)
    plt.tight_layout()
    graph_path = os.path.join(GRAPH_DIR, "graph.png")
    plt.savefig(graph_path, dpi=120)
    plt.close("all")

    content = f"""
    <div class="section-head">
      <div>
        <div class="section-title">Attendance Analytics</div>
        <div class="section-sub">Visual overview of attendance records</div>
      </div>
      <a href="/download" class="btn btn-ghost">⬇ Export CSV</a>
    </div>
    <div class="card">
      <img src='/graph-image' style='width:100%;border-radius:12px'>
    </div>
    """
    return layout("Analytics", content, "analytics")

@app.route("/graph-image")
def graph_image():
    p = os.path.join(GRAPH_DIR, "graph.png")
    return send_file(p) if os.path.exists(p) else ("Not found", 404)


# ─────────────────────────────────────────────
#  CALENDAR
# ─────────────────────────────────────────────

@app.route("/calendar")
def calendar():
    records = {}
    if os.path.exists(ATT_FILE):
        with open(ATT_FILE) as f:
            for row in csv.reader(f):
                if len(row) >= 3:
                    records[row[1]] = row[2]

    if not records:
        cal_html = '<div style="color:var(--muted);text-align:center;padding:40px">No records yet.</div>'
    else:
        cal_html = ""
        for date, status in sorted(records.items(), reverse=True):
            cls = "cal-present" if status == "Present" else "cal-absent"
            icon = "✅" if status == "Present" else "❌"
            cal_html += f"""
            <div class="cal-day {cls}">
              <div class="cal-day-date">{date}</div>
              <div class="cal-day-status">{icon} {status}</div>
            </div>"""

    content = f"""
    <div class="section-head">
      <div>
        <div class="section-title">Attendance Calendar</div>
        <div class="section-sub">Daily attendance overview</div>
      </div>
    </div>
    <div class="card">
      <div class="cal-grid">{cal_html}</div>
    </div>
    """
    return layout("Calendar", content, "calendar")


# ─────────────────────────────────────────────
#  ADMIN
# ─────────────────────────────────────────────

@app.route("/admin")
def admin():
    rows_html = ""
    if os.path.exists(ATT_FILE):
        with open(ATT_FILE) as f:
            for row in csv.reader(f):
                if len(row) >= 3:
                    pill = "pill-green" if row[2] == "Present" else "pill-red"
                    rows_html += f"""
                    <tr>
                      <td><strong>{row[0]}</strong></td>
                      <td>{row[1]}</td>
                      <td><span class="pill {pill}">{row[2]}</span></td>
                    </tr>"""

    content = f"""
    <div class="section-head">
      <div>
        <div class="section-title">Admin Dashboard</div>
        <div class="section-sub">All attendance records and system management</div>
      </div>
      <div style="display:flex;gap:10px">
        <a href="/download" class="btn btn-primary">⬇ Export CSV</a>
        <a href="/delete" class="btn btn-red" onclick="return confirm('Delete ALL data? This cannot be undone.')">🗑 Clear Data</a>
      </div>
    </div>

    <div class="card">
      <div class="table-wrap">
        <table>
          <thead><tr><th>Name</th><th>Date</th><th>Status</th></tr></thead>
          <tbody>{''.join(rows_html) if rows_html else '<tr><td colspan="3" style="text-align:center;color:var(--muted);padding:32px">No records found</td></tr>'}</tbody>
        </table>
      </div>
    </div>
    """
    return layout("Admin", content, "admin")

@app.route("/download")
def download():
    if os.path.exists(ATT_FILE):
        return send_file(ATT_FILE, as_attachment=True)
    return "No data yet"

@app.route("/delete")
def delete():
    try:
        if os.path.exists(ATT_FILE):
            os.remove(ATT_FILE)
        for root, dirs, files in os.walk(DATA_DIR):
            for file in files:
                if file.endswith((".jpg", ".png")):
                    try: os.remove(os.path.join(root, file))
                    except: pass
        content = """
        <div class="alert alert-success">✅ All data deleted successfully.</div>
        <a href="/admin" class="btn btn-ghost">← Back to Admin</a>
        """
        return layout("Data Cleared", content, "admin")
    except Exception as e:
        content = f'<div class="alert alert-error">❌ Error: {str(e)}</div>'
        return layout("Error", content, "admin")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

