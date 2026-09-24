# styles.py — FaceNova Premium UI v4 (Light + Colorful)
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}

/* ══ DESIGN TOKENS — LIGHT MODE ════════════════════════════ */
:root{
  --bg:        #f0f4ff;
  --surface:   #e8eeff;
  --card:      #ffffff;
  --card2:     #f7f9ff;
  --border:    rgba(99,102,241,0.12);
  --border2:   rgba(99,102,241,0.22);
  --border3:   rgba(99,102,241,0.35);

  --blue:      #4f46e5;
  --blue-l:    #6366f1;
  --blue-ll:   #818cf8;
  --cyan:      #0891b2;
  --cyan-l:    #06b6d4;
  --green:     #059669;
  --green-l:   #10b981;
  --green-ll:  #34d399;
  --red:       #dc2626;
  --red-l:     #ef4444;
  --amber:     #d97706;
  --amber-l:   #f59e0b;
  --amber-ll:  #fbbf24;
  --purple:    #7c3aed;
  --purple-l:  #8b5cf6;
  --pink:      #db2777;
  --pink-l:    #ec4899;
  --orange:    #ea580c;
  --orange-l:  #f97316;

  --text:      #1e1b4b;
  --text2:     #4338ca;
  --muted:     #6b7280;
  --muted2:    #9ca3af;

  --sidebar-w: 258px;
  --radius:    18px;
  --radius-sm: 12px;
  --radius-xs: 9px;
  --transition:0.18s cubic-bezier(.4,0,.2,1);

  --shadow-sm: 0 1px 3px rgba(79,70,229,0.08),0 1px 2px rgba(0,0,0,0.06);
  --shadow:    0 4px 16px rgba(79,70,229,0.1),0 2px 6px rgba(0,0,0,0.06);
  --shadow-lg: 0 16px 48px rgba(79,70,229,0.14),0 4px 16px rgba(0,0,0,0.08);
  --shadow-xl: 0 28px 64px rgba(79,70,229,0.18),0 8px 24px rgba(0,0,0,0.1);
}

/* ══ BASE ════════════════════════════════════════════════════ */
html{scroll-behavior:smooth}
body{
  font-family:'Inter',sans-serif;
  background:var(--bg);
  color:var(--text);
  min-height:100vh;
  display:flex;
  line-height:1.6;
  -webkit-font-smoothing:antialiased;
  -moz-osx-font-smoothing:grayscale;
  background-image:
    radial-gradient(ellipse 60% 40% at 80% 0%,rgba(139,92,246,0.08),transparent),
    radial-gradient(ellipse 50% 40% at 0% 100%,rgba(6,182,212,0.06),transparent);
}

/* ══ SCROLLBAR ════════════════════════════════════════════════ */
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-track{background:var(--surface)}
::-webkit-scrollbar-thumb{
  background:linear-gradient(180deg,var(--blue-l),var(--purple-l));
  border-radius:10px;
}
::-webkit-scrollbar-thumb:hover{background:var(--blue)}

