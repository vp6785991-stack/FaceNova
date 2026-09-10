# routes2.py — FaceNova Routes Part 2 (Auth, Teacher, Subscription, SuperAdmin, Landing)
from flask import request, redirect, session, send_file, make_response
from datetime import datetime, timedelta
import os, csv, base64, json
import db
from styles import CSS
from auth import (
    login_required, role_required, school_admin_required,
    super_admin_required, subscription_check,
    login_user, logout_user, current_user, current_school_id,
    hash_password, verify_password, generate_temp_password,
    school_data_dir, assert_same_school,
)
from app_core import (
    app, DATA_DIR, GRAPH_DIR, PLANS, TRIAL_DAYS,
    read_all_records, write_att_record, enrolled_students,
    stats_for_student, daily_summary, students_in_section,
    get_student_section, set_student_section,
    get_profile_image, save_profile_image,
    load_meta, save_meta,
    load_sections, save_sections,
    sub_banner, att_file_for,
    face_detector,
    layout,
)


# ══════════════════════════════════════════════════════
#  AUTH — UNIFIED LOGIN / LOGOUT
# ══════════════════════════════════════════════════════

def pct_ring(pct, size=110, stroke=10):
    """SVG donut ring showing percentage."""
    r   = (size - stroke) / 2
    circ = 2 * 3.14159 * r
    dash = circ * pct / 100
    col  = "#10b981" if pct >= 75 else ("#f59e0b" if pct >= 50 else "#ef4444")
    return f"""
    <div class="ring-wrap" style="width:{size}px;height:{size}px">
      <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
        <circle cx="{size/2}" cy="{size/2}" r="{r}"
                fill="none" stroke="#1a2234" stroke-width="{stroke}"/>
        <circle cx="{size/2}" cy="{size/2}" r="{r}"
                fill="none" stroke="{col}" stroke-width="{stroke}"
                stroke-linecap="round"
                stroke-dasharray="{dash:.1f} {circ:.1f}"/>
      </svg>
      <div class="ring-val">
        <div class="ring-num" style="color:{col}">{pct}%</div>
        <div class="ring-lbl">Rate</div>
      </div>
    </div>"""

# ── UNIFIED LOGIN ─────────────────────────────────────
# Replaces /teacher/login. Single entry point for all roles.

@app.route("/login", methods=["GET","POST"])
def login():
    # already logged in
    if session.get("user_id"):
        return _role_home()

    error = ""
    nxt   = request.args.get("next", "/")

    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","").strip()
        nxt      = request.form.get("next", "/")

        user = db.user_get_by_username(username)
        if user and verify_password(password, user["password_hash"]):
            if not user["is_active"]:
                error = "Your account has been deactivated. Contact your school administrator."
            else:
                login_user(user)
                return redirect(nxt if nxt.startswith("/") else "/")
        else:
            error = "Invalid username or password."

    err_html = f'<div class="alert alert-error" style="margin-bottom:16px">{error}</div>' if error else ""

    # Check if setup has been done yet
    setup_needed = not db.super_admin_exists()
    setup_banner = ""
    if setup_needed:
        setup_banner = '''<div class="alert alert-info" style="margin-bottom:16px">
          👋 First time here? <a href="/setup" style="color:var(--blue);font-weight:700">
          Click here to set up your account →</a>
        </div>'''

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sign In — FaceNova</title>
{{CSS}}
</head>
<body>
<div class="login-wrap">
  <div class="login-card">
    <div class="login-logo">
      <div class="login-logo-icon">🧠</div>
      <div class="login-title">FaceNova AI</div>
      <div class="login-sub">Sign in to your account</div>
    </div>
    {{setup_banner}}
    {{err_html}}
    <form method="POST" action="/login" autocomplete="off">
      <input type="hidden" name="next" value="{{nxt}}">
      <!-- hidden fake fields to trick browser autofill -->
      <input type="text"     style="display:none" name="fake_user">
      <input type="password" style="display:none" name="fake_pass">
      <div class="form-group">
        <label>Username</label>
        <input type="text" name="username"
               placeholder="Enter your username"
               autocomplete="new-password"
               required autofocus
               style="ime-mode:disabled">
      </div>
      <div class="form-group">
        <label>Password</label>
        <input type="password" name="password"
               placeholder="Enter your password"
               autocomplete="new-password"
               required>
      </div>
      <button type="submit" class="btn btn-primary"
              style="width:100%;justify-content:center;padding:13px;font-size:15px;margin-top:6px">
        🔐 &nbsp;Sign In
      </button>
    </form>
    <div style="text-align:center;margin-top:18px;font-size:12px;color:var(--muted)">
      Don't have an account? Contact your School Administrator.
    </div>
    <div style="text-align:center;margin-top:10px">
      <a href="/landing" style="font-size:12px;color:var(--blue);text-decoration:none">← Back to FaceNova Home</a>
    </div>
  </div>
</div>
<script>
  // Clear any browser-autofilled values on page load
  window.addEventListener('load', function() {{{{
    document.querySelector('input[name="username"]').value = '';
    document.querySelector('input[name="password"]').value = '';
  }}}});
