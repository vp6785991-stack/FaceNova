# routes.py — FaceNova All Route Handlers
from flask import request, redirect, session, send_file
from datetime import datetime, timedelta
import os, csv, base64, json
import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from app_core import (
    app, DATA_DIR, GRAPH_DIR, ATT_FILE, GRAPH_DIR,
    PLANS, DEV_CREDENTIALS, TRIAL_DAYS,
    read_all_records, enrolled_students, stats_for_student,
    daily_summary, enrolled_students, students_in_section,
    get_student_section, set_student_section,
    get_profile_image, save_profile_image, load_meta, save_meta,
    load_sections, save_sections, section_color,
    sub_load, sub_save, sub_status, sub_banner, premium_required,
    face_detector, get_face_encoding, match_face,
    layout, CSS, PLANS, pct_ring,
    teacher_required, TEACHER_USERS,
)

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
      <div style="position:relative;z-index:1">
        <div style="display:inline-flex;align-items:center;gap:7px;background:rgba(59,130,246,0.12);border:1px solid rgba(59,130,246,0.25);border-radius:20px;padding:4px 12px;font-size:11.5px;font-weight:600;color:var(--blue);margin-bottom:12px">
          <span style="width:6px;height:6px;border-radius:50%;background:var(--blue);animation:pulse-dot 2s infinite"></span>
          AI Face Recognition Active
        </div>
        <h1>Welcome to FaceNova 🧠</h1>
        <p>Next-generation AI attendance system for offices, schools &amp; colleges.<br>Real-time recognition · Smart analytics · Zero friction.</p>
        <div class="hero-actions">
          <a href="/scan" class="btn btn-cyan">🎥 Start Face Scan</a>
          <a href="/students" class="btn btn-ghost">👥 Students</a>
          <a href="/sections" class="btn btn-ghost">📚 Sections</a>
        </div>
      </div>
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
      <div class="card" style="text-align:center;position:relative;overflow:hidden">
        <div style="position:absolute;top:0;left:0;right:0;height:1.5px;background:linear-gradient(90deg,var(--blue),var(--cyan))"></div>
        <div style="font-size:38px;margin-bottom:10px">📅</div>
        <div class="sec-title">Smart Calendar</div>
        <div style="font-size:12.5px;color:var(--text2);margin:7px 0 15px;line-height:1.5">Monthly heatmap with daily attendance breakdown</div>
        <a href="/calendar" class="btn btn-ghost" style="width:100%;justify-content:center">Open Calendar</a>
      </div>
      <div class="card" style="text-align:center;position:relative;overflow:hidden">
        <div style="position:absolute;top:0;left:0;right:0;height:1.5px;background:linear-gradient(90deg,var(--purple),var(--pink))"></div>
        <div style="font-size:38px;margin-bottom:10px">👤</div>
        <div class="sec-title">Student Profiles</div>
        <div style="font-size:12.5px;color:var(--text2);margin:7px 0 15px;line-height:1.5">Per-student stats, streaks & attendance history</div>
        <a href="/students" class="btn btn-ghost" style="width:100%;justify-content:center">View Students</a>
      </div>
      <div class="card" style="text-align:center;position:relative;overflow:hidden">
        <div style="position:absolute;top:0;left:0;right:0;height:1.5px;background:linear-gradient(90deg,var(--green),var(--cyan))"></div>
        <div style="font-size:38px;margin-bottom:10px">📋</div>
        <div class="sec-title">Daily Log</div>
        <div style="font-size:12.5px;color:var(--text2);margin:7px 0 15px;line-height:1.5">Full present/absent record with timestamps</div>
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
    section  = request.args.get("section","")
    sections = load_sections()
    records   = read_all_records(section)
    present, absent = daily_summary(date_str, records)
    students  = enrolled_students(section)

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
    section      = request.args.get("section","")
    sections     = load_sections()
    all_students = enrolled_students(section)
    records      = read_all_records()

    # section tab bar
    tab_all  = "sec-tab sec-tab-all" + (" sec-tab-active" if not section else "")
    tabs_html = f'<a href="/students" class="{tab_all}">🌐 All</a>'
    for s in sections:
        active = " sec-tab-active" if s == section else ""
        count  = len(students_in_section(s))
        tabs_html += f'<a href="/students?section={s}" class="sec-tab{active}">{s} <span style="font-size:11px;opacity:0.7">({count})</span></a>'

    if not all_students:
        content = f"""
        <div class="sec-head" style="margin-bottom:16px">
          <div><div class="sec-title" style="font-size:20px">👥 Students</div></div>
          <a href="/enroll" class="btn btn-primary">+ Enroll New</a>
        </div>
        <div class="sec-tabs">{tabs_html}</div>
        <div class="card" style="text-align:center;padding:60px">
          <div style="font-size:50px;margin-bottom:14px">👥</div>
          <div class="sec-title">No Students{" in section " + section if section else ""}</div>
          <div style="color:var(--muted);margin-top:8px;margin-bottom:20px">Enroll students to see profiles.</div>
          <a href="/enroll" class="btn btn-primary">+ Enroll First Student</a>
        </div>"""
        return layout("Students", content, "students")

    cards = ""
    for name in all_students:
        s         = stats_for_student(name, records)
        pct_color = "var(--green)" if s["pct"]>=75 else ("var(--amber)" if s["pct"]>=50 else "var(--red)")
        pbar_cls  = "pbar-green" if s["pct"]>=75 else ("pbar-amber" if s["pct"]>=50 else "pbar-red")
        stud_sec  = get_student_section(name)

        prof_url = get_profile_image(name)
        if prof_url:
            img_tag = f'<img src="{prof_url}" class="s-avatar">'
        else:
            img_tag = f'<div class="s-avatar-placeholder">{name[0].upper()}</div>'

        streak_html = f'<div class="streak">🔥 {s["streak"]}d streak</div>' if s["streak"]>0 else ""
        sec_html    = f'<div style="margin-bottom:6px"><span class="sec-badge">{stud_sec}</span></div>' if stud_sec else ""

        cards += f"""
        <div class="student-card">
          <a href="/student/{name}" style="text-decoration:none;color:inherit">
            {img_tag}
            {sec_html}
            <div class="s-name">{name}</div>
            <div class="s-pct" style="color:{pct_color}">{s['pct']}%</div>
            <div style="font-size:11.5px;color:var(--muted);margin-bottom:8px">{s['present']}P / {s['absent']}A of {s['total']}</div>
            <div class="pbar-wrap"><div class="pbar {pbar_cls}" style="width:{s['pct']}%"></div></div>
            <div style="margin-top:8px">{streak_html}</div>
          </a>
        </div>"""

    sec_title = f"Section {section}" if section else "All Students"
    content = f"""
    <div class="sec-head" style="margin-bottom:16px">
      <div><div class="sec-title" style="font-size:20px">👥 {sec_title}</div>
      <div class="sec-sub">{len(all_students)} student(s) · click a card to view full history</div></div>
      <div style="display:flex;gap:8px">
        <a href="/sections" class="btn btn-ghost btn-sm">📚 Sections</a>
        <a href="/enroll" class="btn btn-primary">+ Enroll New</a>
      </div>
    </div>
    <div class="sec-tabs">{tabs_html}</div>
    <div class="student-grid">{cards}</div>
    """
    return layout("Students", content, "students")

