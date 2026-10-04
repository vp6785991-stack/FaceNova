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
    # key, icon, color, badge, days, price_display, period_display, features
    plan_meta = [
        ("FREE_TRIAL",   "🆓", "var(--muted)",  "",             7,
         "₹0",          "7 days free",
         ["Basic face attendance","Up to 50 students","2 teachers","Basic dashboard"]),

        ("BASIC",        "💙", "var(--blue)",   "",             30,
         "₹199",        "per month",
         ["Everything in Free Trial","Up to 200 students","5 teachers","Reports","CSV export","Sections"]),

        ("PROFESSIONAL", "💜", "var(--purple)", "Most Popular", 365,
         "₹1,499",      "per year  ·  save ₹889",
         ["Everything in Basic","Up to 1,000 students","20 teachers","Advanced analytics","Priority support"]),

        ("ENTERPRISE",   "🌟", "var(--amber)",  "Best Value",   1825,
         "₹3,500",      "for 5 years  ·  best value",
         ["Everything in Professional","Unlimited students & teachers","API access","Custom branding","Phone support"]),
    ]

    plan_cards = ""
    for key, icon, color, badge, days, price, period, features in plan_meta:
        badge_html = f'<div class="plan-badge">{badge}</div>' if badge else ""
        popular    = "plan-popular" if badge == "Most Popular" else ""
        feat_html  = "".join(f"<li>{f}</li>" for f in features)
        plan_cards += f"""
        <div class="plan-card {popular}" style="border-top:2px solid {color}">
          {badge_html}
          <div class="plan-icon">{icon}</div>
          <div class="plan-name" style="color:{color}">{key.replace('_',' ').title()}</div>
          <div class="plan-price" style="color:{color};font-family:'Space Grotesk',sans-serif;
               font-size:32px;font-weight:800;letter-spacing:-1px;margin:8px 0 2px;line-height:1">
            {price}
          </div>
          <div class="plan-period" style="font-size:11.5px;color:var(--text2);margin-bottom:16px">
            {period}
          </div>
          <ul class="plan-features">{feat_html}</ul>
          <form method="POST" action="/upgrade/activate">
            <input type="hidden" name="plan" value="{key}">
            <input type="hidden" name="days" value="{days}">
            <button type="submit" class="btn btn-primary"
                    style="width:100%;justify-content:center;padding:13px;font-size:14px">
              🚀 {'Start Free Trial' if key == 'FREE_TRIAL' else 'Get ' + key.replace('_',' ').title()}
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
          <div>✅ A 7-day FREE TRIAL subscription starts automatically</div>
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

    created_banner = '<div class="alert alert-success" style="margin-bottom:16px">✅ School registered successfully! 7-day trial activated.</div>' if created else ""

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
    A <strong style="color:var(--blue)">7-day free trial</strong> has started.<br>
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
#  PUBLIC LANDING PAGE  (professional business style)
# ══════════════════════════════════════════════════════

@app.route("/home")
@app.route("/landing")
def landing():
    import db as _db, os as _os
    setup_done = _db.super_admin_exists()
    cta_url    = "/login" if setup_done else "/setup"
    _wa_num    = _os.environ.get("WHATSAPP_NUMBER","").strip()
    _wa_msg    = "Hi%2C%20I%20want%20to%20know%20more%20about%20FaceNova%20AI"
    wa_url     = f"https://wa.me/91{_wa_num}?text={_wa_msg}" if _wa_num else "#contact"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>FaceNova AI — Smart Face Recognition Attendance for Schools</title>
<meta name="description" content="Replace paper registers with AI face recognition. Built for Indian schools, colleges and coaching centres.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --blue:#4f46e5;--blue2:#3730a3;--cyan:#0891b2;
  --green:#059669;--red:#dc2626;--amber:#d97706;
  --text:#111827;--text2:#4b5563;--muted:#9ca3af;
  --white:#ffffff;--light:#f9fafb;--light2:#f3f4f6;
  --border:#e5e7eb;
}}
html{{scroll-behavior:smooth}}
body{{font-family:'Inter',sans-serif;color:var(--text);background:white;overflow-x:hidden}}
img{{display:block;max-width:100%}}
a{{text-decoration:none}}

/* NAV */
.nav{{
  position:fixed;top:0;left:0;right:0;z-index:100;
  background:rgba(255,255,255,0.96);
  backdrop-filter:blur(20px);
  border-bottom:1px solid var(--border);
  height:64px;padding:0 5%;
  display:flex;align-items:center;justify-content:space-between;
  box-shadow:0 1px 0 var(--border),0 4px 16px rgba(0,0,0,0.04);
}}
.nav-logo{{display:flex;align-items:center;gap:10px}}
.nav-logo-mark{{
  width:36px;height:36px;border-radius:9px;
  background:linear-gradient(135deg,#4f46e5,#7c3aed);
  display:flex;align-items:center;justify-content:center;
  font-size:18px;box-shadow:0 4px 12px rgba(79,70,229,0.35);
}}
.nav-logo-name{{
  font-family:'Space Grotesk',sans-serif;
  font-size:18px;font-weight:800;color:var(--text);letter-spacing:-0.5px;
}}
.nav-logo-name span{{color:var(--blue)}}
.nav-links{{display:flex;align-items:center;gap:28px}}
.nav-links a{{
  font-size:14px;font-weight:500;color:var(--text2);
  transition:color .15s;
}}
.nav-links a:hover{{color:var(--blue)}}
.nav-right{{display:flex;align-items:center;gap:10px}}
.btn-nav-login{{
  padding:8px 18px;border-radius:8px;
  font-size:13.5px;font-weight:600;color:var(--text2);
  border:1.5px solid var(--border);background:white;
  transition:all .15s;
}}
.btn-nav-login:hover{{border-color:var(--blue);color:var(--blue)}}
.btn-nav-cta{{
  padding:8px 20px;border-radius:8px;
  font-size:13.5px;font-weight:700;color:white;
  background:linear-gradient(135deg,#4f46e5,#7c3aed);
  box-shadow:0 4px 12px rgba(79,70,229,0.3);
  transition:all .15s;
}}
.btn-nav-cta:hover{{transform:translateY(-1px);box-shadow:0 6px 18px rgba(79,70,229,0.4)}}
.nav-ham{{display:none;flex-direction:column;gap:5px;cursor:pointer;padding:6px}}
.nav-ham span{{width:20px;height:2px;background:var(--text);border-radius:2px}}
.mob-menu{{
  display:none;position:fixed;top:64px;left:0;right:0;z-index:99;
  background:white;border-bottom:1px solid var(--border);
  padding:16px 5% 24px;flex-direction:column;gap:4px;
  box-shadow:0 8px 24px rgba(0,0,0,0.08);
}}
.mob-menu a{{
  display:block;padding:12px 14px;border-radius:9px;
  font-size:15px;font-weight:500;color:var(--text2);
  transition:all .12s;
}}
.mob-menu a:hover{{background:var(--light2);color:var(--blue)}}
.mob-cta{{
  margin-top:10px;background:linear-gradient(135deg,#4f46e5,#7c3aed)!important;
  color:white!important;text-align:center;font-weight:700!important;
  box-shadow:0 4px 12px rgba(79,70,229,0.3);border-radius:9px;
}}

/* HERO */
.hero{{
  min-height:100vh;
  background:linear-gradient(135deg,#4f46e5 0%,#7c3aed 40%,#0891b2 100%);
  display:flex;align-items:center;
  padding:100px 5% 60px;
  position:relative;overflow:hidden;
}}
.hero::before{{
  content:'';position:absolute;top:-100px;right:-100px;
  width:500px;height:500px;border-radius:50%;
  background:rgba(255,255,255,0.05);
}}
.hero::after{{
  content:'';position:absolute;bottom:-80px;left:10%;
  width:350px;height:350px;border-radius:50%;
  background:rgba(255,255,255,0.04);
}}
.hero-inner{{
  max-width:1100px;margin:0 auto;width:100%;
  display:grid;grid-template-columns:1fr 1fr;
  gap:60px;align-items:center;position:relative;z-index:1;
}}
.hero-tag{{
  display:inline-flex;align-items:center;gap:7px;
  background:rgba(255,255,255,0.15);
  border:1px solid rgba(255,255,255,0.25);
  border-radius:20px;padding:5px 14px;
  font-size:12.5px;font-weight:600;color:white;
  margin-bottom:20px;
}}
.hero-tag-dot{{
  width:7px;height:7px;border-radius:50%;
  background:#34d399;box-shadow:0 0 8px #34d399;
  animation:blink 2s infinite;
}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:0.3}}}}
.hero-h1{{
  font-family:'Space Grotesk',sans-serif;
  font-size:clamp(34px,4.5vw,58px);
  font-weight:800;line-height:1.1;
  letter-spacing:-2px;color:white;
  margin-bottom:18px;
}}
.hero-h1 span{{color:#a5f3fc}}
.hero-sub{{
  font-size:17px;color:rgba(255,255,255,0.85);
  line-height:1.75;margin-bottom:32px;max-width:480px;
}}
.hero-btns{{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:28px}}
.btn-hero-primary{{
  padding:14px 28px;border-radius:10px;
  font-size:15px;font-weight:700;color:var(--blue);
  background:white;
  box-shadow:0 4px 16px rgba(0,0,0,0.15);
  transition:all .2s;display:inline-flex;align-items:center;gap:8px;
}}
.btn-hero-primary:hover{{transform:translateY(-2px);box-shadow:0 8px 24px rgba(0,0,0,0.2)}}
.btn-hero-ghost{{
  padding:14px 28px;border-radius:10px;
  font-size:15px;font-weight:700;color:white;
  background:rgba(255,255,255,0.12);
  border:1.5px solid rgba(255,255,255,0.3);
  transition:all .2s;display:inline-flex;align-items:center;gap:8px;
}}
.btn-hero-ghost:hover{{background:rgba(255,255,255,0.2);transform:translateY(-2px)}}
.hero-note{{font-size:12.5px;color:rgba(255,255,255,0.65);display:flex;align-items:center;gap:6px}}
.hero-note::before{{content:'✓';color:#34d399;font-weight:700}}

/* hero phone mockup */
.hero-phone{{
  display:flex;justify-content:center;align-items:center;
  position:relative;
}}
.phone-frame{{
  width:220px;height:380px;
  background:rgba(255,255,255,0.1);
  border:2px solid rgba(255,255,255,0.2);
  border-radius:40px;
  padding:18px 14px 16px;
  display:flex;flex-direction:column;align-items:center;
  backdrop-filter:blur(10px);
  box-shadow:0 40px 80px rgba(0,0,0,0.3),0 0 0 8px rgba(255,255,255,0.05);
}}
.phone-notch{{
  width:50px;height:5px;background:rgba(255,255,255,0.3);
  border-radius:3px;margin-bottom:14px;flex-shrink:0;
}}
.phone-screen{{
  width:100%;flex:1;border-radius:22px;
  background:rgba(255,255,255,0.08);
  border:1px solid rgba(255,255,255,0.12);
  position:relative;overflow:hidden;
  display:flex;align-items:center;justify-content:center;
  flex-direction:column;
}}
.phone-corners span{{
  position:absolute;width:18px;height:18px;
}}
.pc-tl{{top:10px;left:10px;border-top:2px solid #a5f3fc;border-left:2px solid #a5f3fc;border-radius:3px 0 0 0}}
.pc-tr{{top:10px;right:10px;border-top:2px solid #a5f3fc;border-right:2px solid #a5f3fc;border-radius:0 3px 0 0}}
.pc-bl{{bottom:10px;left:10px;border-bottom:2px solid #a5f3fc;border-left:2px solid #a5f3fc;border-radius:0 0 0 3px}}
.pc-br{{bottom:10px;right:10px;border-bottom:2px solid #a5f3fc;border-right:2px solid #a5f3fc;border-radius:0 0 3px 0}}
.scan-beam-line{{
  position:absolute;left:0;right:0;height:1.5px;
  background:linear-gradient(90deg,transparent,#a5f3fc,transparent);
  box-shadow:0 0 10px rgba(165,243,252,0.6);
  animation:scan-move 2.5s ease-in-out infinite;
}}
@keyframes scan-move{{0%{{top:15%;opacity:0}}5%{{opacity:1}}95%{{opacity:1}}100%{{top:85%;opacity:0}}}}
.phone-face{{font-size:42px;margin-bottom:6px}}
.phone-live{{
  position:absolute;top:10px;right:32px;
  width:7px;height:7px;border-radius:50%;
  background:#34d399;box-shadow:0 0 6px #34d399;
  animation:blink 1.5s infinite;
}}
.phone-result{{
  flex-shrink:0;width:100%;margin-top:10px;
  background:rgba(52,211,153,0.15);
  border:1px solid rgba(52,211,153,0.3);
  border-radius:11px;padding:8px 12px;
  display:flex;align-items:center;gap:8px;
}}
.phone-result-icon{{font-size:14px}}
.phone-result-text{{font-size:10px;color:white;font-weight:600}}
.phone-result-sub{{font-size:9px;color:rgba(255,255,255,0.6)}}
.float-card{{
  position:absolute;
  background:white;border-radius:12px;
  padding:10px 14px;
  box-shadow:0 8px 24px rgba(0,0,0,0.15);
  white-space:nowrap;
}}
.fc-left{{left:-70px;top:30%;animation:float-y 3.2s ease-in-out infinite}}
.fc-right{{right:-70px;bottom:30%;animation:float-y 3.8s ease-in-out infinite .6s}}
@keyframes float-y{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-8px)}}}}
.fc-icon{{font-size:16px;margin-bottom:3px}}
.fc-val{{font-family:'Space Grotesk',sans-serif;font-size:16px;font-weight:800;color:var(--text)}}
.fc-lbl{{font-size:10px;color:var(--muted)}}

/* STATS BAR */
.stats-bar{{
  background:white;border-bottom:1px solid var(--border);
  padding:36px 5%;
  box-shadow:0 4px 16px rgba(0,0,0,0.04);
}}
.stats-bar-inner{{
  max-width:900px;margin:0 auto;
  display:grid;grid-template-columns:repeat(4,1fr);
  gap:20px;text-align:center;
}}
.sbar-num{{
  font-family:'Space Grotesk',sans-serif;
  font-size:clamp(28px,4vw,42px);font-weight:800;
  background:linear-gradient(135deg,var(--blue),var(--cyan));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  margin-bottom:4px;
}}
.sbar-lbl{{font-size:13px;color:var(--muted);font-weight:500}}

/* SECTION BASE */
.section{{padding:80px 5%}}
.section-inner{{max-width:1100px;margin:0 auto}}
.section-tag{{
  display:inline-block;font-size:12px;font-weight:700;
  letter-spacing:1.5px;text-transform:uppercase;
  color:var(--blue);margin-bottom:12px;
}}
.section-h2{{
  font-family:'Space Grotesk',sans-serif;
  font-size:clamp(28px,4vw,42px);font-weight:800;
  letter-spacing:-1px;line-height:1.15;
  color:var(--text);margin-bottom:14px;
}}
.section-sub{{
  font-size:16px;color:var(--text2);
  max-width:520px;line-height:1.75;margin-bottom:48px;
}}
.section-center{{text-align:center}}
.section-center .section-sub{{margin-left:auto;margin-right:auto}}

/* WHAT WE DO — icon grid */
.what-grid{{
  display:grid;grid-template-columns:repeat(3,1fr);gap:24px;
}}
.what-card{{
  background:white;border:1.5px solid var(--border);
  border-radius:16px;padding:28px 24px;
  transition:all .2s;text-align:center;
  box-shadow:0 1px 4px rgba(0,0,0,0.04);
}}
.what-card:hover{{
  transform:translateY(-5px);
  box-shadow:0 16px 40px rgba(79,70,229,0.12);
  border-color:rgba(79,70,229,0.25);
}}
.what-icon{{
  width:56px;height:56px;border-radius:14px;
  background:linear-gradient(135deg,rgba(79,70,229,0.1),rgba(124,58,237,0.08));
  display:flex;align-items:center;justify-content:center;
  font-size:24px;margin:0 auto 16px;
  border:1.5px solid rgba(99,102,241,0.15);
  transition:all .2s;
}}
.what-card:hover .what-icon{{
  background:linear-gradient(135deg,#4f46e5,#7c3aed);
  border-color:transparent;
  transform:scale(1.1);
}}
.what-h{{
  font-family:'Space Grotesk',sans-serif;
  font-size:16px;font-weight:700;margin-bottom:8px;color:var(--text);
}}
.what-p{{font-size:13.5px;color:var(--text2);line-height:1.65}}

/* BEFORE AFTER */
.ba-wrap{{
  display:grid;grid-template-columns:1fr 60px 1fr;
  gap:16px;align-items:stretch;
}}
.ba-card{{border-radius:16px;padding:28px}}
.ba-old{{background:rgba(220,38,38,0.04);border:1.5px solid rgba(220,38,38,0.15)}}
.ba-new{{background:rgba(5,150,105,0.04);border:1.5px solid rgba(5,150,105,0.18)}}
.ba-head{{display:flex;align-items:center;gap:10px;margin-bottom:18px}}
.ba-tag{{
  font-size:11px;font-weight:700;padding:4px 12px;border-radius:20px;
}}
.ba-tag-old{{background:rgba(220,38,38,0.1);color:#dc2626}}
.ba-tag-new{{background:rgba(5,150,105,0.1);color:#059669}}
.ba-item{{
  display:flex;align-items:flex-start;gap:10px;
  margin-bottom:12px;font-size:14px;color:var(--text2);
}}
.ba-arrow-col{{display:flex;align-items:center;justify-content:center}}
.ba-arrow-circle{{
  width:44px;height:44px;border-radius:50%;
  background:linear-gradient(135deg,#4f46e5,#7c3aed);
  display:flex;align-items:center;justify-content:center;
  font-size:18px;color:white;font-weight:700;
  box-shadow:0 4px 14px rgba(79,70,229,0.35);
  flex-shrink:0;
}}

/* HOW IT WORKS */
.steps-grid{{
  display:grid;grid-template-columns:repeat(4,1fr);gap:20px;
}}
.step-card{{
  background:white;border:1.5px solid var(--border);
  border-radius:16px;padding:24px 20px;
  transition:all .2s;position:relative;
  box-shadow:0 1px 4px rgba(0,0,0,0.04);
}}
.step-card:hover{{
  transform:translateY(-4px);
  box-shadow:0 14px 36px rgba(79,70,229,0.12);
  border-color:rgba(79,70,229,0.3);
}}
.step-card::before{{
  content:'';position:absolute;top:0;left:0;right:0;height:3px;
  border-radius:16px 16px 0 0;
  background:linear-gradient(90deg,#4f46e5,#7c3aed);
  opacity:0;transition:opacity .2s;
}}
.step-card:hover::before{{opacity:1}}
.step-num{{
  font-family:'Space Grotesk',sans-serif;
  font-size:10px;font-weight:700;letter-spacing:2px;
  color:var(--muted);text-transform:uppercase;margin-bottom:14px;
}}
.step-icon{{
  width:50px;height:50px;border-radius:13px;
  display:flex;align-items:center;justify-content:center;
  font-size:22px;margin-bottom:14px;
}}
.step-h{{
  font-family:'Space Grotesk',sans-serif;
  font-size:16px;font-weight:700;margin-bottom:7px;color:var(--text);
}}
.step-p{{font-size:13px;color:var(--text2);line-height:1.65}}

/* BLUE SECTION */
.blue-section{{
  background:linear-gradient(135deg,#4f46e5 0%,#7c3aed 50%,#0891b2 100%);
  padding:80px 5%;position:relative;overflow:hidden;
}}
.blue-section::before{{
  content:'';position:absolute;top:-60px;right:-60px;
  width:300px;height:300px;border-radius:50%;
  background:rgba(255,255,255,0.05);
}}
.blue-section-inner{{
  max-width:1100px;margin:0 auto;
  display:grid;grid-template-columns:1fr 1fr;
  gap:60px;align-items:center;position:relative;z-index:1;
}}
.blue-section h2{{
  font-family:'Space Grotesk',sans-serif;
  font-size:clamp(26px,3.5vw,40px);font-weight:800;
  color:white;letter-spacing:-1px;line-height:1.2;margin-bottom:16px;
}}
.blue-section p{{color:rgba(255,255,255,0.82);font-size:15px;line-height:1.75;margin-bottom:24px}}
.blue-fact-grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.blue-fact{{
  background:rgba(255,255,255,0.1);
  border:1px solid rgba(255,255,255,0.18);
  border-radius:14px;padding:18px;
}}
.blue-fact-num{{
  font-family:'Space Grotesk',sans-serif;
  font-size:28px;font-weight:800;color:white;margin-bottom:4px;
}}
.blue-fact-lbl{{font-size:12.5px;color:rgba(255,255,255,0.7)}}

/* PRICING */
.pricing-grid{{
  display:grid;grid-template-columns:repeat(4,1fr);gap:18px;
}}
.pc{{
  background:white;border:1.5px solid var(--border);
  border-radius:18px;padding:28px 20px;
  display:flex;flex-direction:column;
  transition:all .2s;position:relative;
  box-shadow:0 1px 4px rgba(0,0,0,0.04);
}}
.pc:hover{{transform:translateY(-5px);box-shadow:0 16px 40px rgba(79,70,229,0.12)}}
.pc-featured{{
  border-color:var(--blue);
  box-shadow:0 0 0 3px rgba(79,70,229,0.1),0 4px 16px rgba(79,70,229,0.1);
}}
.pc-badge{{
  position:absolute;top:-12px;left:50%;transform:translateX(-50%);
  background:linear-gradient(135deg,#4f46e5,#7c3aed);
  color:white;font-size:11px;font-weight:700;
  padding:4px 14px;border-radius:20px;white-space:nowrap;
  box-shadow:0 4px 12px rgba(79,70,229,0.35);
}}
.pc-icon{{font-size:30px;margin-bottom:12px}}
.pc-name{{
  font-family:'Space Grotesk',sans-serif;
  font-size:16px;font-weight:700;color:var(--text);margin-bottom:12px;
}}
.pc-price{{
  font-family:'Space Grotesk',sans-serif;
  font-size:clamp(24px,3vw,34px);font-weight:800;
  color:var(--blue);line-height:1;margin-bottom:3px;
}}
.pc-period{{font-size:12px;color:var(--muted);margin-bottom:18px}}
.pc-feats{{
  list-style:none;flex:1;display:flex;flex-direction:column;gap:8px;
  margin-bottom:22px;
}}
.pc-feats li{{
  font-size:13px;color:var(--text2);
  display:flex;align-items:center;gap:8px;
}}
.pc-feats li::before{{
  content:'✓';color:var(--green);font-weight:800;flex-shrink:0;
  width:18px;height:18px;background:rgba(5,150,105,0.1);
  border-radius:50%;display:flex;align-items:center;
  justify-content:center;font-size:10px;
}}
.pc-btn{{
  display:block;padding:12px;border-radius:10px;
  font-size:14px;font-weight:700;text-align:center;
  transition:all .15s;
  background:var(--light2);color:var(--text);
  border:1.5px solid var(--border);
}}
.pc-btn:hover{{background:var(--light);border-color:var(--blue);color:var(--blue)}}
.pc-btn-p{{
  background:linear-gradient(135deg,#4f46e5,#7c3aed);
  color:white;border:none;
  box-shadow:0 4px 14px rgba(79,70,229,0.3);
}}
.pc-btn-p:hover{{
  transform:translateY(-1px);
  box-shadow:0 8px 22px rgba(79,70,229,0.4);
}}
.pc-note{{font-size:11px;color:var(--muted);text-align:center;margin-top:8px}}

/* CTA */
.cta-section{{
  background:var(--light);border-top:1px solid var(--border);
  padding:80px 5%;text-align:center;
}}
.cta-h{{
  font-family:'Space Grotesk',sans-serif;
  font-size:clamp(28px,4vw,44px);font-weight:800;
  color:var(--text);letter-spacing:-1.5px;margin-bottom:14px;
}}
.cta-sub{{
  font-size:16px;color:var(--text2);margin-bottom:32px;
  line-height:1.7;max-width:520px;margin-left:auto;margin-right:auto;
}}
.cta-btns{{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}}
.btn-cta-p{{
  padding:14px 30px;border-radius:10px;font-size:15px;font-weight:700;
  color:white;background:linear-gradient(135deg,#4f46e5,#7c3aed);
  box-shadow:0 4px 16px rgba(79,70,229,0.35);
  transition:all .2s;display:inline-flex;align-items:center;gap:8px;
}}
.btn-cta-p:hover{{transform:translateY(-2px);box-shadow:0 8px 24px rgba(79,70,229,0.45)}}
.btn-cta-wa{{
  padding:14px 30px;border-radius:10px;font-size:15px;font-weight:700;
  color:#25D366;background:rgba(37,211,102,0.08);
  border:2px solid rgba(37,211,102,0.25);
  transition:all .2s;display:inline-flex;align-items:center;gap:8px;
}}
.btn-cta-wa:hover{{background:rgba(37,211,102,0.14);transform:translateY(-2px)}}
.cta-note{{font-size:12.5px;color:var(--muted);margin-top:16px}}

/* FOOTER */
.footer{{
  background:var(--text);color:rgba(255,255,255,0.6);
  padding:32px 5%;
  display:flex;align-items:center;justify-content:space-between;
  flex-wrap:wrap;gap:14px;
}}
.footer-logo{{
  font-family:'Space Grotesk',sans-serif;
  font-size:17px;font-weight:800;color:white;
}}
.footer-logo span{{color:#a5f3fc}}
.footer-links{{display:flex;gap:22px}}
.footer-links a{{font-size:13px;color:rgba(255,255,255,0.5);transition:color .15s}}
.footer-links a:hover{{color:white}}
.footer-copy{{font-size:12px}}

/* SCROLL REVEAL */
.rv{{opacity:0;transform:translateY(22px);transition:opacity .55s ease,transform .55s ease}}
.rv.visible{{opacity:1;transform:none}}
.rv-d1{{transition-delay:.08s}}.rv-d2{{transition-delay:.16s}}.rv-d3{{transition-delay:.24s}}

/* RESPONSIVE */
@media(max-width:900px){{
  .hero-inner{{grid-template-columns:1fr;text-align:center;gap:36px}}
  .hero-phone{{order:-1}}
  .hero-sub{{margin:0 auto 32px}}
  .hero-btns{{justify-content:center}}
  .hero-note{{justify-content:center}}
  .fc-left,.fc-right{{display:none}}
  .what-grid{{grid-template-columns:1fr 1fr}}
  .ba-wrap{{grid-template-columns:1fr;gap:10px}}
  .ba-arrow-col{{display:none}}
  .steps-grid{{grid-template-columns:1fr 1fr}}
  .blue-section-inner{{grid-template-columns:1fr}}
  .pricing-grid{{grid-template-columns:1fr 1fr}}
  .nav-links{{display:none}}
  .nav-ham{{display:flex}}
  .stats-bar-inner{{grid-template-columns:1fr 1fr;gap:24px}}
}}
@media(max-width:560px){{
  .section{{padding:52px 5%}}
  .what-grid{{grid-template-columns:1fr}}
  .steps-grid{{grid-template-columns:1fr}}
  .pricing-grid{{grid-template-columns:1fr}}
  .blue-fact-grid{{grid-template-columns:1fr 1fr}}
  .footer{{flex-direction:column;align-items:flex-start}}
  .phone-frame{{width:180px;height:310px}}
}}
</style>
</head>
<body>

<!-- NAV -->
<nav class="nav" id="nav">
  <div class="nav-logo">
    <div class="nav-logo-mark">🧠</div>
    <div class="nav-logo-name">Face<span>Nova</span></div>
  </div>
  <div class="nav-links">
    <a href="#what">What We Do</a>
    <a href="#how">How It Works</a>
    <a href="#pricing">Pricing</a>
    <a href="#contact">Contact</a>
  </div>
  <div class="nav-right">
    <a href="/login" class="btn-nav-login">Sign In</a>
    <a href="{cta_url}" class="btn-nav-cta">Start Free Trial</a>
  </div>
  <div class="nav-ham" onclick="toggleMenu()" id="ham">
    <span></span><span></span><span></span>
  </div>
</nav>
<div class="mob-menu" id="mob-menu">
  <a href="#what" onclick="closeMenu()">What We Do</a>
  <a href="#how" onclick="closeMenu()">How It Works</a>
  <a href="#pricing" onclick="closeMenu()">Pricing</a>
  <a href="/login" onclick="closeMenu()">Sign In</a>
  <a href="{cta_url}" class="mob-cta" onclick="closeMenu()">Start Free Trial →</a>
</div>

<!-- HERO -->
<section class="hero">
  <div class="hero-inner">
    <div>
      <div class="hero-tag">
        <span class="hero-tag-dot"></span>
        AI Face Recognition — Live
      </div>
      <h1 class="hero-h1">
        Smart Attendance<br>for <span>Schools &amp; Colleges</span>
      </h1>
      <p class="hero-sub">
        FaceNova replaces paper registers and time-consuming roll calls with
        instant AI face recognition. Built for Indian schools, colleges and coaching centres.
      </p>
      <div class="hero-btns">
        <a href="{cta_url}" class="btn-hero-primary">🚀 Start Free Trial</a>
        <a href="#how" class="btn-hero-ghost">See How It Works</a>
      </div>
      <div class="hero-note">7-day free trial · No credit card · Cancel anytime</div>
    </div>
    <div class="hero-phone" style="position:relative;display:flex;align-items:flex-end;justify-content:center;gap:20px">
      <!-- Founder photo -->
      <div style="position:relative;z-index:2">
        <img src="data:image/jpeg;base64,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"
             alt="FaceNova Founder"
             style="width:220px;height:310px;object-fit:cover;object-position:top center;
                    border-radius:24px;display:block;
                    border:3px solid rgba(255,255,255,0.25);
                    box-shadow:0 24px 60px rgba(0,0,0,0.3),0 0 0 1px rgba(255,255,255,0.1);
                    animation:fadeUp 0.7s 0.2s cubic-bezier(.34,1.1,.64,1) both">
        <!-- name badge -->
        <div style="position:absolute;bottom:-14px;left:50%;transform:translateX(-50%);
                    background:white;border-radius:12px;padding:8px 16px;
                    box-shadow:0 8px 24px rgba(0,0,0,0.15);
                    white-space:nowrap;text-align:center;min-width:160px">
          <div style="font-family:'Space Grotesk',sans-serif;font-size:13px;font-weight:800;color:#1e1b4b">
            Vasu
          </div>
          <div style="font-size:11px;color:#6b7280;font-weight:500">Founder, FaceNova AI</div>
        </div>
      </div>

      <!-- Phone mockup -->
      <div style="position:relative;z-index:2;margin-bottom:0">
        <div class="float-card fc-right" style="right:-60px;bottom:40%">
          <div class="fc-icon">⚡</div>
          <div class="fc-val">2.4s</div>
          <div class="fc-lbl">Avg scan</div>
        </div>
        <div class="phone-frame" style="width:170px;height:300px">
          <div class="phone-notch"></div>
          <div class="phone-screen">
            <div class="phone-corners">
              <span class="pc-tl"></span><span class="pc-tr"></span>
              <span class="pc-bl"></span><span class="pc-br"></span>
            </div>
            <div class="scan-beam-line"></div>
            <div class="phone-live"></div>
            <div class="phone-face">🧑</div>
            <div style="font-size:9px;color:rgba(255,255,255,0.6)">Scanning...</div>
          </div>
          <div class="phone-result">
            <div class="phone-result-icon">✅</div>
            <div>
              <div class="phone-result-text">Present — 09:02 AM</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- STATS BAR -->
<div class="stats-bar">
  <div class="stats-bar-inner">
    <div class="rv">
      <div class="sbar-num" data-count="3">0</div>
      <div class="sbar-lbl">Seconds per student</div>
    </div>
    <div class="rv rv-d1">
      <div class="sbar-num" data-count="7">0</div>
      <div class="sbar-lbl">Day free trial</div>
    </div>
    <div class="rv rv-d2">
      <div class="sbar-num" data-count="100">0</div>
      <div class="sbar-lbl">% data safety</div>
    </div>
    <div class="rv rv-d3">
      <div class="sbar-num" data-count="0">Free</div>
      <div class="sbar-lbl">To get started</div>
    </div>
  </div>
</div>

<!-- WHAT WE DO -->
<section class="section" id="what" style="background:var(--light)">
  <div class="section-inner">
    <div class="section-center rv">
      <div class="section-tag">What We Do</div>
      <h2 class="section-h2">Everything your school needs<br>for modern attendance</h2>
      <p class="section-sub">No hardware. No app. Works on any phone browser instantly.</p>
    </div>
    <div class="what-grid">
      <div class="what-card rv">
        <div class="what-icon">🧠</div>
        <div class="what-h">AI Face Recognition</div>
        <div class="what-p">Identifies enrolled students instantly. Works indoors with standard lighting — no expensive cameras needed.</div>
      </div>
      <div class="what-card rv rv-d1">
        <div class="what-icon">📅</div>
        <div class="what-h">Attendance Calendar</div>
        <div class="what-p">Visual monthly calendar per student. Green for present, red for absent. Spot patterns instantly.</div>
      </div>
      <div class="what-card rv rv-d2">
        <div class="what-icon">📊</div>
        <div class="what-h">Smart Analytics</div>
        <div class="what-p">Daily logs, weekly trends and monthly reports generated automatically. Export to CSV anytime.</div>
      </div>
      <div class="what-card rv">
        <div class="what-icon">👨‍🏫</div>
        <div class="what-h">Teacher Accounts</div>
        <div class="what-p">Each teacher gets their own secure login. They see only their assigned classes.</div>
      </div>
      <div class="what-card rv rv-d1">
        <div class="what-icon">📚</div>
        <div class="what-h">Multi-Class Sections</div>
        <div class="what-p">Manage 6A, 7B, 9C — any number of sections. Students organised by class automatically.</div>
      </div>
      <div class="what-card rv rv-d2">
        <div class="what-icon">🔒</div>
        <div class="what-h">Secure & Private</div>
        <div class="what-p">Every school's data stored completely separately. Your students are never visible to another school.</div>
      </div>
    </div>
  </div>
</section>

<!-- BEFORE / AFTER -->
<section class="section">
  <div class="section-inner">
    <div class="rv">
      <div class="section-tag">The Problem</div>
      <h2 class="section-h2">Paper registers are<br>wasting teaching time</h2>
      <p class="section-sub">Every minute spent calling names is a minute not spent teaching. FaceNova fixes that.</p>
    </div>
    <div class="ba-wrap rv">
      <div class="ba-card ba-old">
        <div class="ba-head">
          <span style="font-size:22px">😩</span>
          <span class="ba-tag ba-tag-old">Without FaceNova</span>
        </div>
        <div class="ba-item"><b style="color:#dc2626">✗</b>&nbsp; Teacher calls each name manually</div>
        <div class="ba-item"><b style="color:#dc2626">✗</b>&nbsp; 10–15 minutes wasted every class</div>
        <div class="ba-item"><b style="color:#dc2626">✗</b>&nbsp; Registers get lost or damaged</div>
        <div class="ba-item"><b style="color:#dc2626">✗</b>&nbsp; No way to track absence patterns</div>
        <div class="ba-item"><b style="color:#dc2626">✗</b>&nbsp; Proxy attendance goes undetected</div>
      </div>
      <div class="ba-arrow-col">
        <div class="ba-arrow-circle">→</div>
      </div>
      <div class="ba-card ba-new">
        <div class="ba-head">
          <span style="font-size:22px">🚀</span>
          <span class="ba-tag ba-tag-new">With FaceNova</span>
        </div>
        <div class="ba-item"><b style="color:#059669">✓</b>&nbsp; AI scans faces in under 3 seconds</div>
        <div class="ba-item"><b style="color:#059669">✓</b>&nbsp; Full class marked in under 1 minute</div>
        <div class="ba-item"><b style="color:#059669">✓</b>&nbsp; All records stored securely in cloud</div>
        <div class="ba-item"><b style="color:#059669">✓</b>&nbsp; Daily, weekly and monthly reports</div>
        <div class="ba-item"><b style="color:#059669">✓</b>&nbsp; Face recognition prevents proxy</div>
      </div>
    </div>
  </div>
</section>

<!-- HOW IT WORKS -->
<section class="section" id="how" style="background:var(--light)">
  <div class="section-inner">
    <div class="section-center rv">
      <div class="section-tag">How It Works</div>
      <h2 class="section-h2">Set up in minutes.<br>Works every day after that.</h2>
      <p class="section-sub">No special hardware. Works in any modern mobile browser.</p>
    </div>
    <div class="steps-grid">
      <div class="step-card rv">
        <div class="step-num">Step 01</div>
        <div class="step-icon" style="background:rgba(79,70,229,0.08)">📸</div>
        <div class="step-h">Enrol Students</div>
        <div class="step-p">Upload 3–5 clear photos of each student. The AI learns their face in seconds. No special camera needed.</div>
      </div>
      <div class="step-card rv rv-d1">
        <div class="step-num">Step 02</div>
        <div class="step-icon" style="background:rgba(8,145,178,0.08)">🎥</div>
        <div class="step-h">Open the Scanner</div>
        <div class="step-p">Open FaceNova in your browser. Tap Scan. The AI camera turns on — ready to recognise any enrolled face.</div>
      </div>
      <div class="step-card rv rv-d2">
        <div class="step-num">Step 03</div>
        <div class="step-icon" style="background:rgba(5,150,105,0.08)">🧠</div>
        <div class="step-h">AI Marks Present</div>
        <div class="step-p">Student faces the camera. FaceNova identifies them and marks Present automatically. Done in 3 seconds.</div>
      </div>
      <div class="step-card rv" style="transition-delay:.32s">
        <div class="step-num">Step 04</div>
        <div class="step-icon" style="background:rgba(217,119,6,0.08)">📊</div>
        <div class="step-h">View Reports</div>
        <div class="step-p">See daily logs, monthly calendars and analytics. Export to CSV whenever you need.</div>
      </div>
    </div>
  </div>
</section>

<!-- BLUE FACTS SECTION -->
<section class="blue-section">
  <div class="blue-section-inner">
    <div>
      <div style="font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:rgba(255,255,255,0.6);margin-bottom:12px">Why FaceNova</div>
      <h2>Built for the realities<br>of Indian schools</h2>
      <p>Designed with Indian schools in mind — affordable pricing, works on any Android phone, no expensive hardware, simple enough for any teacher to use on day one.</p>
      <a href="{cta_url}" class="btn-hero-primary" style="display:inline-flex">🚀 Start Free Trial</a>
    </div>
    <div class="blue-fact-grid rv">
      <div class="blue-fact">
        <div class="blue-fact-num">₹199</div>
        <div class="blue-fact-lbl">Per month — less than ₹7/day</div>
      </div>
      <div class="blue-fact">
        <div class="blue-fact-num">&lt; 3s</div>
        <div class="blue-fact-lbl">Per student scan time</div>
      </div>
      <div class="blue-fact">
        <div class="blue-fact-num">0</div>
        <div class="blue-fact-lbl">Hardware required</div>
      </div>
      <div class="blue-fact">
        <div class="blue-fact-num">7</div>
        <div class="blue-fact-lbl">Day free trial, no card needed</div>
      </div>
    </div>
  </div>
</section>

<!-- PRICING -->
<section class="section" id="pricing">
  <div class="section-inner">
    <div class="section-center rv">
      <div class="section-tag">Pricing</div>
      <h2 class="section-h2">Simple, honest pricing.<br>No surprises.</h2>
      <p class="section-sub">Start free for 7 days. No credit card required to begin.</p>
    </div>
    <div class="pricing-grid rv">
      <div class="pc">
        <div class="pc-icon">🆓</div>
        <div class="pc-name">Free Trial</div>
        <div class="pc-price">₹0</div>
        <div class="pc-period">7 days free</div>
        <ul class="pc-feats">
          <li>Up to 50 students</li>
          <li>2 teacher accounts</li>
          <li>Face recognition</li>
          <li>Basic dashboard</li>
        </ul>
        <a href="{cta_url}" class="pc-btn">Start Free</a>
        <div class="pc-note">No card needed</div>
      </div>
      <div class="pc pc-featured">
        <div class="pc-badge">Most Popular</div>
        <div class="pc-icon">💙</div>
        <div class="pc-name">Basic</div>
        <div class="pc-price">₹199</div>
        <div class="pc-period">per month</div>
        <ul class="pc-feats">
          <li>Up to 200 students</li>
          <li>5 teacher accounts</li>
          <li>Reports &amp; CSV export</li>
          <li>Class sections</li>
        </ul>
        <a href="{cta_url}" class="pc-btn pc-btn-p">Get Started</a>
        <div class="pc-note">≈ ₹6.60 per day</div>
      </div>
      <div class="pc">
        <div class="pc-icon">💜</div>
        <div class="pc-name">Professional</div>
        <div class="pc-price">₹1,499</div>
        <div class="pc-period">per year · save ₹889</div>
        <ul class="pc-feats">
          <li>Up to 1,000 students</li>
          <li>20 teacher accounts</li>
          <li>Advanced analytics</li>
          <li>Priority support</li>
        </ul>
        <a href="{cta_url}" class="pc-btn">Get Started</a>
        <div class="pc-note">Best for larger schools</div>
      </div>
      <div class="pc">
        <div class="pc-icon">🌟</div>
        <div class="pc-name">Enterprise</div>
        <div class="pc-price">₹3,500</div>
        <div class="pc-period">5 years · best value</div>
        <ul class="pc-feats">
          <li>Unlimited students</li>
          <li>Unlimited teachers</li>
          <li>API access</li>
          <li>Dedicated support</li>
        </ul>
        <a href="{cta_url}" class="pc-btn">Contact Us</a>
        <div class="pc-note">Long-term investment</div>
      </div>
    </div>
  </div>
</section>

<!-- CTA -->
<section class="cta-section" id="contact">
  <div class="rv">
    <h2 class="cta-h">Ready to try FaceNova?</h2>
    <p class="cta-sub">Start your free 7-day trial today. Set up your school in under 10 minutes. No credit card. No commitment.</p>
    <div class="cta-btns">
      <a href="{cta_url}" class="btn-cta-p">🚀 Start Free Trial</a>
      <a href="{wa_url}" target="_blank" rel="noopener" class="btn-cta-wa">💬 WhatsApp Us</a>
    </div>
    <div class="cta-note">7-day free trial · All your data stays yours · Cancel anytime</div>
  </div>
</section>

<!-- FOOTER -->
<footer class="footer">
  <div class="footer-logo">Face<span>Nova</span> AI</div>
  <div class="footer-links">
    <a href="#what">What We Do</a>
    <a href="#how">How It Works</a>
    <a href="#pricing">Pricing</a>
    <a href="/login">Sign In</a>
  </div>
  <div class="footer-copy">© 2026 FaceNova AI · Built for schools that value their time</div>
</footer>

<script>
// Scroll reveal
const rv = new IntersectionObserver(entries => {{
  entries.forEach(e => {{ if(e.isIntersecting){{e.target.classList.add('visible');rv.unobserve(e.target)}} }});
}}, {{threshold:0.1}});
document.querySelectorAll('.rv').forEach(el => rv.observe(el));

// Nav scroll shadow
window.addEventListener('scroll', () => {{
  document.getElementById('nav').style.boxShadow = window.scrollY > 20
    ? '0 4px 24px rgba(0,0,0,0.1)' : '0 1px 0 #e5e7eb,0 4px 16px rgba(0,0,0,0.04)';
}}, {{passive:true}});

// Mobile menu
let open = false;
function toggleMenu(){{open=!open;document.getElementById('mob-menu').style.display=open?'flex':'none'}}
function closeMenu(){{open=false;document.getElementById('mob-menu').style.display='none'}}

// Count up numbers
const co = new IntersectionObserver(entries => {{
  entries.forEach(e => {{
    if(e.isIntersecting){{
      const t = parseInt(e.target.dataset.count);
      if(isNaN(t))return;
      let s=0;
      const dur=1600;
      const step=ts=>{{
        if(!s)s=ts;
        const p=Math.min((ts-s)/dur,1);
        const ease=1-Math.pow(1-p,3);
        e.target.textContent=Math.floor(ease*t).toLocaleString();
        if(p<1)requestAnimationFrame(step);
      }};
      requestAnimationFrame(step);
      co.unobserve(e.target);
    }}
  }});
}},{{threshold:0.5}});
document.querySelectorAll('[data-count]').forEach(el=>co.observe(el));

// Button ripple
document.querySelectorAll('.btn-hero-primary,.btn-hero-ghost,.btn-cta-p,.pc-btn,.btn-nav-cta').forEach(btn=>{{
  btn.addEventListener('click',function(e){{
    const r=document.createElement('span');
    const rect=this.getBoundingClientRect();
    r.style.cssText=`position:absolute;border-radius:50%;
      background:rgba(255,255,255,0.25);width:80px;height:80px;pointer-events:none;
      left:${{e.clientX-rect.left-40}}px;top:${{e.clientY-rect.top-40}}px;
      transform:scale(0);animation:rpl 0.5s ease-out forwards`;
    this.style.position='relative';this.style.overflow='hidden';
    this.appendChild(r);setTimeout(()=>r.remove(),500);
  }});
}});
const rs=document.createElement('style');
rs.textContent='@keyframes rpl{{to{{transform:scale(3);opacity:0}}}}';
document.head.appendChild(rs);
</script>
</body>
</html>"""
    return html