</script>
</body></html>"""
    return html

# Keep /teacher/login as alias for backward compatibility
@app.route("/teacher/login")
def teacher_login_redirect():
    return redirect("/login")

@app.route("/logout")
@app.route("/teacher/logout")
def logout():
    logout_user()
    return redirect("/login")

def _role_home():
    """Redirect user to their home page based on role."""
    role = session.get("role","")
    if role == "SUPER_ADMIN":
        return redirect("/superadmin")
    if role == "SCHOOL_ADMIN":
        return redirect("/teacher")
    return redirect("/")

# ── MAIN TEACHER DASHBOARD ────────────────────────────

@app.route("/teacher")
@login_required
@role_required("TEACHER","SCHOOL_ADMIN","SUPER_ADMIN")
def teacher_dashboard():
    section   = request.args.get("section","")
    sections  = load_sections()
    records   = read_all_records(section)
    students  = enrolled_students(section)
    today_str = datetime.now().strftime("%Y-%m-%d")
    teacher   = session.get("full_name", session.get("username","Teacher"))

    present_today, absent_today = daily_summary(today_str, records)
    total_students = len(students)
    pct_today = round(len(present_today) / (len(present_today)+len(absent_today)) * 100) if (present_today or absent_today) else 0
    total_records = len(records)
    all_present   = sum(1 for r in records if r["status"] == "Present")
    overall_pct   = round(all_present / total_records * 100) if total_records else 0

    # ── KPI cards
    kpi_pbar = "pbar-green" if pct_today>=75 else ("pbar-amber" if pct_today>=50 else "pbar-red")
    kpis = f"""
    <div class="stats-row" style="margin-bottom:20px">
      <div class="stat s-blue">
        <div class="stat-ico" style="background:rgba(59,130,246,0.15)">👥</div>
        <div class="stat-val">{total_students}</div>
        <div class="stat-lbl">Total Students</div>
      </div>
      <div class="stat s-green">
        <div class="stat-ico" style="background:rgba(16,185,129,0.15)">✅</div>
        <div class="stat-val">{len(present_today)}</div>
        <div class="stat-lbl">Present Today</div>
      </div>
      <div class="stat s-red">
        <div class="stat-ico" style="background:rgba(239,68,68,0.15)">❌</div>
        <div class="stat-val">{len(absent_today)}</div>
        <div class="stat-lbl">Absent Today</div>
      </div>
      <div class="stat s-purple" style="border-top:2px solid transparent;border-image:linear-gradient(90deg,var(--purple),#a78bfa) 1">
        <div class="stat-ico" style="background:rgba(139,92,246,0.15)">📊</div>
        <div class="stat-val">{overall_pct}%</div>
        <div class="stat-lbl">Overall Rate</div>
      </div>
    </div>
    <div class="card" style="padding:16px 20px;margin-bottom:20px">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
        <span style="font-size:12px;font-weight:700;color:var(--muted)">TODAY'S ATTENDANCE RATE</span>
        <span style="font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:18px">{pct_today}%</span>
      </div>
      <div class="pbar-wrap"><div class="pbar {kpi_pbar}" style="width:{pct_today}%"></div></div>
    </div>"""

    # ── Absent list with chips
    if absent_today:
        chips = "".join(f"""
        <div class="absent-chip">
          <div class="absent-chip-avatar">{r["name"][0].upper()}</div>
          <span style="font-size:13px;font-weight:600">{r["name"]}</span>
          <span style="font-size:11px;color:var(--muted)">· {r["time"]}</span>
        </div>""" for r in absent_today)
        absent_block = f'<div style="display:flex;flex-wrap:wrap;gap:4px">{chips}</div>'
    else:
        absent_block = '<div style="color:var(--muted);font-size:13px;padding:8px 0">🎉 No absentees recorded today!</div>'

    # ── Student performance table
    at_risk   = []
    below_avg = []
    good      = []
    perf_rows = ""
    for name in students:
        s = stats_for_student(name, records)
        risk_cls = "risk-high" if s["pct"]<50 else ("risk-mid" if s["pct"]<75 else "risk-ok")
        pill_cls = "pill-red" if s["pct"]<50 else ("pill-amber" if s["pct"]<75 else "pill-green")
        trend_icon = "📈" if s["streak"]>2 else ("📉" if s["pct"]<50 else "➡️")

        # last seen
        mine = [r for r in records if r["name"]==name]
        last_seen = mine[-1]["date"] if mine else "Never"

        # profile pic
        user_dir = os.path.join(DATA_DIR, name)
        if os.path.isdir(user_dir):
            imgs = [f for f in os.listdir(user_dir) if f.lower().endswith((".jpg",".jpeg",".png"))]
            avatar = f'<img src="/img/{name}/{imgs[0]}" style="width:32px;height:32px;border-radius:50%;object-fit:cover;border:1.5px solid var(--border)">' if imgs else f'<div style="width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,var(--blue),var(--purple));display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700">{name[0].upper()}</div>'
        else:
            avatar = f'<div style="width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,var(--blue),var(--purple));display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700">{name[0].upper()}</div>'

        perf_rows += f"""<tr class="{risk_cls}">
          <td>
            <div style="display:flex;align-items:center;gap:10px">
              {avatar}
              <div>
                <div style="font-weight:600;font-size:13.5px">{name}</div>
                <div style="font-size:11px;color:var(--muted)">Last seen: {last_seen}</div>
              </div>
            </div>
          </td>
          <td style="font-weight:700;color:var(--green)">{s["present"]}</td>
          <td style="font-weight:700;color:var(--red)">{s["absent"]}</td>
          <td>{s["total"]}</td>
          <td>
            <div style="display:flex;align-items:center;gap:8px">
              <div class="pbar-wrap" style="width:70px;flex-shrink:0">
                <div class="pbar {"pbar-green" if s["pct"]>=75 else ("pbar-amber" if s["pct"]>=50 else "pbar-red")}" style="width:{s["pct"]}%"></div>
              </div>
              <span class="pill {pill_cls}" style="font-size:11px">{s["pct"]}%</span>
            </div>
          </td>
          <td>{trend_icon} {"🔥"+str(s["streak"])+"d" if s["streak"]>0 else "—"}</td>
          <td><a href="/student/{name}" class="btn btn-ghost btn-sm" style="font-size:11.5px">View →</a></td>
        </tr>"""

        if s["pct"] < 50:   at_risk.append(name)
        elif s["pct"] < 75: below_avg.append(name)
        else:                good.append(name)

    # ── Risk notices
    notices = ""
    if at_risk:
        notices += f'<div class="notice notice-red">🚨 <strong>{len(at_risk)} student(s) at risk</strong> (below 50%): {", ".join(at_risk)}</div>'
    if below_avg:
        notices += f'<div class="notice notice-warn">⚠️ <strong>{len(below_avg)} student(s) need attention</strong> (50–74%): {", ".join(below_avg)}</div>'

    # ── Quick actions
    quick_actions = """
    <div class="qa-grid">
      <a href="/scan" class="qa-btn">
        <div class="qa-btn-icon" style="background:rgba(6,182,212,0.15)">🎥</div>
        <div><div style="font-weight:700">Start Scan</div><div style="font-size:11.5px;color:var(--muted)">Mark attendance now</div></div>
      </a>
      <a href="/daily" class="qa-btn">
        <div class="qa-btn-icon" style="background:rgba(59,130,246,0.15)">📋</div>
        <div><div style="font-weight:700">Today's Log</div><div style="font-size:11.5px;color:var(--muted)">Full daily record</div></div>
      </a>
      <a href="/enroll" class="qa-btn">
        <div class="qa-btn-icon" style="background:rgba(16,185,129,0.15)">➕</div>
        <div><div style="font-weight:700">Enroll Student</div><div style="font-size:11.5px;color:var(--muted)">Add new face</div></div>
      </a>
      <a href="/calendar" class="qa-btn">
        <div class="qa-btn-icon" style="background:rgba(139,92,246,0.15)">📅</div>
        <div><div style="font-weight:700">Calendar</div><div style="font-size:11.5px;color:var(--muted)">Monthly view</div></div>
      </a>
      <a href="/graph" class="qa-btn">
        <div class="qa-btn-icon" style="background:rgba(245,158,11,0.15)">📊</div>
        <div><div style="font-weight:700">Analytics</div><div style="font-size:11.5px;color:var(--muted)">Charts & trends</div></div>
      </a>
      <a href="/download" class="qa-btn">
        <div class="qa-btn-icon" style="background:rgba(16,185,129,0.12)">⬇</div>
        <div><div style="font-weight:700">Export CSV</div><div style="font-size:11.5px;color:var(--muted)">Download records</div></div>
      </a>
    </div>"""

    # ── Class performance rings (good / below / at-risk)
    rings = f"""
    <div style="display:flex;gap:20px;justify-content:space-around;padding:10px 0">
      <div style="text-align:center">
        {pct_ring(len(good)*100//total_students if total_students else 0, 90, 8)}
        <div style="font-size:12px;color:var(--green);font-weight:600;margin-top:4px">On Track</div>
        <div style="font-size:11px;color:var(--muted)">{len(good)} students</div>
      </div>
      <div style="text-align:center">
        {pct_ring(len(below_avg)*100//total_students if total_students else 0, 90, 8)}
        <div style="font-size:12px;color:var(--amber);font-weight:600;margin-top:4px">Need Help</div>
        <div style="font-size:11px;color:var(--muted)">{len(below_avg)} students</div>
      </div>
      <div style="text-align:center">
        {pct_ring(len(at_risk)*100//total_students if total_students else 0, 90, 8)}
        <div style="font-size:12px;color:var(--red);font-weight:600;margin-top:4px">At Risk</div>
        <div style="font-size:11px;color:var(--muted)">{len(at_risk)} students</div>
      </div>
    </div>"""

    # section tab bar for teacher dashboard
    tab_all  = "sec-tab sec-tab-all" + (" sec-tab-active" if not section else "")
    sec_tabs = f'<a href="/teacher" class="{tab_all}">🌐 All Sections</a>'
    for s in sections:
        active = " sec-tab-active" if s==section else ""
        sec_tabs += f'<a href="/teacher?section={s}" class="sec-tab{active}">{s}</a>'

    sec_label = f"Section {section}" if section else "All Sections"

    content = f"""
    <div class="td-hero">
      <h1>Welcome back, {teacher.title()} 👋</h1>
      <p>Class overview for <strong>{today_str}</strong> · {sec_label} · FaceNova AI</p>
      <div style="margin-top:16px;display:flex;gap:10px">
        <a href="/scan" class="btn btn-cyan">🎥 Start Scan</a>
        <a href="/teacher/logout" class="btn btn-ghost" style="font-size:12.5px">Sign Out</a>
      </div>
    </div>
    <div class="sec-tabs">{sec_tabs}</div>

    {notices}
    {kpis}

    <div class="grid-2" style="margin-bottom:20px">
      <!-- Absent today -->
      <div class="card">
        <div class="sec-head" style="margin-bottom:14px">
          <div>
            <div class="sec-title">❌ Absent Today</div>
            <div class="sec-sub">{len(absent_today)} student(s) not marked present</div>
          </div>
          <span class="pill pill-red">{len(absent_today)}</span>
        </div>
        {absent_block}
      </div>

      <!-- Class performance rings -->
      <div class="card">
        <div class="sec-head" style="margin-bottom:14px">
          <div>
            <div class="sec-title">🎯 Class Performance</div>
            <div class="sec-sub">Overall attendance health</div>
          </div>
        </div>
        {rings}
      </div>
    </div>

    <!-- Full student table -->
    <div class="card" style="margin-bottom:20px">
      <div class="sec-head" style="margin-bottom:16px">
        <div>
          <div class="sec-title">👥 All Students — Attendance Overview</div>
          <div class="sec-sub">Click "View →" for full individual history</div>
        </div>
        <a href="/students" class="btn btn-ghost btn-sm">All Profiles</a>
      </div>
      <div style="display:flex;gap:12px;margin-bottom:14px;font-size:12px">
        <span style="display:flex;align-items:center;gap:5px"><span style="width:10px;height:10px;border-radius:2px;background:var(--green);display:inline-block"></span>≥75% Good</span>
        <span style="display:flex;align-items:center;gap:5px"><span style="width:10px;height:10px;border-radius:2px;background:var(--amber);display:inline-block"></span>50–74% Warning</span>
        <span style="display:flex;align-items:center;gap:5px"><span style="width:10px;height:10px;border-radius:2px;background:var(--red);display:inline-block"></span>&lt;50% At Risk</span>
      </div>
      <div class="tbl-wrap">
        <table>
          <thead>
            <tr>
              <th>Student</th><th>Present</th><th>Absent</th>
              <th>Total</th><th>Rate</th><th>Trend</th><th>Action</th>
            </tr>
          </thead>
          <tbody>{perf_rows or '<tr><td colspan="7" style="text-align:center;color:var(--muted);padding:24px">No students enrolled yet</td></tr>'}</tbody>
        </table>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="card">
      <div class="sec-head" style="margin-bottom:16px">
        <div>
          <div class="sec-title">⚡ Quick Actions</div>
          <div class="sec-sub">Jump to any feature instantly</div>
        </div>
      </div>
      {quick_actions}
    </div>
    """
    return layout("Teacher Dashboard", content, "teacher")


# ══════════════════════════════════════════════════════
#  ADMIN
# ══════════════════════════════════════════════════════

@app.route("/admin")
@login_required
@school_admin_required
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








# ══════════════════════════════════════════════════════
#  SUBSCRIPTION ROUTES (db-backed, per-school)
# ══════════════════════════════════════════════════════

@app.route("/upgrade")
@login_required
def upgrade_page():
    sid  = current_school_id()
    sub  = db.sub_get(sid) if sid else None
    role = session.get("role","")
    locked = request.args.get("locked","")

    locked_banner = ""
    if locked:
        locked_banner = '<div class="alert alert-warn" style="margin-bottom:20px">🔒 <strong>Premium Feature</strong> — Upgrade to access this feature.</div>'

    # Status card
    status_card = ""
    if sub:
        if sub["is_trial"]:
            status_card = f"""<div style="background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.2);border-radius:14px;padding:16px 20px;margin-bottom:22px;display:flex;align-items:center;gap:14px">
              <span style="font-size:28px">🎉</span>
              <div>
                <div style="font-weight:700;color:var(--blue)">Free Trial Active — {sub['days_left']} day{"s" if sub['days_left']!=1 else ""} remaining</div>
                <div style="font-size:13px;color:var(--text2)">Trial started {sub.get('trial_start','—')} · Ends {sub.get('trial_end','—')}</div>
              </div>
            </div>"""
        elif sub["is_active"]:
            status_card = f"""<div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);border-radius:14px;padding:16px 20px;margin-bottom:22px;display:flex;align-items:center;gap:14px">
              <span style="font-size:28px">✅</span>
              <div>
                <div style="font-weight:700;color:var(--green-l)">{sub['plan_name'].replace('_',' ').title()} Active</div>
                <div style="font-size:13px;color:var(--text2)">Valid until {sub.get('subscription_end','—')}</div>
              </div>
            </div>"""
        elif sub["is_expired"]:
            status_card = """<div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);border-radius:14px;padding:16px 20px;margin-bottom:22px;display:flex;align-items:center;gap:14px">
              <span style="font-size:28px">🔒</span>
              <div>
                <div style="font-weight:700;color:var(--red-l)">Subscription Expired</div>
                <div style="font-size:13px;color:var(--text2)">Your data is safe. Choose a plan below to restore access.</div>
              </div>
            </div>"""

    # Plan definitions
    plan_meta = [
        ("FREE_TRIAL",    "🆓", "var(--muted)",   "",             30,  ["Basic face attendance","Up to 50 students","2 teachers","Basic dashboard"]),
        ("BASIC",         "💙", "var(--blue)",     "",             180, ["Everything in Free Trial","Up to 200 students","5 teachers","Reports","CSV export","Sections"]),
        ("PROFESSIONAL",  "💜", "var(--purple)",   "Most Popular", 365, ["Everything in Basic","Up to 1,000 students","20 teachers","Advanced analytics","Priority support"]),
        ("ENTERPRISE",    "🌟", "var(--amber)",    "Best Value",   1825,["Everything in Professional","Unlimited students & teachers","API access","Custom branding","Phone support"]),
    ]

    plan_cards = ""
    for key, icon, color, badge, days, features in plan_meta:
        badge_html = f'<div class="plan-badge">{badge}</div>' if badge else ""
        popular    = "plan-popular" if badge == "Most Popular" else ""
        feat_html  = "".join(f"<li>{f}</li>" for f in features)
        plan_cards += f"""
        <div class="plan-card {popular}" style="border-top:2px solid {color}">
          {badge_html}
          <div class="plan-icon">{icon}</div>
          <div class="plan-name" style="color:{color}">{key.replace('_',' ').title()}</div>
          <ul class="plan-features">{feat_html}</ul>
          <form method="POST" action="/upgrade/activate">
            <input type="hidden" name="plan" value="{key}">
            <input type="hidden" name="days" value="{days}">
            <button type="submit" class="btn btn-primary"
                    style="width:100%;justify-content:center;padding:13px;font-size:14px">
              🚀 Start Plan
            </button>
          </form>
        </div>"""

    content = f"""
    {locked_banner}
    <div class="upgrade-hero">
      <h1 style="font-size:clamp(22px,5vw,36px)">FaceNova Premium</h1>
      <p>Unlock unlimited students, advanced analytics, multi-teacher management, and priority support.</p>
    </div>
    {status_card}
    <div class="alert alert-info" style="margin-bottom:20px">
      ⚠️ <strong>Demo Mode:</strong> No real payment is processed. Plans activate instantly for testing.
    </div>
    <div class="plan-grid">{plan_cards}</div>
    """
    return layout("⭐ Subscription Plans", content, "upgrade")


@app.route("/upgrade/activate", methods=["POST"])
@login_required
@role_required("SCHOOL_ADMIN","SUPER_ADMIN")
def upgrade_activate():
    sid      = current_school_id()
    plan_key = request.form.get("plan","BASIC")
    days     = int(request.form.get("days","365"))
    if sid:
        db.sub_activate(sid, plan_key, days)
    return redirect("/upgrade")


@app.route("/school/subscription")
@login_required
@school_admin_required
def school_subscription():
    sid  = current_school_id()
    sub  = db.sub_get(sid)
    hist = db.sub_history_get(sid)
    feat = sub["features"] if sub else {}

    hist_rows = "".join(f"""<tr>
      <td>{h['created_at'][:16]}</td>
      <td style="font-weight:600">{h['event']}</td>
      <td>{(h.get('plan_name') or '—').replace('_',' ').title()}</td>
      <td style="color:var(--text2)">{h.get('note','')}</td>
    </tr>""" for h in hist) or '<tr><td colspan="4" style="text-align:center;color:var(--muted);padding:20px">No history</td></tr>'

    feat_rows = "".join(f"""<tr>
      <td>{k.replace('_',' ').title()}</td>
      <td>{"✅" if v is True else ("❌" if v is False else f"<strong>{v}</strong>")}</td>
    </tr>""" for k,v in feat.items() if k != "label")

    content = f"""
    <div class="sec-head" style="margin-bottom:20px">
      <div><div class="sec-title" style="font-size:20px">📋 Subscription Details</div></div>
      <a href="/upgrade" class="btn btn-primary">Manage Plans</a>
    </div>
    <div class="grid-2" style="align-items:start;margin-bottom:20px">
      <div class="card">
        <div class="sec-title" style="margin-bottom:14px">Current Status</div>
        <table style="font-size:13.5px"><tbody>
          <tr><td style="color:var(--muted);padding:8px 0;border:none;width:140px">Status</td>
              <td style="border:none"><span class="pill {'pill-green' if sub and sub['is_active'] else ('pill-blue' if sub and sub['is_trial'] else 'pill-red')}">{sub['status'] if sub else '—'}</span></td></tr>
          <tr><td style="color:var(--muted);padding:8px 0;border:none">Plan</td>
              <td style="border:none;font-weight:600">{(sub.get('plan_name') or '—').replace('_',' ').title() if sub else '—'}</td></tr>
          <tr><td style="color:var(--muted);padding:8px 0;border:none">Trial Start</td>
              <td style="border:none">{sub.get('trial_start','—') if sub else '—'}</td></tr>
          <tr><td style="color:var(--muted);padding:8px 0;border:none">Trial End</td>
              <td style="border:none">{sub.get('trial_end','—') if sub else '—'}</td></tr>
          <tr><td style="color:var(--muted);padding:8px 0;border:none">Sub Start</td>
              <td style="border:none">{sub.get('subscription_start','—') if sub else '—'}</td></tr>
          <tr><td style="color:var(--muted);padding:8px 0;border:none">Sub End</td>
              <td style="border:none">{sub.get('subscription_end','—') if sub else '—'}</td></tr>
          <tr><td style="color:var(--muted);padding:8px 0;border:none">Max Students</td>
              <td style="border:none;font-weight:600">{feat.get('max_students','—')}</td></tr>
          <tr><td style="color:var(--muted);padding:8px 0;border:none">Max Teachers</td>
              <td style="border:none;font-weight:600">{feat.get('max_teachers','—')}</td></tr>
        </tbody></table>
      </div>
      <div class="card">
        <div class="sec-title" style="margin-bottom:14px">Plan Features</div>
        <div class="tbl-wrap"><table>
          <thead><tr><th>Feature</th><th>Status</th></tr></thead>
          <tbody>{feat_rows}</tbody>
        </table></div>
      </div>
    </div>
    <div class="card">
      <div class="sec-title" style="margin-bottom:14px">Subscription History</div>
      <div class="tbl-wrap"><table>
        <thead><tr><th>Date</th><th>Event</th><th>Plan</th><th>Note</th></tr></thead>
        <tbody>{hist_rows}</tbody>
      </table></div>
    </div>"""
    return layout("Subscription", content, "upgrade")


# ══════════════════════════════════════════════════════
#  TEACHER MANAGEMENT (SCHOOL_ADMIN)
# ══════════════════════════════════════════════════════

@app.route("/manage/teachers")
@login_required
@school_admin_required
def manage_teachers():
    sid      = current_school_id()
    teachers = db.users_by_school(sid, role="TEACHER")
    sections = load_sections()

    rows = ""
    for t in teachers:
        secs = json.loads(t.get("assigned_sections","[]") or "[]")
        status_pill = '<span class="pill pill-green">Active</span>' if t["is_active"] else '<span class="pill pill-red">Inactive</span>'
        rows += f"""<tr>
          <td><strong>{t['full_name'] or t['username']}</strong><br>
              <span style="font-size:11px;color:var(--muted)">{t['teacher_id'] or '—'}</span></td>
          <td>{t['username']}</td>
          <td>{t['email'] or '—'}</td>
          <td>{', '.join(secs) if secs else '—'}</td>
          <td>{status_pill}</td>
          <td>{t.get('last_login','—') or '—'}</td>
          <td>
            <a href="/manage/teachers/{t['id']}/edit" class="btn btn-ghost btn-xs">Edit</a>
            <a href="/manage/teachers/{t['id']}/toggle"
               class="btn {'btn-red' if t['is_active'] else 'btn-green'} btn-xs"
               onclick="return confirm('{"Deactivate" if t["is_active"] else "Activate"} this teacher?')">
               {"Deactivate" if t['is_active'] else "Activate"}
            </a>
          </td>
        </tr>"""

    content = f"""
    <div class="sec-head" style="margin-bottom:20px">
      <div><div class="sec-title" style="font-size:20px">👨‍🏫 Teacher Management</div>
      <div class="sec-sub">Create and manage teacher accounts for your school</div></div>
      <a href="/manage/teachers/new" class="btn btn-primary">+ Add Teacher</a>
    </div>
    <div class="card">
      <div class="tbl-wrap"><table>
        <thead><tr><th>Name</th><th>Username</th><th>Email</th><th>Sections</th><th>Status</th><th>Last Login</th><th>Actions</th></tr></thead>
        <tbody>{rows or '<tr><td colspan="7" style="text-align:center;color:var(--muted);padding:24px">No teachers yet — add your first teacher above.</td></tr>'}</tbody>
      </table></div>
    </div>"""
    return layout("Teachers", content, "admin")


@app.route("/manage/teachers/new", methods=["GET","POST"])
@login_required
@school_admin_required
def teacher_new():
    sid      = current_school_id()
    sections = load_sections()
    msg      = ""

    if request.method == "POST":
        full_name  = request.form.get("full_name","").strip()
        username   = request.form.get("username","").strip()
        email      = request.form.get("email","").strip()
        teacher_id = request.form.get("teacher_id","").strip()
        password   = request.form.get("password","").strip()
        sel_secs   = request.form.getlist("sections")

        if not all([full_name, username, password]):
            msg = '<div class="alert alert-error">Full name, username and password are required.</div>'
        else:
            ok, err = db.user_create(
                school_id=sid, role="TEACHER",
                username=username, password_hash=hash_password(password),
                full_name=full_name, email=email, teacher_id=teacher_id,
                sections=sel_secs,
            )
            if ok:
                return redirect("/manage/teachers?created=1")
            else:
                msg = f'<div class="alert alert-error">❌ {err} — username may already exist.</div>'

    sec_checkboxes = "".join(f"""
    <label style="display:flex;align-items:center;gap:8px;margin-bottom:8px;cursor:pointer">
      <input type="checkbox" name="sections" value="{s}"
             style="width:16px;height:16px;accent-color:var(--blue)">
      <span style="font-size:13.5px">{s}</span>
    </label>""" for s in sections)

    created = '<div class="alert alert-success" style="margin-bottom:16px">✅ Teacher created successfully.</div>' if request.args.get("created") else ""

    content = f"""
    <div style="margin-bottom:16px">
      <a href="/manage/teachers" class="btn btn-ghost btn-sm">← Back to Teachers</a>
    </div>
    {created}
    <div class="grid-2" style="align-items:start">
      <div class="card">
        <div class="sec-title" style="margin-bottom:18px">➕ Add New Teacher</div>
        {msg}
        <form method="POST">
          <div class="form-group">
            <label>Full Name *</label>
            <input type="text" name="full_name" placeholder="e.g. Mrs. Priya Sharma" required>
          </div>
          <div class="form-group">
            <label>Username * (used to log in)</label>
            <input type="text" name="username" placeholder="e.g. priya.sharma" required>
          </div>
          <div class="form-group">
            <label>Email</label>
            <input type="text" name="email" placeholder="teacher@school.edu">
          </div>
          <div class="form-group">
            <label>Teacher ID</label>
            <input type="text" name="teacher_id" placeholder="e.g. TCH-001">
          </div>
          <div class="form-group">
            <label>Password * (share this with the teacher)</label>
            <input type="password" name="password" placeholder="Min 8 characters" required>
          </div>
          <div class="form-group">
            <label>Assign to Sections</label>
            <div style="background:rgba(255,255,255,0.03);border:1px solid var(--border);border-radius:9px;padding:12px">
              {sec_checkboxes or '<span style="color:var(--muted);font-size:13px">No sections configured. <a href="/sections/manage" style="color:var(--blue)">Add sections first</a></span>'}
            </div>
          </div>
          <button type="submit" class="btn btn-primary" style="width:100%;justify-content:center;padding:13px">
            ✅ Create Teacher Account
          </button>
        </form>
      </div>
      <div class="card">
        <div class="sec-title" style="margin-bottom:14px">📋 Instructions</div>
        <div style="display:flex;flex-direction:column;gap:14px;font-size:13.5px">
          <div style="display:flex;gap:10px"><div style="background:rgba(59,130,246,0.15);color:var(--blue);border-radius:8px;width:28px;height:28px;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0">1</div>
            <div><strong>Choose a unique username</strong><br><span style="color:var(--text2)">Teachers log in using this — cannot be changed later</span></div></div>
          <div style="display:flex;gap:10px"><div style="background:rgba(6,182,212,0.15);color:var(--cyan);border-radius:8px;width:28px;height:28px;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0">2</div>
            <div><strong>Set a strong password</strong><br><span style="color:var(--text2)">Share it securely — password is hashed and never visible again</span></div></div>
          <div style="display:flex;gap:10px"><div style="background:rgba(16,185,129,0.15);color:var(--green);border-radius:8px;width:28px;height:28px;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0">3</div>
            <div><strong>Assign sections</strong><br><span style="color:var(--text2)">Teachers only see students in their assigned sections</span></div></div>
        </div>
        <div class="alert alert-warn" style="margin-top:20px;font-size:12.5px">
          ⚠️ Passwords are hashed with PBKDF2-SHA256. You cannot retrieve it after creation. Use "Reset Password" if needed.
        </div>
      </div>
    </div>"""
    return layout("Add Teacher", content, "admin")


@app.route("/manage/teachers/<int:tid>/edit", methods=["GET","POST"])
@login_required
@school_admin_required
def teacher_edit(tid):
    sid     = current_school_id()
    teacher = db.user_get_by_id(tid)
    if not teacher or teacher["school_id"] != sid or teacher["role"] != "TEACHER":
        return redirect("/manage/teachers")

    sections = load_sections()
    msg      = ""
    assigned = json.loads(teacher.get("assigned_sections","[]") or "[]")

    if request.method == "POST":
        action = request.form.get("action","update")

        if action == "update":
            full_name  = request.form.get("full_name","").strip()
            email      = request.form.get("email","").strip()
            teacher_id = request.form.get("teacher_id","").strip()
            sel_secs   = request.form.getlist("sections")
            import json as _json
            db.user_update(tid, full_name=full_name, email=email,
                           teacher_id=teacher_id,
                           assigned_sections=_json.dumps(sel_secs))
            msg = '<div class="alert alert-success">✅ Teacher updated successfully.</div>'
            teacher  = db.user_get_by_id(tid)
            assigned = _json.loads(teacher.get("assigned_sections","[]") or "[]")

        elif action == "reset_password":
            new_pass = generate_temp_password()
            db.user_update(tid, password_hash=hash_password(new_pass))
            msg = f'<div class="alert alert-success">✅ Password reset. New temporary password: <strong style="font-family:monospace;font-size:15px;color:var(--amber-l)">{new_pass}</strong><br><span style="font-size:12px">Share this with the teacher and ask them to remember it. It will not be shown again.</span></div>'

    sec_checkboxes = "".join(f"""
    <label style="display:flex;align-items:center;gap:8px;margin-bottom:8px;cursor:pointer">
      <input type="checkbox" name="sections" value="{s}"
             {"checked" if s in assigned else ""}
             style="width:16px;height:16px;accent-color:var(--blue)">
      <span style="font-size:13.5px">{s}</span>
    </label>""" for s in sections)

    content = f"""
    <div style="margin-bottom:16px">
      <a href="/manage/teachers" class="btn btn-ghost btn-sm">← Back to Teachers</a>
    </div>
    {msg}
    <div class="grid-2" style="align-items:start">
      <div class="card">
        <div class="sec-title" style="margin-bottom:18px">✏️ Edit Teacher — {teacher['full_name'] or teacher['username']}</div>
        <form method="POST">
          <input type="hidden" name="action" value="update">
          <div class="form-group">
            <label>Username (cannot change)</label>
            <input type="text" value="{teacher['username']}" disabled style="opacity:0.5">
          </div>
          <div class="form-group">
            <label>Full Name</label>
            <input type="text" name="full_name" value="{teacher['full_name'] or ''}" required>
          </div>
          <div class="form-group">
            <label>Email</label>
            <input type="text" name="email" value="{teacher['email'] or ''}">
          </div>
          <div class="form-group">
            <label>Teacher ID</label>
            <input type="text" name="teacher_id" value="{teacher['teacher_id'] or ''}">
          </div>
          <div class="form-group">
            <label>Assigned Sections</label>
            <div style="background:rgba(255,255,255,0.03);border:1px solid var(--border);border-radius:9px;padding:12px">
              {sec_checkboxes or '<span style="color:var(--muted);font-size:13px">No sections configured.</span>'}
            </div>
          </div>
          <button type="submit" class="btn btn-primary" style="width:100%;justify-content:center;padding:12px">
            💾 Save Changes
          </button>
        </form>
      </div>
      <div class="card">
        <div class="sec-title" style="margin-bottom:14px">🔐 Reset Password</div>
        <div style="color:var(--text2);font-size:13.5px;margin-bottom:16px">
          Generate a new temporary password for this teacher. The password is shown once — save it before leaving this page.
        </div>
        <form method="POST" onsubmit="return confirm('Reset password for {teacher['full_name'] or teacher['username']}?')">
          <input type="hidden" name="action" value="reset_password">
          <button type="submit" class="btn btn-ghost" style="width:100%;justify-content:center">
            🔄 Generate Temp Password
          </button>
        </form>
        <div style="margin-top:20px;padding-top:16px;border-top:1px solid var(--border)">
          <div style="font-size:12px;font-weight:700;color:var(--muted);margin-bottom:10px">ACCOUNT INFO</div>
          <div style="font-size:13px;color:var(--text2)">
            Status: <strong>{"Active" if teacher["is_active"] else "Inactive"}</strong><br>
            Created: <strong>{(teacher.get("created_at") or "—")[:10]}</strong><br>
            Last Login: <strong>{(teacher.get("last_login") or "Never")[:16]}</strong>
          </div>
        </div>
      </div>
    </div>"""
    return layout(f"Edit Teacher", content, "admin")


@app.route("/manage/teachers/<int:tid>/toggle")
@login_required
@school_admin_required
def teacher_toggle(tid):
    sid     = current_school_id()
    teacher = db.user_get_by_id(tid)
    if teacher and teacher["school_id"] == sid and teacher["role"] == "TEACHER":
        new_status = 0 if teacher["is_active"] else 1
        db.user_update(tid, is_active=new_status)
    return redirect("/manage/teachers")


# ══════════════════════════════════════════════════════
#  SUPER ADMIN PANEL
# ══════════════════════════════════════════════════════

@app.route("/superadmin")
@super_admin_required
def superadmin_panel():
    schools = db.school_list()
    # count users per school
    school_rows = ""
    for s in schools:
        sub  = db.sub_get(s["id"])
        teachers = db.users_by_school(s["id"], "TEACHER")
        admins   = db.users_by_school(s["id"], "SCHOOL_ADMIN")
        stat     = sub["status"] if sub else "—"
        pill     = "pill-green" if stat=="ACTIVE" else ("pill-blue" if stat=="TRIAL" else "pill-red")
        school_rows += f"""<tr>
          <td><strong>{s['name']}</strong><br>
              <span style="font-size:11px;color:var(--muted)">{s['id']}</span></td>
          <td>{s['email'] or '—'}</td>
          <td>{len(admins)}</td>
          <td>{len(teachers)}</td>
          <td><span class="pill {pill}">{stat}</span></td>
          <td>{sub.get('plan_name','—').replace('_',' ').title() if sub else '—'}</td>
          <td>
            <a href="/superadmin/school/{s['id']}" class="btn btn-ghost btn-xs">Manage</a>
          </td>
        </tr>"""

    content = f"""
    <div class="td-hero">
      <h1>👑 Super Admin Panel</h1>
      <p>FaceNova SaaS Platform Management · {len(schools)} school{"s" if len(schools)!=1 else ""} registered</p>
    </div>
    <div class="stats-row" style="margin-bottom:22px">
      <div class="stat s-blue">
        <div class="stat-ico" style="background:rgba(59,130,246,0.15)">🏫</div>
        <div class="stat-val">{len(schools)}</div>
        <div class="stat-lbl">Schools</div>
      </div>
      <div class="stat s-green">
        <div class="stat-ico" style="background:rgba(16,185,129,0.15)">✅</div>
        <div class="stat-val">{sum(1 for s in schools if db.sub_get(s['id']) and db.sub_get(s['id'])['is_active'])}</div>
        <div class="stat-lbl">Active Plans</div>
      </div>
      <div class="stat s-amber">
        <div class="stat-ico" style="background:rgba(245,158,11,0.15)">🎉</div>
        <div class="stat-val">{sum(1 for s in schools if db.sub_get(s['id']) and db.sub_get(s['id'])['is_trial'])}</div>
        <div class="stat-lbl">On Trial</div>
      </div>
      <div class="stat s-red">
        <div class="stat-ico" style="background:rgba(239,68,68,0.15)">⚠️</div>
        <div class="stat-val">{sum(1 for s in schools if db.sub_get(s['id']) and db.sub_get(s['id'])['is_expired'])}</div>
        <div class="stat-lbl">Expired</div>
      </div>
    </div>
    <div class="card" style="margin-bottom:20px">
      <div class="sec-head" style="margin-bottom:16px">
        <div class="sec-title">🏫 All Schools</div>
        <a href="/superadmin/school/new" class="btn btn-primary">+ Register School</a>
      </div>
      <div class="tbl-wrap"><table>
        <thead><tr><th>School</th><th>Email</th><th>Admins</th><th>Teachers</th><th>Sub Status</th><th>Plan</th><th></th></tr></thead>
        <tbody>{school_rows or '<tr><td colspan="7" style="text-align:center;color:var(--muted);padding:24px">No schools registered yet.</td></tr>'}</tbody>
      </table></div>
    </div>"""
    return layout("Super Admin", content, "admin")


@app.route("/superadmin/school/new", methods=["GET","POST"])
@super_admin_required
def superadmin_school_new():
    msg = ""
    if request.method == "POST":
        school_id   = request.form.get("school_id","").strip().lower().replace(" ","-")
        school_name = request.form.get("school_name","").strip()
        admin_user  = request.form.get("admin_username","").strip()
        admin_pass  = request.form.get("admin_password","").strip()
        email       = request.form.get("email","").strip()

        if not all([school_id, school_name, admin_user, admin_pass]):
            msg = '<div class="alert alert-error">All fields are required.</div>'
        else:
            ok, err = db.school_create(school_id, school_name, email=email)
            if not ok:
                msg = f'<div class="alert alert-error">❌ {err}</div>'
            else:
                ok2, err2 = db.user_create(
                    school_id=school_id, role="SCHOOL_ADMIN",
                    username=admin_user,
                    password_hash=hash_password(admin_pass),
                    full_name=f"{school_name} Administrator",
                    email=email,
                )
                if ok2:
                    return redirect(f"/superadmin/school/{school_id}?created=1")
                else:
                    msg = f'<div class="alert alert-error">School created but admin creation failed: {err2}</div>'

    content = f"""
    <div style="margin-bottom:16px">
      <a href="/superadmin" class="btn btn-ghost btn-sm">← Back to Admin Panel</a>
    </div>
    {msg}
    <div class="grid-2" style="align-items:start">
      <div class="card">
        <div class="sec-title" style="margin-bottom:18px">🏫 Register New School</div>
        <form method="POST">
          <div style="font-size:11px;font-weight:700;color:var(--muted);letter-spacing:1px;margin-bottom:12px">SCHOOL INFO</div>
          <div class="form-group">
            <label>School ID (unique slug) *</label>
            <input type="text" name="school_id" placeholder="e.g. delhi-public-school" required>
          </div>
          <div class="form-group">
            <label>School Name *</label>
            <input type="text" name="school_name" placeholder="e.g. Delhi Public School" required>
          </div>
          <div class="form-group">
            <label>Email</label>
            <input type="text" name="email" placeholder="admin@school.edu">
          </div>
          <div style="font-size:11px;font-weight:700;color:var(--muted);letter-spacing:1px;margin:16px 0 12px;padding-top:16px;border-top:1px solid var(--border)">SCHOOL ADMIN ACCOUNT</div>
          <div class="form-group">
            <label>Admin Username *</label>
            <input type="text" name="admin_username" placeholder="e.g. dps.admin" required>
          </div>
          <div class="form-group">
            <label>Admin Password *</label>
            <input type="password" name="admin_password" placeholder="Strong password" required>
          </div>
          <button type="submit" class="btn btn-primary" style="width:100%;justify-content:center;padding:13px">
            🏫 Register School + Create Admin
          </button>
        </form>
      </div>
      <div class="card">
        <div class="sec-title" style="margin-bottom:14px">ℹ️ What happens next</div>
        <div style="display:flex;flex-direction:column;gap:14px;font-size:13.5px;color:var(--text2)">
          <div>✅ School is created with a unique ID</div>
          <div>✅ A 10-day FREE TRIAL subscription starts automatically</div>
          <div>✅ SCHOOL_ADMIN account is created with the credentials you provide</div>
          <div>✅ Admin can log in immediately at <strong style="color:var(--text)">/login</strong></div>
          <div>✅ Admin can create teacher accounts from their dashboard</div>
          <div>✅ Data for this school is stored separately from all other schools</div>
        </div>
      </div>
    </div>"""
    return layout("Register School", content, "admin")


@app.route("/superadmin/school/<school_id>")
@super_admin_required
def superadmin_school_detail(school_id):
    school   = db.school_get(school_id)
    if not school:
        return redirect("/superadmin")
    sub      = db.sub_get(school_id)
    hist     = db.sub_history_get(school_id)
    admins   = db.users_by_school(school_id, "SCHOOL_ADMIN")
    teachers = db.users_by_school(school_id, "TEACHER")
    created  = request.args.get("created","")

    created_banner = '<div class="alert alert-success" style="margin-bottom:16px">✅ School registered successfully! 10-day trial activated.</div>' if created else ""

    hist_rows = "".join(f"""<tr>
      <td>{h['created_at'][:16]}</td>
      <td style="font-weight:600">{h['event']}</td>
      <td>{(h.get('plan_name') or '—').replace('_',' ').title()}</td>
      <td style="color:var(--text2)">{h.get('note','')}</td>
    </tr>""" for h in hist)

    teacher_rows = "".join(f"""<tr>
      <td><strong>{t['full_name'] or t['username']}</strong></td>
      <td>{t['username']}</td>
      <td><span class="pill {'pill-green' if t['is_active'] else 'pill-red'}">{'Active' if t['is_active'] else 'Inactive'}</span></td>
    </tr>""" for t in teachers)

    content = f"""
    <div style="margin-bottom:16px">
      <a href="/superadmin" class="btn btn-ghost btn-sm">← All Schools</a>
    </div>
    {created_banner}
    <div class="hero" style="margin-bottom:20px">
      <div>
        <h1>🏫 {school['name']}</h1>
        <p>ID: <strong>{school['id']}</strong> · Email: {school['email'] or '—'}</p>
      </div>
    </div>
    <div class="grid-2" style="align-items:start;margin-bottom:20px">
      <div class="card">
        <div class="sec-title" style="margin-bottom:14px">📋 Subscription</div>
        <table style="font-size:13.5px"><tbody>
          <tr><td style="color:var(--muted);border:none;padding:7px 0;width:120px">Status</td>
              <td style="border:none"><span class="pill {'pill-green' if sub and sub['is_active'] else ('pill-blue' if sub and sub['is_trial'] else 'pill-red')}">{sub['status'] if sub else '—'}</span></td></tr>
          <tr><td style="color:var(--muted);border:none;padding:7px 0">Plan</td>
              <td style="border:none;font-weight:600">{(sub.get('plan_name') or '—').replace('_',' ').title() if sub else '—'}</td></tr>
          <tr><td style="color:var(--muted);border:none;padding:7px 0">Trial End</td>
              <td style="border:none">{sub.get('trial_end','—') if sub else '—'}</td></tr>
          <tr><td style="color:var(--muted);border:none;padding:7px 0">Sub End</td>
              <td style="border:none">{sub.get('subscription_end','—') if sub else '—'}</td></tr>
        </tbody></table>
        <div style="margin-top:14px;display:flex;gap:8px;flex-wrap:wrap">
          <form method="POST" action="/superadmin/school/{school_id}/extend" style="display:inline">
            <input type="hidden" name="days" value="10">
            <button type="submit" class="btn btn-cyan btn-sm">+10 Day Trial</button>
          </form>
          <form method="POST" action="/superadmin/school/{school_id}/activate" style="display:inline">
            <input type="hidden" name="plan" value="PROFESSIONAL">
            <input type="hidden" name="days" value="365">
            <button type="submit" class="btn btn-green btn-sm">Activate Pro</button>
          </form>
        </div>
      </div>
      <div class="card">
        <div class="sec-title" style="margin-bottom:14px">👥 Users</div>
        <div style="margin-bottom:10px;font-size:13px;color:var(--text2)">
          School Admins: <strong style="color:var(--text)">{len(admins)}</strong> &nbsp;·&nbsp;
          Teachers: <strong style="color:var(--text)">{len(teachers)}</strong>
        </div>
        <div class="tbl-wrap"><table>
          <thead><tr><th>Name</th><th>Username</th><th>Status</th></tr></thead>
          <tbody>{teacher_rows or '<tr><td colspan="3" style="text-align:center;color:var(--muted);padding:14px">No teachers yet</td></tr>'}</tbody>
        </table></div>
      </div>
    </div>
    <div class="card">
      <div class="sec-title" style="margin-bottom:14px">📜 Subscription History</div>
      <div class="tbl-wrap"><table>
        <thead><tr><th>Date</th><th>Event</th><th>Plan</th><th>Note</th></tr></thead>
        <tbody>{hist_rows or '<tr><td colspan="4" style="text-align:center;color:var(--muted);padding:16px">No history</td></tr>'}</tbody>
      </table></div>
    </div>"""
    return layout(school['name'], content, "admin")


@app.route("/superadmin/school/<school_id>/extend", methods=["POST"])
@super_admin_required
def superadmin_extend_trial(school_id):
    days = int(request.form.get("days","10"))
    db.sub_extend_trial(school_id, days)
    return redirect(f"/superadmin/school/{school_id}")


@app.route("/superadmin/school/<school_id>/activate", methods=["POST"])
@super_admin_required
def superadmin_activate_plan(school_id):
    plan = request.form.get("plan","PROFESSIONAL")
    days = int(request.form.get("days","365"))
    db.sub_activate(school_id, plan, days)
    return redirect(f"/superadmin/school/{school_id}")


# ══════════════════════════════════════════════════════
#  RAZORPAY PAYMENT
# ══════════════════════════════════════════════════════
import os as _os, json as _json, hashlib as _hashlib, hmac as _hmac

RAZORPAY_KEY_ID     = _os.environ.get("RAZORPAY_KEY_ID","")
RAZORPAY_KEY_SECRET = _os.environ.get("RAZORPAY_KEY_SECRET","")

RAZORPAY_PLANS = {
    "BASIC":        {"amount":19900,  "days":30,   "label":"Basic — ₹199/month"},
    "PROFESSIONAL": {"amount":149900, "days":365,  "label":"Professional — ₹1,499/year"},
    "ENTERPRISE":   {"amount":399900, "days":1825, "label":"Enterprise — ₹3,999/5 years"},
}

@app.route("/pay/<plan_key>")
@login_required
@role_required("SCHOOL_ADMIN","SUPER_ADMIN")
def pay_page(plan_key):
    if plan_key not in RAZORPAY_PLANS:
        return redirect("/upgrade")
    plan = RAZORPAY_PLANS[plan_key]
    sid  = current_school_id()

    if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
        content = f"""
        <div style="max-width:480px;margin:40px auto">
          <div class="card" style="text-align:center;padding:36px">
            <div style="font-size:48px;margin-bottom:14px">⚠️</div>
            <div class="sec-title" style="margin-bottom:10px">Razorpay Not Configured</div>
            <div style="color:var(--text2);font-size:13.5px;line-height:1.7;margin-bottom:20px">
              Add your Razorpay API keys to your environment variables on Render:<br><br>
              <code style="background:rgba(255,255,255,0.05);padding:10px 16px;border-radius:8px;display:block;text-align:left;font-size:12px">
                RAZORPAY_KEY_ID = rzp_live_XXXXX<br>
                RAZORPAY_KEY_SECRET = your_secret
              </code><br>
              Get free keys at <strong>razorpay.com</strong> → Settings → API Keys
            </div>
            <form method="POST" action="/upgrade/activate">
              <input type="hidden" name="plan" value="{plan_key}">
              <input type="hidden" name="days" value="{plan['days']}">
              <button type="submit" class="btn btn-ghost" style="width:100%;justify-content:center">
                🧪 Activate Demo (No Payment)
              </button>
            </form>
            <a href="/upgrade" style="display:block;margin-top:12px;font-size:13px;color:var(--muted)">← Back</a>
          </div>
        </div>"""
        return layout("Payment", content, "upgrade")

    import urllib.request as _ur, base64 as _b64
    order_data = _json.dumps({"amount":plan["amount"],"currency":"INR",
                               "receipt":f"fn_{sid}_{plan_key}"}).encode()
    creds = _b64.b64encode(f"{RAZORPAY_KEY_ID}:{RAZORPAY_KEY_SECRET}".encode()).decode()
    req   = _ur.Request("https://api.razorpay.com/v1/orders", data=order_data,
                         headers={"Content-Type":"application/json",
                                  "Authorization":f"Basic {creds}"}, method="POST")
    try:
        with _ur.urlopen(req, timeout=10) as resp:
            order = _json.loads(resp.read())
    except Exception as e:
        content = f'<div class="alert alert-error">❌ Payment order failed: {e}</div><a href="/upgrade" class="btn btn-ghost">← Back</a>'
        return layout("Error", content, "upgrade")

    school = db.school_get(sid) or {}
    content = f"""
    <div style="max-width:520px;margin:30px auto">
      <div class="card" style="padding:32px;text-align:center">
        <div style="font-size:44px;margin-bottom:10px">💳</div>
        <div class="sec-title" style="font-size:20px;margin-bottom:6px">{plan['label']}</div>
        <div style="color:var(--text2);font-size:13px;margin-bottom:20px">Secure payment via Razorpay</div>
        <button id="rzp-btn" class="btn btn-primary" style="width:100%;justify-content:center;padding:14px;font-size:15px">
          🔐 Pay ₹{plan['amount']//100} Securely
        </button>
        <div style="margin-top:10px;font-size:12px;color:var(--muted)">UPI · Cards · Net Banking · Wallets</div>
        <a href="/upgrade" style="display:block;margin-top:14px;font-size:13px;color:var(--muted)">← Cancel</a>
      </div>
    </div>
    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
    <script>
    var options={{key:"{RAZORPAY_KEY_ID}",amount:"{order['amount']}",currency:"INR",
      name:"FaceNova AI",description:"{plan['label']}",order_id:"{order['id']}",
      prefill:{{name:"{school.get('name','')}",email:"{school.get('email','')}"}},
      theme:{{color:"#2563eb"}},
      handler:function(r){{
        fetch('/pay/verify',{{method:'POST',headers:{{'Content-Type':'application/json'}},
          body:JSON.stringify({{razorpay_order_id:r.razorpay_order_id,
            razorpay_payment_id:r.razorpay_payment_id,
            razorpay_signature:r.razorpay_signature,
            plan:'{plan_key}',days:{plan['days']}}})}})
        .then(r=>r.json()).then(d=>{{if(d.success)window.location='/pay/success';
          else alert('Verification failed: '+d.error);}});
      }}}};
    document.getElementById('rzp-btn').onclick=function(){{
      this.disabled=true;new Razorpay(options).open();}};
    </script>"""
    return layout("Checkout", content, "upgrade")


@app.route("/pay/verify", methods=["POST"])
@login_required
def pay_verify():
    try:
        data       = _json.loads(request.data)
        order_id   = data.get("razorpay_order_id","")
        payment_id = data.get("razorpay_payment_id","")
        signature  = data.get("razorpay_signature","")
        plan_key   = data.get("plan","")
        days       = int(data.get("days",30))
        expected   = _hmac.new(RAZORPAY_KEY_SECRET.encode(),
                               f"{order_id}|{payment_id}".encode(),
                               _hashlib.sha256).hexdigest()
        if not _hmac.compare_digest(expected, signature):
            return app.response_class(_json.dumps({"success":False,"error":"Invalid signature"}),
                                      mimetype="application/json", status=400)
        sid = current_school_id()
        if sid and plan_key in RAZORPAY_PLANS:
            db.sub_activate(sid, plan_key, days)
        return app.response_class(_json.dumps({"success":True}), mimetype="application/json")
    except Exception as e:
        return app.response_class(_json.dumps({"success":False,"error":str(e)}),
                                  mimetype="application/json", status=500)


@app.route("/pay/success")
@login_required
def pay_success():
    content = """
    <div style="max-width:480px;margin:60px auto;text-align:center">
      <div class="card" style="padding:44px">
        <div style="font-size:72px;margin-bottom:18px">🎉</div>
        <div class="sec-title" style="font-size:24px;margin-bottom:10px">Payment Successful!</div>
        <div style="color:var(--text2);font-size:14px;line-height:1.7;margin-bottom:26px">
          Your subscription is now <strong style="color:var(--green-l)">Active</strong>.<br>All premium features unlocked.
        </div>
        <a href="/" class="btn btn-primary" style="width:100%;justify-content:center;padding:14px">🏠 Go to Dashboard</a>
        <a href="/school/subscription" style="display:block;margin-top:12px;font-size:13px;color:var(--text2)">View subscription details →</a>
      </div>
    </div>"""
    return layout("Payment Successful", content, "upgrade")


# ══════════════════════════════════════════════════════
#  FIRST-RUN SETUP WIZARD
# ══════════════════════════════════════════════════════

@app.route("/setup", methods=["GET","POST"])
def setup_page():
    if db.super_admin_exists():
        return redirect("/login")
    msg = ""
    if request.method == "POST":
        su_user  = request.form.get("su_username","").strip()
        su_pass  = request.form.get("su_password","").strip()
        su_email = request.form.get("su_email","").strip()
        if not su_user or not su_pass:
            msg = '<div class="alert alert-error">Username and password required.</div>'
        elif len(su_pass) < 8:
            msg = '<div class="alert alert-error">Password must be at least 8 characters.</div>'
        else:
            ok, err = db.user_create(school_id=None, role="SUPER_ADMIN",
                                     username=su_user, password_hash=hash_password(su_pass),
                                     full_name="Super Administrator", email=su_email)
            if ok:
                return redirect("/setup/school")
            else:
                msg = f'<div class="alert alert-error">❌ {err}</div>'
    html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>FaceNova Setup</title>{CSS}</head><body>
<div class="login-wrap" style="flex-direction:column;padding:20px">
<div style="max-width:480px;width:100%">
<div style="display:flex;gap:4px;margin-bottom:24px">
  <div style="flex:1;height:3px;border-radius:3px;background:linear-gradient(90deg,var(--blue),var(--cyan))"></div>
  <div style="flex:1;height:3px;border-radius:3px;background:rgba(255,255,255,0.1)"></div>
  <div style="flex:1;height:3px;border-radius:3px;background:rgba(255,255,255,0.1)"></div>
</div>
<div class="login-card">
<div class="login-logo">
  <div class="login-logo-icon">🧠</div>
  <div class="login-title">Welcome to FaceNova</div>
  <div class="login-sub">Step 1 of 3 — Create Super Admin</div>
</div>
{msg}
<form method="POST">
  <div class="form-group"><label>Username *</label>
    <input type="text" name="su_username" placeholder="e.g. superadmin" required autofocus></div>
  <div class="form-group"><label>Password * (min 8 chars)</label>
    <input type="password" name="su_password" placeholder="Strong password" required></div>
  <div class="form-group"><label>Email (optional)</label>
    <input type="text" name="su_email" placeholder="admin@school.com"></div>
  <button type="submit" class="btn btn-primary" style="width:100%;justify-content:center;padding:13px">
    Continue →
  </button>
</form>
<div style="margin-top:16px;padding:12px;background:rgba(255,255,255,0.03);border:1px solid var(--border);border-radius:9px;font-size:12px;color:var(--muted)">
  ⚠️ Save your password — it cannot be recovered.
</div>
</div></div></div></body></html>"""
    return html


@app.route("/setup/school", methods=["GET","POST"])
def setup_school():
    if not db.super_admin_exists():
        return redirect("/setup")
    msg = ""
    if request.method == "POST":
        school_id   = request.form.get("school_id","").strip().lower().replace(" ","-")
        school_name = request.form.get("school_name","").strip()
        admin_user  = request.form.get("admin_username","").strip()
        admin_pass  = request.form.get("admin_password","").strip()
        email       = request.form.get("email","").strip()
        if not all([school_id, school_name, admin_user, admin_pass]):
            msg = '<div class="alert alert-error">All fields required.</div>'
        else:
            ok, err = db.school_create(school_id, school_name, email=email)
            if ok:
                ok2, err2 = db.user_create(school_id=school_id, role="SCHOOL_ADMIN",
                                           username=admin_user, password_hash=hash_password(admin_pass),
                                           full_name=f"{school_name} Admin", email=email)
                if ok2:
                    return redirect("/setup/done")
                msg = f'<div class="alert alert-error">School created but admin failed: {err2}</div>'
            else:
                msg = f'<div class="alert alert-error">❌ {err}</div>'
    html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>FaceNova Setup</title>{CSS}</head><body>
<div class="login-wrap" style="flex-direction:column;padding:20px">
<div style="max-width:480px;width:100%">
<div style="display:flex;gap:4px;margin-bottom:24px">
  <div style="flex:1;height:3px;border-radius:3px;background:linear-gradient(90deg,var(--blue),var(--cyan))"></div>
  <div style="flex:1;height:3px;border-radius:3px;background:linear-gradient(90deg,var(--blue),var(--cyan))"></div>
  <div style="flex:1;height:3px;border-radius:3px;background:rgba(255,255,255,0.1)"></div>
</div>
<div class="login-card">
<div class="login-logo">
  <div class="login-logo-icon">🏫</div>
  <div class="login-title">Register Your School</div>
  <div class="login-sub">Step 2 of 3 — School + Admin account</div>
</div>
{msg}
<form method="POST">
  <div class="form-group"><label>School Name *</label>
    <input type="text" name="school_name" placeholder="e.g. Delhi Public School" required autofocus></div>
  <div class="form-group"><label>School ID * (no spaces)</label>
    <input type="text" name="school_id" placeholder="e.g. dps-delhi" required></div>
  <div class="form-group"><label>Email</label>
    <input type="text" name="email" placeholder="info@school.edu"></div>
  <div style="border-top:1px solid var(--border);margin:14px 0;padding-top:14px">
    <div style="font-size:11px;font-weight:700;color:var(--muted);margin-bottom:12px;letter-spacing:1px">ADMIN LOGIN</div>
    <div class="form-group"><label>Admin Username *</label>
      <input type="text" name="admin_username" placeholder="e.g. school.admin" required></div>
    <div class="form-group"><label>Admin Password *</label>
      <input type="password" name="admin_password" placeholder="Strong password" required></div>
  </div>
  <button type="submit" class="btn btn-primary" style="width:100%;justify-content:center;padding:13px">
    Continue →
  </button>
</form>
</div></div></div></body></html>"""
    return html


@app.route("/setup/done")
def setup_done():
    if not db.super_admin_exists():
        return redirect("/setup")
    html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Setup Complete — FaceNova</title>{CSS}</head><body>
<div class="login-wrap" style="flex-direction:column;padding:20px">
<div style="max-width:480px;width:100%">
<div style="display:flex;gap:4px;margin-bottom:24px">
  <div style="flex:1;height:3px;border-radius:3px;background:linear-gradient(90deg,var(--blue),var(--cyan))"></div>
  <div style="flex:1;height:3px;border-radius:3px;background:linear-gradient(90deg,var(--blue),var(--cyan))"></div>
  <div style="flex:1;height:3px;border-radius:3px;background:linear-gradient(90deg,var(--blue),var(--cyan))"></div>
</div>
<div class="login-card" style="text-align:center">
  <div style="font-size:64px;margin-bottom:16px">🎉</div>
  <div class="login-title" style="margin-bottom:8px">Setup Complete!</div>
  <div style="color:var(--text2);font-size:13.5px;line-height:1.7;margin-bottom:22px">
    FaceNova is ready!<br>
    A <strong style="color:var(--blue)">10-day free trial</strong> has started.<br>
    Sign in with your School Admin account.
  </div>
  <a href="/login" class="btn btn-primary" style="width:100%;justify-content:center;padding:14px;display:flex">
    🔐 Sign In Now
  </a>
  <div style="margin-top:16px;padding:12px;background:rgba(255,255,255,0.03);border:1px solid var(--border);border-radius:9px;font-size:12px;color:var(--muted);text-align:left">
    After signing in:<br>
    1. <strong style="color:var(--text)">Sections</strong> → add class sections<br>
    2. <strong style="color:var(--text)">Teachers</strong> → create teacher accounts<br>
    3. <strong style="color:var(--text)">Enroll</strong> → add students with face photos<br>
    4. <strong style="color:var(--text)">Scan</strong> → start attendance!
  </div>
</div></div></div></body></html>"""
    return html



# ══════════════════════════════════════════════════════
#  PUBLIC LANDING PAGE  (premium redesign)
# ══════════════════════════════════════════════════════

@app.route("/home")
@app.route("/landing")
def landing():
    import db as _db, os as _os
    setup_done = _db.super_admin_exists()
    cta_url    = "/login" if setup_done else "/setup"

    # WhatsApp number from env var — never hardcoded in source
    _wa_num = _os.environ.get("WHATSAPP_NUMBER", "").strip()
    _wa_msg = "Hi%2C%20I%20want%20to%20know%20more%20about%20FaceNova%20AI"
    wa_url  = f"https://wa.me/91{_wa_num}?text={_wa_msg}" if _wa_num else "#contact"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>FaceNova AI — Face Recognition Attendance for Schools</title>
<meta name="description" content="Replace paper registers with instant AI face recognition. Built for Indian schools, colleges and coaching centres.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#020810;--s1:#060e1c;--s2:#091426;--card:#0c1a30;
  --b:#2563eb;--bl:#3b82f6;--c:#06b6d4;--g:#10b981;
  --gl:#34d399;--a:#f59e0b;--r:#ef4444;
  --t:#eef2ff;--t2:#94a3b8;--m:#475569;
  --brd:rgba(255,255,255,0.07);--brd2:rgba(255,255,255,0.11);
}}
html{{scroll-behavior:smooth}}
body{{font-family:'Inter',sans-serif;background:var(--bg);color:var(--t);line-height:1.6;overflow-x:hidden}}
::-webkit-scrollbar{{width:3px}}
::-webkit-scrollbar-thumb{{background:rgba(59,130,246,0.3);border-radius:3px}}
img{{display:block;max-width:100%}}

/* ── NAVBAR ───────────────────────────────────── */
.nav{{
  position:fixed;top:0;left:0;right:0;z-index:200;
  height:60px;padding:0 clamp(16px,5%,80px);
  display:flex;align-items:center;justify-content:space-between;
  background:rgba(2,8,16,0.8);
  backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);
  border-bottom:1px solid var(--brd);
  transition:box-shadow .3s;
}}
.nav.scrolled{{box-shadow:0 4px 32px rgba(0,0,0,0.5)}}
.logo{{display:flex;align-items:center;gap:10px;text-decoration:none}}
.logo-mark{{
  width:34px;height:34px;border-radius:9px;font-size:17px;
  background:linear-gradient(135deg,var(--b),var(--c));
  display:flex;align-items:center;justify-content:center;
  box-shadow:0 0 14px rgba(37,99,235,0.5);
}}
.logo-name{{font-family:'Space Grotesk',sans-serif;font-size:17px;font-weight:700;color:var(--t)}}
.logo-name em{{color:var(--c);font-style:normal}}
.nav-links{{display:flex;align-items:center;gap:26px}}
.nav-links a{{color:var(--t2);font-size:13.5px;font-weight:500;text-decoration:none;transition:color .15s}}
.nav-links a:hover{{color:var(--t)}}
.nav-btns{{display:flex;align-items:center;gap:10px}}
.btn-nav-ghost{{
  padding:7px 16px;border-radius:7px;font-size:13px;font-weight:600;
  color:var(--t2);text-decoration:none;border:1px solid var(--brd2);
  background:rgba(255,255,255,0.04);transition:all .15s;
}}
.btn-nav-ghost:hover{{color:var(--t);background:rgba(255,255,255,0.08)}}
.btn-nav-cta{{
  padding:7px 18px;border-radius:7px;font-size:13px;font-weight:700;
  color:#fff;text-decoration:none;
  background:linear-gradient(135deg,var(--b),#1d4ed8);
  box-shadow:0 3px 12px rgba(37,99,235,0.35);transition:all .15s;
}}
.btn-nav-cta:hover{{transform:translateY(-1px);box-shadow:0 5px 18px rgba(37,99,235,0.5)}}
.nav-ham{{display:none;flex-direction:column;gap:5px;cursor:pointer;padding:4px}}
.nav-ham span{{width:22px;height:2px;background:var(--t2);border-radius:2px;transition:all .2s}}
.mob-menu{{
  display:none;position:fixed;top:60px;left:0;right:0;z-index:190;
  background:rgba(6,14,28,0.98);backdrop-filter:blur(20px);
  border-bottom:1px solid var(--brd);padding:16px 5% 24px;
  flex-direction:column;gap:4px;
}}
.mob-menu a{{
  display:block;padding:12px 16px;border-radius:9px;
  color:var(--t2);text-decoration:none;font-size:15px;font-weight:500;
  transition:all .15s;
}}
.mob-menu a:hover{{background:rgba(255,255,255,0.05);color:var(--t)}}
.mob-menu .mob-cta{{
  margin-top:12px;
  background:linear-gradient(135deg,var(--b),#1d4ed8);
  color:#fff!important;text-align:center;font-weight:700;
  box-shadow:0 4px 14px rgba(37,99,235,0.35);
}}

/* ── HERO ─────────────────────────────────────── */
.hero{{
  min-height:100vh;padding:80px clamp(16px,5%,80px) 60px;
  display:flex;align-items:center;position:relative;overflow:hidden;
}}
.hero-glow{{
  position:absolute;inset:0;pointer-events:none;
  background:
    radial-gradient(ellipse 70% 60% at 65% 45%,rgba(37,99,235,0.11) 0%,transparent 65%),
    radial-gradient(ellipse 40% 35% at 20% 75%,rgba(6,182,212,0.07) 0%,transparent 55%);
}}
.hero-grid{{
  position:absolute;inset:0;pointer-events:none;
  background-image:
    linear-gradient(rgba(255,255,255,0.022) 1px,transparent 1px),
    linear-gradient(90deg,rgba(255,255,255,0.022) 1px,transparent 1px);
  background-size:56px 56px;
  mask-image:radial-gradient(ellipse 90% 80% at 65% 40%,black 20%,transparent 80%);
}}
.hero-inner{{
  position:relative;z-index:1;max-width:1200px;margin:0 auto;width:100%;
  display:grid;grid-template-columns:1fr 1fr;gap:56px;align-items:center;
}}
.hero-eyebrow{{
  display:inline-flex;align-items:center;gap:7px;
  background:rgba(37,99,235,0.1);border:1px solid rgba(37,99,235,0.22);
  border-radius:20px;padding:5px 13px;
  font-size:12px;font-weight:600;color:var(--bl);margin-bottom:20px;
}}
.hero-eyebrow-dot{{
  width:6px;height:6px;border-radius:50%;background:var(--bl);
  box-shadow:0 0 6px var(--bl);animation:pulse-dot 2s infinite;
}}
@keyframes pulse-dot{{0%,100%{{opacity:1}}50%{{opacity:0.35}}}}
.hero-h1{{
  font-family:'Space Grotesk',sans-serif;
  font-size:clamp(34px,4.5vw,60px);
  font-weight:800;line-height:1.09;letter-spacing:-2px;
  margin-bottom:20px;
}}
.hero-h1 .grad{{
  background:linear-gradient(90deg,var(--bl) 0%,var(--c) 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}}
.hero-sub{{
  font-size:16px;color:var(--t2);line-height:1.75;
  max-width:460px;margin-bottom:32px;font-weight:400;
}}
.hero-actions{{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:28px}}
.btn-cta{{
  padding:13px 26px;border-radius:9px;font-size:14.5px;font-weight:700;
  text-decoration:none;display:inline-flex;align-items:center;gap:8px;
  transition:all .2s;position:relative;overflow:hidden;
}}
.btn-cta-primary{{
  background:linear-gradient(135deg,var(--b),#1d4ed8);color:#fff;
  box-shadow:0 4px 18px rgba(37,99,235,0.38);
}}
.btn-cta-primary:hover{{transform:translateY(-2px);box-shadow:0 8px 26px rgba(37,99,235,0.55)}}
.btn-cta-outline{{
  background:rgba(255,255,255,0.05);color:var(--t);
  border:1px solid var(--brd2);
}}
.btn-cta-outline:hover{{background:rgba(255,255,255,0.09)}}
.hero-note{{font-size:12px;color:var(--m);display:flex;align-items:center;gap:6px}}
.hero-note::before{{content:'✓';color:var(--g);font-weight:700}}

/* ── PHONE MOCKUP ─────────────────────────────── */
.mockup-wrap{{display:flex;justify-content:center;align-items:center;position:relative;padding:20px}}
.phone{{
  width:210px;height:370px;
  background:linear-gradient(180deg,#0c1e3a,#060e1c);
  border-radius:38px;border:1.5px solid rgba(255,255,255,0.13);
  box-shadow:0 0 0 8px rgba(255,255,255,0.03),0 40px 80px rgba(0,0,0,0.7),0 0 60px rgba(37,99,235,0.15);
  padding:18px 12px 14px;
  display:flex;flex-direction:column;align-items:center;overflow:hidden;
  position:relative;z-index:2;
}}
.phone-notch{{width:52px;height:5px;background:rgba(255,255,255,0.12);border-radius:3px;margin-bottom:14px;flex-shrink:0}}
.phone-screen{{
  width:100%;flex:1;border-radius:18px;
  background:linear-gradient(160deg,#0d2040,#091424);
  border:1px solid rgba(255,255,255,0.07);
  position:relative;overflow:hidden;
  display:flex;flex-direction:column;align-items:center;justify-content:center;
}}
/* scan corners */
.sc{{position:absolute;width:20px;height:20px}}
.sc-tl{{top:10px;left:10px;border-top:2px solid var(--c);border-left:2px solid var(--c);border-radius:3px 0 0 0}}
.sc-tr{{top:10px;right:10px;border-top:2px solid var(--c);border-right:2px solid var(--c);border-radius:0 3px 0 0}}
.sc-bl{{bottom:10px;left:10px;border-bottom:2px solid var(--c);border-left:2px solid var(--c);border-radius:0 0 0 3px}}
.sc-br{{bottom:10px;right:10px;border-bottom:2px solid var(--c);border-right:2px solid var(--c);border-radius:0 0 3px 0}}
.scan-beam{{
  position:absolute;left:0;right:0;height:1.5px;
  background:linear-gradient(90deg,transparent 0%,rgba(6,182,212,0.9) 50%,transparent 100%);
  box-shadow:0 0 12px rgba(6,182,212,0.6);
  animation:beam 2.8s ease-in-out infinite;
}}
@keyframes beam{{0%{{top:12%;opacity:0}}5%{{opacity:1}}95%{{opacity:1}}100%{{top:88%;opacity:0}}}}
.detect-live{{
  position:absolute;top:10px;right:34px;
  width:7px;height:7px;border-radius:50%;background:var(--g);
  box-shadow:0 0 7px var(--g);animation:pulse-dot 1.4s infinite;
}}
.face-icon{{font-size:44px;filter:drop-shadow(0 0 16px rgba(37,99,235,0.4));margin-bottom:6px}}
.face-ring{{
  position:absolute;
  border-radius:50%;border:1.5px solid rgba(6,182,212,0.3);
  animation:ring-expand 2.8s ease-out infinite;
}}
.face-ring:nth-child(1){{width:90px;height:90px;top:calc(50% - 45px - 16px);left:calc(50% - 45px)}}
.face-ring:nth-child(2){{width:110px;height:110px;top:calc(50% - 55px - 16px);left:calc(50% - 55px);animation-delay:.6s}}
@keyframes ring-expand{{0%{{transform:scale(0.9);opacity:0.7}}100%{{transform:scale(1.15);opacity:0}}}}
.phone-bar{{
  flex-shrink:0;width:100%;margin-top:10px;
  background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.22);
  border-radius:9px;padding:7px 10px;
  display:flex;align-items:center;gap:8px;
}}
.phone-bar-icon{{font-size:14px}}
.phone-bar-text{{font-size:10px;font-weight:600;color:var(--gl)}}
/* floating pills */
.fp{{
  position:absolute;z-index:3;
  background:rgba(10,22,42,0.92);border:1px solid var(--brd2);
  border-radius:11px;padding:9px 13px;
  backdrop-filter:blur(12px);white-space:nowrap;
}}
.fp-tl{{top:14%;left:-66px;animation:fp-float 3.2s ease-in-out infinite}}
.fp-br{{bottom:18%;right:-70px;animation:fp-float 3.8s ease-in-out infinite .6s}}
.fp-b{{bottom:4%;left:50%;transform:translateX(-50%);animation:fp-float 4s ease-in-out infinite 1s}}
@keyframes fp-float{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-7px)}}}}
.fp-b{{transform:translateX(-50%)!important}}
.fp-val{{font-family:'Space Grotesk',sans-serif;font-size:15px;font-weight:700;color:var(--t)}}
.fp-lbl{{font-size:10px;color:var(--m)}}
.fp-icon{{font-size:15px;margin-bottom:2px}}

/* ── SECTION BASE ─────────────────────────────── */
.section{{padding:80px clamp(16px,5%,80px)}}
.section-inner{{max-width:1100px;margin:0 auto}}
.eyebrow{{font-size:11.5px;font-weight:700;letter-spacing:1.2px;
  text-transform:uppercase;color:var(--c);margin-bottom:12px;display:block}}
.section-h2{{
  font-family:'Space Grotesk',sans-serif;
  font-size:clamp(26px,3.5vw,42px);font-weight:800;
  letter-spacing:-1px;line-height:1.15;margin-bottom:14px;
}}
.section-lead{{font-size:16px;color:var(--t2);max-width:520px;line-height:1.75;margin-bottom:44px}}

/* ── BEFORE / AFTER ───────────────────────────── */
.ba-grid{{display:grid;grid-template-columns:1fr auto 1fr;gap:20px;align-items:stretch}}
.ba-card{{background:var(--card);border-radius:18px;padding:28px}}
.ba-old{{border:1px solid rgba(239,68,68,0.18)}}
.ba-new{{border:1px solid rgba(16,185,129,0.22)}}
.ba-head{{display:flex;align-items:center;gap:10px;margin-bottom:20px}}
.ba-tag{{font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px}}
.ba-tag-old{{background:rgba(239,68,68,0.12);color:#f87171}}
.ba-tag-new{{background:rgba(16,185,129,0.12);color:var(--gl)}}
.ba-item{{display:flex;align-items:flex-start;gap:9px;margin-bottom:11px;font-size:13.5px;color:var(--t2)}}
.ba-item b{{flex-shrink:0;font-size:15px;margin-top:1px}}
.ba-arrow{{
  display:flex;align-items:center;justify-content:center;
  width:40px;flex-shrink:0;
}}
.ba-arrow-inner{{
  width:36px;height:36px;border-radius:50%;
  background:linear-gradient(135deg,var(--b),var(--c));
  display:flex;align-items:center;justify-content:center;
  font-size:16px;box-shadow:0 0 18px rgba(37,99,235,0.35);
  flex-shrink:0;
}}

/* ── HOW IT WORKS ─────────────────────────────── */
.steps{{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}}
.step{{
  background:var(--card);border:1px solid var(--brd);
  border-radius:18px;padding:26px 20px;
  transition:border-color .2s,transform .2s;
  position:relative;overflow:hidden;
}}
.step::after{{
  content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,var(--b),var(--c));
  opacity:0;transition:opacity .2s;
}}
.step:hover{{transform:translateY(-4px);border-color:rgba(37,99,235,0.28)}}
.step:hover::after{{opacity:1}}
.step-num{{font-size:10.5px;font-weight:700;letter-spacing:1.5px;color:var(--m);margin-bottom:12px}}
.step-ico{{
  width:48px;height:48px;border-radius:13px;
  display:flex;align-items:center;justify-content:center;font-size:22px;margin-bottom:14px;
}}
.step-h{{font-family:'Space Grotesk',sans-serif;font-size:16px;font-weight:700;margin-bottom:7px}}
.step-p{{font-size:13px;color:var(--t2);line-height:1.65}}

/* ── FEATURES ─────────────────────────────────── */
.feat-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}}
.feat{{
  background:var(--card);border:1px solid var(--brd);
  border-radius:16px;padding:22px;transition:all .2s;
}}
.feat:hover{{border-color:rgba(37,99,235,0.25);background:#0e2040}}
.feat-ico{{
  width:42px;height:42px;border-radius:11px;
  display:flex;align-items:center;justify-content:center;font-size:19px;margin-bottom:13px;
}}
.feat-h{{font-family:'Space Grotesk',sans-serif;font-size:15px;font-weight:700;margin-bottom:6px}}
.feat-p{{font-size:13px;color:var(--t2);line-height:1.6}}

/* ── DASHBOARD PREVIEW ───────────────────────── */
.dash-wrap{{
  border-radius:20px;overflow:hidden;
  border:1px solid var(--brd2);
  box-shadow:0 0 80px rgba(37,99,235,0.12),0 40px 100px rgba(0,0,0,0.6);
  background:var(--s2);
}}
.dash-bar{{
  background:#060e1c;padding:10px 16px;
  display:flex;align-items:center;gap:8px;
  border-bottom:1px solid var(--brd);
}}
.dash-dot{{width:10px;height:10px;border-radius:50%}}
.dash-dot-r{{background:#ef4444}}
.dash-dot-y{{background:#f59e0b}}
.dash-dot-g{{background:#10b981}}
.dash-url{{
  flex:1;background:rgba(255,255,255,0.04);border:1px solid var(--brd);
  border-radius:5px;padding:4px 10px;font-size:11px;color:var(--m);
  display:flex;align-items:center;gap:6px;
}}
.dash-body{{padding:20px;display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}
.dash-stat{{
  background:var(--card);border-radius:12px;padding:16px;
  border:1px solid var(--brd);
}}
.dash-stat-v{{
  font-family:'Space Grotesk',sans-serif;font-size:22px;font-weight:700;
  margin-bottom:4px;
}}
.dash-stat-l{{font-size:11px;color:var(--t2)}}
.dash-chart{{
  grid-column:span 4;background:var(--card);border-radius:12px;
  padding:16px;border:1px solid var(--brd);height:80px;
  display:flex;align-items:flex-end;gap:6px;overflow:hidden;
}}
.dash-bar-item{{
  flex:1;border-radius:4px 4px 0 0;
  background:linear-gradient(180deg,rgba(37,99,235,0.7),rgba(37,99,235,0.2));
  min-width:0;transition:all .3s;
}}
.dash-bar-item:hover{{background:linear-gradient(180deg,var(--bl),rgba(37,99,235,0.4))}}

/* ── PRICING ──────────────────────────────────── */
.price-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}}
.pc{{
  background:var(--card);border:1px solid var(--brd);
  border-radius:20px;padding:26px 20px;
  display:flex;flex-direction:column;position:relative;
  transition:all .2s;
}}
.pc:hover{{transform:translateY(-4px);box-shadow:0 16px 40px rgba(0,0,0,0.4)}}
.pc-popular{{
  border-color:rgba(37,99,235,0.4);
  background:linear-gradient(180deg,rgba(37,99,235,0.07),var(--card));
}}
.pc-badge{{
  position:absolute;top:-11px;left:50%;transform:translateX(-50%);
  background:linear-gradient(135deg,var(--b),var(--c));
  color:#fff;font-size:10.5px;font-weight:700;
  padding:3px 12px;border-radius:20px;white-space:nowrap;
}}
.pc-icon{{font-size:28px;margin-bottom:10px}}
.pc-name{{font-family:'Space Grotesk',sans-serif;font-size:15px;font-weight:700;margin-bottom:14px}}
.pc-amount{{
  font-family:'Space Grotesk',sans-serif;
  font-size:clamp(22px,3vw,32px);font-weight:800;line-height:1;margin-bottom:3px;
}}
.pc-period{{font-size:11.5px;color:var(--m);margin-bottom:18px}}
.pc-feats{{list-style:none;margin-bottom:22px;flex:1;display:flex;flex-direction:column;gap:7px}}
.pc-feats li{{font-size:12.5px;color:var(--t2);display:flex;align-items:center;gap:7px}}
.pc-feats li::before{{content:'✓';color:var(--g);font-weight:700;flex-shrink:0}}
.pc-btn{{
  display:block;padding:11px;border-radius:9px;
  font-size:13px;font-weight:700;text-decoration:none;
  text-align:center;transition:all .15s;
  background:rgba(255,255,255,0.05);color:var(--t);border:1px solid var(--brd2);
}}
.pc-btn:hover{{background:rgba(255,255,255,0.09)}}
.pc-btn-p{{
  background:linear-gradient(135deg,var(--b),#1d4ed8);color:#fff;border:none;
  box-shadow:0 4px 14px rgba(37,99,235,0.3);
}}
.pc-btn-p:hover{{box-shadow:0 6px 20px rgba(37,99,235,0.5);transform:translateY(-1px)}}
.pc-note{{font-size:10.5px;color:var(--m);text-align:center;margin-top:9px}}

/* ── CTA BANNER ───────────────────────────────── */
.cta-banner{{
  background:linear-gradient(135deg,rgba(37,99,235,0.14),rgba(6,182,212,0.08));
  border:1px solid rgba(37,99,235,0.2);
  border-radius:24px;padding:56px 40px;text-align:center;
  position:relative;overflow:hidden;
}}
.cta-banner::before{{
  content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse 60% 60% at 50% 50%,rgba(37,99,235,0.1),transparent);
}}
.cta-banner-h{{
  font-family:'Space Grotesk',sans-serif;
  font-size:clamp(26px,3.5vw,42px);font-weight:800;
  letter-spacing:-1px;margin-bottom:14px;position:relative;z-index:1;
}}
.cta-banner-sub{{font-size:15px;color:var(--t2);margin-bottom:28px;position:relative;z-index:1;line-height:1.7}}
.cta-actions{{display:flex;gap:12px;justify-content:center;flex-wrap:wrap;position:relative;z-index:1}}
.cta-note{{font-size:12px;color:var(--m);margin-top:14px;position:relative;z-index:1}}

/* ── FOOTER ───────────────────────────────────── */
.footer{{
  padding:32px clamp(16px,5%,80px);
  border-top:1px solid var(--brd);
  display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:14px;
}}
.footer-r{{display:flex;gap:22px}}
.footer-r a{{font-size:13px;color:var(--m);text-decoration:none;transition:color .15s}}
.footer-r a:hover{{color:var(--t2)}}
.footer-copy{{font-size:12px;color:var(--m)}}

/* ── SCROLL REVEAL ────────────────────────────── */
.rv{{opacity:0;transform:translateY(20px);transition:opacity .5s ease,transform .5s ease}}
.rv.in{{opacity:1;transform:none}}
.rv-d1{{transition-delay:.08s}}
.rv-d2{{transition-delay:.16s}}
.rv-d3{{transition-delay:.24s}}

/* ── RESPONSIVE ───────────────────────────────── */
@media(max-width:900px){{
  .hero-inner{{grid-template-columns:1fr;gap:36px;text-align:center}}
  .hero-sub,.hero-note{{margin-left:auto;margin-right:auto}}
  .hero-actions{{justify-content:center}}
  .phone-wrap-order{{order:-1}}
  .fp-tl,.fp-br,.fp-b{{display:none}}
  .ba-grid{{grid-template-columns:1fr;gap:12px}}
  .ba-arrow{{display:none}}
  .steps{{grid-template-columns:1fr 1fr}}
  .feat-grid{{grid-template-columns:1fr 1fr}}
  .price-grid{{grid-template-columns:1fr 1fr}}
  .nav-links{{display:none}}
  .nav-btns .btn-nav-ghost{{display:none}}
  .nav-ham{{display:flex}}
  .dash-body{{grid-template-columns:1fr 1fr}}
  .dash-chart{{grid-column:span 2}}
}}
@media(max-width:560px){{
  .section{{padding:52px 16px}}
  .steps{{grid-template-columns:1fr}}
  .feat-grid{{grid-template-columns:1fr}}
  .price-grid{{grid-template-columns:1fr}}
  .cta-banner{{padding:36px 20px}}
  .footer{{flex-direction:column;align-items:flex-start}}
  .dash-body{{grid-template-columns:1fr 1fr}}
}}
</style>
</head>
<body>

<!-- NAV -->
<nav class="nav" id="nav">
  <a href="/landing" class="logo">
    <div class="logo-mark">🧠</div>
    <div class="logo-name">Face<em>Nova</em></div>
  </a>
  <div class="nav-links">
    <a href="#how">How It Works</a>
    <a href="#features">Features</a>
    <a href="#pricing">Pricing</a>
  </div>
  <div class="nav-btns">
    <a href="/login" class="btn-nav-ghost">Sign In</a>
    <a href="/setup" id="nav-cta" class="btn-nav-cta">Start Free Trial</a>
  </div>
  <div class="nav-ham" onclick="toggleMenu()" id="ham">
    <span></span><span></span><span></span>
  </div>
</nav>

<!-- MOBILE MENU -->
<div class="mob-menu" id="mob-menu">
  <a href="#how"      onclick="closeMenu()">How It Works</a>
  <a href="#features" onclick="closeMenu()">Features</a>
  <a href="#pricing"  onclick="closeMenu()">Pricing</a>
  <a href="/login"    onclick="closeMenu()">Sign In</a>
  <a href="/setup" id="mob-cta" class="mob-cta" onclick="closeMenu()">Start Free Trial</a>
</div>

<!-- HERO -->
<section class="hero">
  <div class="hero-glow"></div>
  <div class="hero-grid"></div>
  <div class="hero-inner">
    <div>
      <div class="hero-eyebrow rv">
        <span class="hero-eyebrow-dot"></span>
        AI-Powered Face Recognition
      </div>
      <h1 class="hero-h1 rv">
        Attendance done<br><span class="grad">in 3 seconds.</span>
      </h1>
      <p class="hero-sub rv">
        FaceNova replaces paper registers and time-consuming roll calls with instant
        AI face recognition — built for Indian schools, colleges and coaching centres.
      </p>
      <div class="hero-actions rv">
        <a href="/setup" id="h-cta" class="btn-cta btn-cta-primary">🚀 Start Free Trial</a>
        <a href="#how" class="btn-cta btn-cta-outline">See How It Works</a>
      </div>
      <div class="hero-note rv">10-day free trial · No credit card · Cancel any time</div>
    </div>

    <div class="phone-wrap-order mockup-wrap rv">
      <!-- Floating pills -->
      <div class="fp fp-tl">
        <div class="fp-icon">⚡</div>
        <div class="fp-val">2.4s</div>
        <div class="fp-lbl">Avg scan time</div>
      </div>
      <div class="fp fp-br">
        <div class="fp-icon">🎯</div>
        <div class="fp-val">AI Ready</div>
        <div class="fp-lbl">Face matched</div>
      </div>

      <!-- Phone mockup -->
      <div class="phone">
        <div class="phone-notch"></div>
        <div class="phone-screen">
          <div class="sc sc-tl"></div><div class="sc sc-tr"></div>
          <div class="sc sc-bl"></div><div class="sc sc-br"></div>
          <div class="scan-beam"></div>
          <div class="detect-live"></div>
          <div class="face-ring"></div>
          <div class="face-ring"></div>
          <div class="face-icon">🧑</div>
          <div style="font-size:10px;color:var(--t2);margin-top:4px">Scanning...</div>
        </div>
        <div class="phone-bar">
          <div class="phone-bar-icon">✅</div>
          <div>
            <div class="phone-bar-text">Rahul Sharma — Present</div>
            <div style="font-size:9px;color:var(--m)">09:02 AM · Class 8A</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- BEFORE → AFTER -->
<section class="section" style="background:linear-gradient(180deg,var(--bg),var(--s1))">
  <div class="section-inner">
    <span class="eyebrow rv">The Problem</span>
    <h2 class="section-h2 rv">Paper registers are<br>wasting teaching time.</h2>
    <p class="section-lead rv">Every minute spent calling names is a minute not spent teaching. FaceNova fixes that.</p>

    <div class="ba-grid rv">
      <div class="ba-card ba-old">
        <div class="ba-head">
          <span style="font-size:22px">😩</span>
          <span class="ba-tag ba-tag-old">Paper Register</span>
        </div>
        <div class="ba-item"><b>❌</b> Teacher calls each name one by one</div>
        <div class="ba-item"><b>❌</b> 10–15 minutes lost every single class</div>
        <div class="ba-item"><b>❌</b> Registers get damaged, lost or forged</div>
        <div class="ba-item"><b>❌</b> No way to track attendance trends</div>
        <div class="ba-item"><b>❌</b> Parents notified days later, if at all</div>
        <div class="ba-item"><b>❌</b> Proxy attendance goes undetected</div>
      </div>
      <div class="ba-arrow"><div class="ba-arrow-inner">→</div></div>
      <div class="ba-card ba-new">
        <div class="ba-head">
          <span style="font-size:22px">🚀</span>
          <span class="ba-tag ba-tag-new">FaceNova AI</span>
        </div>
        <div class="ba-item"><b>✅</b> AI scans and recognises faces instantly</div>
        <div class="ba-item"><b>✅</b> Full class marked in under 1 minute</div>
        <div class="ba-item"><b>✅</b> All records stored securely in the cloud</div>
        <div class="ba-item"><b>✅</b> Daily, weekly and monthly reports ready</div>
        <div class="ba-item"><b>✅</b> Absent alerts can be sent immediately</div>
        <div class="ba-item"><b>✅</b> Face recognition prevents proxy attempts</div>
      </div>
    </div>
  </div>
</section>

<!-- HOW IT WORKS -->
<section class="section" id="how">
  <div class="section-inner">
    <span class="eyebrow rv">How It Works</span>
    <h2 class="section-h2 rv">Set up in minutes.<br>Works every day after that.</h2>
    <p class="section-lead rv">No special hardware. No app to download. Works in any modern mobile browser.</p>

    <div class="steps">
      <div class="step rv">
        <div class="step-num">STEP 01</div>
        <div class="step-ico" style="background:rgba(37,99,235,0.1)">📸</div>
        <div class="step-h">Enrol Students</div>
        <div class="step-p">Upload 3–5 clear photos of each student. The AI learns their face in seconds. No special camera needed.</div>
      </div>
      <div class="step rv rv-d1">
        <div class="step-num">STEP 02</div>
        <div class="step-ico" style="background:rgba(6,182,212,0.1)">🎥</div>
        <div class="step-h">Open the Scanner</div>
        <div class="step-p">Open FaceNova in your phone browser. Tap Scan. The AI camera turns on and is immediately ready.</div>
      </div>
      <div class="step rv rv-d2">
        <div class="step-num">STEP 03</div>
        <div class="step-ico" style="background:rgba(16,185,129,0.1)">🧠</div>
        <div class="step-h">AI Marks Attendance</div>
        <div class="step-p">Student faces the camera. FaceNova identifies them and marks Present automatically. Done.</div>
      </div>
      <div class="step rv rv-d3">
        <div class="step-num">STEP 04</div>
        <div class="step-ico" style="background:rgba(245,158,11,0.1)">📊</div>
        <div class="step-h">View Reports</div>
        <div class="step-p">See daily logs, monthly calendars, charts and analytics. Export to CSV whenever you need.</div>
      </div>
    </div>
  </div>
</section>

<!-- DASHBOARD PREVIEW -->
<section class="section" style="background:var(--s1);padding-top:60px;padding-bottom:60px">
  <div class="section-inner">
    <span class="eyebrow rv">Dashboard Preview</span>
    <h2 class="section-h2 rv">Everything in one clear view.</h2>
    <p class="section-lead rv" style="margin-bottom:28px">Real-time attendance, analytics and student management — all in a clean, fast dashboard.</p>
    <div class="dash-wrap rv">
      <div class="dash-bar">
        <div class="dash-dot dash-dot-r"></div>
        <div class="dash-dot dash-dot-y"></div>
        <div class="dash-dot dash-dot-g"></div>
        <div class="dash-url">
          <span style="color:var(--g);font-size:10px">🔒</span>
          facenova-ai.onrender.com/dashboard
        </div>
      </div>
      <div class="dash-body">
        <div class="dash-stat" style="border-top:2px solid var(--bl)">
          <div class="dash-stat-v" style="color:var(--bl)">42</div>
          <div class="dash-stat-l">Enrolled Students</div>
        </div>
        <div class="dash-stat" style="border-top:2px solid var(--g)">
          <div class="dash-stat-v" style="color:var(--g)">38</div>
          <div class="dash-stat-l">Present Today</div>
        </div>
        <div class="dash-stat" style="border-top:2px solid var(--r)">
          <div class="dash-stat-v" style="color:var(--r)">4</div>
          <div class="dash-stat-l">Absent Today</div>
    </div>
        <div class="dash-stat" style="border-top:2px solid var(--a)">
          <div class="dash-stat-v" style="color:var(--a)">90%</div>
          <div class="dash-stat-l">Attendance Rate</div>
        </div>
        <div class="dash-chart" id="demo-chart"></div>
      </div>
    </div>
  </div>
</section>

<!-- FEATURES -->
<section class="section" id="features">
  <div class="section-inner">
    <span class="eyebrow rv">Features</span>
    <h2 class="section-h2 rv">Everything your school needs.</h2>
    <p class="section-lead rv">Designed specifically for the realities of Indian schools, coaching centres and colleges.</p>
    <div class="feat-grid">
      <div class="feat rv">
        <div class="feat-ico" style="background:rgba(37,99,235,0.1)">🧠</div>
        <div class="feat-h">AI Face Recognition</div>
        <div class="feat-p">Computer vision identifies enrolled faces reliably. Works indoors with standard lighting — no expensive hardware required.</div>
      </div>
      <div class="feat rv rv-d1">
        <div class="feat-ico" style="background:rgba(6,182,212,0.1)">📅</div>
        <div class="feat-h">Attendance Calendar</div>
        <div class="feat-p">Visual monthly calendar per student. Green for present, red for absent. Spot attendance patterns at a glance.</div>
      </div>
      <div class="feat rv rv-d2">
        <div class="feat-ico" style="background:rgba(16,185,129,0.1)">📊</div>
        <div class="feat-h">Smart Reports</div>
        <div class="feat-p">Daily logs, weekly trends and monthly summaries generated automatically. Export any report as a CSV file.</div>
      </div>
      <div class="feat rv">
        <div class="feat-ico" style="background:rgba(139,92,246,0.1)">👨‍🏫</div>
        <div class="feat-h">Teacher Accounts</div>
        <div class="feat-p">Each teacher gets their own secure login. They see only their assigned classes — no confusion, no shared passwords.</div>
      </div>
      <div class="feat rv rv-d1">
        <div class="feat-ico" style="background:rgba(245,158,11,0.1)">📚</div>
        <div class="feat-h">Multi-Class Sections</div>
        <div class="feat-p">Manage 6A, 7B, 9C — any number of sections. Students are automatically organised by their assigned class.</div>
      </div>
      <div class="feat rv rv-d2">
        <div class="feat-ico" style="background:rgba(239,68,68,0.1)">🔒</div>
        <div class="feat-h">School Data Isolation</div>
        <div class="feat-p">Every school's data is stored completely separately. Your students and records are never shared with or visible to another school.</div>
      </div>
    </div>
  </div>
</section>

<!-- PRICING -->
<section class="section" id="pricing" style="background:var(--s1)">
  <div class="section-inner">
    <span class="eyebrow rv">Pricing</span>
    <h2 class="section-h2 rv">Honest pricing.<br>No surprises.</h2>
    <p class="section-lead rv">Start free for 10 days. No credit card required to begin.</p>
    <div class="price-grid rv">
      <div class="pc">
        <div class="pc-icon">🆓</div>
        <div class="pc-name">Free Trial</div>
        <div class="pc-amount">₹0</div>
        <div class="pc-period">10 days</div>
        <ul class="pc-feats">
          <li>Up to 50 students</li>
          <li>2 teacher accounts</li>
          <li>Face recognition scanning</li>
          <li>Basic dashboard</li>
        </ul>
        <a href="/setup" id="pc-cta-0" class="pc-btn">Start Free</a>
        <div class="pc-note">No card needed</div>
      </div>
      <div class="pc pc-popular">
        <div class="pc-badge">Most Popular</div>
        <div class="pc-icon">💙</div>
        <div class="pc-name">Basic</div>
        <div class="pc-amount">₹199</div>
        <div class="pc-period">per month</div>
        <ul class="pc-feats">
          <li>Up to 200 students</li>
          <li>5 teacher accounts</li>
          <li>Reports & CSV export</li>
          <li>Class sections</li>
          <li>Teacher dashboard</li>
        </ul>
        <a href="/setup" id="pc-cta-1" class="pc-btn pc-btn-p">Get Started</a>
        <div class="pc-note">≈ ₹6.60 per day</div>
      </div>
      <div class="pc">
        <div class="pc-icon">💜</div>
        <div class="pc-name">Professional</div>
        <div class="pc-amount">₹1,499</div>
        <div class="pc-period">per year · saves ₹889 vs monthly</div>
        <ul class="pc-feats">
          <li>Up to 1,000 students</li>
          <li>20 teacher accounts</li>
          <li>Advanced analytics</li>
          <li>Priority support</li>
        </ul>
        <a href="/setup" id="pc-cta-2" class="pc-btn">Get Started</a>
        <div class="pc-note">Best for larger schools</div>
      </div>
      <div class="pc">
        <div class="pc-icon">🌟</div>
        <div class="pc-name">Enterprise</div>
        <div class="pc-amount">₹3,500</div>
        <div class="pc-period">5 years · lowest per-year cost</div>
        <ul class="pc-feats">
          <li>Unlimited students</li>
          <li>Unlimited teachers</li>
          <li>API access</li>
          <li>Dedicated support</li>
        </ul>
        <a href="/setup" id="pc-cta-3" class="pc-btn">Contact Us</a>
        <div class="pc-note">Long-term investment</div>
      </div>
    </div>
  </div>
</section>

<!-- CTA BANNER -->
<section class="section">
  <div class="section-inner">
    <div class="cta-banner rv">
      <h2 class="cta-banner-h">Ready to try FaceNova?</h2>
      <p class="cta-banner-sub">
        Start your free 10-day trial today. Set up your school in under 10 minutes.<br>
        No credit card. No commitment. Full access to all features during your trial.
      </p>
      <div class="cta-actions">
        <a href="/setup" id="cta-main" class="btn-cta btn-cta-primary">🚀 Start Free Trial</a>
        <a href="{wa_url}"
           target="_blank" rel="noopener"
           class="btn-cta btn-cta-outline">💬 Talk to Us on WhatsApp</a>
      </div>
      <div class="cta-note">10-day free trial · Setup takes under 10 minutes · All data stays yours</div>
    </div>
  </div>
</section>

<!-- FOOTER -->
<footer class="footer">
  <div>
    <div class="logo-name" style="font-family:'Space Grotesk',sans-serif;font-size:16px;font-weight:700;color:var(--t2)">
      Face<em style="color:var(--c);font-style:normal">Nova</em> AI
    </div>
    <div class="footer-copy" style="margin-top:4px">Built for schools that value their teachers' time.</div>
  </div>
  <div class="footer-r">
    <a href="#how">How It Works</a>
    <a href="#features">Features</a>
    <a href="#pricing">Pricing</a>
    <a href="/login">Sign In</a>
  </div>
</footer>

<script>
// ── Scroll reveal
const rv = new IntersectionObserver(entries => {{
  entries.forEach(e => {{ if(e.isIntersecting){{e.target.classList.add('in');rv.unobserve(e.target)}} }});
}},{{threshold:0.1}});
document.querySelectorAll('.rv').forEach(el => rv.observe(el));

// ── Nav shadow on scroll
const nav = document.getElementById('nav');
window.addEventListener('scroll',() => {{
  nav.classList.toggle('scrolled', window.scrollY > 30);
}},{{passive:true}});

// ── Mobile menu
let menuOpen = false;
function toggleMenu(){{
  menuOpen = !menuOpen;
  document.getElementById('mob-menu').style.display = menuOpen ? 'flex' : 'none';
}}
function closeMenu(){{
  menuOpen = false;
  document.getElementById('mob-menu').style.display = 'none';
}}

// ── Set CTA links based on whether setup is done
// (server-side rendered below)

// ── Demo bar chart animation
function buildChart(){{
  const chart = document.getElementById('demo-chart');
  if(!chart) return;
  const vals = [72,85,60,90,88,75,92,68,95,80,88,85,70,94];
  chart.innerHTML = vals.map((v,i) =>
    `<div class="dash-bar-item" style="height:${{v}}%;opacity:${{0.5+v/200}};transition-delay:${{i*0.04}}s"></div>`
  ).join('');
}}
buildChart();

// ── Button ripple
document.querySelectorAll('.btn-cta, .pc-btn, .btn-nav-cta').forEach(btn => {{
  btn.addEventListener('click', function(e){{
    const r = document.createElement('span');
    const rect = this.getBoundingClientRect();
    r.style.cssText = `position:absolute;border-radius:50%;background:rgba(255,255,255,0.18);
      width:80px;height:80px;pointer-events:none;
      left:${{e.clientX-rect.left-40}}px;top:${{e.clientY-rect.top-40}}px;
      transform:scale(0);animation:rpl .5s ease-out forwards`;
    this.style.position='relative';this.style.overflow='hidden';
    this.appendChild(r);
    setTimeout(()=>r.remove(),500);
  }});
}});
const rplStyle = document.createElement('style');
rplStyle.textContent = '@keyframes rpl{{to{{transform:scale(3);opacity:0}}}}';
document.head.appendChild(rplStyle);
</script>
</body>
</html>"""
    return html