# ══════════════════════════════════════════════════════
#  SINGLE STUDENT DETAIL
# ══════════════════════════════════════════════════════


@app.route("/profile-img/<name>")
def profile_img(name):
    user_dir = os.path.join(DATA_DIR, name)
    for ext in ("jpg","jpeg","png","webp"):
        pf = os.path.join(user_dir, f"_profile.{ext}")
        if os.path.exists(pf):
            return send_file(pf)
    return ("Not found", 404)


@app.route("/student/<name>/upload-profile", methods=["POST"])
def upload_profile(name):
    f = request.files.get("profile_photo")
    if not f or f.filename == "":
        return redirect(f"/student/{name}?msg=no_file")
    try:
        save_profile_image(name, f)
        return redirect(f"/student/{name}?msg=ok")
    except Exception as e:
        return redirect(f"/student/{name}?msg=err")

@app.route("/student/<name>")
def student_detail(name):
    records = read_all_records()
    mine    = [r for r in records if r["name"] == name]
    s       = stats_for_student(name, records)

    pbar_cls   = "pbar-green" if s["pct"]>=75 else ("pbar-amber" if s["pct"]>=50 else "pbar-red")
    status_msg = "🟢 Good Standing" if s["pct"]>=75 else ("🟡 Needs Improvement" if s["pct"]>=50 else "🔴 Low Attendance — At Risk")
    stud_sec   = get_student_section(name)
    sections   = load_sections()
    sec_options = "".join(f'<option value="{s}" {"selected" if s==stud_sec else ""}>{s}</option>' for s in sections)

    rows = "".join(f"""<tr>
      <td>{r['date']}</td><td>{r['time']}</td>
      <td><span class="pill {'pill-green' if r['status']=='Present' else 'pill-red'}">{r['status']}</span></td>
    </tr>""" for r in reversed(mine)) or \
    '<tr><td colspan="3" style="text-align:center;color:var(--muted);padding:20px">No records</td></tr>'

    # profile image — priority: custom _profile > first face photo > initials
    profile_url = get_profile_image(name)
    msg         = request.args.get("msg","")

    if profile_url:
        avatar_inner = f'<img src="{profile_url}?t={datetime.now().timestamp()}" style="width:110px;height:110px;border-radius:50%;object-fit:cover;border:3px solid var(--border)">'
    else:
        avatar_inner = f'<div class="avatar-placeholder">{name[0].upper()}</div>'

    msg_html = ""
    if msg == "ok":
        msg_html = '<div class="alert alert-success" style="margin-bottom:12px">✅ Profile photo updated!</div>'
    elif msg == "err":
        msg_html = '<div class="alert alert-error" style="margin-bottom:12px">❌ Upload failed. Try again.</div>'
    elif msg == "no_file":
        msg_html = '<div class="alert alert-warn" style="margin-bottom:12px">⚠️ Please select a photo first.</div>'

    sec_badge = f'<div style="margin-bottom:10px"><span class="sec-badge">{stud_sec}</span></div>' if stud_sec else ""

    content = f"""
    <div style="display:flex;gap:8px;margin-bottom:18px">
      <a href="/students" class="btn btn-ghost btn-sm">← All Students</a>
      {f'<a href="/students?section={stud_sec}" class="btn btn-ghost btn-sm">← Section {stud_sec}</a>' if stud_sec else ""}
    </div>
    {msg_html}
    <div class="grid-2" style="align-items:start">

      <!-- LEFT: profile card -->
      <div class="card" style="text-align:center">

        <!-- clickable avatar with hover overlay -->
        <div class="profile-avatar-wrap" onclick="document.getElementById('profileInput').click()" title="Click to change photo">
          {avatar_inner}
          <div class="profile-avatar-overlay">
            <span>📷</span>
            <small>Change Photo</small>
          </div>
        </div>

        <!-- hidden upload form -->
        <form id="profileForm" action="/student/{name}/upload-profile"
              method="POST" enctype="multipart/form-data" style="display:none">
          <input type="file" id="profileInput" name="profile_photo"
                 accept="image/*" onchange="previewAndUpload(this)">
        </form>

        <!-- live preview (shows before submit) -->
        <img id="profilePreview" class="profile-preview" alt="Preview">

        <!-- upload button -->
        <div>
          <label for="profileInput" class="profile-upload-btn">
            📷 &nbsp;{("Change" if profile_url else "Upload")} Profile Photo
          </label>
        </div>

        <div style="margin-top:14px">
          {sec_badge}
          <div style="font-family:'Space Grotesk',sans-serif;font-size:22px;font-weight:700;margin-bottom:4px">{name}</div>
          <div style="margin-bottom:14px;font-size:13.5px">{status_msg}</div>
          <div style="font-family:'Space Grotesk',sans-serif;font-size:42px;font-weight:700;margin-bottom:4px">{s['pct']}%</div>
          <div style="color:var(--muted);font-size:13px;margin-bottom:14px">Attendance Rate</div>
          <div class="pbar-wrap" style="margin-bottom:16px"><div class="pbar {pbar_cls}" style="width:{s['pct']}%"></div></div>
          <div style="display:flex;justify-content:space-around;font-size:13px">
            <div><div style="font-weight:700;font-size:20px;color:var(--green)">{s['present']}</div><div style="color:var(--muted)">Present</div></div>
            <div><div style="font-weight:700;font-size:20px;color:var(--red)">{s['absent']}</div><div style="color:var(--muted)">Absent</div></div>
            <div><div style="font-weight:700;font-size:20px;color:var(--amber)">{s['streak']}</div><div style="color:var(--muted)">Streak</div></div>
          </div>
        </div>

        <!-- face photos used for recognition -->
        <div style="margin-top:20px;padding-top:16px;border-top:1px solid var(--border)">
          <div style="font-size:11px;font-weight:700;color:var(--muted);letter-spacing:1px;margin-bottom:10px">FACE PHOTOS (RECOGNITION)</div>
          <div style="display:flex;flex-wrap:wrap;gap:6px;justify-content:center" id="facePhotos">
          </div>
          <div style="font-size:11px;color:var(--muted);margin-top:8px">
            These are used by the AI scanner. Profile photo above is for display only.
          </div>
        </div>
      </div>

      <!-- RIGHT: history card -->
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

    <script>
    function previewAndUpload(input) {{
      const file = input.files[0];
      if (!file) return;
      // show live preview
      const reader = new FileReader();
      reader.onload = e => {{
        const prev = document.getElementById('profilePreview');
        prev.src = e.target.result;
        prev.style.display = 'block';
        // hide old avatar while previewing
        const wrap = prev.previousElementSibling ? document.querySelector('.profile-avatar-wrap') : null;
      }};
      reader.readAsDataURL(file);
      // auto-submit after short delay so preview is visible
      setTimeout(() => document.getElementById('profileForm').submit(), 600);
    }}

    // load face photo thumbnails via existing img route
    (function(){{
      const faceDiv = document.getElementById('facePhotos');
      // face photos are in /img/{name}/ — we'll just link to the gallery
      faceDiv.innerHTML = '<a href="/gallery" class="btn btn-ghost btn-sm" style="font-size:11.5px">View in Gallery →</a>';
    }})();
    </script>
    """
    return layout(name, content, "students")


