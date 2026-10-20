# styles.py — FaceNova Premium UI v6 (Bright, colourful, app-style)
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{color-scheme:light;scroll-behavior:smooth}
::selection{background:rgba(99,102,241,0.22)}

/* ══ DESIGN TOKENS ═══════════════════════════════════ */
:root{
  --bg:#f3f5ff;--surface:#eaeeff;--card:#ffffff;--card2:#f8f9ff;
  --border:rgba(99,102,241,0.14);
  --border2:rgba(99,102,241,0.26);
  --border3:rgba(99,102,241,0.42);

  --blue:#6366f1;--blue-d:#4f46e5;--blue-l:#4f46e5;
  --cyan:#0891b2;--cyan-d:#0e7490;
  --green:#10b981;--green-l:#059669;
  --red:#ef4444;--red-l:#dc2626;
  --amber:#f59e0b;--amber-l:#d97706;
  --purple:#8b5cf6;--purple-l:#7c3aed;
  --pink:#ec4899;

  --text:#1e1b4b;--text2:#52607a;--muted:#6b7a90;--muted2:#94a3b8;

  --sidebar-w:262px;
  --radius:18px;--radius-sm:12px;--radius-xs:9px;
  --t:0.2s cubic-bezier(.4,0,.2,1);

  --shadow-sm:0 1px 2px rgba(30,27,75,0.06),0 2px 10px rgba(79,70,229,0.06);
  --shadow:0 6px 24px rgba(79,70,229,0.10),0 1px 3px rgba(30,27,75,0.05);
  --shadow-lg:0 16px 48px rgba(79,70,229,0.18),0 2px 8px rgba(30,27,75,0.06);
  --grad:linear-gradient(135deg,#4f46e5 0%,#7c3aed 55%,#06b6d4 100%);
}

/* ══ BASE ════════════════════════════════════════════ */
body{
  font-family:'Inter',sans-serif;
  background:var(--bg);color:var(--text);
  min-height:100vh;display:flex;line-height:1.6;
  -webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;
  background-image:
    radial-gradient(ellipse 60% 45% at 85% -5%,rgba(139,92,246,0.14),transparent),
    radial-gradient(ellipse 50% 40% at -5% 100%,rgba(6,182,212,0.12),transparent),
    radial-gradient(rgba(99,102,241,0.10) 1px,transparent 1px);
  background-size:auto,auto,26px 26px;
  background-attachment:fixed;
}
a{-webkit-tap-highlight-color:transparent}
:focus-visible{outline:2.5px solid rgba(99,102,241,0.55);outline-offset:2px}
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:linear-gradient(180deg,#818cf8,#a78bfa);border-radius:10px}

/* ══ SIDEBAR ═════════════════════════════════════════ */
.sidebar{
  width:var(--sidebar-w);
  background:linear-gradient(180deg,#ffffff 0%,#f6f7ff 100%);
  border-right:1px solid var(--border);
  display:flex;flex-direction:column;
  position:fixed;top:0;bottom:0;left:0;z-index:100;overflow:hidden;
  box-shadow:6px 0 36px rgba(79,70,229,0.08);
}
.sidebar::before{
  content:'';position:absolute;top:-70px;left:-70px;width:240px;height:240px;border-radius:50%;
  background:radial-gradient(circle,rgba(99,102,241,0.14),transparent 70%);pointer-events:none;
}
.sidebar::after{
  content:'';position:absolute;bottom:40px;right:-60px;width:200px;height:200px;border-radius:50%;
  background:radial-gradient(circle,rgba(6,182,212,0.10),transparent 70%);pointer-events:none;
}
.sidebar-logo{padding:22px 20px 16px;border-bottom:1px solid var(--border);position:relative;z-index:1}
.logo-mark{display:flex;align-items:center;gap:12px}
.logo-icon{
  width:40px;height:40px;border-radius:12px;background:var(--grad);
  display:flex;align-items:center;justify-content:center;font-size:19px;flex-shrink:0;
  box-shadow:0 6px 18px rgba(79,70,229,0.4);
  animation:logo-float 4s ease-in-out infinite;
}
@keyframes logo-float{0%,100%{transform:translateY(0) rotate(0)}50%{transform:translateY(-3px) rotate(3deg)}}
.logo-text{font-family:'Space Grotesk',sans-serif;font-size:20px;font-weight:800;letter-spacing:-0.6px;color:var(--text)}
.logo-text span{background:var(--grad);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.logo-tag{font-size:9px;font-weight:700;letter-spacing:2px;color:var(--muted2);text-transform:uppercase;margin-top:2px}
.sidebar-section{font-size:9.5px;font-weight:700;letter-spacing:2.2px;color:var(--muted2);text-transform:uppercase;padding:20px 20px 6px;position:relative;z-index:1}
.nav-item{
  display:flex;align-items:center;gap:11px;padding:10px 16px 10px 18px;
  color:var(--text2);text-decoration:none;font-size:13.5px;font-weight:500;
  transition:all var(--t);border-radius:13px;margin:2px 12px;position:relative;z-index:1;
}
.nav-item svg{width:17px;height:17px;flex-shrink:0;opacity:0.65;transition:all var(--t)}
.nav-item:hover{color:var(--blue-d);background:rgba(99,102,241,0.09);transform:translateX(2px)}
.nav-item:hover svg{opacity:1}
.nav-active{
  color:#fff!important;background:var(--grad)!important;font-weight:600!important;
  box-shadow:0 8px 22px rgba(79,70,229,0.38);transform:none!important;
}
.nav-active svg{opacity:1!important}
.sidebar-footer{margin-top:auto;padding:14px 20px 18px;border-top:1px solid var(--border);position:relative;z-index:1}
.status-dot{
  display:inline-block;width:8px;height:8px;background:var(--green);border-radius:50%;margin-right:8px;
  box-shadow:0 0 0 3px rgba(16,185,129,0.2);animation:pulse-dot 2.5s infinite;
}
@keyframes pulse-dot{0%,100%{box-shadow:0 0 0 3px rgba(16,185,129,0.22)}50%{box-shadow:0 0 0 7px rgba(16,185,129,0.04)}}

/* ══ MAIN + TOPBAR ═══════════════════════════════════ */
.main{margin-left:var(--sidebar-w);flex:1;display:flex;flex-direction:column;min-height:100vh;min-width:0}
.topbar{
  height:60px;padding:0 28px;background:rgba(255,255,255,0.82);
  backdrop-filter:blur(22px) saturate(1.8);-webkit-backdrop-filter:blur(22px) saturate(1.8);
  border-bottom:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between;
  position:sticky;top:0;z-index:50;box-shadow:0 4px 20px rgba(79,70,229,0.05);
}
.topbar-title{font-family:'Space Grotesk',sans-serif;font-size:16px;font-weight:700;letter-spacing:-0.3px}
.topbar-right{display:flex;align-items:center;gap:10px}
.tbadge{
  background:linear-gradient(135deg,rgba(79,70,229,0.10),rgba(124,58,237,0.08));
  border:1px solid rgba(99,102,241,0.25);color:var(--blue-d);
  padding:5px 13px;border-radius:20px;font-size:11px;font-weight:700;letter-spacing:0.3px;
}
.page{padding:24px 28px;flex:1}

/* ══ HERO BANNERS ════════════════════════════════════ */
.hero,.td-hero{
  border-radius:24px;padding:30px 30px;margin-bottom:22px;position:relative;overflow:hidden;
  background:var(--grad);color:#fff;
  box-shadow:0 18px 50px rgba(79,70,229,0.32);
  animation:fadeUp 0.55s cubic-bezier(.34,1.2,.64,1) both;
}
.hero::before,.td-hero::before{
  content:'';position:absolute;top:-80px;right:-60px;width:280px;height:280px;border-radius:50%;
  background:rgba(255,255,255,0.10);pointer-events:none;
}
.hero::after{
  content:'';position:absolute;bottom:-90px;left:12%;width:240px;height:240px;border-radius:50%;
  background:rgba(255,255,255,0.07);pointer-events:none;
}
.td-hero::after{content:'👨‍🏫';position:absolute;right:26px;top:50%;transform:translateY(-50%);font-size:72px;opacity:0.18}
.hero h1,.td-hero h1{
  font-family:'Space Grotesk',sans-serif;font-size:24px;font-weight:800;margin-bottom:6px;
  letter-spacing:-0.6px;position:relative;z-index:1;color:#fff;
}
.hero p,.td-hero p{color:rgba(255,255,255,0.88);font-size:13.5px;line-height:1.65;position:relative;z-index:1;word-break:break-word}
.hero>div,.hero-actions{position:relative;z-index:1}
.hero>div[style*="inline-flex"]{
  background:rgba(255,255,255,0.18)!important;color:#fff!important;
  border:1px solid rgba(255,255,255,0.35)!important;backdrop-filter:blur(6px);
}
.hero-actions{margin-top:18px;display:flex;gap:10px;flex-wrap:wrap;width:100%}
.hero-actions .btn{flex:1;min-width:0;justify-content:center}
.hero .btn-cyan,.td-hero .btn-cyan{background:#fff;color:var(--blue-d);box-shadow:0 8px 24px rgba(0,0,0,0.18)}
.hero .btn-cyan:hover,.td-hero .btn-cyan:hover{box-shadow:0 12px 30px rgba(0,0,0,0.24)}
.hero .btn-ghost,.td-hero .btn-ghost{background:rgba(255,255,255,0.16);color:#fff;border:1.5px solid rgba(255,255,255,0.4);box-shadow:none}
.hero .btn-ghost:hover,.td-hero .btn-ghost:hover{background:rgba(255,255,255,0.26);color:#fff}
.hero .btn-primary,.td-hero .btn-primary{background:#fff;color:var(--blue-d)}

/* ══ STAT CARDS ══════════════════════════════════════ */
.stats-row{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:22px}
.stat{
  background:var(--card);border:1px solid var(--border);border-radius:var(--radius);
  padding:20px 18px;position:relative;overflow:hidden;box-shadow:var(--shadow-sm);
  transition:transform var(--t),box-shadow var(--t);
  animation:fadeUp 0.5s cubic-bezier(.34,1.2,.64,1) both;
}
.stat:nth-child(1){animation-delay:.05s}.stat:nth-child(2){animation-delay:.11s}
.stat:nth-child(3){animation-delay:.17s}.stat:nth-child(4){animation-delay:.23s}
.stat:hover{transform:translateY(-5px);box-shadow:var(--shadow-lg)}
.stat::before{content:'';position:absolute;top:0;left:0;right:0;height:4px}
.stat::after{content:'';position:absolute;bottom:-26px;right:-26px;width:100px;height:100px;border-radius:50%;opacity:0.10}
.s-blue::before{background:linear-gradient(90deg,#4f46e5,#818cf8)}.s-blue::after{background:#4f46e5}
.s-green::before{background:linear-gradient(90deg,#059669,#34d399)}.s-green::after{background:#10b981}
.s-red::before{background:linear-gradient(90deg,#dc2626,#f87171)}.s-red::after{background:#ef4444}
.s-amber::before{background:linear-gradient(90deg,#d97706,#fbbf24)}.s-amber::after{background:#f59e0b}
.s-purple::before{background:linear-gradient(90deg,#7c3aed,#c4b5fd)}.s-purple::after{background:#8b5cf6}
.stat-ico{width:42px;height:42px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:18px;margin-bottom:14px}
.stat-val{
  font-family:'Space Grotesk',sans-serif;font-size:34px;font-weight:800;line-height:1;
  margin-bottom:5px;letter-spacing:-1.5px;animation:countUp 0.6s 0.2s cubic-bezier(.34,1.4,.64,1) both;
}
.stat-lbl{font-size:12px;color:var(--text2);font-weight:600}

/* ══ PROGRESS ════════════════════════════════════════ */
.pbar-wrap{background:rgba(99,102,241,0.10);border-radius:20px;height:8px;overflow:hidden}
.pbar{height:100%;border-radius:20px;transition:width 1.2s cubic-bezier(.4,0,.2,1);position:relative;overflow:hidden}
.pbar::after{
  content:'';position:absolute;inset:0;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,0.5),transparent);
  transform:translateX(-100%);animation:sheen 2.6s ease-in-out infinite;
}
@keyframes sheen{to{transform:translateX(100%)}}
.pbar-green{background:linear-gradient(90deg,#059669,#34d399)}
.pbar-amber{background:linear-gradient(90deg,#d97706,#fbbf24)}
.pbar-red{background:linear-gradient(90deg,#dc2626,#f87171)}
.pbar-blue{background:linear-gradient(90deg,#4f46e5,#06b6d4)}

/* ══ CARDS ═══════════════════════════════════════════ */
.card{
  background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:22px;
  box-shadow:var(--shadow-sm);transition:box-shadow var(--t),border-color var(--t),transform var(--t);
  animation:fadeUp 0.5s 0.08s cubic-bezier(.34,1.1,.64,1) both;
}
.card:hover{box-shadow:var(--shadow);border-color:var(--border2)}
.card-glass{
  background:rgba(255,255,255,0.7);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border:1px solid var(--border);border-radius:var(--radius);padding:22px;box-shadow:var(--shadow-sm);
}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.grid-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}
.sec-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;gap:10px}
.sec-title{font-family:'Space Grotesk',sans-serif;font-size:16px;font-weight:700;letter-spacing:-0.3px;color:var(--text)}
.sec-sub{font-size:12px;color:var(--muted);margin-top:2px}

/* ══ TABLES ══════════════════════════════════════════ */
.tbl-wrap{overflow-x:auto;border-radius:var(--radius-sm)}
table{width:100%;border-collapse:collapse;font-size:13px}
thead th{
  background:linear-gradient(180deg,rgba(99,102,241,0.07),rgba(99,102,241,0.03));
  padding:11px 14px;text-align:left;font-size:10px;font-weight:700;letter-spacing:1.3px;
  text-transform:uppercase;color:var(--blue-d);border-bottom:1px solid var(--border);
}
tbody td{padding:12px 14px;border-bottom:1px solid rgba(99,102,241,0.08);transition:background var(--t);color:var(--text)}
tbody tr:hover td{background:rgba(99,102,241,0.04)}
tbody tr:last-child td{border-bottom:none}
tbody tr{animation:fadeIn 0.35s ease both}

/* ══ PILLS ═══════════════════════════════════════════ */
.pill{display:inline-flex;align-items:center;gap:4px;padding:3px 11px;border-radius:20px;font-size:11px;font-weight:700;letter-spacing:0.2px}
.pill-green{background:rgba(16,185,129,0.12);color:#047857;border:1px solid rgba(16,185,129,0.28)}
.pill-red{background:rgba(239,68,68,0.10);color:#b91c1c;border:1px solid rgba(239,68,68,0.26)}
.pill-amber{background:rgba(245,158,11,0.13);color:#b45309;border:1px solid rgba(245,158,11,0.3)}
.pill-blue{background:rgba(99,102,241,0.10);color:var(--blue-d);border:1px solid rgba(99,102,241,0.26)}
.pill-purple{background:rgba(139,92,246,0.11);color:#6d28d9;border:1px solid rgba(139,92,246,0.28)}

/* ══ BUTTONS ═════════════════════════════════════════ */
.btn{
  display:inline-flex;align-items:center;gap:7px;padding:10px 19px;border:none;border-radius:var(--radius-sm);
  font-size:13px;font-weight:600;cursor:pointer;transition:all var(--t);text-decoration:none;
  font-family:'Inter',sans-serif;position:relative;overflow:hidden;-webkit-tap-highlight-color:transparent;
}
.btn::before{
  content:'';position:absolute;top:0;left:-80%;width:60%;height:100%;
  background:linear-gradient(100deg,transparent,rgba(255,255,255,0.35),transparent);
  transform:skewX(-20deg);transition:left 0.55s ease;pointer-events:none;
}
.btn:hover::before{left:130%}
.btn-primary{background:linear-gradient(135deg,#4f46e5,#7c3aed);color:#fff;box-shadow:0 6px 18px rgba(79,70,229,0.38)}
.btn-primary:hover{transform:translateY(-2px);box-shadow:0 12px 28px rgba(79,70,229,0.48)}
.btn-primary:active{transform:translateY(0)}
.btn-cyan{background:linear-gradient(135deg,#0891b2,#06b6d4);color:#fff;box-shadow:0 6px 18px rgba(6,182,212,0.38)}
.btn-cyan:hover{transform:translateY(-2px);box-shadow:0 12px 28px rgba(6,182,212,0.48)}
.btn-ghost{background:#fff;color:var(--text);border:1.5px solid var(--border2);box-shadow:var(--shadow-sm)}
.btn-ghost:hover{background:var(--surface);border-color:var(--border3);color:var(--blue-d);transform:translateY(-1px);box-shadow:var(--shadow)}
.btn-red{background:rgba(239,68,68,0.09);color:#b91c1c;border:1.5px solid rgba(239,68,68,0.25)}
.btn-red:hover{background:rgba(239,68,68,0.17);transform:translateY(-1px)}
.btn-green{background:linear-gradient(135deg,#059669,#10b981);color:#fff;box-shadow:0 6px 18px rgba(16,185,129,0.38)}
.btn-green:hover{transform:translateY(-2px);box-shadow:0 12px 28px rgba(16,185,129,0.48)}
.btn-sm{padding:7px 14px;font-size:12px}
.btn-xs{padding:4px 11px;font-size:11px;border-radius:8px}
.btn::after{
  content:'';position:absolute;width:90px;height:90px;background:rgba(255,255,255,0.3);border-radius:50%;
  transform:scale(0);opacity:0;top:50%;left:50%;margin:-45px 0 0 -45px;pointer-events:none;
}
.btn:active::after{animation:rippleBtn .45s ease-out}
@keyframes rippleBtn{0%{transform:scale(0);opacity:1}100%{transform:scale(3);opacity:0}}

/* ══ FORMS ═══════════════════════════════════════════ */
.form-group{margin-bottom:16px}
label{display:block;font-size:11px;font-weight:700;color:var(--blue-d);margin-bottom:7px;letter-spacing:0.5px;text-transform:uppercase}
input[type=text],input[type=password],input[type=email],input[type=number],input[type=search],input[type=tel],input[type=date],select,textarea{
  width:100%;background:#fff;border:1.5px solid var(--border2);border-radius:var(--radius-xs);
  padding:11px 14px;color:var(--text);font-size:14px;font-family:'Inter',sans-serif;
  transition:all var(--t);outline:none;box-shadow:var(--shadow-sm);
}
input[type=text]:focus,input[type=password]:focus,input[type=email]:focus,input[type=number]:focus,
input[type=search]:focus,input[type=tel]:focus,input[type=date]:focus,select:focus,textarea:focus{
  border-color:var(--blue);box-shadow:0 0 0 4px rgba(99,102,241,0.14),var(--shadow-sm);
}
input::placeholder,textarea::placeholder{color:var(--muted2)}
select option{background:#fff;color:var(--text)}
input[type=checkbox]{accent-color:var(--blue-d)}
input[type=file]{
  width:100%;background:rgba(99,102,241,0.04);border:2px dashed rgba(99,102,241,0.32);
  border-radius:var(--radius-sm);padding:16px 14px;color:var(--text2);font-size:13px;
  font-family:'Inter',sans-serif;cursor:pointer;transition:all var(--t);
}
input[type=file]:hover{border-color:var(--blue);background:rgba(99,102,241,0.09)}

/* ══ ALERTS ══════════════════════════════════════════ */
.alert{padding:12px 16px;border-radius:var(--radius-xs);font-size:13px;margin-bottom:16px;display:flex;align-items:center;gap:9px;font-weight:500;animation:slideIn .35s cubic-bezier(.34,1.3,.64,1)}
@keyframes slideIn{from{opacity:0;transform:translateY(-10px)}to{opacity:1;transform:none}}
.alert-success{background:rgba(16,185,129,0.10);border:1.5px solid rgba(16,185,129,0.28);color:#047857}
.alert-error{background:rgba(239,68,68,0.09);border:1.5px solid rgba(239,68,68,0.26);color:#b91c1c}
.alert-info{background:rgba(99,102,241,0.09);border:1.5px solid rgba(99,102,241,0.26);color:var(--blue-d)}
.alert-warn{background:rgba(245,158,11,0.12);border:1.5px solid rgba(245,158,11,0.3);color:#b45309}
.notice{padding:11px 15px;border-radius:var(--radius-xs);font-size:13px;display:flex;align-items:center;gap:8px;margin-bottom:9px}
.notice-warn{background:rgba(245,158,11,0.12);border:1.5px solid rgba(245,158,11,0.3);color:#b45309}

/* ══ LOG ITEMS ═══════════════════════════════════════ */
.log-item{display:flex;align-items:center;gap:13px;padding:11px 0;border-bottom:1px solid rgba(99,102,241,0.08);transition:all var(--t)}
.log-item:last-child{border-bottom:none}
.log-item:hover{padding-left:5px}
.log-avatar{
  width:38px;height:38px;border-radius:11px;flex-shrink:0;background:linear-gradient(135deg,#4f46e5,#8b5cf6);
  display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px;color:#fff;
  box-shadow:0 4px 12px rgba(79,70,229,0.28);
}
.log-info{flex:1;min-width:0}
.log-name{font-weight:600;font-size:13.5px;color:var(--text)}
.log-time{font-size:11.5px;color:var(--muted);margin-top:1px}

/* ══ LOGIN / SETUP ═══════════════════════════════════ */
.login-wrap{
  min-height:100vh;width:100%;display:flex;align-items:center;justify-content:center;padding:20px;
  background:linear-gradient(135deg,#eef2ff 0%,#f5f3ff 50%,#ecfeff 100%);
  background-image:
    radial-gradient(ellipse 60% 50% at 25% 15%,rgba(99,102,241,0.20),transparent),
    radial-gradient(ellipse 50% 45% at 85% 85%,rgba(139,92,246,0.18),transparent),
    radial-gradient(ellipse 40% 40% at 60% 55%,rgba(6,182,212,0.12),transparent);
}
.login-card{
  background:rgba(255,255,255,0.92);backdrop-filter:blur(30px);-webkit-backdrop-filter:blur(30px);
  border:1.5px solid rgba(99,102,241,0.18);border-radius:28px;padding:40px 36px;width:100%;max-width:430px;
  box-shadow:0 30px 80px rgba(79,70,229,0.22);position:relative;overflow:hidden;
  animation:cardPop .5s cubic-bezier(.34,1.3,.64,1) both;
}
@keyframes cardPop{from{opacity:0;transform:scale(0.92) translateY(18px)}to{opacity:1;transform:none}}
.login-card::before{content:'';position:absolute;top:0;left:0;right:0;height:5px;background:var(--grad)}
.login-logo{text-align:center;margin-bottom:28px}
.login-logo-icon{
  width:68px;height:68px;border-radius:20px;margin:0 auto 16px;background:var(--grad);
  display:flex;align-items:center;justify-content:center;font-size:30px;
  box-shadow:0 12px 32px rgba(79,70,229,0.4);animation:logo-float 4s ease-in-out infinite;
}
.login-title{font-family:'Space Grotesk',sans-serif;font-size:25px;font-weight:800;letter-spacing:-0.7px;margin-bottom:4px}
.login-sub{font-size:13.5px;color:var(--muted)}

/* ══ FACE SCAN — APP STYLE ═══════════════════════════ */
.scan-app-wrap{display:flex;flex-direction:column;align-items:center;max-width:480px;margin:0 auto}
.scan-viewfinder{
  width:100%;aspect-ratio:3/4;max-height:62vh;background:#0b1020;border-radius:28px;overflow:hidden;position:relative;
  box-shadow:0 0 0 4px rgba(99,102,241,0.35),0 28px 70px rgba(79,70,229,0.35);
}
.scan-viewfinder video{width:100%;height:100%;object-fit:cover;display:block;border-radius:0}
.vf-corner{position:absolute;width:30px;height:30px;z-index:10}
.vf-tl{top:16px;left:16px;border-top:3.5px solid #22d3ee;border-left:3.5px solid #22d3ee;border-radius:8px 0 0 0;animation:cornerGlow 2s ease-in-out infinite}
.vf-tr{top:16px;right:16px;border-top:3.5px solid #22d3ee;border-right:3.5px solid #22d3ee;border-radius:0 8px 0 0;animation:cornerGlow 2s ease-in-out infinite .25s}
.vf-bl{bottom:16px;left:16px;border-bottom:3.5px solid #22d3ee;border-left:3.5px solid #22d3ee;border-radius:0 0 0 8px;animation:cornerGlow 2s ease-in-out infinite .5s}
.vf-br{bottom:16px;right:16px;border-bottom:3.5px solid #22d3ee;border-right:3.5px solid #22d3ee;border-radius:0 0 8px 0;animation:cornerGlow 2s ease-in-out infinite .75s}
@keyframes cornerGlow{0%,100%{opacity:0.7;box-shadow:none}50%{opacity:1;box-shadow:0 0 14px rgba(34,211,238,0.7)}}
.vf-beam{
  position:absolute;left:0;right:0;height:2.5px;z-index:9;
  background:linear-gradient(90deg,transparent,rgba(34,211,238,0.95),transparent);
  box-shadow:0 0 18px rgba(34,211,238,0.8);animation:beamScan 2.5s ease-in-out infinite;
}
@keyframes beamScan{0%{top:10%;opacity:0}5%{opacity:1}95%{opacity:1}100%{top:90%;opacity:0}}
.vf-face-ring{
  position:absolute;top:50%;left:50%;transform:translate(-50%,-52%);width:170px;height:195px;border-radius:50%;
  border:2.5px solid rgba(34,211,238,0.5);z-index:9;animation:faceRing 2.5s ease-in-out infinite;
}
.vf-face-ring::before{content:'';position:absolute;inset:-12px;border-radius:50%;border:1.5px solid rgba(34,211,238,0.3);animation:faceRingInner 2.5s ease-in-out infinite .5s}
@keyframes faceRingInner{0%,100%{opacity:0.35}50%{opacity:1}}
@keyframes faceRing{
  0%,100%{border-color:rgba(34,211,238,0.45);transform:translate(-50%,-52%) scale(1)}
  50%{border-color:rgba(34,211,238,0.9);transform:translate(-50%,-52%) scale(1.04)}
}
.vf-live-badge{
  position:absolute;top:16px;left:50%;transform:translateX(-50%);background:rgba(11,16,32,0.6);
  backdrop-filter:blur(8px);border:1px solid rgba(52,211,153,0.5);border-radius:20px;padding:5px 13px;
  font-size:11px;font-weight:700;color:#6ee7b7;display:flex;align-items:center;gap:6px;z-index:10;
}
.vf-live-dot{width:7px;height:7px;border-radius:50%;background:#34d399;box-shadow:0 0 8px #34d399;animation:pulse-dot 1.5s infinite}
.vf-instruction{position:absolute;bottom:0;left:0;right:0;background:linear-gradient(0deg,rgba(11,16,32,0.8),transparent);padding:28px 16px 18px;text-align:center;z-index:10}
.vf-instruction p{font-size:13px;color:rgba(255,255,255,0.92);font-weight:500}
.scan-btn-wrap{width:100%;padding:18px 0 4px}
.scan-btn-main{
  width:100%;padding:17px;border-radius:var(--radius);font-size:16px;font-weight:700;
  background:linear-gradient(135deg,#4f46e5 0%,#7c3aed 50%,#06b6d4 100%);color:#fff;border:none;cursor:pointer;
  display:flex;align-items:center;justify-content:center;gap:10px;
  box-shadow:0 12px 32px rgba(79,70,229,0.42);transition:all var(--t);font-family:'Inter',sans-serif;
  position:relative;overflow:hidden;-webkit-tap-highlight-color:transparent;
}
.scan-btn-main:hover{transform:translateY(-2px);box-shadow:0 16px 40px rgba(79,70,229,0.52)}
.scan-btn-main:active{transform:scale(0.97)}
.scan-btn-main:disabled{opacity:0.8;cursor:wait}
.scan-result-card{
  width:100%;background:var(--card);border:1px solid var(--border2);border-radius:var(--radius);padding:22px;margin-top:16px;
  box-shadow:var(--shadow-lg);animation:scaleIn .4s cubic-bezier(.34,1.3,.64,1) both;
}
.scan-result-avatar{width:84px;height:84px;border-radius:50%;object-fit:cover;margin:0 auto 12px;display:block;border:4px solid var(--green)}
.scan-result-avatar-placeholder{
  width:84px;height:84px;border-radius:50%;background:linear-gradient(135deg,#4f46e5,#8b5cf6);
  display:flex;align-items:center;justify-content:center;font-size:30px;font-weight:800;color:#fff;
  margin:0 auto 12px;border:4px solid var(--border2);
}
.scan-result-name{font-family:'Space Grotesk',sans-serif;font-size:22px;font-weight:800;text-align:center;margin-bottom:6px;letter-spacing:-0.5px}
.scan-result-status{display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:12px}

/* ══ ENROLL — APP STYLE ══════════════════════════════ */
.enroll-app{max-width:520px;margin:0 auto}
.enroll-hero{
  background:var(--grad);color:#fff;border-radius:22px;padding:22px;margin-bottom:18px;
  display:flex;align-items:center;gap:16px;box-shadow:0 16px 44px rgba(79,70,229,0.3);
  position:relative;overflow:hidden;animation:fadeUp .45s cubic-bezier(.34,1.2,.64,1) both;
}
.enroll-hero::before{content:'';position:absolute;top:-60px;right:-40px;width:180px;height:180px;border-radius:50%;background:rgba(255,255,255,0.1)}
.enroll-hero-icon{
  width:56px;height:56px;border-radius:16px;flex-shrink:0;background:rgba(255,255,255,0.2);
  border:1px solid rgba(255,255,255,0.35);display:flex;align-items:center;justify-content:center;font-size:25px;position:relative;
}
.enroll-hero h2{font-family:'Space Grotesk',sans-serif;font-size:18px;font-weight:800;margin-bottom:3px;letter-spacing:-0.4px;position:relative}
.enroll-hero p{font-size:12.5px;color:rgba(255,255,255,0.9);line-height:1.5;position:relative}
.enroll-step{
  display:flex;gap:13px;align-items:flex-start;background:var(--card);border:1px solid var(--border);
  border-radius:var(--radius-sm);padding:14px;margin-bottom:11px;box-shadow:var(--shadow-sm);transition:all var(--t);
}
.enroll-step:hover{transform:translateX(4px);border-color:var(--border2);box-shadow:var(--shadow)}
.enroll-step-num{
  width:30px;height:30px;border-radius:9px;flex-shrink:0;background:var(--grad);
  display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;color:#fff;
  box-shadow:0 4px 12px rgba(79,70,229,0.32);
}
.enroll-step h4{font-size:13.5px;font-weight:700;margin-bottom:2px;color:var(--text)}
.enroll-step p{font-size:12px;color:var(--text2);line-height:1.5}

/* ══ STUDENTS / GALLERY / SECTIONS ═══════════════════ */
.student-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:14px}
.student-card{
  background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:22px 14px 18px;text-align:center;
  box-shadow:var(--shadow-sm);transition:all var(--t);position:relative;overflow:hidden;
  animation:scaleIn .4s cubic-bezier(.34,1.2,.64,1) both;
}
.student-card:nth-child(1){animation-delay:.04s}.student-card:nth-child(2){animation-delay:.08s}
.student-card:nth-child(3){animation-delay:.12s}.student-card:nth-child(4){animation-delay:.16s}
.student-card:nth-child(n+5){animation-delay:.2s}
.student-card::before{content:'';position:absolute;top:0;left:0;right:0;height:4px;background:var(--grad);opacity:0;transition:opacity var(--t)}
.student-card:hover{transform:translateY(-6px);box-shadow:var(--shadow-lg);border-color:var(--border2)}
.student-card:hover::before{opacity:1}
.s-avatar{width:72px;height:72px;border-radius:50%;object-fit:cover;margin:0 auto 11px;border:3px solid #fff;box-shadow:0 6px 18px rgba(79,70,229,0.25);transition:all var(--t)}
.student-card:hover .s-avatar{transform:scale(1.07);box-shadow:0 8px 24px rgba(79,70,229,0.4)}
.s-avatar-placeholder{
  width:72px;height:72px;border-radius:50%;background:linear-gradient(135deg,#4f46e5,#8b5cf6);
  display:flex;align-items:center;justify-content:center;font-size:25px;font-weight:800;color:#fff;
  margin:0 auto 11px;box-shadow:0 6px 18px rgba(79,70,229,0.3);
}
.s-name{font-weight:700;font-size:13.5px;margin-bottom:3px;color:var(--text)}
.s-pct{font-family:'Space Grotesk',sans-serif;font-size:24px;font-weight:800}
.gallery-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(185px,1fr));gap:14px}
.gallery-item{
  background:var(--card);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;
  box-shadow:var(--shadow-sm);transition:all var(--t);animation:scaleIn .4s cubic-bezier(.34,1.2,.64,1) both;
}
.gallery-item:hover{transform:translateY(-6px);box-shadow:var(--shadow-lg);border-color:var(--border2)}
.gallery-item img{width:100%;height:155px;object-fit:cover;display:block;transition:transform .4s ease}
.gallery-item:hover img{transform:scale(1.06)}
.gallery-item-info{padding:12px 14px}
.gallery-item-name,.gallery-item a{font-size:13.5px;font-weight:700;color:var(--text);text-decoration:none}
.log-item a,.student-card a{color:inherit;text-decoration:none}
.gallery-item-stat{font-size:11.5px;color:var(--muted);margin-top:2px}
.sec-tabs{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:20px}
.sec-tab{
  padding:7px 16px;border-radius:20px;font-size:12.5px;font-weight:600;text-decoration:none;
  border:1.5px solid var(--border2);color:var(--text2);background:#fff;box-shadow:var(--shadow-sm);
  transition:all var(--t);animation:fadeIn .4s ease both;
}
.sec-tab:hover{color:var(--blue-d);border-color:var(--blue);transform:translateY(-1px)}
.sec-tab-active{background:var(--grad)!important;border-color:transparent!important;color:#fff!important;box-shadow:0 8px 20px rgba(79,70,229,0.35)!important}
.sec-tab-all:not(.sec-tab-active){background:rgba(139,92,246,0.08);color:var(--purple-l)}
.sec-badge{display:inline-block;padding:2px 10px;border-radius:7px;font-size:10px;font-weight:700;background:rgba(99,102,241,0.10);color:var(--blue-d);border:1px solid rgba(99,102,241,0.24)}
.section-card{
  background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:20px;
  box-shadow:var(--shadow-sm);transition:all var(--t);cursor:pointer;text-decoration:none;display:block;
  position:relative;overflow:hidden;color:var(--text);animation:scaleIn .4s cubic-bezier(.34,1.2,.64,1) both;
}
.section-card::before{content:'';position:absolute;top:0;left:0;right:0;height:4px;background:var(--grad);opacity:0;transition:opacity var(--t)}
.section-card:hover{transform:translateY(-6px);box-shadow:var(--shadow-lg);border-color:var(--border2)}
.section-card:hover::before{opacity:1}
.section-card-name{font-family:'Space Grotesk',sans-serif;font-size:26px;font-weight:800;margin-bottom:3px;letter-spacing:-0.8px}
.section-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(205px,1fr));gap:14px}

/* ══ PROFILE IMAGE ═══════════════════════════════════ */
.profile-avatar-wrap{position:relative;width:112px;height:112px;margin:0 auto 14px;cursor:pointer}
.profile-avatar-wrap img,.profile-avatar-wrap .avatar-placeholder{
  width:112px;height:112px;border-radius:50%;object-fit:cover;border:4px solid #fff;display:block;
  transition:all var(--t);box-shadow:0 8px 28px rgba(79,70,229,0.3);
}
.profile-avatar-wrap .avatar-placeholder{background:linear-gradient(135deg,#4f46e5,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:38px;font-weight:800;color:#fff}
.profile-avatar-wrap:hover img,.profile-avatar-wrap:hover .avatar-placeholder{filter:brightness(0.6)}
.profile-avatar-overlay{position:absolute;inset:0;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;opacity:0;transition:opacity var(--t);pointer-events:none;gap:3px}
.profile-avatar-wrap:hover .profile-avatar-overlay{opacity:1}
.profile-avatar-overlay span{font-size:20px}
.profile-avatar-overlay small{font-size:10.5px;font-weight:700;color:#fff}
.profile-upload-btn{
  display:inline-flex;align-items:center;gap:6px;padding:7px 16px;border-radius:20px;font-size:12px;font-weight:600;
  background:rgba(99,102,241,0.09);border:1.5px solid rgba(99,102,241,0.28);color:var(--blue-d);cursor:pointer;
  transition:all var(--t);margin-top:4px;
}
.profile-upload-btn:hover{background:rgba(99,102,241,0.17)}
.profile-preview{width:112px;height:112px;border-radius:50%;object-fit:cover;border:4px solid var(--cyan);display:none;margin:0 auto 8px;box-shadow:0 0 20px rgba(6,182,212,0.4)}

/* ══ CALENDAR ════════════════════════════════════════ */
.cal-nav{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px}
.cal-month{font-family:'Space Grotesk',sans-serif;font-size:21px;font-weight:800;letter-spacing:-0.6px}
.cal-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:6px}
.cal-dow{text-align:center;font-size:10px;font-weight:700;color:var(--blue-d);padding:6px 0;letter-spacing:1px;text-transform:uppercase}
.cal-cell{
  border-radius:var(--radius-xs);padding:9px 4px;text-align:center;min-height:56px;border:1.5px solid transparent;
  background:#fff;cursor:pointer;transition:all var(--t);box-shadow:var(--shadow-sm);
}
.cal-cell:hover{border-color:var(--blue);box-shadow:var(--shadow);transform:translateY(-2px)}
.cal-cell.empty{opacity:0;pointer-events:none}
.cal-cell.today{border-color:var(--blue);background:rgba(99,102,241,0.08)}
.cal-cell.c-present{background:rgba(16,185,129,0.10);border-color:rgba(16,185,129,0.35)}
.cal-cell.c-absent{background:rgba(239,68,68,0.08);border-color:rgba(239,68,68,0.3)}
.cal-cell.c-partial{background:rgba(245,158,11,0.11);border-color:rgba(245,158,11,0.34)}
.cal-day-num{font-size:12.5px;font-weight:700;margin-bottom:4px;color:var(--text)}
.cal-dots{display:flex;gap:3px;justify-content:center}
.dot{width:6px;height:6px;border-radius:50%}
.dot-g{background:var(--green)}.dot-r{background:var(--red)}
.cal-legend{display:flex;gap:14px;align-items:center;margin-top:14px;font-size:12px;color:var(--text2);flex-wrap:wrap}
.leg-dot{width:9px;height:9px;border-radius:50%;display:inline-block;margin-right:5px}
.streak{display:inline-flex;align-items:center;gap:4px;background:rgba(245,158,11,0.13);border:1.5px solid rgba(245,158,11,0.32);color:#b45309;border-radius:20px;padding:3px 10px;font-size:11.5px;font-weight:700}

/* ══ TEACHER DASHBOARD BITS ══════════════════════════ */
.risk-high td:first-child{border-left:3px solid var(--red)!important}
.risk-mid td:first-child{border-left:3px solid var(--amber)!important}
.risk-ok td:first-child{border-left:3px solid var(--green)!important}
.absent-chip{display:inline-flex;align-items:center;gap:7px;background:rgba(239,68,68,0.07);border:1.5px solid rgba(239,68,68,0.22);border-radius:11px;padding:7px 12px;margin:4px;transition:all var(--t)}
.absent-chip:hover{background:rgba(239,68,68,0.13);transform:translateY(-2px)}
.absent-chip-avatar{width:26px;height:26px;border-radius:50%;background:linear-gradient(135deg,#dc2626,#f87171);display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:#fff;flex-shrink:0}
.qa-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.qa-btn{
  display:flex;align-items:center;gap:10px;padding:13px 14px;background:#fff;border:1.5px solid var(--border);
  border-radius:var(--radius-sm);text-decoration:none;color:var(--text);font-size:13px;font-weight:600;
  transition:all var(--t);box-shadow:var(--shadow-sm);
}
.qa-btn:hover{border-color:var(--blue);transform:translateY(-3px);box-shadow:var(--shadow);color:var(--blue-d)}
.qa-btn-icon{width:34px;height:34px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:15px;flex-shrink:0}
.ring-wrap{position:relative;width:110px;height:110px;margin:0 auto 8px}
.ring-wrap svg{transform:rotate(-90deg)}
.ring-val{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;flex-direction:column;text-align:center}
.ring-num{font-family:'Space Grotesk',sans-serif;font-size:22px;font-weight:800}
.ring-lbl{font-size:10px;color:var(--muted);margin-top:1px}

/* ══ SCAN RING (legacy) ══════════════════════════════ */
.scan-wrap{position:relative;display:inline-block}
.scan-ring{position:absolute;inset:-14px;border-radius:50%;border:2px solid var(--blue);opacity:0;animation:ringOut 2.8s ease-in-out infinite}
.scan-ring:nth-child(2){animation-delay:.93s;border-color:var(--purple)}
.scan-ring:nth-child(3){animation-delay:1.86s;border-color:var(--cyan)}
@keyframes ringOut{0%{transform:scale(0.82);opacity:0.9}100%{transform:scale(1.25);opacity:0}}
video{border-radius:var(--radius);display:block}

/* ══ SUBSCRIPTION ════════════════════════════════════ */
.upgrade-hero{
  border-radius:26px;padding:48px 38px;text-align:center;background:var(--grad);position:relative;overflow:hidden;
  margin-bottom:28px;box-shadow:0 22px 60px rgba(79,70,229,0.36);animation:fadeUp .55s cubic-bezier(.34,1.1,.64,1) both;
}
.upgrade-hero::before{content:'';position:absolute;top:-100px;left:50%;transform:translateX(-50%);width:460px;height:320px;border-radius:50%;background:rgba(255,255,255,0.10)}
.upgrade-hero h1{font-family:'Space Grotesk',sans-serif;font-size:clamp(26px,4vw,38px);font-weight:800;letter-spacing:-1.5px;color:#fff;position:relative;z-index:1;margin-bottom:12px}
.upgrade-hero p{color:rgba(255,255,255,0.9);font-size:14.5px;position:relative;z-index:1;line-height:1.7;max-width:520px;margin:0 auto}
.plan-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-bottom:26px}
.plan-card{
  background:var(--card);border:1.5px solid var(--border);border-radius:22px;padding:28px 22px;text-align:center;
  position:relative;overflow:hidden;transition:all var(--t);box-shadow:var(--shadow);
  animation:fadeUp .5s cubic-bezier(.34,1.2,.64,1) both;
}
.plan-card:nth-child(1){animation-delay:.05s}.plan-card:nth-child(2){animation-delay:.12s}
.plan-card:nth-child(3){animation-delay:.19s}.plan-card:nth-child(4){animation-delay:.26s}
.plan-card:hover{transform:translateY(-8px);box-shadow:var(--shadow-lg);border-color:var(--blue)}
.plan-card::before{content:'';position:absolute;top:0;left:0;right:0;height:4px;background:var(--grad)}
.plan-monthly::before{background:linear-gradient(90deg,#4f46e5,#818cf8)}
.plan-yearly::before{background:linear-gradient(90deg,#7c3aed,#ec4899)}
.plan-5year::before{background:linear-gradient(90deg,#d97706,#10b981)}
.plan-popular{border-color:var(--blue)!important;box-shadow:0 0 0 4px rgba(99,102,241,0.13),var(--shadow-lg)!important}
.plan-badge{
  position:absolute;top:16px;right:14px;background:linear-gradient(135deg,#7c3aed,#ec4899);color:#fff;
  padding:4px 12px;border-radius:20px;font-size:10.5px;font-weight:700;box-shadow:0 4px 12px rgba(139,92,246,0.42);
}
.plan-icon{font-size:40px;margin-bottom:12px}
.plan-name{font-family:'Space Grotesk',sans-serif;font-size:17px;font-weight:800;margin-bottom:6px;letter-spacing:-0.3px}
.plan-price{font-family:'Space Grotesk',sans-serif;font-size:40px;font-weight:800;letter-spacing:-2px;margin-bottom:4px;line-height:1}
.plan-period{font-size:12.5px;color:var(--muted);margin-bottom:20px}
.plan-features{list-style:none;text-align:left;margin-bottom:24px;display:flex;flex-direction:column;gap:10px}
.plan-features li{display:flex;align-items:center;gap:10px;font-size:13px;color:var(--text2)}
.plan-features li::before{
  content:"✓";color:#047857;font-weight:800;flex-shrink:0;background:rgba(16,185,129,0.13);
  width:19px;height:19px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:10px;
}
.expired-overlay{position:fixed;inset:0;z-index:9999;background:rgba(238,242,255,0.88);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);display:flex;align-items:center;justify-content:center}
.expired-modal{
  background:#fff;border:1.5px solid rgba(239,68,68,0.25);border-radius:26px;padding:46px 40px;max-width:470px;width:90%;
  text-align:center;position:relative;overflow:hidden;box-shadow:0 30px 80px rgba(79,70,229,0.28);
  animation:cardPop .4s cubic-bezier(.34,1.3,.64,1) both;
}
.expired-modal::before{content:'';position:absolute;top:0;left:0;right:0;height:5px;background:linear-gradient(90deg,#dc2626,#7c3aed,#4f46e5)}
.lock-icon{font-size:58px;margin-bottom:16px;display:block}
.expired-title{font-family:'Space Grotesk',sans-serif;font-size:24px;font-weight:800;color:var(--red-l);margin-bottom:10px}
.expired-sub{color:var(--text2);font-size:14px;line-height:1.7;margin-bottom:24px}
.dev-table td,.dev-table th{padding:10px 14px;border-bottom:1px solid var(--border);font-size:13px}
.dev-table th{font-size:10px;letter-spacing:1.2px;text-transform:uppercase;color:var(--blue-d)}

/* ══ ANIMATIONS ══════════════════════════════════════ */
@keyframes fadeUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:none}}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
@keyframes scaleIn{from{opacity:0;transform:scale(0.92)}to{opacity:1;transform:scale(1)}}
@keyframes countUp{from{opacity:0;transform:translateY(8px) scale(0.85)}to{opacity:1;transform:none}}
@keyframes shimmer{0%{background-position:-200% center}100%{background-position:200% center}}
.shimmer-text{background:linear-gradient(90deg,#4f46e5,#7c3aed,#06b6d4,#4f46e5);background-size:200% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;animation:shimmer 3s linear infinite}
.sidebar{animation:slideInLeft .45s cubic-bezier(.34,1.1,.64,1) both}
@keyframes slideInLeft{from{opacity:0;transform:translateX(-22px)}to{opacity:1;transform:none}}

/* ══ RESPONSIVE ══════════════════════════════════════ */
@media(max-width:768px){.plan-grid{grid-template-columns:1fr}}
@media(max-width:960px){
  .sidebar{display:none}
  .main{margin-left:0!important;padding-bottom:74px}
  .stats-row{grid-template-columns:1fr 1fr}
  .grid-2,.grid-3{grid-template-columns:1fr}
  .page{overflow-x:hidden;max-width:100vw}
  .hero,.td-hero{overflow:hidden}
  .card{overflow:hidden;word-break:break-word}
  [style*="repeat(4"]{grid-template-columns:1fr 1fr!important}
}
@media(max-width:560px){
  .page{padding:14px;overflow-x:hidden;max-width:100vw}
  body{overflow-x:hidden}
  .plan-grid{grid-template-columns:1fr!important}
  .hero,.td-hero{padding:22px 18px;border-radius:22px}
  .hero h1,.td-hero h1{font-size:19px}
  .login-card{padding:34px 22px;border-radius:24px}
  .stat{padding:16px 14px}
  .stat-val{font-size:28px}
  video{width:100%!important;max-width:100%}
  .scan-wrap{width:100%}
  .tbl-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch}
  table{min-width:400px}
  .sec-tabs{overflow-x:auto;flex-wrap:nowrap;padding-bottom:6px;-webkit-overflow-scrolling:touch}
  .sec-tab{flex-shrink:0}
  .upgrade-hero{padding:32px 20px}
  .qa-grid{grid-template-columns:1fr}
  .scan-viewfinder{aspect-ratio:1/1;max-height:80vw}
}

/* ══ MOBILE BOTTOM NAV ═══════════════════════════════ */
.mobile-nav{
  display:none;position:fixed;bottom:0;left:0;right:0;height:68px;background:rgba(255,255,255,0.94);
  backdrop-filter:blur(24px) saturate(1.8);-webkit-backdrop-filter:blur(24px) saturate(1.8);
  border-top:1px solid var(--border);z-index:200;padding:0 6px;padding-bottom:env(safe-area-inset-bottom);
  box-shadow:0 -8px 32px rgba(79,70,229,0.12);
}
.mobile-nav-inner{display:flex;align-items:stretch;height:100%}
.mnav-item{
  flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-decoration:none;
  color:var(--muted2);font-size:10px;font-weight:600;gap:4px;border-radius:16px;margin:7px 2px;position:relative;
  transition:all .18s cubic-bezier(.4,0,.2,1);-webkit-tap-highlight-color:transparent;
  animation:fadeUp .35s cubic-bezier(.34,1.3,.64,1) both;
}
.mnav-item:nth-child(1){animation-delay:.04s}.mnav-item:nth-child(2){animation-delay:.08s}
.mnav-item:nth-child(3){animation-delay:.12s}.mnav-item:nth-child(4){animation-delay:.16s}.mnav-item:nth-child(5){animation-delay:.2s}
.mnav-item svg{width:22px;height:22px;flex-shrink:0;transition:all .18s}
.mnav-item:active{transform:scale(0.88)}
.mnav-active{color:var(--blue-d)!important;background:rgba(99,102,241,0.11)}
.mnav-active svg{transform:scale(1.14);filter:drop-shadow(0 3px 6px rgba(79,70,229,0.4))}
.mnav-active::before{content:'';position:absolute;top:-7px;left:50%;transform:translateX(-50%);width:26px;height:3.5px;border-radius:3px;background:var(--grad);box-shadow:0 2px 10px rgba(79,70,229,0.5)}
.mnav-premium{color:var(--amber-l)!important}
.mnav-premium.mnav-active{background:rgba(245,158,11,0.13)}
.mnav-premium.mnav-active svg{filter:drop-shadow(0 3px 6px rgba(245,158,11,0.5))}
.mnav-premium.mnav-active::before{background:linear-gradient(90deg,#f59e0b,#f97316);box-shadow:0 2px 10px rgba(245,158,11,0.5)}

/* ══ MOBILE TOPBAR ═══════════════════════════════════ */
.mobile-topbar{
  display:none;position:fixed;top:0;left:0;right:0;z-index:150;height:56px;padding:0 16px;
  background:rgba(255,255,255,0.94);backdrop-filter:blur(22px) saturate(1.8);-webkit-backdrop-filter:blur(22px) saturate(1.8);
  border-bottom:1px solid var(--border);align-items:center;justify-content:space-between;box-shadow:0 6px 24px rgba(79,70,229,0.09);
}
.mobile-logo{font-family:'Space Grotesk',sans-serif;font-size:18px;font-weight:800;display:flex;align-items:center;gap:9px;color:var(--text);letter-spacing:-0.4px}
.mobile-logo span{background:var(--grad);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.hamburger-btn{
  width:38px;height:38px;border-radius:11px;background:var(--surface);border:1.5px solid var(--border2);
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px;cursor:pointer;
  transition:all .15s;-webkit-tap-highlight-color:transparent;
}
.hamburger-btn:active{transform:scale(0.92)}
.hamburger-btn span{display:block;width:18px;height:2.5px;background:var(--blue-d);border-radius:2px}

/* ══ DRAWER ══════════════════════════════════════════ */
.drawer-overlay{display:none;position:fixed;inset:0;z-index:190;background:rgba(30,27,75,0.35);backdrop-filter:blur(5px);-webkit-backdrop-filter:blur(5px)}
.drawer{
  position:fixed;top:0;right:-290px;bottom:0;width:272px;z-index:195;background:linear-gradient(180deg,#fff,#f6f7ff);
  border-left:1.5px solid var(--border);transition:right .3s cubic-bezier(.4,0,.2,1);display:flex;flex-direction:column;
  padding:20px 0;overflow-y:auto;box-shadow:-12px 0 48px rgba(79,70,229,0.2);
}
.drawer.open{right:0}
.drawer-header{padding:8px 20px 16px;border-bottom:1px solid var(--border);margin-bottom:8px;display:flex;align-items:center;justify-content:space-between}
.drawer-close{width:34px;height:34px;border-radius:10px;border:none;background:var(--surface);color:var(--text2);font-size:16px;cursor:pointer;transition:all .15s;display:flex;align-items:center;justify-content:center}
.drawer-close:hover{background:rgba(99,102,241,0.14);color:var(--blue-d)}
.drawer-item{display:flex;align-items:center;gap:12px;padding:13px 20px;color:var(--text2);text-decoration:none;font-size:14px;font-weight:500;transition:all .12s;border-left:3px solid transparent}
.drawer-item svg{width:18px;height:18px;flex-shrink:0;opacity:0.6}
.drawer-item:hover{color:var(--blue-d);background:rgba(99,102,241,0.07)}
.drawer-item:hover svg{opacity:1}
.drawer-active{color:var(--blue-d)!important;border-left-color:var(--blue)!important;background:rgba(99,102,241,0.10)!important;font-weight:600!important}
.drawer-active svg{opacity:1!important}

@media(max-width:960px){
  .mobile-nav{display:flex}
  .mobile-topbar{display:flex;background:rgba(255,255,255,0.98)}
  .topbar{display:none}
  .main{padding-top:56px}
  .page{margin-top:0}
}
@media(prefers-reduced-motion:reduce){
  *,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important}
}
</style>
"""