/* ══ SIDEBAR ══════════════════════════════════════════════════ */
.sidebar{
  width:var(--sidebar-w);
  background:linear-gradient(180deg,#ffffff 0%,#f7f9ff 100%);
  border-right:1px solid var(--border);
  display:flex;flex-direction:column;
  position:fixed;top:0;bottom:0;left:0;z-index:100;
  overflow:hidden;
  box-shadow:4px 0 32px rgba(79,70,229,0.08);
}
.sidebar::before{
  content:'';position:absolute;top:-40px;left:-40px;
  width:200px;height:200px;border-radius:50%;
  background:radial-gradient(circle,rgba(99,102,241,0.07) 0%,transparent 70%);
  pointer-events:none;
}

.sidebar-logo{
  padding:22px 20px 18px;
  border-bottom:1px solid var(--border);
  position:relative;z-index:1;
}
.logo-mark{display:flex;align-items:center;gap:12px}
.logo-icon{
  width:38px;height:38px;border-radius:11px;
  background:linear-gradient(135deg,#4f46e5,#7c3aed);
  display:flex;align-items:center;justify-content:center;
  font-size:18px;
  box-shadow:0 4px 14px rgba(79,70,229,0.4);
  flex-shrink:0;
  animation:logo-float 4s ease-in-out infinite;
}
@keyframes logo-float{
  0%,100%{transform:translateY(0) rotate(0deg)}
  50%{transform:translateY(-3px) rotate(2deg)}
}
.logo-text{
  font-family:'Space Grotesk',sans-serif;
  font-size:19px;font-weight:800;letter-spacing:-0.5px;color:var(--text);
}
.logo-text span{
  background:linear-gradient(90deg,var(--blue),var(--purple));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}
.logo-tag{
  font-size:9px;font-weight:700;letter-spacing:2px;
  color:var(--muted2);text-transform:uppercase;margin-top:2px;
}

.sidebar-section{
  font-size:9px;font-weight:700;letter-spacing:2.2px;
  color:var(--muted2);text-transform:uppercase;
  padding:20px 20px 6px;
}

.nav-item{
  display:flex;align-items:center;gap:11px;
  padding:9px 16px 9px 18px;
  color:var(--muted);text-decoration:none;
  font-size:13px;font-weight:500;
  transition:all var(--transition);
  border-radius:12px;
  margin:1px 10px;
}
.nav-item svg{width:16px;height:16px;flex-shrink:0;opacity:0.5;transition:all var(--transition)}
.nav-item:hover{
  color:var(--blue);
  background:rgba(99,102,241,0.07);
}
.nav-item:hover svg{opacity:1;transform:translateX(2px)}
.nav-active{
  color:white!important;
  background:linear-gradient(135deg,var(--blue),var(--purple))!important;
  font-weight:600!important;
  box-shadow:0 4px 14px rgba(79,70,229,0.35);
}
.nav-active svg{opacity:1!important;filter:brightness(10)}

.sidebar-footer{
  margin-top:auto;padding:14px 20px 18px;
  border-top:1px solid var(--border);
}
.status-dot{
  display:inline-block;width:7px;height:7px;
  background:var(--green-l);border-radius:50%;
  margin-right:8px;
  box-shadow:0 0 0 3px rgba(16,185,129,0.2);
  animation:pulse-dot 2.5s infinite;
}
@keyframes pulse-dot{
  0%,100%{box-shadow:0 0 0 3px rgba(16,185,129,0.2)}
  50%{box-shadow:0 0 0 6px rgba(16,185,129,0.05)}
}

/* ══ TOPBAR ════════════════════════════════════════════════════ */
.main{margin-left:var(--sidebar-w);flex:1;display:flex;flex-direction:column;min-height:100vh}
.topbar{
  height:58px;padding:0 28px;
  background:rgba(255,255,255,0.85);
  backdrop-filter:blur(20px) saturate(1.8);
  -webkit-backdrop-filter:blur(20px) saturate(1.8);
  border-bottom:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between;
  position:sticky;top:0;z-index:50;
  box-shadow:0 1px 0 var(--border),0 4px 16px rgba(79,70,229,0.04);
}
.topbar-title{
  font-family:'Space Grotesk',sans-serif;
  font-size:15px;font-weight:700;color:var(--text);letter-spacing:-0.2px;
}
.topbar-right{display:flex;align-items:center;gap:10px}
.tbadge{
  background:linear-gradient(135deg,rgba(79,70,229,0.1),rgba(124,58,237,0.08));
  border:1px solid rgba(99,102,241,0.25);
  color:var(--blue);padding:4px 12px;
  border-radius:20px;font-size:11px;font-weight:700;
  letter-spacing:0.3px;
}
.page{padding:24px 28px;flex:1}

/* ══ STAT CARDS ════════════════════════════════════════════════ */
.stats-row{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:22px}
.stat{
  background:white;
  border:1px solid var(--border);
  border-radius:var(--radius);
  padding:20px 18px;position:relative;overflow:hidden;
  transition:transform var(--transition),box-shadow var(--transition);
  box-shadow:var(--shadow-sm);
}
.stat:hover{
  transform:translateY(-4px);
  box-shadow:var(--shadow-lg);
}
.stat::before{
  content:'';position:absolute;top:0;left:0;right:0;height:3px;
  border-radius:var(--radius) var(--radius) 0 0;
}
.stat::after{
  content:'';position:absolute;bottom:-20px;right:-20px;
  width:90px;height:90px;border-radius:50%;opacity:0.08;
}
.s-blue::before{background:linear-gradient(90deg,#4f46e5,#818cf8)}
.s-blue::after{background:#4f46e5}
.s-green::before{background:linear-gradient(90deg,#059669,#34d399)}
.s-green::after{background:#059669}
.s-red::before{background:linear-gradient(90deg,#dc2626,#f87171)}
.s-red::after{background:#dc2626}
.s-amber::before{background:linear-gradient(90deg,#d97706,#fbbf24)}
.s-amber::after{background:#d97706}
.s-purple::before{background:linear-gradient(90deg,#7c3aed,#a78bfa)}
.s-purple::after{background:#7c3aed}
.stat-ico{
  width:40px;height:40px;border-radius:11px;
  display:flex;align-items:center;justify-content:center;
  font-size:18px;margin-bottom:14px;
}
.stat-val{
  font-family:'Space Grotesk',sans-serif;
  font-size:34px;font-weight:800;line-height:1;margin-bottom:4px;
  letter-spacing:-1.5px;
  animation:count-up 0.6s cubic-bezier(.34,1.4,.64,1) both;
}
.stat-lbl{font-size:12px;color:var(--muted);font-weight:500}

/* ══ PROGRESS ════════════════════════════════════════════════ */
.pbar-wrap{
  background:rgba(99,102,241,0.08);
  border-radius:20px;height:6px;overflow:hidden;
}
.pbar{height:100%;border-radius:20px;transition:width 1.2s cubic-bezier(.4,0,.2,1)}
.pbar-green{background:linear-gradient(90deg,#059669,#34d399)}
.pbar-amber{background:linear-gradient(90deg,#d97706,#fbbf24)}
.pbar-red{background:linear-gradient(90deg,#dc2626,#f87171)}
.pbar-blue{background:linear-gradient(90deg,#4f46e5,#818cf8)}

/* ══ CARDS ════════════════════════════════════════════════════ */
.card{
  background:white;
  border:1px solid var(--border);
  border-radius:var(--radius);
  padding:22px;
  transition:box-shadow var(--transition),border-color var(--transition);
  box-shadow:var(--shadow-sm);
}
.card:hover{
  box-shadow:var(--shadow);
  border-color:var(--border2);
}
.card-glass{
  background:rgba(255,255,255,0.7);
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border:1px solid var(--border);
  border-radius:var(--radius);padding:22px;
  box-shadow:var(--shadow-sm);
}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.grid-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}
.sec-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px}
.sec-title{
  font-family:'Space Grotesk',sans-serif;
  font-size:15px;font-weight:700;letter-spacing:-0.2px;color:var(--text);
}
.sec-sub{font-size:12px;color:var(--muted);margin-top:2px}

/* ══ TABLE ════════════════════════════════════════════════════ */
.tbl-wrap{overflow-x:auto;border-radius:var(--radius-sm)}
table{width:100%;border-collapse:collapse;font-size:13px}
thead th{
  background:rgba(79,70,229,0.04);
  padding:11px 14px;text-align:left;
  font-size:10px;font-weight:700;
  letter-spacing:1.2px;text-transform:uppercase;
  color:var(--blue-l);
  border-bottom:1px solid var(--border);
}
tbody td{
  padding:12px 14px;
  border-bottom:1px solid rgba(99,102,241,0.06);
  transition:background var(--transition);
  color:var(--text);
}
tbody tr:hover td{background:rgba(79,70,229,0.03)}
tbody tr:last-child td{border-bottom:none}

/* ══ PILLS ════════════════════════════════════════════════════ */
.pill{
  display:inline-flex;align-items:center;gap:4px;
  padding:3px 10px;border-radius:20px;
  font-size:11px;font-weight:600;letter-spacing:0.2px;
}
.pill-green{background:rgba(5,150,105,0.1);color:#059669;border:1px solid rgba(5,150,105,0.2)}
.pill-red{background:rgba(220,38,38,0.08);color:#dc2626;border:1px solid rgba(220,38,38,0.15)}
.pill-amber{background:rgba(217,119,6,0.1);color:#d97706;border:1px solid rgba(217,119,6,0.2)}
.pill-blue{background:rgba(79,70,229,0.08);color:var(--blue);border:1px solid rgba(99,102,241,0.2)}
.pill-purple{background:rgba(124,58,237,0.08);color:var(--purple);border:1px solid rgba(124,58,237,0.2)}

/* ══ BUTTONS ════════════════════════════════════════════════ */
.btn{
  display:inline-flex;align-items:center;gap:7px;
  padding:9px 18px;border:none;border-radius:var(--radius-sm);
  font-size:13px;font-weight:600;cursor:pointer;
  transition:all var(--transition);
  text-decoration:none;font-family:'Inter',sans-serif;
  letter-spacing:0.1px;position:relative;overflow:hidden;
  -webkit-tap-highlight-color:transparent;
}
.btn-primary{
  background:linear-gradient(135deg,#4f46e5 0%,#7c3aed 100%);
  color:white;
  box-shadow:0 4px 14px rgba(79,70,229,0.35);
}
.btn-primary:hover{
  transform:translateY(-2px);
  box-shadow:0 8px 24px rgba(79,70,229,0.45);
  background:linear-gradient(135deg,#4338ca,#6d28d9);
}
.btn-primary:active{transform:translateY(0)}
.btn-cyan{
  background:linear-gradient(135deg,#0891b2,#0e7490);
  color:white;
  box-shadow:0 4px 14px rgba(8,145,178,0.3);
}
.btn-cyan:hover{transform:translateY(-2px);box-shadow:0 8px 22px rgba(6,182,212,0.4)}
.btn-ghost{
  background:white;
  color:var(--text);
  border:1.5px solid var(--border2);
  box-shadow:var(--shadow-sm);
}
.btn-ghost:hover{
  background:var(--surface);
  border-color:var(--border3);
  transform:translateY(-1px);
  box-shadow:var(--shadow);
}
.btn-red{
  background:rgba(220,38,38,0.08);color:#dc2626;
  border:1.5px solid rgba(220,38,38,0.2);
}
.btn-red:hover{background:rgba(220,38,38,0.15);transform:translateY(-1px)}
.btn-green{
  background:linear-gradient(135deg,#059669,#047857);color:white;
  box-shadow:0 4px 14px rgba(5,150,105,0.3);
}
.btn-green:hover{transform:translateY(-2px);box-shadow:0 8px 22px rgba(5,150,105,0.4)}
.btn-sm{padding:6px 13px;font-size:12px}
.btn-xs{padding:4px 10px;font-size:11px;border-radius:7px}
/* ripple */
.btn::after{
  content:'';position:absolute;
  width:80px;height:80px;
  background:rgba(255,255,255,0.3);
  border-radius:50%;
  transform:scale(0);opacity:0;
  top:50%;left:50%;margin:-40px 0 0 -40px;
  pointer-events:none;
}
.btn:active::after{
  animation:ripple-btn 0.4s ease-out;
}
@keyframes ripple-btn{
  0%{transform:scale(0);opacity:1}
  100%{transform:scale(3);opacity:0}
}

/* ══ FORMS ════════════════════════════════════════════════════ */
.form-group{margin-bottom:16px}
label{
  display:block;font-size:11.5px;font-weight:700;
  color:var(--blue);margin-bottom:7px;letter-spacing:0.4px;text-transform:uppercase;
}
input[type=text],input[type=password],select,textarea{
  width:100%;
  background:white;
  border:1.5px solid var(--border2);
  border-radius:var(--radius-xs);
  padding:10px 13px;
  color:var(--text);font-size:13.5px;
  font-family:'Inter',sans-serif;
  transition:all var(--transition);
  outline:none;
  box-shadow:var(--shadow-sm);
}
input[type=text]:focus,input[type=password]:focus,select:focus,textarea:focus{
  border-color:var(--blue);
  box-shadow:0 0 0 3px rgba(79,70,229,0.12),var(--shadow-sm);
}
input::placeholder{color:var(--muted2)}
select option{background:white;color:var(--text)}
input[type=file]{
  width:100%;
  background:rgba(79,70,229,0.03);
  border:2px dashed rgba(99,102,241,0.25);
  border-radius:var(--radius-xs);
  padding:14px 13px;color:var(--muted);
  font-size:13px;font-family:'Inter',sans-serif;
  cursor:pointer;transition:all var(--transition);
}
input[type=file]:hover{border-color:var(--blue);background:rgba(79,70,229,0.06)}

/* ══ ALERTS ══════════════════════════════════════════════════ */
.alert{
  padding:12px 16px;border-radius:var(--radius-xs);
  font-size:13px;margin-bottom:16px;
  display:flex;align-items:center;gap:9px;
  animation:slide-down 0.3s cubic-bezier(.34,1.3,.64,1);
}
@keyframes slide-down{from{opacity:0;transform:translateY(-10px)}to{opacity:1;transform:none}}
.alert-success{background:rgba(5,150,105,0.08);border:1.5px solid rgba(5,150,105,0.2);color:#059669}
.alert-error{background:rgba(220,38,38,0.07);border:1.5px solid rgba(220,38,38,0.2);color:#dc2626}
.alert-info{background:rgba(79,70,229,0.07);border:1.5px solid rgba(99,102,241,0.2);color:var(--blue)}
.alert-warn{background:rgba(217,119,6,0.08);border:1.5px solid rgba(217,119,6,0.2);color:#d97706}

/* ══ HERO BANNER ════════════════════════════════════════════ */
.hero{
  border-radius:22px;padding:28px 30px;margin-bottom:22px;
  position:relative;overflow:hidden;
  background:linear-gradient(135deg,#4f46e5 0%,#7c3aed 50%,#0891b2 100%);
  box-shadow:0 8px 32px rgba(79,70,229,0.3);
}
.hero::before{
  content:'';position:absolute;top:-60px;right:-40px;
  width:220px;height:220px;border-radius:50%;
  background:rgba(255,255,255,0.07);
  pointer-events:none;
}
.hero::after{
  content:'';position:absolute;bottom:-50px;left:20%;
  width:180px;height:180px;border-radius:50%;
  background:rgba(255,255,255,0.05);
  pointer-events:none;
}
.hero h1{
  font-family:'Space Grotesk',sans-serif;
  font-size:22px;font-weight:800;margin-bottom:5px;
  letter-spacing:-0.5px;position:relative;z-index:1;color:white;
}
.hero p{color:rgba(255,255,255,0.82);font-size:13.5px;
  position:relative;z-index:1;line-height:1.6;word-break:break-word}
.hero-actions{margin-top:18px;display:flex;gap:10px;
  position:relative;z-index:1;flex-wrap:wrap;width:100%}
.hero-actions .btn{flex:1;min-width:0;justify-content:center}

/* ══ LOG ITEMS ══════════════════════════════════════════════ */
.log-item{
  display:flex;align-items:center;gap:13px;
  padding:11px 0;border-bottom:1px solid rgba(99,102,241,0.07);
  transition:all var(--transition);
}
.log-item:last-child{border-bottom:none}
.log-item:hover{padding-left:4px}
.log-avatar{
  width:36px;height:36px;border-radius:10px;flex-shrink:0;
  background:linear-gradient(135deg,var(--blue),var(--purple));
  display:flex;align-items:center;justify-content:center;
  font-weight:700;font-size:13px;color:white;
  box-shadow:0 2px 8px rgba(79,70,229,0.25);
}
.log-info{flex:1}
.log-name{font-weight:600;font-size:13.5px;color:var(--text)}
.log-time{font-size:11px;color:var(--muted);margin-top:1px}

/* ══ LOGIN PAGE ═════════════════════════════════════════════ */
.login-wrap{
  min-height:100vh;width:100%;
  display:flex;align-items:center;justify-content:center;
  background:linear-gradient(135deg,#f0f4ff 0%,#e8eeff 40%,#f5f0ff 100%);
  background-image:
    radial-gradient(ellipse 60% 50% at 30% 20%,rgba(99,102,241,0.1),transparent),
    radial-gradient(ellipse 50% 40% at 80% 80%,rgba(124,58,237,0.08),transparent),
    radial-gradient(ellipse 40% 35% at 60% 50%,rgba(8,145,178,0.06),transparent);
  padding:20px;
}
.login-card{
  background:white;
  border:1.5px solid var(--border2);
  border-radius:24px;
  padding:40px 36px;
  width:100%;max-width:420px;
  box-shadow:var(--shadow-xl);
  position:relative;overflow:hidden;
  animation:card-pop 0.45s cubic-bezier(.34,1.3,.64,1) both;
}
@keyframes card-pop{
  from{opacity:0;transform:scale(0.92) translateY(16px)}
  to{opacity:1;transform:none}
}
.login-card::before{
  content:'';position:absolute;top:0;left:0;right:0;height:4px;
  background:linear-gradient(90deg,#4f46e5,#7c3aed,#0891b2);
  border-radius:24px 24px 0 0;
}
.login-logo{text-align:center;margin-bottom:28px}
.login-logo-icon{
  width:64px;height:64px;border-radius:18px;margin:0 auto 14px;
  background:linear-gradient(135deg,#4f46e5,#7c3aed);
  display:flex;align-items:center;justify-content:center;font-size:28px;
  box-shadow:0 8px 24px rgba(79,70,229,0.35);
}
.login-title{
  font-family:'Space Grotesk',sans-serif;
  font-size:24px;font-weight:800;letter-spacing:-0.5px;
  margin-bottom:4px;color:var(--text);
}
.login-sub{font-size:13.5px;color:var(--muted)}

/* ══ STUDENT CARDS ══════════════════════════════════════════ */
.student-grid{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(175px,1fr));
  gap:14px;
}
.student-card{
  background:white;border:1.5px solid var(--border);
  border-radius:var(--radius);padding:22px 16px 18px;
  text-align:center;
  transition:all var(--transition);
  box-shadow:var(--shadow-sm);
}
.student-card:hover{
  transform:translateY(-5px);
  border-color:var(--blue-l);
  box-shadow:var(--shadow-lg);
}
.s-avatar{
  width:70px;height:70px;border-radius:50%;object-fit:cover;
  margin:0 auto 10px;
  border:3px solid white;
  box-shadow:0 4px 14px rgba(79,70,229,0.15);
  transition:all var(--transition);
}
.student-card:hover .s-avatar{
  box-shadow:0 4px 20px rgba(79,70,229,0.3);
  transform:scale(1.05);
}
.s-avatar-placeholder{
  width:70px;height:70px;border-radius:50%;
  background:linear-gradient(135deg,#4f46e5,#7c3aed);
  display:flex;align-items:center;justify-content:center;
  font-size:24px;font-weight:800;color:white;
  margin:0 auto 10px;
  box-shadow:0 4px 14px rgba(79,70,229,0.25);
}
.s-name{font-weight:700;font-size:13.5px;margin-bottom:3px;color:var(--text)}
.s-pct{
  font-family:'Space Grotesk',sans-serif;
  font-size:24px;font-weight:800;
}

/* ══ GALLERY ══════════════════════════════════════════════ */
.gallery-grid{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(190px,1fr));
  gap:14px;
}
.gallery-item{
  background:white;border:1.5px solid var(--border);
  border-radius:var(--radius);overflow:hidden;
  transition:all var(--transition);box-shadow:var(--shadow-sm);
}
.gallery-item:hover{
  transform:translateY(-5px);
  border-color:var(--blue-l);
  box-shadow:var(--shadow-lg);
}
.gallery-item img{
  width:100%;height:155px;object-fit:cover;display:block;
  transition:transform 0.3s ease;
}
.gallery-item:hover img{transform:scale(1.04)}
.gallery-item-info{padding:12px 14px}
.gallery-item-name{font-size:13.5px;font-weight:700;color:var(--text)}
.gallery-item-stat{font-size:11.5px;color:var(--muted);margin-top:2px}

/* ══ CALENDAR ═════════════════════════════════════════════ */
.cal-nav{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px}
.cal-month{font-family:'Space Grotesk',sans-serif;font-size:20px;font-weight:800;color:var(--text)}
.cal-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:5px}
.cal-dow{
  text-align:center;font-size:10px;font-weight:700;
  color:var(--blue-l);padding:6px 0;
  letter-spacing:1px;text-transform:uppercase;
}
.cal-cell{
  border-radius:var(--radius-xs);padding:9px 5px;text-align:center;
  min-height:56px;border:1.5px solid transparent;
  background:white;
  cursor:pointer;transition:all var(--transition);
  box-shadow:var(--shadow-sm);
}
.cal-cell:hover{border-color:var(--blue-l);box-shadow:var(--shadow)}
.cal-cell.empty{opacity:0;pointer-events:none}
.cal-cell.today{border-color:var(--blue);background:rgba(79,70,229,0.05)}
.cal-cell.c-present{background:rgba(5,150,105,0.07);border-color:rgba(5,150,105,0.3)}
.cal-cell.c-absent{background:rgba(220,38,38,0.06);border-color:rgba(220,38,38,0.2)}
.cal-cell.c-partial{background:rgba(217,119,6,0.07);border-color:rgba(217,119,6,0.25)}
.cal-day-num{font-size:12.5px;font-weight:600;margin-bottom:4px;color:var(--text)}
.cal-dots{display:flex;gap:3px;justify-content:center;flex-wrap:wrap}
.dot{width:5px;height:5px;border-radius:50%}
.dot-g{background:var(--green-l)}
.dot-r{background:var(--red-l)}
.cal-legend{display:flex;gap:14px;align-items:center;margin-top:14px;font-size:12px;color:var(--muted);flex-wrap:wrap}
.leg-dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:5px}

/* ══ SCAN RING ═══════════════════════════════════════════ */
.scan-wrap{position:relative;display:inline-block}
.scan-ring{
  position:absolute;inset:-14px;border-radius:50%;
  border:2px solid var(--blue);opacity:0;
  animation:ring 2.8s ease-in-out infinite;
  box-shadow:0 0 10px rgba(79,70,229,0.2);
}
.scan-ring:nth-child(2){animation-delay:0.93s;border-color:var(--purple)}
.scan-ring:nth-child(3){animation-delay:1.86s;border-color:var(--cyan)}
@keyframes ring{
  0%{transform:scale(0.82);opacity:0.9}
  100%{transform:scale(1.25);opacity:0}
}
video{border-radius:var(--radius);display:block}

/* ══ SECTION TABS ════════════════════════════════════════ */
.sec-tabs{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:20px}
.sec-tab{
  padding:6px 15px;border-radius:20px;font-size:12.5px;font-weight:600;
  text-decoration:none;border:1.5px solid var(--border2);
  color:var(--muted);background:white;
  transition:all var(--transition);
  box-shadow:var(--shadow-sm);
}
.sec-tab:hover{background:var(--surface);color:var(--blue);border-color:var(--blue-l)}
.sec-tab-active{
  background:linear-gradient(135deg,#4f46e5,#7c3aed)!important;
  border-color:transparent!important;color:white!important;
  box-shadow:0 4px 12px rgba(79,70,229,0.3)!important;
}
.sec-badge{
  display:inline-block;padding:2px 9px;border-radius:6px;
  font-size:10px;font-weight:700;
  background:rgba(79,70,229,0.1);color:var(--blue);
  border:1px solid rgba(99,102,241,0.2);
}

/* ══ SECTION OVERVIEW ════════════════════════════════════ */
.section-card{
  background:white;border:1.5px solid var(--border);
  border-radius:var(--radius);padding:20px;
  transition:all var(--transition);
  cursor:pointer;text-decoration:none;display:block;
  box-shadow:var(--shadow-sm);
  position:relative;overflow:hidden;
}
.section-card::before{
  content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:linear-gradient(90deg,var(--blue),var(--purple));
  opacity:0;transition:opacity var(--transition);
}
.section-card:hover{
  transform:translateY(-4px);
  box-shadow:var(--shadow-lg);
  border-color:var(--border2);
}
.section-card:hover::before{opacity:1}
.section-card-name{
  font-family:'Space Grotesk',sans-serif;
  font-size:24px;font-weight:800;margin-bottom:3px;
  letter-spacing:-0.5px;color:var(--text);
}
.section-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:13px}

/* ══ PROFILE IMAGE ═══════════════════════════════════════ */
.profile-avatar-wrap{position:relative;width:110px;height:110px;margin:0 auto 14px;cursor:pointer}
.profile-avatar-wrap img,
.profile-avatar-wrap .avatar-placeholder{
  width:110px;height:110px;border-radius:50%;object-fit:cover;
  border:3px solid white;display:block;
  transition:all var(--transition);
  box-shadow:0 4px 20px rgba(79,70,229,0.2);
}
.profile-avatar-wrap .avatar-placeholder{
  background:linear-gradient(135deg,var(--blue),var(--purple));
  display:flex;align-items:center;justify-content:center;
  font-size:36px;font-weight:800;color:white;
}
.profile-avatar-wrap:hover img,
.profile-avatar-wrap:hover .avatar-placeholder{filter:brightness(0.6)}
.profile-avatar-overlay{
  position:absolute;inset:0;border-radius:50%;
  display:flex;flex-direction:column;
  align-items:center;justify-content:center;
  opacity:0;transition:opacity var(--transition);
  pointer-events:none;gap:3px;
}
.profile-avatar-wrap:hover .profile-avatar-overlay{opacity:1}
.profile-avatar-overlay span{font-size:20px}
.profile-avatar-overlay small{font-size:10.5px;font-weight:700;color:white}
.profile-upload-btn{
  display:inline-flex;align-items:center;gap:6px;
  padding:6px 15px;border-radius:20px;font-size:12px;font-weight:600;
  background:rgba(79,70,229,0.08);border:1.5px solid rgba(99,102,241,0.25);
  color:var(--blue);cursor:pointer;transition:all var(--transition);margin-top:4px;
}
.profile-upload-btn:hover{background:rgba(79,70,229,0.15)}
.profile-preview{
  width:110px;height:110px;border-radius:50%;object-fit:cover;
  border:3px solid var(--blue);display:none;margin:0 auto 8px;
  box-shadow:0 0 20px rgba(79,70,229,0.3);
}

/* ══ TEACHER DASHBOARD ══════════════════════════════════ */
.td-hero{
  border-radius:22px;padding:26px 30px;margin-bottom:20px;
  position:relative;overflow:hidden;
  background:linear-gradient(135deg,#4f46e5 0%,#7c3aed 60%,#0891b2 100%);
  box-shadow:0 8px 32px rgba(79,70,229,0.3);
}
.td-hero::before{
  content:'';position:absolute;top:-60px;right:-40px;
  width:240px;height:240px;border-radius:50%;
  background:rgba(255,255,255,0.07);pointer-events:none;
}
.td-hero::after{
  content:'👨‍🏫';
  position:absolute;right:28px;top:50%;transform:translateY(-50%);
  font-size:72px;opacity:0.12;
}
.td-hero h1{
  font-family:'Space Grotesk',sans-serif;
  font-size:24px;font-weight:800;margin-bottom:5px;
  letter-spacing:-0.5px;color:white;
}
.td-hero p{color:rgba(255,255,255,0.8);font-size:13.5px;line-height:1.6}
.risk-high td:first-child{border-left:3px solid var(--red-l)!important}
.risk-mid  td:first-child{border-left:3px solid var(--amber-l)!important}
.risk-ok   td:first-child{border-left:3px solid var(--green-l)!important}
.absent-chip{
  display:inline-flex;align-items:center;gap:7px;
  background:rgba(220,38,38,0.07);
  border:1.5px solid rgba(220,38,38,0.2);
  border-radius:10px;padding:7px 12px;margin:4px;
  transition:all var(--transition);
}
.absent-chip:hover{background:rgba(220,38,38,0.12);transform:translateY(-1px)}
.absent-chip-avatar{
  width:26px;height:26px;border-radius:50%;
  background:linear-gradient(135deg,var(--red),#f87171);
  display:flex;align-items:center;justify-content:center;
  font-size:11px;font-weight:700;color:white;flex-shrink:0;
}
.qa-grid{display:grid;grid-template-columns:1fr 1fr;gap:9px}
.qa-btn{
  display:flex;align-items:center;gap:10px;padding:12px 14px;
  background:white;border:1.5px solid var(--border);
  border-radius:var(--radius-sm);text-decoration:none;color:var(--text);
  font-size:13px;font-weight:600;transition:all var(--transition);
  box-shadow:var(--shadow-sm);
}
.qa-btn:hover{
  background:var(--surface);border-color:var(--blue-l);
  transform:translateY(-2px);box-shadow:var(--shadow);color:var(--blue);
}
.qa-btn-icon{
  width:32px;height:32px;border-radius:9px;
  display:flex;align-items:center;justify-content:center;
  font-size:14px;flex-shrink:0;
}
.ring-wrap{position:relative;width:110px;height:110px;margin:0 auto 8px}
.ring-wrap svg{transform:rotate(-90deg)}
.ring-val{
  position:absolute;inset:0;display:flex;
  align-items:center;justify-content:center;flex-direction:column;text-align:center;
}
.ring-num{font-family:'Space Grotesk',sans-serif;font-size:22px;font-weight:800;color:var(--text)}
.ring-lbl{font-size:10px;color:var(--muted);margin-top:1px}
.notice{padding:11px 15px;border-radius:var(--radius-xs);font-size:13px;display:flex;align-items:center;gap:8px;margin-bottom:9px}
.notice-warn{background:rgba(217,119,6,0.08);border:1.5px solid rgba(217,119,6,0.2);color:#d97706}

/* ══ SUBSCRIPTION / UPGRADE ═════════════════════════════ */
.upgrade-hero{
  border-radius:22px;padding:50px 40px;text-align:center;
  background:linear-gradient(135deg,#4f46e5 0%,#7c3aed 50%,#0891b2 100%);
  position:relative;overflow:hidden;margin-bottom:28px;
  box-shadow:0 12px 40px rgba(79,70,229,0.35);
}
.upgrade-hero::before{
  content:'';position:absolute;top:-80px;left:50%;transform:translateX(-50%);
  width:400px;height:300px;border-radius:50%;
  background:rgba(255,255,255,0.07);pointer-events:none;
}
.upgrade-hero h1{
  font-family:'Space Grotesk',sans-serif;
  font-size:36px;font-weight:800;letter-spacing:-1.5px;
  color:white;position:relative;z-index:1;margin-bottom:12px;
}
.upgrade-hero p{color:rgba(255,255,255,0.82);font-size:15px;position:relative;z-index:1;line-height:1.7}

.plan-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-bottom:28px}
.plan-card{
  background:white;border:1.5px solid var(--border);
  border-radius:20px;padding:28px 22px;text-align:center;
  position:relative;overflow:hidden;
  transition:all var(--transition);box-shadow:var(--shadow);
}
.plan-card:hover{
  transform:translateY(-8px);
  box-shadow:var(--shadow-xl);
  border-color:var(--blue-l);
}
.plan-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px}
.plan-monthly::before{background:linear-gradient(90deg,#4f46e5,#818cf8)}
.plan-yearly::before{background:linear-gradient(90deg,#7c3aed,#ec4899)}
.plan-5year::before{background:linear-gradient(90deg,#d97706,#059669)}
.plan-popular{
  border-color:var(--blue)!important;
  box-shadow:0 0 0 3px rgba(79,70,229,0.12),var(--shadow)!important;
}
.plan-badge{
  position:absolute;top:14px;right:14px;
  background:linear-gradient(135deg,var(--blue),var(--purple));
  color:white;padding:3px 11px;border-radius:20px;
  font-size:10.5px;font-weight:700;
  box-shadow:0 2px 8px rgba(79,70,229,0.35);
}
.plan-icon{font-size:38px;margin-bottom:14px}
.plan-name{
  font-family:'Space Grotesk',sans-serif;
  font-size:17px;font-weight:800;margin-bottom:8px;color:var(--text);
}
.plan-price{
  font-family:'Space Grotesk',sans-serif;
  font-size:42px;font-weight:800;letter-spacing:-2px;
  margin-bottom:4px;line-height:1;
}
.plan-period{font-size:12.5px;color:var(--muted);margin-bottom:20px}
.plan-features{
  list-style:none;text-align:left;margin-bottom:24px;
  display:flex;flex-direction:column;gap:9px;
}
.plan-features li{
  display:flex;align-items:center;gap:10px;
  font-size:13px;color:var(--muted);
}
.plan-features li::before{
  content:"✓";color:var(--green);font-weight:800;flex-shrink:0;
  background:rgba(5,150,105,0.1);width:18px;height:18px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;font-size:10px;
}

/* ══ EXPIRED OVERLAY ════════════════════════════════════ */
.expired-overlay{
  position:fixed;inset:0;z-index:9999;
  background:rgba(240,244,255,0.85);
  backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
  display:flex;align-items:center;justify-content:center;
}
.expired-modal{
  background:white;
  border:1.5px solid rgba(220,38,38,0.2);
  border-radius:24px;padding:48px 42px;max-width:480px;width:90%;
  text-align:center;position:relative;
  box-shadow:var(--shadow-xl);
  animation:card-pop 0.32s cubic-bezier(.34,1.3,.64,1) both;
}
.expired-modal::before{
  content:'';position:absolute;top:0;left:0;right:0;height:4px;
  background:linear-gradient(90deg,#dc2626,#7c3aed,#4f46e5);
  border-radius:24px 24px 0 0;
}
.lock-icon{font-size:58px;margin-bottom:18px;display:block}
.expired-title{
  font-family:'Space Grotesk',sans-serif;font-size:24px;font-weight:800;
  color:#dc2626;margin-bottom:10px;
}
.expired-sub{color:var(--muted);font-size:14px;line-height:1.7;margin-bottom:26px}

/* ══ DEV TABLE ═══════════════════════════════════════════ */
.dev-table td,.dev-table th{padding:10px 14px;border-bottom:1px solid var(--border);font-size:13px}
.dev-table th{font-size:9.5px;letter-spacing:1.2px;text-transform:uppercase;color:var(--blue-l)}

/* ══ STREAK BADGE ════════════════════════════════════════ */
.streak{
  display:inline-flex;align-items:center;gap:4px;
  background:rgba(217,119,6,0.1);
  border:1.5px solid rgba(217,119,6,0.25);
  color:#d97706;border-radius:20px;
  padding:3px 9px;font-size:11.5px;font-weight:700;
}

/* ══ RESPONSIVE ══════════════════════════════════════════ */
@media(max-width:768px){
  .plan-grid{grid-template-columns:1fr}
}
@media(max-width:960px){
  .sidebar{display:none}
  .main{margin-left:0!important}
  .stats-row{grid-template-columns:1fr 1fr}
  .grid-2,.grid-3{grid-template-columns:1fr}
  .main{padding-bottom:72px}
  .page{overflow-x:hidden;max-width:100vw}
  .hero{overflow:hidden}
  .hero p{word-break:break-word}
  .card{overflow:hidden;word-break:break-word}
  [style*="repeat(4"]{grid-template-columns:1fr 1fr!important}
}
@media(max-width:560px){
  .page{padding:12px;overflow-x:hidden;max-width:100vw}
  body{overflow-x:hidden}
  .stats-row{grid-template-columns:1fr 1fr}
  .plan-grid{grid-template-columns:1fr!important}
  .hero{padding:18px 16px}
  .hero h1{font-size:18px}
  .login-card{padding:32px 20px;border-radius:20px}
  .stat-val{font-size:28px}
  video{width:100%!important;max-width:100%}
  .scan-wrap{width:100%}
  .tbl-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch}
  table{min-width:400px}
  .sec-tabs{overflow-x:auto;flex-wrap:nowrap;padding-bottom:6px}
  .sec-tab{flex-shrink:0}
  .upgrade-hero{padding:28px 18px}
  .upgrade-hero h1{font-size:24px}
  .qa-grid{grid-template-columns:1fr}
}

/* ══ MOBILE BOTTOM NAV ═══════════════════════════════════ */
.mobile-nav{
  display:none;
  position:fixed;bottom:0;left:0;right:0;
  height:66px;
  background:rgba(255,255,255,0.95);
  backdrop-filter:blur(24px) saturate(1.8);
  -webkit-backdrop-filter:blur(24px) saturate(1.8);
  border-top:1px solid var(--border);
  z-index:200;padding:0 4px;
  padding-bottom:env(safe-area-inset-bottom);
  box-shadow:0 -4px 24px rgba(79,70,229,0.1);
}
.mobile-nav-inner{display:flex;align-items:stretch;height:100%}
.mnav-item{
  flex:1;display:flex;flex-direction:column;
  align-items:center;justify-content:center;
  text-decoration:none;color:var(--muted2);
  font-size:9.5px;font-weight:600;gap:4px;
  border-radius:14px;margin:6px 2px;
  transition:all 0.15s cubic-bezier(.4,0,.2,1);
  -webkit-tap-highlight-color:transparent;
}
.mnav-item svg{width:20px;height:20px;flex-shrink:0;transition:all 0.15s}
.mnav-item:active{transform:scale(0.88)}
.mnav-active{
  color:var(--blue)!important;
  background:rgba(79,70,229,0.08);
}
.mnav-active svg{
  transform:scale(1.15);
  filter:drop-shadow(0 2px 6px rgba(79,70,229,0.4));
}
.mnav-active::before{
  content:'';position:absolute;top:-6px;left:50%;transform:translateX(-50%);
  width:24px;height:3px;border-radius:3px;
  background:linear-gradient(90deg,var(--blue),var(--purple));
  box-shadow:0 0 8px rgba(79,70,229,0.4);
}
.mnav-premium{color:var(--amber)!important}
.mnav-premium.mnav-active{
  color:var(--amber)!important;
  background:rgba(217,119,6,0.08);
}
.mnav-premium.mnav-active svg{
  filter:drop-shadow(0 2px 6px rgba(217,119,6,0.5));
}
.mnav-premium.mnav-active::before{
  background:linear-gradient(90deg,var(--amber),var(--orange));
}

/* ══ MOBILE TOPBAR ══════════════════════════════════════ */
.mobile-topbar{
  display:none;position:fixed;top:0;left:0;right:0;z-index:150;
  height:54px;padding:0 16px;
  background:rgba(255,255,255,0.95);
  backdrop-filter:blur(20px) saturate(1.8);
  -webkit-backdrop-filter:blur(20px) saturate(1.8);
  border-bottom:1px solid var(--border);
  align-items:center;justify-content:space-between;
  box-shadow:0 4px 20px rgba(79,70,229,0.08);
}
.mobile-logo{
  font-family:'Space Grotesk',sans-serif;font-size:17px;font-weight:800;
  display:flex;align-items:center;gap:8px;color:var(--text);
}
.mobile-logo span{
  background:linear-gradient(90deg,var(--blue),var(--purple));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}
.hamburger-btn{
  width:36px;height:36px;border-radius:10px;
  background:var(--surface);border:1.5px solid var(--border2);
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  gap:5px;cursor:pointer;transition:all 0.15s;
  -webkit-tap-highlight-color:transparent;
}
.hamburger-btn:hover{background:rgba(79,70,229,0.08)}
.hamburger-btn span{
  display:block;width:18px;height:2px;
  background:var(--blue);border-radius:2px;
}

/* ══ DRAWER ══════════════════════════════════════════════ */
.drawer-overlay{
  display:none;position:fixed;inset:0;z-index:190;
  background:rgba(30,27,75,0.25);
  backdrop-filter:blur(5px);-webkit-backdrop-filter:blur(5px);
}
.drawer{
  position:fixed;top:0;right:-280px;bottom:0;width:265px;z-index:195;
  background:white;
  border-left:1.5px solid var(--border);
  transition:right 0.28s cubic-bezier(.4,0,.2,1);
  display:flex;flex-direction:column;padding:20px 0;
  overflow-y:auto;
  box-shadow:-8px 0 40px rgba(79,70,229,0.12);
}
.drawer.open{right:0}
.drawer-header{
  padding:8px 20px 16px;border-bottom:1px solid var(--border);
  margin-bottom:8px;
  display:flex;align-items:center;justify-content:space-between;
}
.drawer-close{
  width:32px;height:32px;border-radius:8px;border:none;
  background:var(--surface);color:var(--muted);
  font-size:16px;cursor:pointer;transition:all 0.15s;
  display:flex;align-items:center;justify-content:center;
}
.drawer-close:hover{background:rgba(79,70,229,0.08);color:var(--blue)}
.drawer-item{
  display:flex;align-items:center;gap:12px;
  padding:12px 20px;color:var(--muted);text-decoration:none;
  font-size:13.5px;font-weight:500;transition:all 0.12s;
  border-left:3px solid transparent;
}
.drawer-item svg{width:17px;height:17px;flex-shrink:0;opacity:0.5}
.drawer-item:hover{
  color:var(--blue);background:rgba(79,70,229,0.05);
}
.drawer-item:hover svg{opacity:1}
.drawer-active{
  color:var(--blue)!important;
  border-left-color:var(--blue)!important;
  background:rgba(79,70,229,0.07)!important;
  font-weight:600!important;
}
.drawer-active svg{opacity:1!important}

@media(max-width:960px){
  .mobile-nav{display:flex}
  .mobile-topbar{display:flex}
  .topbar{display:none}
  .page{margin-top:54px}
}

/* ══ ANIMATIONS ══════════════════════════════════════════ */
@keyframes fadeUp{
  from{opacity:0;transform:translateY(20px)}
  to{opacity:1;transform:translateY(0)}
}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
@keyframes scaleIn{
  from{opacity:0;transform:scale(0.9)}
  to{opacity:1;transform:scale(1)}
}
@keyframes slideInLeft{
  from{opacity:0;transform:translateX(-20px)}
  to{opacity:1;transform:translateX(0)}
}
@keyframes count-up{
  from{opacity:0;transform:translateY(8px) scale(0.85)}
  to{opacity:1;transform:translateY(0) scale(1)}
}
@keyframes shimmer{
  0%{background-position:-200% center}
  100%{background-position:200% center}
}
@keyframes bounce-in{
  0%{opacity:0;transform:scale(0.7)}
  70%{transform:scale(1.05)}
  100%{opacity:1;transform:scale(1)}
}

/* page load */
.hero{animation:fadeUp 0.5s cubic-bezier(.34,1.2,.64,1) both}
.stats-row .stat:nth-child(1){animation:fadeUp 0.45s 0.06s cubic-bezier(.34,1.2,.64,1) both}
.stats-row .stat:nth-child(2){animation:fadeUp 0.45s 0.12s cubic-bezier(.34,1.2,.64,1) both}
.stats-row .stat:nth-child(3){animation:fadeUp 0.45s 0.18s cubic-bezier(.34,1.2,.64,1) both}
.stats-row .stat:nth-child(4){animation:fadeUp 0.45s 0.24s cubic-bezier(.34,1.2,.64,1) both}
.card{animation:fadeUp 0.45s 0.1s cubic-bezier(.34,1.1,.64,1) both}
.sidebar{animation:slideInLeft 0.4s cubic-bezier(.34,1.1,.64,1) both}
.mobile-nav{animation:fadeUp 0.35s 0.15s cubic-bezier(.34,1.1,.64,1) both}
.student-card{animation:scaleIn 0.35s cubic-bezier(.34,1.2,.64,1) both}
.student-card:nth-child(1){animation-delay:.04s}
.student-card:nth-child(2){animation-delay:.08s}
.student-card:nth-child(3){animation-delay:.12s}
.student-card:nth-child(4){animation-delay:.16s}
.student-card:nth-child(n+5){animation-delay:.20s}
.gallery-item{animation:scaleIn 0.35s cubic-bezier(.34,1.2,.64,1) both}
.gallery-item:nth-child(1){animation-delay:.04s}
.gallery-item:nth-child(2){animation-delay:.08s}
.gallery-item:nth-child(3){animation-delay:.12s}
.gallery-item:nth-child(n+4){animation-delay:.16s}
.plan-card:nth-child(1){animation:fadeUp 0.4s 0.05s cubic-bezier(.34,1.2,.64,1) both}
.plan-card:nth-child(2){animation:fadeUp 0.4s 0.12s cubic-bezier(.34,1.2,.64,1) both}
.plan-card:nth-child(3){animation:fadeUp 0.4s 0.19s cubic-bezier(.34,1.2,.64,1) both}
.mnav-item:nth-child(1){animation:fadeUp 0.3s 0.05s cubic-bezier(.34,1.3,.64,1) both}
.mnav-item:nth-child(2){animation:fadeUp 0.3s 0.10s cubic-bezier(.34,1.3,.64,1) both}
.mnav-item:nth-child(3){animation:fadeUp 0.3s 0.15s cubic-bezier(.34,1.3,.64,1) both}
.mnav-item:nth-child(4){animation:fadeUp 0.3s 0.20s cubic-bezier(.34,1.3,.64,1) both}
.mnav-item:nth-child(5){animation:fadeUp 0.3s 0.25s cubic-bezier(.34,1.3,.64,1) both}
tbody tr{animation:fadeIn 0.3s ease both}
tbody tr:nth-child(1){animation-delay:.04s}
tbody tr:nth-child(2){animation-delay:.07s}
tbody tr:nth-child(3){animation-delay:.10s}
tbody tr:nth-child(4){animation-delay:.13s}
tbody tr:nth-child(n+5){animation-delay:.16s}
.pill{animation:bounce-in 0.3s cubic-bezier(.34,1.4,.64,1) both}
.alert{animation:slide-down 0.3s cubic-bezier(.34,1.3,.64,1) both!important}
@keyframes slide-down{from{opacity:0;transform:translateY(-10px)}to{opacity:1;transform:none}}
.sec-tab{animation:fadeIn 0.35s ease both}
.sec-tab:nth-child(1){animation-delay:.02s}
.sec-tab:nth-child(2){animation-delay:.05s}
.sec-tab:nth-child(3){animation-delay:.08s}
.sec-tab:nth-child(n+4){animation-delay:.11s}

/* hover glows — coloured per card */
.s-blue:hover{box-shadow:0 16px 40px rgba(79,70,229,0.18)!important}
.s-green:hover{box-shadow:0 16px 40px rgba(5,150,105,0.18)!important}
.s-red:hover{box-shadow:0 16px 40px rgba(220,38,38,0.15)!important}
.s-amber:hover{box-shadow:0 16px 40px rgba(217,119,6,0.18)!important}

/* shimmer helper class */
.shimmer-text{
  background:linear-gradient(90deg,var(--blue) 0%,var(--purple) 40%,var(--cyan) 60%,var(--blue) 100%);
  background-size:200% auto;
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  animation:shimmer 3s linear infinite;
}

@media(prefers-reduced-motion:reduce){
  *{animation-duration:0.01ms!important;
    animation-iteration-count:1!important;
    transition-duration:0.01ms!important}
}
</style>
"""