# ══════════════════════════════════════════════════════
#  SECTIONS — OVERVIEW + MANAGEMENT
# ══════════════════════════════════════════════════════

SECTION_COLORS = [
    ("59,130,246","3b82f6"),  # blue
    ("6,182,212","06b6d4"),   # cyan
    ("16,185,129","10b981"),  # green
    ("139,92,246","8b5cf6"),  # purple
    ("245,158,11","f59e0b"),  # amber
    ("239,68,68","ef4444"),   # red
    ("236,72,153","ec4899"),  # pink
    ("20,184,166","14b8a6"),  # teal
]

def section_color(idx):
    r, h = SECTION_COLORS[idx % len(SECTION_COLORS)]
    return r, h

@app.route("/sections")
def sections_overview():
    sections = load_sections()
    records  = read_all_records()
    today    = datetime.now().strftime("%Y-%m-%d")

    cards_html = ""
    for i, sec in enumerate(sections):
        rgb, hex_col = section_color(i)
        stud_list    = students_in_section(sec)
        count        = len(stud_list)
        sec_records  = [r for r in records if r.get("section") == sec]
        total_r      = len(sec_records)
        present_r    = sum(1 for r in sec_records if r["status"]=="Present")
        pct          = round(present_r/total_r*100) if total_r else 0
        pbar_cls     = "pbar-green" if pct>=75 else ("pbar-amber" if pct>=50 else "pbar-red")

        today_sec = [r for r in sec_records if r["date"]==today]
        today_p   = sum(1 for r in today_sec if r["status"]=="Present")
        today_pct = round(today_p/len(today_sec)*100) if today_sec else 0

        # avatar strip (up to 5)
        avatars = ""
        for s in stud_list[:5]:
            user_dir = os.path.join(DATA_DIR, s)
            if os.path.isdir(user_dir):
                imgs = [f for f in os.listdir(user_dir)
                        if f.lower().endswith((".jpg",".jpeg",".png")) and not f.startswith("_")]
                if imgs:
                    avatars += f'<img src="/img/{s}/{imgs[0]}" style="width:28px;height:28px;border-radius:50%;object-fit:cover;border:2px solid var(--bg);margin-left:-6px">' 
                    continue
            avatars += f'<div style="width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,rgba({rgb},0.8),rgba({rgb},0.4));display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;border:2px solid var(--bg);margin-left:-6px">{s[0].upper()}</div>'
        more_label   = "" if count<=5 else f'<span style="font-size:11px;color:var(--muted);margin-left:10px">+{count-5} more</span>'
        avatar_strip = f'<div style="display:flex;align-items:center;margin-top:12px;padding-left:6px">{avatars}{more_label}</div>'

        cards_html += f"""
        <a href="/students?section={sec}" class="section-card" style="border-top:3px solid #{hex_col}">
          <div style="display:flex;align-items:start;justify-content:space-between;margin-bottom:12px">
            <div>
              <div class="section-card-name" style="color:#{hex_col}">{sec}</div>
              <div style="font-size:12px;color:var(--muted)">{count} student{"s" if count!=1 else ""}</div>
            </div>
            <div style="text-align:right">
              <div style="font-family:'Space Grotesk',sans-serif;font-size:24px;font-weight:700">{pct}%</div>
              <div style="font-size:11px;color:var(--muted)">overall</div>
            </div>
          </div>
          <div class="pbar-wrap"><div class="pbar {pbar_cls}" style="width:{pct}%"></div></div>
          <div style="display:flex;justify-content:space-between;margin-top:10px;font-size:12px;color:var(--muted)">
            <span>Today: <strong style="color:var(--text)">{today_p} present</strong></span>
            <span>{today_pct}% rate</span>
          </div>
          {avatar_strip}
          <div style="display:flex;gap:8px;margin-top:14px">
            <span style="font-size:12px;padding:4px 10px;border-radius:6px;background:rgba({rgb},0.1);color:#{hex_col}">View Students →</span>
            <span style="font-size:12px;padding:4px 10px;border-radius:6px;background:rgba(255,255,255,0.04);color:var(--muted)">Daily Log</span>
          </div>
        </a>"""

    # summary KPIs
    total_students = sum(len(students_in_section(s)) for s in sections)
    all_records    = len(records)
    all_present    = sum(1 for r in records if r["status"]=="Present")
    overall_pct    = round(all_present/all_records*100) if all_records else 0

    content = f"""
    <div class="sec-head" style="margin-bottom:10px">
      <div><div class="sec-title" style="font-size:20px">📚 Class Sections</div>
      <div class="sec-sub">Overview of all sections — click to filter students</div></div>
      <div style="display:flex;gap:8px">
        <a href="/sections/manage" class="btn btn-ghost btn-sm">⚙ Manage Sections</a>
        <a href="/enroll" class="btn btn-primary">+ Enroll Student</a>
      </div>
    </div>

    <div class="stats-row" style="margin-bottom:22px">
      <div class="stat s-blue">
        <div class="stat-ico" style="background:rgba(59,130,246,0.15)">📚</div>
        <div class="stat-val">{len(sections)}</div>
        <div class="stat-lbl">Total Sections</div>
      </div>
      <div class="stat s-green">
        <div class="stat-ico" style="background:rgba(16,185,129,0.15)">👥</div>
        <div class="stat-val">{total_students}</div>
        <div class="stat-lbl">Total Students</div>
      </div>
      <div class="stat s-amber">
        <div class="stat-ico" style="background:rgba(245,158,11,0.15)">📊</div>
        <div class="stat-val">{overall_pct}%</div>
        <div class="stat-lbl">Overall Rate</div>
      </div>
      <div class="stat s-purple" style="border-top:2px solid var(--purple)">
        <div class="stat-ico" style="background:rgba(139,92,246,0.15)">📋</div>
        <div class="stat-val">{all_records}</div>
        <div class="stat-lbl">Total Records</div>
      </div>
    </div>

    <div class="section-grid">{cards_html or '<div class="card" style="text-align:center;padding:40px;grid-column:1/-1"><div style="font-size:50px;margin-bottom:14px">📚</div><div class="sec-title">No Sections Yet</div><a href="/sections/manage" class="btn btn-primary" style="margin-top:16px;display:inline-flex">⚙ Create Sections</a></div>'}</div>
    """
    return layout("Sections", content, "sections")


