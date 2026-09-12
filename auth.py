# auth.py — FaceNova Authentication & Authorization
# Uses werkzeug.security (ships with Flask) for password hashing.
# Never stores plain-text passwords. Never trusts client-supplied roles/school_id.

import os
from functools import wraps
from flask import session, redirect, request, g
from werkzeug.security import generate_password_hash, check_password_hash
import db

# ── Password utilities ────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return generate_password_hash(plain, method="pbkdf2:sha256", salt_length=16)

def verify_password(plain: str, hashed: str) -> bool:
    return check_password_hash(hashed, plain)

def generate_temp_password(length=12) -> str:
    import secrets, string
    alphabet = string.ascii_letters + string.digits + "!@#$"
    return "".join(secrets.choice(alphabet) for _ in range(length))


# ── Session helpers ───────────────────────────────────────────────────────

def login_user(user: dict):
    """Write user info into session. Never write role from client — only from DB."""
    session.clear()
    session["user_id"]    = user["id"]
    session["username"]   = user["username"]
    session["role"]       = user["role"]          # from DB — never from form
    session["school_id"]  = user["school_id"]     # from DB — never from form
    session["full_name"]  = user["full_name"] or user["username"]
    session.permanent     = True
    db.user_set_last_login(user["id"])

def logout_user():
    session.clear()

def current_user() -> dict | None:
    """Return current user dict from DB using session user_id."""
    uid = session.get("user_id")
    if not uid:
        return None
    return db.user_get_by_id(uid)

def current_school_id() -> str | None:
    """
    The only trusted source of school_id is the session (set at login from DB).
    Never read school_id from request.form or request.args for auth decisions.
    """
    return session.get("school_id")

def is_authenticated() -> bool:
    return bool(session.get("user_id"))

def has_role(*roles) -> bool:
    return session.get("role") in roles


# ── Route decorators ──────────────────────────────────────────────────────

def login_required(f):
    """Redirect to /login if not authenticated."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not is_authenticated():
            return redirect(f"/login?next={request.path}")
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    """Allow only users with one of the specified roles."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not is_authenticated():
                return redirect(f"/login?next={request.path}")
            if session.get("role") not in roles:
                return _forbidden()
            return f(*args, **kwargs)
        return decorated
    return decorator

def school_admin_required(f):
    """Shortcut: require SCHOOL_ADMIN or SUPER_ADMIN."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not is_authenticated():
            return redirect(f"/login?next={request.path}")
        if session.get("role") not in ("SCHOOL_ADMIN", "SUPER_ADMIN"):
            return _forbidden()
        return f(*args, **kwargs)
    return decorated

def super_admin_required(f):
    """Shortcut: require SUPER_ADMIN only."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not is_authenticated():
            return redirect("/login")
        if session.get("role") != "SUPER_ADMIN":
            return _forbidden()
        return f(*args, **kwargs)
    return decorated