@app.route("/sections/manage", methods=["GET","POST"])
def sections_manage():
    sections = load_sections()
    msg = ""

    if request.method == "POST":
        action = request.form.get("action","")
        if action == "add":
            new_sec = request.form.get("new_section","").strip().upper()
            if new_sec and new_sec not in sections:
                sections.append(new_sec)
                save_sections(sections)
                msg = f'<div class="alert alert-success">✅ Section <strong>{new_sec}</strong> added.</div>'
            elif new_sec in sections:
                msg = f'<div class="alert alert-warn">⚠️ Section {new_sec} already exists.</div>'
        elif action == "delete":
            del_sec = request.form.get("del_section","")
            if del_sec in sections:
                sections.remove(del_sec)
                save_sections(sections)
                msg = f'<div class="alert alert-success">✅ Section <strong>{del_sec}</strong> removed.</div>'
        elif action == "reassign":
            student  = request.form.get("student","").strip()
            new_sec  = request.form.get("new_sec","").strip()
            if student and new_sec:
                set_student_section(student, new_sec)
                msg = f'<div class="alert alert-success">✅ {student} moved to <strong>{new_sec}</strong>.</div>'

    # build rows
    section_rows = ""
    for i, sec in enumerate(sections):
        rgb, hex_col = section_color(i)
        count = len(students_in_section(sec))
        section_rows += f"""<tr>
          <td><span style="font-weight:700;color:#{hex_col}">{sec}</span></td>
          <td>{count}</td>
          <td>
            <form method="POST" style="display:inline" onsubmit="return confirm('Delete section {sec}?')">
              <input type="hidden" name="action" value="delete">
              <input type="hidden" name="del_section" value="{sec}">
              <button type="submit" class="btn btn-red btn-sm">🗑 Remove</button>
            </form>
            <a href="/students?section={sec}" class="btn btn-ghost btn-sm">View →</a>
          </td>
        </tr>"""

    # reassign student
    all_s = enrolled_students()
    student_opts = "".join(f'<option value="{s}">{s} ({get_student_section(s) or "unassigned"})</option>' for s in all_s)
    sec_opts     = "".join(f'<option value="{s}">{s}</option>' for s in sections)

    content = f"""
    <div style="margin-bottom:18px">
      <a href="/sections" class="btn btn-ghost btn-sm">← Back to Sections</a>
    </div>
    {msg}
    <div class="grid-2" style="align-items:start">
      <div class="card">
        <div class="sec-title" style="margin-bottom:16px">📚 All Sections</div>
        <div class="tbl-wrap">
          <table>
            <thead><tr><th>Section</th><th>Students</th><th>Actions</th></tr></thead>
            <tbody>{section_rows or '<tr><td colspan="3" style="text-align:center;color:var(--muted);padding:20px">No sections yet</td></tr>'}</tbody>
          </table>
        </div>
        <div style="margin-top:20px;padding-top:16px;border-top:1px solid var(--border)">
          <div class="sec-title" style="font-size:14px;margin-bottom:12px">➕ Add New Section</div>
          <form method="POST" style="display:flex;gap:8px">
            <input type="hidden" name="action" value="add">
            <input type="text" name="new_section" placeholder="e.g. 10B" style="flex:1;margin:0" required>
            <button type="submit" class="btn btn-primary">Add</button>
          </form>
        </div>
      </div>

      <div class="card">
        <div class="sec-title" style="margin-bottom:16px">🔄 Reassign Student to Section</div>
        <form method="POST">
          <input type="hidden" name="action" value="reassign">
          <div class="form-group">
            <label>Student</label>
            <select name="student" required>
              <option value="">— Select Student —</option>
              {student_opts}
            </select>
          </div>
          <div class="form-group">
            <label>Move to Section</label>
            <select name="new_sec" required>
              <option value="">— Select Section —</option>
              {sec_opts}
            </select>
          </div>
          <button type="submit" class="btn btn-cyan" style="width:100%;justify-content:center;padding:12px">
            🔄 Reassign
          </button>
        </form>
      </div>
    </div>
    """
    return layout("Manage Sections", content, "sections")


# ══════════════════════════════════════════════════════
#  ENROLL
# ══════════════════════════════════════════════════════

@app.route("/enroll")
def enroll_page():
    sections    = load_sections()
    sec_options = "".join(f'<option value="{s}">{s}</option>' for s in sections)
    content = f"""
    <div class="sec-head" style="margin-bottom:20px">
      <div><div class="sec-title" style="font-size:20px">📸 Enroll New Student</div>
      <div class="sec-sub">Upload face photos and assign to a class section</div></div>
      <a href="/sections" class="btn btn-ghost btn-sm">⚙ Manage Sections</a>
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
            <label>Class Section</label>
            <select name='section' required>
              <option value="">— Select Section —</option>
              {sec_options}
            </select>
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
          <div>✅ Assign the correct class section</div>
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
        name    = request.form["name"].strip()
        section = request.form.get("section","").strip()
        files   = request.files.getlist("photos")
        os.makedirs(os.path.join(DATA_DIR, name), exist_ok=True)
        if section:
            set_student_section(name, section)
        saved = 0
        for f in files:
            f.save(os.path.join(DATA_DIR, name, f"{datetime.now().timestamp()}.jpg"))
            saved += 1
        sec_badge = f'<span class="sec-badge" style="margin-left:8px">{section}</span>' if section else ""
        content = f"""
        <div class="alert alert-success">✅ {name} enrolled with {saved} photo(s) in section {section or "—"}.</div>
        <div class="card" style="text-align:center;padding:40px">
          <div style="font-size:56px;margin-bottom:14px">🎉</div>
          <div style="display:flex;align-items:center;justify-content:center;gap:8px;margin-bottom:6px">
            <div class="sec-title" style="font-size:20px">{name}</div>{sec_badge}
          </div>
          <div style="color:var(--muted);margin-bottom:22px">{saved} face photo(s) saved.</div>
          <div style="display:flex;gap:10px;justify-content:center">
            <a href="/enroll" class="btn btn-primary">Enroll Another</a>
            <a href="/sections" class="btn btn-ghost">View Sections</a>
            <a href="/students" class="btn btn-ghost">All Students</a>
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

        student_section = get_student_section(person) if person not in ("Unknown","No Face Detected") else ""
        with open(ATT_FILE, "a", newline="") as f:
            csv.writer(f).writerow([person, today, status, time_str, student_section])

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
        prof_url = get_profile_image(name)
        if not prof_url:
            continue
        s = stats_for_student(name, records)
        pbar_cls = "pbar-green" if s["pct"]>=75 else ("pbar-amber" if s["pct"]>=50 else "pbar-red")
        cards += f"""
        <a href="/student/{name}" style="text-decoration:none">
          <div class="gallery-item">
            <img src='{prof_url}' alt='{name}'>
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
#  TEACHER AUTH + DASHBOARD
# ══════════════════════════════════════════════════════

def teacher_required(f):
    """Decorator: redirect to login if not authenticated."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("teacher_logged_in"):
            return redirect("/teacher/login")
        return f(*args, **kwargs)
    return decorated

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

# ── LOGIN ─────────────────────────────────────────────

@app.route("/teacher/login", methods=["GET","POST"])
def teacher_login():
    error = ""
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","").strip()
        if TEACHER_USERS.get(username) == password:
            session["teacher_logged_in"] = True
            session["teacher_name"]      = username
            return redirect("/teacher")
        else:
            error = "Invalid username or password."

    error_html = f'<div class="alert alert-error">{error}</div>' if error else ""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Teacher Login — FaceNova</title>
{CSS}
</head>
<body>
<div class="login-wrap">
  <div class="login-card">
    <div class="login-logo">
      <div class="login-logo-icon">👨‍🏫</div>
      <div class="login-title">Teacher Portal</div>
      <div class="login-sub">Sign in to access your class dashboard</div>
    </div>
    {error_html}
    <form method="POST" action="/teacher/login">
      <div class="form-group">
        <label>Username</label>
        <input type="text" name="username" placeholder="e.g. teacher" required autofocus>
      </div>
      <div class="form-group">
        <label>Password</label>
        <input type="password" name="password" placeholder="••••••••" required>
      </div>
      <button type="submit" class="btn btn-primary" style="width:100%;justify-content:center;padding:13px;font-size:15px;margin-top:6px">
        🔐 &nbsp;Sign In
      </button>
    </form>
    <div style="text-align:center;margin-top:20px;font-size:12px;color:var(--muted)">
      Default: <strong>teacher</strong> / <strong>facenova123</strong>
    </div>
    <div style="text-align:center;margin-top:14px">
      <a href="/" style="color:var(--blue);font-size:13px">← Back to Main Dashboard</a>
    </div>
  </div>
</div>