def subscription_check(f):
    """
    If subscription is EXPIRED: allow only dashboard (/), /login, /upgrade.
    All other routes are blocked with a clear message.
    Data is NEVER deleted.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not is_authenticated():
            return f(*args, **kwargs)
        # SUPER_ADMIN always passes
        if session.get("role") == "SUPER_ADMIN":
            return f(*args, **kwargs)
        school_id = current_school_id()
        if not school_id:
            return f(*args, **kwargs)
        sub = db.sub_get(school_id)
        if sub and sub["is_expired"]:
            allowed = ("/", "/login", "/logout", "/upgrade",
                       "/upgrade/activate", "/school/subscription")
            if request.path not in allowed:
                from styles import CSS
                return _subscription_expired_page(CSS, sub)
        return f(*args, **kwargs)
    return decorated


# ── Org-level data isolation ──────────────────────────────────────────────

def school_data_dir(school_id: str) -> str:
    """
    Every school's data lives in data/<school_id>/.
    This is the ONLY correct way to compute school data paths.
    Never use a school_id from the client — always from session.
    """
    path = os.path.join("data", school_id)
    os.makedirs(path, exist_ok=True)
    return path

def assert_same_school(resource_school_id: str):
    """
    Raise a 403 if the resource's school_id doesn't match the logged-in user's school_id.
    SUPER_ADMIN can access any school.
    """
    if session.get("role") == "SUPER_ADMIN":
        return True
    if session.get("school_id") != resource_school_id:
        raise PermissionError("Cross-school access denied")
    return True


# ── Bootstrap: create SUPER_ADMIN on first run ────────────────────────────

def bootstrap_super_admin():
    """
    Called once at startup. Creates the SUPER_ADMIN account from env vars.
    Does nothing if a SUPER_ADMIN already exists.
    Credentials come from environment, never from source code.
    """
    if db.super_admin_exists():
        return

    username = os.environ.get("SUPER_ADMIN_USERNAME", "superadmin")
    password = os.environ.get("SUPER_ADMIN_PASSWORD", "")

    if not password:
        # Generate a secure random password and print it ONCE to the console
        import secrets, string
        password = "".join(
            secrets.choice(string.ascii_letters + string.digits + "!@#$%^&*")
            for _ in range(20)
        )
        print("\n" + "="*60)
        print("  FaceNova — SUPER_ADMIN created on first run")
        print(f"  Username : {username}")
        print(f"  Password : {password}")
        print("  Save this password — it will NOT be shown again.")
        print("  Set SUPER_ADMIN_PASSWORD env var to use your own.")
        print("="*60 + "\n")

    ok, err = db.user_create(
        school_id=None,
        role="SUPER_ADMIN",
        username=username,
        password_hash=hash_password(password),
        full_name="Super Administrator",
        email=os.environ.get("SUPER_ADMIN_EMAIL", ""),
    )
    if not ok:
        print(f"[FaceNova] SUPER_ADMIN bootstrap failed: {err}")


# ── Private helpers ───────────────────────────────────────────────────────

def _forbidden():
    from styles import CSS
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>Access Denied — FaceNova</title>{CSS}</head>
<body>
<div style="min-height:100vh;display:flex;align-items:center;justify-content:center;background:var(--bg)">
  <div style="text-align:center;padding:40px">
    <div style="font-size:60px;margin-bottom:16px">🔒</div>
    <div style="font-family:'Space Grotesk',sans-serif;font-size:22px;font-weight:700;
                color:var(--red-l);margin-bottom:10px">Access Denied</div>
    <div style="color:var(--text2);margin-bottom:24px">
      You don't have permission to view this page.
    </div>
    <a href="/" style="color:var(--blue);font-size:14px">← Go to Dashboard</a>
  </div>
</div></body></html>"""
    from flask import make_response
    return make_response(html, 403)

def _subscription_expired_page(CSS, sub):
    from flask import make_response
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>Subscription Expired — FaceNova</title>{CSS}</head>
<body>
<div style="min-height:100vh;display:flex;align-items:center;justify-content:center;
            background:var(--bg)">
  <div style="max-width:480px;width:90%;background:var(--card);border:1px solid
              rgba(239,68,68,0.3);border-radius:22px;padding:44px 38px;text-align:center;
              box-shadow:0 32px 80px rgba(0,0,0,0.6)">
    <div style="font-size:58px;margin-bottom:18px">🔒</div>
    <div style="font-family:'Space Grotesk',sans-serif;font-size:22px;font-weight:800;
                color:var(--red-l);margin-bottom:10px">Subscription Expired</div>
    <div style="color:var(--text2);font-size:14px;line-height:1.7;margin-bottom:24px">
      Your {sub.get('plan_name','').replace('_',' ')} subscription has expired.<br>
      <strong style="color:var(--text)">All your data is safe</strong> — nothing has been deleted.<br>
      Upgrade to restore full access.
    </div>
    <a href="/upgrade" style="display:block;padding:14px;background:linear-gradient(135deg,
       #2563eb,#7c3aed);color:white;border-radius:12px;font-weight:700;
       font-size:15px;text-decoration:none;margin-bottom:12px">
      🚀 View Upgrade Plans
    </a>
    <a href="/" style="font-size:13px;color:var(--text2);text-decoration:none">
      ← Return to Dashboard
    </a>
    <div style="margin-top:20px;font-size:12px;color:var(--muted)">
      Need help? Contact FaceNova support.
    </div>
  </div>
</div></body></html>"""
    return make_response(html, 402)