{_exp_popup}
</body></html>"""
    return html

@app.route("/teacher/logout")
def teacher_logout():
    session.clear()
    return redirect("/teacher/login")

# ── MAIN TEACHER DASHBOARD ────────────────────────────

@app.route("/teacher")
@teacher_required
def teacher_dashboard():
    section   = request.args.get("section","")
    sections  = load_sections()
    records   = read_all_records(section)
    students  = enrolled_students(section)
    today_str = datetime.now().strftime("%Y-%m-%d")
    teacher   = session.get("teacher_name", "Teacher")

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


# ══════════════════════════════════════════════════════
#  SUBSCRIPTION ROUTES
# ══════════════════════════════════════════════════════

@app.route("/upgrade")
def upgrade_page():
    s       = sub_status()
    rec     = s["rec"]
    locked  = request.args.get("locked", "")

    locked_banner = ""
    if locked:
        locked_banner = """<div class="alert alert-warn" style="margin-bottom:20px">
          🔒 <strong>Premium Feature</strong> — This feature requires an active subscription.
          Upgrade below to unlock all features.
        </div>"""

    status_card = ""
    if s["is_trial"]:
        status_card = f"""<div style="background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.2);
          border-radius:14px;padding:16px 20px;margin-bottom:22px;display:flex;align-items:center;gap:14px">
          <span style="font-size:28px">🎉</span>
          <div>
            <div style="font-weight:700;color:var(--blue);margin-bottom:2px">Free Trial Active</div>
            <div style="font-size:13px;color:var(--text2)">{s['days_left']} day{"s" if s['days_left']!=1 else ""} remaining
            · Trial started {rec.get('trial_start','—')} · Ends {rec.get('trial_end','—')}</div>
          </div>
        </div>"""
    elif s["is_premium"]:
        status_card = f"""<div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);
          border-radius:14px;padding:16px 20px;margin-bottom:22px;display:flex;align-items:center;gap:14px">
          <span style="font-size:28px">✅</span>
          <div>
            <div style="font-weight:700;color:var(--green-l);margin-bottom:2px">Premium Active — {rec.get('plan','').title()} Plan</div>
            <div style="font-size:13px;color:var(--text2)">Valid until {rec.get('premium_end','—')}</div>
          </div>
        </div>"""
    elif s["is_expired"]:
        status_card = """<div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);
          border-radius:14px;padding:16px 20px;margin-bottom:22px;display:flex;align-items:center;gap:14px">
          <span style="font-size:28px">🔒</span>
          <div>
            <div style="font-weight:700;color:var(--red-l);margin-bottom:2px">Free Trial Expired</div>
            <div style="font-size:13px;color:var(--text2)">Choose a plan below to restore access. Your data is safe.</div>
          </div>
        </div>"""

    plan_cards = ""
    plan_meta = [
        ("monthly", "💙", "var(--blue)",   "",          ["Face recognition scanning","Up to 500 students","All analytics & reports","Calendar & daily logs","Teacher dashboard","Multi-class sections","CSV export","Email support"]),
        ("yearly",  "💜", "var(--purple)", "Most Popular",["Everything in Monthly","Save ₹889 vs monthly","Priority support","Advanced analytics","Student profile photos","Sections management","Up to 2000 students","Dedicated account manager"]),
        ("5year",   "🌟", "var(--amber)",  "Best Value",  ["Everything in Yearly","Save ₹5,457 vs monthly","Lifetime-like pricing","Up to 10,000 students","White-label option","Custom school branding","API access","Phone support"]),
    ]
    for key, icon, color, badge, features in plan_meta:
        p = PLANS[key]
        badge_html = f'<div class="plan-badge">{badge}</div>' if badge else ""
        popular    = "plan-popular" if badge == "Most Popular" else ""
        feat_html  = "".join(f"<li>{f}</li>" for f in features)
        plan_cards += f"""
        <div class="plan-card plan-{key} {popular}">
          {badge_html}
          <div class="plan-icon">{icon}</div>
          <div class="plan-name">{p['name']}</div>
          <div class="plan-price" style="color:{color}">{p['label'].split('/')[0].strip()}</div>
          <div class="plan-period">per {p['label'].split('/')[1].strip()}</div>
          <ul class="plan-features">{feat_html}</ul>
          <form method="POST" action="/upgrade/activate">
            <input type="hidden" name="plan" value="{key}">
            <button type="submit" class="btn btn-primary" style="width:100%;justify-content:center;padding:13px;font-size:14px">
              🚀 Get {p['name']}
            </button>
          </form>
        </div>"""

    content = f"""
    {locked_banner}
    <div class="upgrade-hero">
      <div style="display:inline-flex;align-items:center;gap:8px;background:rgba(139,92,246,0.15);
        border:1px solid rgba(139,92,246,0.3);border-radius:20px;padding:5px 16px;
        font-size:12px;font-weight:700;color:var(--purple-l);margin-bottom:16px;position:relative;z-index:1">
        ⭐ FaceNova Premium
      </div>
      <h1>Upgrade Your School's<br>Attendance System</h1>
      <p style="max-width:500px;margin:0 auto">
        Unlock unlimited students, advanced AI analytics, multi-class management,
        and priority support. Choose the plan that fits your school.
      </p>
    </div>

    {status_card}

    <div class="plan-grid">{plan_cards}</div>

    <div class="card" style="margin-top:10px">
      <div class="sec-head" style="margin-bottom:16px">
        <div><div class="sec-title">🤝 All Plans Include</div></div>
      </div>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px">
        {"".join(f'<div style="display:flex;align-items:center;gap:10px;font-size:13.5px"><span style="color:var(--green);font-weight:700;font-size:15px">✓</span>{f}</div>'
          for f in ["AI Face Recognition","Attendance Calendar","Daily & Monthly Reports",
                    "Student Profiles","Section Management","Data Export (CSV)",
                    "Teacher Dashboard","Secure Data Storage","Regular Updates","Mobile Friendly"])}
      </div>
    </div>

    <div style="text-align:center;margin-top:20px;color:var(--muted);font-size:12.5px">
      🔒 Secure Payment &nbsp;·&nbsp; All data safe on expiry &nbsp;·&nbsp;
      Cancel anytime &nbsp;·&nbsp;
      <a href="/dev/login" style="color:var(--muted)">Admin</a>
    </div>
    """
    return layout("⭐ Premium Plans", content, "upgrade")


@app.route("/upgrade/activate", methods=["POST"])
def upgrade_activate():
    plan_key = request.form.get("plan","")
    if plan_key not in PLANS:
        return redirect("/upgrade")
    p   = PLANS[plan_key]
    now = datetime.now()
    end = now + timedelta(days=p["period"])
    rec = sub_load()
    rec["status"]         = "active"
    rec["plan"]           = plan_key
    rec["premium_start"]  = now.strftime("%Y-%m-%d")
    rec["premium_end"]    = end.strftime("%Y-%m-%d")
    rec["payment_status"] = "paid"
    rec["history"].append({
        "event":  "activated",
        "plan":   plan_key,
        "date":   now.strftime("%Y-%m-%d %H:%M:%S"),
        "end":    end.strftime("%Y-%m-%d"),
    })
    sub_save(rec)

    content = f"""
    <div style="text-align:center;padding:60px 20px">
      <div style="font-size:72px;margin-bottom:20px">🎉</div>
      <div class="sec-title" style="font-size:26px;margin-bottom:10px">Welcome to Premium!</div>
      <div style="color:var(--text2);font-size:15px;margin-bottom:6px">
        <strong style="color:var(--green-l)">{p['name']}</strong> activated successfully
      </div>
      <div style="color:var(--muted);font-size:13px;margin-bottom:28px">
        Valid until <strong>{end.strftime('%d %B %Y')}</strong>
      </div>
      <div style="display:flex;gap:12px;justify-content:center">
        <a href="/" class="btn btn-primary">🏠 Go to Dashboard</a>
        <a href="/students" class="btn btn-ghost">👥 Students</a>
      </div>
    </div>"""
    return layout("Premium Activated!", content, "upgrade")


# ══════════════════════════════════════════════════════
#  DEVELOPER PANEL
# ══════════════════════════════════════════════════════

@app.route("/dev/login", methods=["GET","POST"])
def dev_login():
    error = ""
    if request.method == "POST":
        u = request.form.get("username","").strip()
        p = request.form.get("password","").strip()
        if DEV_CREDENTIALS.get(u) == p:
            session["dev_logged_in"] = True
            session["dev_user"]      = u
            return redirect("/dev")
        error = "Invalid developer credentials."

    err_html = f'<div class="alert alert-error">{error}</div>' if error else ""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Developer Login — FaceNova</title>
{CSS}
</head>
<body>
<div class="login-wrap">
  <div class="login-card">
    <div class="login-logo">
      <div class="login-logo-icon" style="background:linear-gradient(135deg,#7c3aed,#2563eb)">👑</div>
      <div class="login-title">Developer Portal</div>
      <div class="login-sub">Restricted access · FaceNova Admin</div>
    </div>
    {err_html}
    <form method="POST">
      <div class="form-group">
        <label>Username</label>
        <input type="text" name="username" placeholder="Developer username" required autofocus>
      </div>
      <div class="form-group">
        <label>Password</label>
        <input type="password" name="password" placeholder="••••••••••••" required>
      </div>
      <button type="submit" class="btn btn-primary" style="width:100%;justify-content:center;padding:13px">
        👑 Developer Sign In
      </button>
    </form>
    <div style="text-align:center;margin-top:18px">
      <a href="/" style="color:var(--muted);font-size:12.5px">← Back to App</a>
    </div>
  </div>
</div>
</body></html>"""
    return html


@app.route("/dev/logout")
def dev_logout():
    session.pop("dev_logged_in", None)
    session.pop("dev_user", None)
    return redirect("/")


@app.route("/dev")
def dev_panel():
    if not session.get("dev_logged_in"):
        return redirect("/dev/login")

    rec      = sub_load()
    students = enrolled_students()
    records  = read_all_records()
    sections = load_sections()

    # subscription history
    hist_rows = ""
    for h in reversed(rec.get("history", [])):
        hist_rows += f"""<tr>
          <td>{h.get('date','—')}</td>
          <td style="font-weight:600">{h.get('event','—').upper()}</td>
          <td><span class="pill pill-blue">{PLANS.get(h.get('plan',''),{}).get('name', h.get('plan','—'))}</span></td>
          <td>{h.get('end','—')}</td>
        </tr>"""

    # quick actions
    now = datetime.now()

    content = f"""
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:22px">
      <div>
        <div style="font-family:'Space Grotesk',sans-serif;font-size:22px;font-weight:800;margin-bottom:4px">
          👑 Developer Panel
        </div>
        <div style="color:var(--text2);font-size:13px">Logged in as <strong>{session.get('dev_user')}</strong> · Lifetime Premium</div>
      </div>
      <a href="/dev/logout" class="btn btn-ghost btn-sm">Sign Out</a>
    </div>

    <!-- KPI row -->
    <div class="stats-row" style="margin-bottom:22px">
      <div class="stat s-blue">
        <div class="stat-ico" style="background:rgba(59,130,246,0.15)">👥</div>
        <div class="stat-val">{len(students)}</div>
        <div class="stat-lbl">Total Students</div>
      </div>
      <div class="stat s-green">
        <div class="stat-ico" style="background:rgba(16,185,129,0.15)">📋</div>
        <div class="stat-val">{len(records)}</div>
        <div class="stat-lbl">Attendance Records</div>
      </div>
      <div class="stat s-purple" style="border-top:2px solid var(--purple)">
        <div class="stat-ico" style="background:rgba(139,92,246,0.15)">📚</div>
        <div class="stat-val">{len(sections)}</div>
        <div class="stat-lbl">Sections</div>
      </div>
      <div class="stat s-amber">
        <div class="stat-ico" style="background:rgba(245,158,11,0.15)">⭐</div>
        <div class="stat-val">{rec.get('status','—').upper()}</div>
        <div class="stat-lbl">Sub Status</div>
      </div>
    </div>

    <div class="grid-2" style="align-items:start">

      <!-- Subscription control -->
      <div class="card">
        <div class="sec-title" style="margin-bottom:16px">⚙️ Subscription Control</div>

        <div style="background:rgba(255,255,255,0.03);border:1px solid var(--border);border-radius:10px;padding:14px;margin-bottom:16px;font-size:13px">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
            <div><span style="color:var(--muted)">Status:</span> <strong>{rec.get('status','—').upper()}</strong></div>
            <div><span style="color:var(--muted)">Plan:</span> <strong>{PLANS.get(rec.get('plan',''),{{}}).get('name','—')}</strong></div>
            <div><span style="color:var(--muted)">Trial Start:</span> <strong>{rec.get('trial_start','—')}</strong></div>
            <div><span style="color:var(--muted)">Trial End:</span> <strong>{rec.get('trial_end','—')}</strong></div>
            <div><span style="color:var(--muted)">Premium Start:</span> <strong>{rec.get('premium_start','—')}</strong></div>
            <div><span style="color:var(--muted)">Premium End:</span> <strong>{rec.get('premium_end','—')}</strong></div>
          </div>
        </div>

        <!-- Activate Premium -->
        <form method="POST" action="/dev/action" style="margin-bottom:10px">
          <input type="hidden" name="action" value="activate_premium">
          <div class="form-group">
            <label>Activate Premium Plan</label>
            <select name="plan">
              {"".join(f'<option value="{k}">{v["name"]} — {v["label"]}</option>' for k,v in PLANS.items())}
            </select>
          </div>
          <button type="submit" class="btn btn-green" style="width:100%;justify-content:center">
            ✅ Activate Premium
          </button>
        </form>

        <!-- Extend Trial -->
        <form method="POST" action="/dev/action" style="margin-bottom:10px">
          <input type="hidden" name="action" value="extend_trial">
          <div class="form-group">
            <label>Extend Trial by Days</label>
            <input type="text" name="days" value="10" placeholder="Number of days">
          </div>
          <button type="submit" class="btn btn-cyan" style="width:100%;justify-content:center">
            📅 Extend Trial
          </button>
        </form>

        <!-- Reset to Trial -->
        <form method="POST" action="/dev/action"
              onsubmit="return confirm('Reset subscription to fresh trial?')">
          <input type="hidden" name="action" value="reset_trial">
          <button type="submit" class="btn btn-ghost" style="width:100%;justify-content:center">
            🔄 Reset to Fresh Trial
          </button>
        </form>
      </div>

      <!-- History -->
      <div class="card">
        <div class="sec-title" style="margin-bottom:16px">📋 Subscription History</div>
        <div class="tbl-wrap">
          <table class="dev-table">
            <thead><tr><th>Date</th><th>Event</th><th>Plan</th><th>Valid Until</th></tr></thead>
            <tbody>{hist_rows or '<tr><td colspan="4" style="text-align:center;color:var(--muted);padding:20px">No history yet</td></tr>'}</tbody>
          </table>
        </div>
      </div>
    </div>

    <div style="margin-top:16px;display:flex;gap:10px;flex-wrap:wrap">
      <a href="/" class="btn btn-ghost">🏠 Dashboard</a>
      <a href="/students" class="btn btn-ghost">👥 Students</a>
      <a href="/sections" class="btn btn-ghost">📚 Sections</a>
      <a href="/admin" class="btn btn-ghost">⚙ Admin</a>
      <a href="/upgrade" class="btn btn-ghost">⭐ Upgrade Page</a>
    </div>
    """
    return layout("Developer Panel", content, "admin")


@app.route("/dev/action", methods=["POST"])
def dev_action():
    if not session.get("dev_logged_in"):
        return redirect("/dev/login")

    action = request.form.get("action","")
    rec    = sub_load()
    now    = datetime.now()

    if action == "activate_premium":
        plan_key = request.form.get("plan","monthly")
        if plan_key in PLANS:
            p   = PLANS[plan_key]
            end = now + timedelta(days=p["period"])
            rec["status"]        = "active"
            rec["plan"]          = plan_key
            rec["premium_start"] = now.strftime("%Y-%m-%d")
            rec["premium_end"]   = end.strftime("%Y-%m-%d")
            rec["payment_status"]= "dev_activated"
            rec["history"].append({"event":"dev_activated","plan":plan_key,
                                   "date":now.strftime("%Y-%m-%d %H:%M:%S"),
                                   "end":end.strftime("%Y-%m-%d")})

    elif action == "extend_trial":
        try:
            days = int(request.form.get("days","10"))
        except:
            days = 10
        try:
            cur_end = datetime.strptime(rec["trial_end"], "%Y-%m-%d")
        except:
            cur_end = now
        new_end = max(cur_end, now) + timedelta(days=days)
        rec["trial_end"] = new_end.strftime("%Y-%m-%d")
        if rec.get("status") == "expired":
            rec["status"] = "trial"
        rec["history"].append({"event":"trial_extended","plan":"trial",
                               "date":now.strftime("%Y-%m-%d %H:%M:%S"),
                               "end":new_end.strftime("%Y-%m-%d")})

    elif action == "reset_trial":
        end = now + timedelta(days=TRIAL_DAYS)
        rec["status"]        = "trial"
        rec["plan"]          = None
        rec["trial_start"]   = now.strftime("%Y-%m-%d")
        rec["trial_end"]     = end.strftime("%Y-%m-%d")
        rec["premium_start"] = None
        rec["premium_end"]   = None
        rec["payment_status"]= None
        rec["history"].append({"event":"reset_trial","plan":"trial",
                               "date":now.strftime("%Y-%m-%d %H:%M:%S"),
                               "end":end.strftime("%Y-%m-%d")})

    sub_save(rec)
    return redirect("/dev")
