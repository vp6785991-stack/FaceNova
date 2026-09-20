# styles.py — FaceNova Premium UI (v3)
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}

/* ══ DESIGN TOKENS ══════════════════════════════════════ */
:root{
  --bg:       #020912;
  --surface:  #050d1a;
  --card:     #080f1e;
  --card2:    #0c1526;
  --border:   rgba(255,255,255,0.055);
  --border2:  rgba(255,255,255,0.10);
  --border3:  rgba(255,255,255,0.15);

  --blue:     #3b82f6;
  --blue-d:   #1d4ed8;
  --blue-dd:  #1e40af;
  --cyan:     #06b6d4;
  --cyan-d:   #0891b2;
  --green:    #10b981;
  --green-l:  #34d399;
  --red:      #ef4444;
  --red-l:    #f87171;
  --amber:    #f59e0b;
  --amber-l:  #fcd34d;
  --purple:   #8b5cf6;
  --purple-l: #a78bfa;
  --pink:     #ec4899;

  --text:     #eef4ff;
  --text2:    #8ba3c7;
  --muted:    #3d5470;

  --glow-blue:  0 0 32px rgba(59,130,246,0.22);
  --glow-cyan:  0 0 32px rgba(6,182,212,0.22);
  --glow-green: 0 0 32px rgba(16,185,129,0.22);

  --sidebar-w:258px;
  --radius:18px;
  --radius-sm:11px;
  --radius-xs:8px;
  --transition:0.17s cubic-bezier(.4,0,.2,1);

  /* card depth layers */
  --card-shadow: 0 1px 0 rgba(255,255,255,0.04) inset,
                 0 -1px 0 rgba(0,0,0,0.3) inset;
}

/* ══ BASE ════════════════════════════════════════════════ */
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
    radial-gradient(ellipse 80% 50% at 50% -10%, rgba(59,130,246,0.06), transparent),
    url("data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.018'/%3E%3C/svg%3E");
}

/* ══ SCROLLBAR ═══════════════════════════════════════════ */
::-webkit-scrollbar{width:4px;height:4px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{
  background:rgba(59,130,246,0.25);border-radius:10px;
  transition:background .2s;
}
::-webkit-scrollbar-thumb:hover{background:rgba(59,130,246,0.45)}

/* ══ GLASSMORPHISM ═══════════════════════════════════════ */
.glass{
  background:rgba(8,15,30,0.55);
  backdrop-filter:blur(28px) saturate(1.5);
  -webkit-backdrop-filter:blur(28px) saturate(1.5);
  border:1px solid rgba(255,255,255,0.075);
  box-shadow:var(--card-shadow);
}

/* ══ SIDEBAR ════════════════════════════════════════════ */
.sidebar{
  width:var(--sidebar-w);
  background:linear-gradient(180deg,#06101f 0%,#030810 100%);
  border-right:1px solid var(--border);
  display:flex;flex-direction:column;
  position:fixed;top:0;bottom:0;left:0;z-index:100;
  overflow:hidden;
  box-shadow:4px 0 40px rgba(0,0,0,0.5);
}
/* ambient glow behind sidebar */
.sidebar::before{
  content:'';position:absolute;top:-60px;left:-60px;
  width:260px;height:260px;border-radius:50%;
  background:radial-gradient(circle,rgba(37,99,235,0.09) 0%,transparent 70%);
  pointer-events:none;
}
.sidebar::after{
  content:'';position:absolute;bottom:60px;left:0;right:0;
  height:160px;
  background:radial-gradient(ellipse 80% 100% at 50% 100%,rgba(139,92,246,0.04),transparent);
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
  background:linear-gradient(135deg,#1d4ed8,#06b6d4);
  display:flex;align-items:center;justify-content:center;
  font-size:18px;
  box-shadow:0 0 20px rgba(37,99,235,0.55),0 0 0 1px rgba(255,255,255,0.08) inset;
  flex-shrink:0;
}
.logo-text{font-family:'Space Grotesk',sans-serif;font-size:19px;font-weight:700;letter-spacing:-0.5px;color:var(--text)}
.logo-text span{
  background:linear-gradient(90deg,var(--cyan),var(--blue));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}
.logo-tag{
  font-size:9.5px;font-weight:700;letter-spacing:1.8px;
  color:var(--muted);text-transform:uppercase;margin-top:2px;
}

.sidebar-section{
  font-size:9px;font-weight:700;letter-spacing:2.2px;
  color:var(--muted);text-transform:uppercase;
  padding:20px 20px 6px;position:relative;z-index:1;
}

.nav-item{
  display:flex;align-items:center;gap:11px;
  padding:9px 16px 9px 20px;
  color:var(--text2);text-decoration:none;
  font-size:13px;font-weight:500;
  transition:all var(--transition);
  border-left:2px solid transparent;
  margin:1px 10px 1px 0;
  border-radius:0 12px 12px 0;
  position:relative;z-index:1;
}
.nav-item svg{width:16px;height:16px;flex-shrink:0;opacity:0.7;transition:all var(--transition)}
.nav-item:hover{
  color:var(--text);
  background:rgba(255,255,255,0.045);
  border-left-color:rgba(255,255,255,0.18);
}
.nav-item:hover svg{opacity:1;transform:translateX(1px)}
.nav-active{
  color:#fff!important;
  background:linear-gradient(90deg,rgba(37,99,235,0.22),rgba(37,99,235,0.04))!important;
  border-left-color:var(--blue)!important;
  font-weight:600!important;
  text-shadow:0 0 14px rgba(59,130,246,0.5);
}
.nav-active svg{opacity:1!important;filter:drop-shadow(0 0 4px rgba(59,130,246,0.6))}
.nav-active::after{
  content:'';position:absolute;right:0;top:50%;transform:translateY(-50%);
  width:2.5px;height:55%;border-radius:2px 0 0 2px;
  background:linear-gradient(180deg,var(--cyan),var(--blue));
  box-shadow:0 0 8px var(--blue);
}

.sidebar-footer{
  margin-top:auto;padding:14px 20px 18px;
  border-top:1px solid var(--border);position:relative;z-index:1;
}
.status-dot{
  display:inline-block;width:7px;height:7px;
  background:var(--green);border-radius:50%;
  margin-right:8px;box-shadow:0 0 8px var(--green);
  animation:pulse-dot 2.5s infinite;
}
@keyframes pulse-dot{
  0%,100%{opacity:1;box-shadow:0 0 8px var(--green)}
  50%{opacity:0.45;box-shadow:0 0 2px var(--green)}
}

/* ══ TOPBAR ═════════════════════════════════════════════ */
.main{margin-left:var(--sidebar-w);flex:1;display:flex;flex-direction:column;min-height:100vh}
.topbar{
  height:58px;padding:0 28px;
  background:rgba(2,9,18,0.75);
  backdrop-filter:blur(28px) saturate(1.4);
  -webkit-backdrop-filter:blur(28px) saturate(1.4);
  border-bottom:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between;
  position:sticky;top:0;z-index:50;
}
.topbar-title{
  font-family:'Space Grotesk',sans-serif;
  font-size:15px;font-weight:600;color:var(--text);letter-spacing:-0.2px;
}
.topbar-right{display:flex;align-items:center;gap:10px}
.tbadge{
  background:rgba(37,99,235,0.14);
  border:1px solid rgba(59,130,246,0.22);
  color:var(--blue);padding:4px 12px;
  border-radius:20px;font-size:11px;font-weight:700;
  letter-spacing:0.4px;
  box-shadow:0 0 12px rgba(59,130,246,0.1);
}
.page{padding:24px 28px;flex:1}

/* ══ STAT CARDS ═════════════════════════════════════════ */
.stats-row{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:22px}
.stat{
  background:var(--card);
  border:1px solid var(--border);
  border-radius:var(--radius);
  padding:20px 18px;position:relative;overflow:hidden;
  transition:transform var(--transition),border-color var(--transition),box-shadow var(--transition);
  box-shadow:var(--card-shadow);
}
.stat:hover{
  transform:translateY(-3px);
  border-color:rgba(255,255,255,0.1);
  box-shadow:var(--card-shadow),0 14px 40px rgba(0,0,0,0.4);
}
.stat::before{
  content:'';position:absolute;top:0;left:0;right:0;height:1.5px;
  border-radius:var(--radius) var(--radius) 0 0;
}
.stat::after{
  content:'';position:absolute;top:-20px;right:-20px;
  width:90px;height:90px;border-radius:50%;
  opacity:0.06;transition:opacity var(--transition);
}
.stat:hover::after{opacity:0.1}
.s-blue::before{background:linear-gradient(90deg,var(--blue),var(--cyan))}
.s-blue::after{background:var(--blue)}
.s-green::before{background:linear-gradient(90deg,var(--green),var(--green-l))}
.s-green::after{background:var(--green)}
.s-red::before{background:linear-gradient(90deg,var(--red),var(--red-l))}
.s-red::after{background:var(--red)}
.s-amber::before{background:linear-gradient(90deg,var(--amber),var(--amber-l))}
.s-amber::after{background:var(--amber)}
.s-purple::before{background:linear-gradient(90deg,var(--purple),var(--purple-l))}
.s-purple::after{background:var(--purple)}
.stat-ico{
  width:38px;height:38px;border-radius:10px;
  display:flex;align-items:center;justify-content:center;
  font-size:17px;margin-bottom:14px;
}
.stat-val{
  font-family:'Space Grotesk',sans-serif;
  font-size:32px;font-weight:700;line-height:1;margin-bottom:4px;
  letter-spacing:-1px;
}
.stat-lbl{font-size:11.5px;color:var(--text2);font-weight:500;letter-spacing:0.1px}

/* ══ PROGRESS ════════════════════════════════════════════ */
.pbar-wrap{
  background:rgba(255,255,255,0.04);
  border-radius:20px;height:5px;overflow:hidden;
  box-shadow:0 1px 3px rgba(0,0,0,0.3) inset;
}
.pbar{height:100%;border-radius:20px;transition:width 1s cubic-bezier(.4,0,.2,1)}
.pbar-green{background:linear-gradient(90deg,var(--green),var(--green-l))}
.pbar-amber{background:linear-gradient(90deg,var(--amber),var(--amber-l))}
.pbar-red{background:linear-gradient(90deg,var(--red),var(--red-l))}
.pbar-blue{background:linear-gradient(90deg,var(--blue),var(--cyan))}

/* ══ CARDS ═══════════════════════════════════════════════ */
.card{
  background:var(--card);
  border:1px solid var(--border);
  border-radius:var(--radius);
  padding:22px;
  transition:border-color var(--transition);
  box-shadow:var(--card-shadow);
  position:relative;
}
.card::before{
  content:'';position:absolute;inset:0;border-radius:var(--radius);
  background:linear-gradient(145deg,rgba(255,255,255,0.025) 0%,transparent 50%);
  pointer-events:none;
}
.card:hover{border-color:var(--border2)}
.card-glass{
  background:rgba(8,15,30,0.5);
  backdrop-filter:blur(28px);-webkit-backdrop-filter:blur(28px);
  border:1px solid rgba(255,255,255,0.07);
  border-radius:var(--radius);padding:22px;
  box-shadow:var(--card-shadow);
}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.grid-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}
.sec-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px}
.sec-title{
  font-family:'Space Grotesk',sans-serif;
  font-size:15px;font-weight:700;letter-spacing:-0.2px;
}
.sec-sub{font-size:12px;color:var(--text2);margin-top:2px}

/* ══ TABLE ═══════════════════════════════════════════════ */
.tbl-wrap{overflow-x:auto;border-radius:var(--radius-sm)}
table{width:100%;border-collapse:collapse;font-size:13px}
thead th{
  background:rgba(255,255,255,0.025);
  padding:11px 14px;text-align:left;
  font-size:9.5px;font-weight:700;
  letter-spacing:1.4px;text-transform:uppercase;
  color:var(--muted);border-bottom:1px solid var(--border);
}
tbody td{
  padding:12px 14px;border-bottom:1px solid rgba(255,255,255,0.035);
  transition:background var(--transition);
}
tbody tr:hover td{background:rgba(59,130,246,0.03)}
tbody tr:last-child td{border-bottom:none}

/* ══ PILLS ═══════════════════════════════════════════════ */
.pill{
  display:inline-flex;align-items:center;gap:4px;
  padding:3px 10px;border-radius:20px;
  font-size:11px;font-weight:600;letter-spacing:0.3px;
}
.pill-green{background:rgba(16,185,129,0.1);color:var(--green-l);border:1px solid rgba(16,185,129,0.18)}
.pill-red{background:rgba(239,68,68,0.1);color:var(--red-l);border:1px solid rgba(239,68,68,0.18)}
.pill-amber{background:rgba(245,158,11,0.1);color:var(--amber-l);border:1px solid rgba(245,158,11,0.18)}
.pill-blue{background:rgba(59,130,246,0.1);color:var(--blue);border:1px solid rgba(59,130,246,0.18)}
.pill-purple{background:rgba(139,92,246,0.1);color:var(--purple-l);border:1px solid rgba(139,92,246,0.18)}

/* ══ BUTTONS ═════════════════════════════════════════════ */
.btn{
  display:inline-flex;align-items:center;gap:7px;
  padding:9px 18px;border:none;border-radius:var(--radius-sm);
  font-size:13px;font-weight:600;cursor:pointer;
  transition:all var(--transition);
  text-decoration:none;font-family:'Inter',sans-serif;
  letter-spacing:0.1px;position:relative;overflow:hidden;
  -webkit-tap-highlight-color:transparent;
}
/* shimmer layer on all buttons */
.btn::before{
  content:'';position:absolute;inset:0;
  background:linear-gradient(180deg,rgba(255,255,255,0.08) 0%,transparent 50%);
  pointer-events:none;border-radius:inherit;
}
.btn-primary{
  background:linear-gradient(135deg,#2563eb 0%,#1d4ed8 60%,#1e40af 100%);
  color:white;
  box-shadow:0 1px 0 rgba(255,255,255,0.12) inset,0 4px 16px rgba(37,99,235,0.35);
}
.btn-primary:hover{
  background:linear-gradient(135deg,#3b82f6,#2563eb,#1d4ed8);
  transform:translateY(-1.5px);
  box-shadow:0 1px 0 rgba(255,255,255,0.12) inset,0 8px 24px rgba(37,99,235,0.45);
}
.btn-primary:active{transform:translateY(0)}
.btn-cyan{
  background:linear-gradient(135deg,#0891b2,#0e7490);
  color:white;
  box-shadow:0 1px 0 rgba(255,255,255,0.1) inset,0 4px 14px rgba(8,145,178,0.3);
}
.btn-cyan:hover{
  background:linear-gradient(135deg,#06b6d4,#0891b2);
  transform:translateY(-1.5px);
  box-shadow:0 1px 0 rgba(255,255,255,0.1) inset,0 8px 22px rgba(6,182,212,0.4);
}
.btn-ghost{
  background:rgba(255,255,255,0.04);
  color:var(--text2);
  border:1px solid var(--border2);
}
.btn-ghost:hover{
  background:rgba(255,255,255,0.08);
  color:var(--text);
  border-color:var(--border3);
  transform:translateY(-1px);
}
.btn-red{
  background:rgba(239,68,68,0.1);color:var(--red-l);
  border:1px solid rgba(239,68,68,0.2);
}
.btn-red:hover{background:rgba(239,68,68,0.2);transform:translateY(-1px)}
.btn-green{
  background:linear-gradient(135deg,#059669,#047857);color:white;
  box-shadow:0 4px 14px rgba(5,150,105,0.3);
}
.btn-green:hover{transform:translateY(-1.5px);box-shadow:0 8px 22px rgba(16,185,129,0.4)}
.btn-sm{padding:6px 13px;font-size:12px}
.btn-xs{padding:4px 10px;font-size:11px;border-radius:7px}

/* ══ FORMS ═══════════════════════════════════════════════ */
.form-group{margin-bottom:16px}
label{
  display:block;font-size:11px;font-weight:700;
  color:var(--text2);margin-bottom:7px;letter-spacing:0.6px;text-transform:uppercase;
}
input[type=text],input[type=password],select,textarea{
  width:100%;
  background:rgba(255,255,255,0.035);
  border:1px solid var(--border2);
  border-radius:var(--radius-xs);
  padding:10px 13px;
  color:var(--text);font-size:13.5px;
  font-family:'Inter',sans-serif;
  transition:border-color var(--transition),box-shadow var(--transition),background var(--transition);
  outline:none;
  box-shadow:0 1px 3px rgba(0,0,0,0.2) inset;
}
input[type=text]:focus,input[type=password]:focus,select:focus,textarea:focus{
  border-color:rgba(59,130,246,0.6);
  box-shadow:0 0 0 3px rgba(59,130,246,0.1),0 1px 3px rgba(0,0,0,0.2) inset;
  background:rgba(59,130,246,0.04);
}
input::placeholder{color:var(--muted)}
select option{background:#0a1120;color:var(--text)}
input[type=file]{
  width:100%;
  background:rgba(255,255,255,0.025);
  border:1.5px dashed rgba(255,255,255,0.1);
  border-radius:var(--radius-xs);
  padding:14px 13px;color:var(--text2);
  font-size:13px;font-family:'Inter',sans-serif;
  cursor:pointer;transition:border-color var(--transition);
}
input[type=file]:hover{border-color:rgba(59,130,246,0.4)}

/* ══ ALERTS ══════════════════════════════════════════════ */
.alert{
  padding:11px 15px;border-radius:var(--radius-xs);
  font-size:13px;margin-bottom:16px;
  display:flex;align-items:center;gap:9px;
  animation:slide-in 0.22s cubic-bezier(.34,1.56,.64,1);
}
@keyframes slide-in{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}
.alert-success{background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);color:var(--green-l)}
.alert-error{background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);color:var(--red-l)}
.alert-info{background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.2);color:var(--blue)}
.alert-warn{background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.2);color:var(--amber-l)}

/* ══ HERO BANNER ═════════════════════════════════════════ */
.hero{
  border-radius:20px;padding:28px 30px;margin-bottom:22px;
  position:relative;overflow:hidden;
  background:linear-gradient(135deg,
    rgba(37,99,235,0.14) 0%,
    rgba(6,182,212,0.05) 50%,
    rgba(139,92,246,0.07) 100%);
  border:1px solid rgba(59,130,246,0.16);
  box-shadow:0 0 60px rgba(37,99,235,0.06),var(--card-shadow);
}
.hero::before{
  content:'';position:absolute;top:-60px;right:-50px;
  width:240px;height:240px;border-radius:50%;
  background:radial-gradient(circle,rgba(59,130,246,0.1) 0%,transparent 70%);
  pointer-events:none;
}
.hero::after{
  content:'';position:absolute;bottom:-50px;left:28%;
  width:180px;height:180px;border-radius:50%;
  background:radial-gradient(circle,rgba(6,182,212,0.06) 0%,transparent 70%);
  pointer-events:none;
}
.hero h1{
  font-family:'Space Grotesk',sans-serif;
  font-size:23px;font-weight:800;margin-bottom:5px;
  letter-spacing:-0.5px;position:relative;z-index:1;
  word-break:break-word;
}
.hero p{color:var(--text2);font-size:13.5px;position:relative;z-index:1;line-height:1.6;word-break:break-word}
.hero-actions{margin-top:18px;display:flex;gap:8px;position:relative;z-index:1;flex-wrap:wrap;width:100%}
.hero-actions .btn{flex:1;min-width:0;justify-content:center;text-align:center}

/* ══ LOG ITEMS ═══════════════════════════════════════════ */
.log-item{
  display:flex;align-items:center;gap:13px;
  padding:11px 0;border-bottom:1px solid rgba(255,255,255,0.035);
  transition:all var(--transition);
}
.log-item:last-child{border-bottom:none}
.log-item:hover{padding-left:4px}
.log-avatar{
  width:36px;height:36px;border-radius:9px;flex-shrink:0;
  background:linear-gradient(135deg,var(--blue),var(--purple));
  display:flex;align-items:center;justify-content:center;
  font-weight:700;font-size:14px;
  box-shadow:0 2px 8px rgba(37,99,235,0.3);
}
.log-info{flex:1}
.log-name{font-weight:600;font-size:13.5px}
.log-time{font-size:11px;color:var(--text2);margin-top:1px;letter-spacing:0.1px}

/* ══ LOGIN PAGE ══════════════════════════════════════════ */
.login-wrap{
  min-height:100vh;width:100%;
  display:flex;align-items:center;justify-content:center;
  background:var(--bg);
  background-image:
    radial-gradient(ellipse 70% 60% at 50% 0%,rgba(37,99,235,0.1),transparent),
    radial-gradient(ellipse 40% 40% at 80% 80%,rgba(139,92,246,0.05),transparent);
  padding:20px;
}
.login-card{
  background:rgba(8,15,30,0.6);
  backdrop-filter:blur(40px) saturate(1.4);
  -webkit-backdrop-filter:blur(40px) saturate(1.4);
  border:1px solid rgba(255,255,255,0.08);
  border-radius:24px;
  padding:40px 36px;
  width:100%;max-width:420px;
  box-shadow:0 40px 100px rgba(0,0,0,0.6),0 0 0 1px rgba(255,255,255,0.04) inset;
  position:relative;overflow:hidden;
}
.login-card::before{
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(59,130,246,0.5),rgba(6,182,212,0.3),transparent);
}
.login-logo{text-align:center;margin-bottom:28px}
.login-logo-icon{
  width:60px;height:60px;border-radius:17px;margin:0 auto 14px;
  background:linear-gradient(135deg,#1d4ed8,#06b6d4);
  display:flex;align-items:center;justify-content:center;font-size:26px;
  box-shadow:0 0 30px rgba(37,99,235,0.45),0 0 0 1px rgba(255,255,255,0.08) inset;
}
.login-title{
  font-family:'Space Grotesk',sans-serif;
  font-size:22px;font-weight:800;letter-spacing:-0.5px;margin-bottom:4px;
}
.login-sub{font-size:13px;color:var(--text2)}

/* ══ STUDENT CARDS ═══════════════════════════════════════ */
.student-grid{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(185px,1fr));
  gap:14px;
}
.student-card{
  background:var(--card);
  border:1px solid var(--border);
  border-radius:var(--radius);
  padding:22px 16px 18px;
  text-align:center;
  transition:all var(--transition);
  position:relative;overflow:hidden;
  box-shadow:var(--card-shadow);
}
.student-card::before{
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,0.08),transparent);
}
.student-card::after{
  content:'';position:absolute;inset:0;border-radius:var(--radius);
  background:linear-gradient(135deg,rgba(255,255,255,0.015) 0%,transparent 50%);
  pointer-events:none;
}
.student-card:hover{
  transform:translateY(-5px);
  border-color:rgba(59,130,246,0.22);
  box-shadow:0 16px 40px rgba(0,0,0,0.45),0 0 20px rgba(37,99,235,0.08);
}
.s-avatar{
  width:72px;height:72px;border-radius:50%;object-fit:cover;
  margin:0 auto 10px;
  border:2px solid rgba(255,255,255,0.1);
  box-shadow:0 0 0 4px rgba(255,255,255,0.025);
  transition:all var(--transition);
}
.student-card:hover .s-avatar{
  box-shadow:0 0 0 4px rgba(59,130,246,0.18);
  border-color:rgba(59,130,246,0.4);
}
.s-avatar-placeholder{
  width:72px;height:72px;border-radius:50%;
  background:linear-gradient(135deg,var(--blue),var(--purple));
  display:flex;align-items:center;justify-content:center;
  font-size:24px;font-weight:700;
  margin:0 auto 10px;
  border:2px solid rgba(139,92,246,0.25);
  box-shadow:0 0 16px rgba(139,92,246,0.2);
}
.s-name{font-weight:700;font-size:13.5px;margin-bottom:3px;letter-spacing:-0.1px}
.s-pct{font-family:'Space Grotesk',sans-serif;font-size:24px;font-weight:700}

/* ══ GALLERY ═════════════════════════════════════════════ */
.gallery-grid{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(195px,1fr));
  gap:14px;
}
.gallery-item{
  background:var(--card);border:1px solid var(--border);
  border-radius:var(--radius);overflow:hidden;
  transition:all var(--transition);box-shadow:var(--card-shadow);
}
.gallery-item:hover{
  transform:translateY(-5px);
  border-color:rgba(59,130,246,0.2);
  box-shadow:0 16px 36px rgba(0,0,0,0.45);
}
.gallery-item img{
  width:100%;height:158px;object-fit:cover;display:block;
  transition:filter var(--transition);
}
.gallery-item:hover img{filter:brightness(1.08)}
.gallery-item-info{padding:12px 14px}
.gallery-item-name{font-size:13.5px;font-weight:700}
.gallery-item-stat{font-size:11.5px;color:var(--text2);margin-top:2px}

/* ══ CALENDAR ════════════════════════════════════════════ */
.cal-nav{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px}
.cal-month{font-family:'Space Grotesk',sans-serif;font-size:20px;font-weight:700;letter-spacing:-0.5px}
.cal-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:5px}
.cal-dow{
  text-align:center;font-size:10px;font-weight:700;
  color:var(--muted);padding:6px 0;
  letter-spacing:1px;text-transform:uppercase;
}
.cal-cell{
  border-radius:var(--radius-xs);padding:9px 5px;text-align:center;
  min-height:58px;border:1px solid var(--border);
  background:rgba(255,255,255,0.012);
  cursor:pointer;transition:all var(--transition);
  position:relative;
}
.cal-cell:hover{background:rgba(255,255,255,0.045);border-color:var(--border2)}
.cal-cell.empty{opacity:0;pointer-events:none}
.cal-cell.today{border-color:rgba(59,130,246,0.4);background:rgba(59,130,246,0.06)}
.cal-cell.c-present{background:rgba(16,185,129,0.07);border-color:rgba(16,185,129,0.22)}
.cal-cell.c-absent{background:rgba(239,68,68,0.07);border-color:rgba(239,68,68,0.22)}
.cal-cell.c-partial{background:rgba(245,158,11,0.07);border-color:rgba(245,158,11,0.22)}
.cal-day-num{font-size:12.5px;font-weight:600;margin-bottom:4px}
.cal-dots{display:flex;gap:3px;justify-content:center;flex-wrap:wrap}
.dot{width:5px;height:5px;border-radius:50%}
.dot-g{background:var(--green)}
.dot-r{background:var(--red)}
.cal-legend{display:flex;gap:14px;align-items:center;margin-top:14px;font-size:12px;color:var(--text2);flex-wrap:wrap}
.leg-dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:5px}

/* ══ STREAK BADGE ════════════════════════════════════════ */
.streak{
  display:inline-flex;align-items:center;gap:4px;
  background:rgba(245,158,11,0.1);
  border:1px solid rgba(245,158,11,0.18);
  color:var(--amber-l);border-radius:20px;
  padding:3px 9px;font-size:11.5px;font-weight:700;
  box-shadow:0 0 10px rgba(245,158,11,0.1);
}

/* ══ SCAN RING ═══════════════════════════════════════════ */
.scan-wrap{position:relative;display:inline-block}
.scan-ring{
  position:absolute;inset:-14px;border-radius:50%;
  border:1.5px solid var(--cyan);opacity:0;
  animation:ring 2.8s ease-in-out infinite;
}
.scan-ring:nth-child(2){animation-delay:0.93s}
.scan-ring:nth-child(3){animation-delay:1.86s}
@keyframes ring{
  0%{transform:scale(0.82);opacity:0.85}
  100%{transform:scale(1.2);opacity:0}
}
video{border-radius:var(--radius);display:block}

/* ══ SECTION TABS ════════════════════════════════════════ */
.sec-tabs{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:20px}
.sec-tab{
  padding:6px 15px;border-radius:20px;font-size:12.5px;font-weight:600;
  text-decoration:none;border:1px solid var(--border2);
  color:var(--text2);background:rgba(255,255,255,0.025);
  transition:all var(--transition);
}
.sec-tab:hover{background:rgba(255,255,255,0.065);color:var(--text)}
.sec-tab-active{
  background:rgba(37,99,235,0.16)!important;
  border-color:rgba(59,130,246,0.35)!important;
  color:var(--blue)!important;
  box-shadow:0 0 12px rgba(37,99,235,0.1);
}
.sec-tab-all{background:rgba(139,92,246,0.07);border-color:rgba(139,92,246,0.18);color:var(--purple-l)}
.sec-tab-all.sec-tab-active{
  background:rgba(139,92,246,0.18)!important;
  color:var(--purple-l)!important;
  box-shadow:0 0 12px rgba(139,92,246,0.1);
}
.sec-badge{
  display:inline-block;padding:2px 9px;border-radius:6px;
  font-size:10px;font-weight:700;letter-spacing:0.5px;
  background:rgba(59,130,246,0.1);color:var(--blue);
  border:1px solid rgba(59,130,246,0.18);
}

/* ══ SECTION OVERVIEW ════════════════════════════════════ */
.section-card{
  background:var(--card);border:1px solid var(--border);
  border-radius:var(--radius);padding:20px;
  transition:all var(--transition);
  cursor:pointer;text-decoration:none;display:block;
  position:relative;overflow:hidden;
  box-shadow:var(--card-shadow);
}
.section-card::before{
  content:'';position:absolute;inset:0;
  background:linear-gradient(135deg,rgba(255,255,255,0.018) 0%,transparent 55%);
  pointer-events:none;
}
.section-card:hover{
  transform:translateY(-4px);
  box-shadow:0 16px 44px rgba(0,0,0,0.5);
  border-color:rgba(59,130,246,0.2);
}
.section-card-name{
  font-family:'Space Grotesk',sans-serif;
  font-size:24px;font-weight:800;margin-bottom:3px;letter-spacing:-0.5px;
}
.section-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:13px}

/* ══ PROFILE IMAGE ═══════════════════════════════════════ */
.profile-avatar-wrap{
  position:relative;width:110px;height:110px;
  margin:0 auto 14px;cursor:pointer;
}
.profile-avatar-wrap img,
.profile-avatar-wrap .avatar-placeholder{
  width:110px;height:110px;border-radius:50%;object-fit:cover;
  border:2px solid rgba(255,255,255,0.1);display:block;
  transition:all var(--transition);
  box-shadow:0 0 0 4px rgba(255,255,255,0.025),0 8px 24px rgba(0,0,0,0.4);
}
.profile-avatar-wrap .avatar-placeholder{
  background:linear-gradient(135deg,var(--blue),var(--purple));
  display:flex;align-items:center;justify-content:center;
  font-size:36px;font-weight:700;color:white;
}
.profile-avatar-wrap:hover img,
.profile-avatar-wrap:hover .avatar-placeholder{filter:brightness(0.5)}
.profile-avatar-overlay{
  position:absolute;inset:0;border-radius:50%;
  display:flex;flex-direction:column;
  align-items:center;justify-content:center;
  opacity:0;transition:opacity var(--transition);
  pointer-events:none;gap:3px;
}
.profile-avatar-wrap:hover .profile-avatar-overlay{opacity:1}
.profile-avatar-overlay span{font-size:20px}
.profile-avatar-overlay small{font-size:10.5px;font-weight:700;color:white;letter-spacing:0.4px}
.profile-upload-btn{
  display:inline-flex;align-items:center;gap:6px;
  padding:6px 15px;border-radius:20px;font-size:12px;font-weight:600;
  background:rgba(59,130,246,0.1);
  border:1px solid rgba(59,130,246,0.22);
  color:var(--blue);cursor:pointer;
  transition:all var(--transition);margin-top:4px;
}
.profile-upload-btn:hover{background:rgba(59,130,246,0.2)}
.profile-preview{
  width:110px;height:110px;border-radius:50%;object-fit:cover;
  border:2.5px solid var(--cyan);display:none;margin:0 auto 8px;
  box-shadow:0 0 16px rgba(6,182,212,0.3);
}

/* ══ TEACHER DASHBOARD ═══════════════════════════════════ */
.td-hero{
  border-radius:20px;padding:26px 30px;margin-bottom:20px;
  position:relative;overflow:hidden;
  background:linear-gradient(135deg,
    rgba(37,99,235,0.16) 0%,
    rgba(139,92,246,0.08) 50%,
    rgba(6,182,212,0.06) 100%);
  border:1px solid rgba(59,130,246,0.18);
  box-shadow:0 0 50px rgba(37,99,235,0.06),var(--card-shadow);
}
.td-hero::before{
  content:'';position:absolute;top:-80px;right:-60px;
  width:280px;height:280px;border-radius:50%;
  background:radial-gradient(circle,rgba(139,92,246,0.1) 0%,transparent 70%);
  pointer-events:none;
}
.td-hero::after{
  content:'👨‍🏫';
  position:absolute;right:28px;top:50%;transform:translateY(-50%);
  font-size:72px;opacity:0.08;
}
.td-hero h1{
  font-family:'Space Grotesk',sans-serif;
  font-size:24px;font-weight:800;margin-bottom:5px;
  letter-spacing:-0.5px;position:relative;z-index:1;
}
.td-hero p{color:var(--text2);font-size:13.5px;position:relative;z-index:1;line-height:1.6}

/* table row risk coloring */
.risk-high td:first-child{border-left:2.5px solid var(--red)!important}
.risk-mid  td:first-child{border-left:2.5px solid var(--amber)!important}
.risk-ok   td:first-child{border-left:2.5px solid var(--green)!important}

.absent-chip{
  display:inline-flex;align-items:center;gap:7px;
  background:rgba(239,68,68,0.07);
  border:1px solid rgba(239,68,68,0.18);
  border-radius:10px;padding:7px 12px;margin:4px;
  transition:all var(--transition);
}
.absent-chip:hover{background:rgba(239,68,68,0.13);transform:translateY(-1px)}
.absent-chip-avatar{
  width:26px;height:26px;border-radius:50%;
  background:linear-gradient(135deg,var(--red),#f87171);
  display:flex;align-items:center;justify-content:center;
  font-size:11px;font-weight:700;flex-shrink:0;
}
.qa-grid{display:grid;grid-template-columns:1fr 1fr;gap:9px}
.qa-btn{
  display:flex;align-items:center;gap:10px;padding:12px 14px;
  background:rgba(255,255,255,0.025);border:1px solid var(--border);
  border-radius:var(--radius-sm);text-decoration:none;color:var(--text);
  font-size:13px;font-weight:600;transition:all var(--transition);
  box-shadow:var(--card-shadow);
}
.qa-btn:hover{
  background:rgba(255,255,255,0.06);
  border-color:var(--border2);
  transform:translateY(-2px);
  box-shadow:0 6px 20px rgba(0,0,0,0.3);
}
.qa-btn-icon{
  width:32px;height:32px;border-radius:8px;
  display:flex;align-items:center;justify-content:center;
  font-size:14px;flex-shrink:0;
}
.ring-wrap{position:relative;width:110px;height:110px;margin:0 auto 8px}
.ring-wrap svg{transform:rotate(-90deg)}
.ring-val{
  position:absolute;inset:0;display:flex;
  align-items:center;justify-content:center;flex-direction:column;text-align:center;
}
.ring-num{font-family:'Space Grotesk',sans-serif;font-size:22px;font-weight:700}
.ring-lbl{font-size:10px;color:var(--text2);margin-top:1px}
.notice{
  padding:11px 15px;border-radius:var(--radius-xs);
  font-size:13px;display:flex;align-items:center;gap:8px;margin-bottom:9px;
}
.notice-warn{background:rgba(245,158,11,0.07);border:1px solid rgba(245,158,11,0.18);color:var(--amber-l)}

/* ══ SUBSCRIPTION / UPGRADE ══════════════════════════════ */
.upgrade-hero{
  border-radius:22px;padding:50px 40px;text-align:center;
  background:linear-gradient(145deg,#06101f 0%,#080e1d 40%,#0b1224 100%);
  border:1px solid rgba(59,130,246,0.14);
  position:relative;overflow:hidden;margin-bottom:28px;
  box-shadow:0 0 80px rgba(37,99,235,0.07),var(--card-shadow);
}
.upgrade-hero::before{
  content:'';position:absolute;top:-100px;left:50%;transform:translateX(-50%);
  width:500px;height:300px;border-radius:50%;
  background:radial-gradient(ellipse,rgba(37,99,235,0.1) 0%,transparent 70%);
  pointer-events:none;
}
.upgrade-hero::after{
  content:'';position:absolute;bottom:-80px;right:-60px;
  width:280px;height:280px;border-radius:50%;
  background:radial-gradient(circle,rgba(139,92,246,0.08) 0%,transparent 70%);
  pointer-events:none;
}
.upgrade-hero h1{
  font-family:'Space Grotesk',sans-serif;
  font-size:36px;font-weight:800;letter-spacing:-1.5px;
  position:relative;z-index:1;margin-bottom:12px;
  background:linear-gradient(135deg,#eef4ff 30%,#94a3b8 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}
.upgrade-hero p{color:var(--text2);font-size:15px;position:relative;z-index:1;line-height:1.7;max-width:480px;margin:0 auto}

.plan-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-bottom:28px}
.plan-card{
  background:linear-gradient(160deg,rgba(10,18,34,0.9) 0%,rgba(6,12,24,0.95) 100%);
  border:1px solid var(--border2);border-radius:20px;
  padding:28px 22px;text-align:center;position:relative;overflow:hidden;
  transition:all var(--transition);
  box-shadow:var(--card-shadow);
}
.plan-card:hover{
  transform:translateY(-7px);
  box-shadow:0 24px 60px rgba(0,0,0,0.55),0 0 30px rgba(37,99,235,0.08);
  border-color:rgba(255,255,255,0.12);
}
.plan-card::before{content:'';position:absolute;top:0;left:0;right:0;height:1.5px}
.plan-monthly::before{background:linear-gradient(90deg,var(--blue),var(--cyan))}
.plan-yearly::before{background:linear-gradient(90deg,var(--purple),var(--pink))}
.plan-5year::before{background:linear-gradient(90deg,var(--amber),var(--green))}
.plan-popular{
  border-color:rgba(139,92,246,0.3)!important;
  box-shadow:0 0 40px rgba(139,92,246,0.08),var(--card-shadow)!important;
}
.plan-popular:hover{box-shadow:0 24px 60px rgba(0,0,0,0.55),0 0 40px rgba(139,92,246,0.14)!important}
.plan-badge{
  position:absolute;top:14px;right:14px;
  background:linear-gradient(135deg,var(--purple),var(--pink));
  color:white;padding:3px 11px;border-radius:20px;font-size:10.5px;font-weight:700;
  box-shadow:0 2px 8px rgba(139,92,246,0.4);
}
.plan-icon{font-size:38px;margin-bottom:14px}
.plan-name{
  font-family:'Space Grotesk',sans-serif;
  font-size:16px;font-weight:700;margin-bottom:8px;letter-spacing:-0.2px;
}
.plan-price{
  font-family:'Space Grotesk',sans-serif;
  font-size:40px;font-weight:800;letter-spacing:-1.5px;
  margin-bottom:4px;line-height:1;
}
.plan-period{font-size:12.5px;color:var(--text2);margin-bottom:20px}
.plan-features{
  list-style:none;text-align:left;margin-bottom:24px;
  display:flex;flex-direction:column;gap:9px;
}
.plan-features li{
  display:flex;align-items:center;gap:10px;
  font-size:13px;color:var(--text2);
}
.plan-features li::before{
  content:"✓";color:var(--green);font-weight:700;flex-shrink:0;
  font-size:12px;
}

/* ══ EXPIRED OVERLAY ═════════════════════════════════════ */
.expired-overlay{
  position:fixed;inset:0;z-index:9999;
  background:rgba(2,9,18,0.93);
  backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
  display:flex;align-items:center;justify-content:center;
}
.expired-modal{
  background:rgba(8,15,30,0.85);
  backdrop-filter:blur(40px);-webkit-backdrop-filter:blur(40px);
  border:1px solid rgba(239,68,68,0.25);
  border-radius:24px;padding:48px 42px;max-width:480px;width:90%;
  text-align:center;position:relative;overflow:hidden;
  box-shadow:0 40px 100px rgba(0,0,0,0.75);
  animation:modal-in 0.32s cubic-bezier(.34,1.56,.64,1);
}
@keyframes modal-in{from{opacity:0;transform:scale(0.88)}to{opacity:1;transform:none}}
.expired-modal::before{
  content:'';position:absolute;top:0;left:0;right:0;height:1.5px;
  background:linear-gradient(90deg,transparent,var(--red),var(--purple),var(--blue),transparent);
}
.lock-icon{font-size:58px;margin-bottom:18px;display:block}
.expired-title{
  font-family:'Space Grotesk',sans-serif;font-size:24px;font-weight:800;
  color:var(--red-l);margin-bottom:10px;letter-spacing:-0.5px;
}
.expired-sub{color:var(--text2);font-size:14px;line-height:1.7;margin-bottom:26px}

/* ══ DEV TABLE ═══════════════════════════════════════════ */
.dev-table td,.dev-table th{padding:10px 14px;border-bottom:1px solid var(--border);font-size:13px}
.dev-table th{font-size:9.5px;letter-spacing:1.2px;text-transform:uppercase;color:var(--muted)}

/* ══ RESPONSIVE — TABLET ═════════════════════════════════ */
@media(max-width:768px){
  .plan-grid{grid-template-columns:1fr}
}

/* ══ RESPONSIVE — MOBILE ═════════════════════════════════ */
@media(max-width:960px){
  .sidebar{display:none}
  .main{margin-left:0 !important}
  .stats-row{grid-template-columns:1fr 1fr}
  .grid-2,.grid-3{grid-template-columns:1fr}
  .main{padding-bottom:72px}
  [style*="repeat(4"]{grid-template-columns:1fr 1fr !important}
  /* prevent ANY horizontal overflow */
  .page{overflow-x:hidden;max-width:100vw}
  .hero{overflow:hidden}
  .hero p{word-break:break-word}
  .card{overflow:hidden;word-break:break-word}
  .stat{overflow:hidden}
}
@media(max-width:560px){
  .page{padding:12px;overflow-x:hidden;max-width:100vw}
  .stats-row{grid-template-columns:1fr 1fr}
  body{overflow-x:hidden}
  .plan-grid{grid-template-columns:1fr !important}
  .hero{padding:18px}
  .hero h1{font-size:19px}
  .login-card{padding:32px 22px;border-radius:20px}
  .plan-card{min-width:0;word-break:break-word}
  .stat-val{font-size:26px}
  video{width:100%!important;max-width:100%}
  .scan-wrap{width:100%}
  .tbl-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch}
  table{min-width:400px}
  .sec-tabs{overflow-x:auto;flex-wrap:nowrap;padding-bottom:6px;-webkit-overflow-scrolling:touch}
  .sec-tab{flex-shrink:0}
  .upgrade-hero{padding:30px 20px}
  .upgrade-hero h1{font-size:26px}
  .qa-grid{grid-template-columns:1fr}
}

/* ══ MOBILE BOTTOM NAV ═══════════════════════════════════ */
.mobile-nav{
  display:none;
  position:fixed;bottom:0;left:0;right:0;
  height:66px;
  background:rgba(2,8,18,0.97);
  backdrop-filter:blur(24px) saturate(1.3);
  -webkit-backdrop-filter:blur(24px) saturate(1.3);
  border-top:1px solid rgba(255,255,255,0.07);
  z-index:200;padding:0 4px;
  padding-bottom:env(safe-area-inset-bottom);
  box-shadow:0 -4px 24px rgba(0,0,0,0.5);
}
.mobile-nav-inner{display:flex;align-items:stretch;height:100%}
.mnav-item{
  flex:1;display:flex;flex-direction:column;
  align-items:center;justify-content:center;
  text-decoration:none;color:var(--muted);
  font-size:9.5px;font-weight:600;gap:4px;
  border-radius:14px;margin:6px 2px;
  transition:all 0.15s cubic-bezier(.4,0,.2,1);
  letter-spacing:0.2px;position:relative;
  -webkit-tap-highlight-color:transparent;
}
.mnav-item svg{width:20px;height:20px;flex-shrink:0;transition:transform 0.15s}
.mnav-item:active{transform:scale(0.9)}
.mnav-item:hover,.mnav-active{color:var(--blue)!important}
.mnav-active{background:rgba(37,99,235,0.1)}
.mnav-active svg{transform:scale(1.1);filter:drop-shadow(0 0 4px rgba(59,130,246,0.5))}
.mnav-active::before{
  content:'';position:absolute;top:-6px;left:50%;transform:translateX(-50%);
  width:22px;height:2px;border-radius:2px;
  background:linear-gradient(90deg,var(--blue),var(--cyan));
  box-shadow:0 0 8px var(--blue);
}
.mnav-premium{color:rgba(252,211,77,0.6)!important}
.mnav-premium:hover,.mnav-premium.mnav-active{color:var(--amber-l)!important}
.mnav-premium.mnav-active{background:rgba(245,158,11,0.09)}
.mnav-premium.mnav-active svg{filter:drop-shadow(0 0 4px rgba(245,158,11,0.5))}
.mnav-premium.mnav-active::before{
  background:linear-gradient(90deg,var(--amber),var(--amber-l));
  box-shadow:0 0 8px var(--amber);
}

/* ══ MOBILE TOPBAR ═══════════════════════════════════════ */
.mobile-topbar{
  display:none;position:fixed;top:0;left:0;right:0;z-index:150;
  height:54px;padding:0 16px;
  background:rgba(2,8,18,0.96);
  backdrop-filter:blur(24px) saturate(1.3);
  -webkit-backdrop-filter:blur(24px) saturate(1.3);
  border-bottom:1px solid rgba(255,255,255,0.06);
  align-items:center;justify-content:space-between;
  box-shadow:0 4px 24px rgba(0,0,0,0.4);
}
.mobile-logo{
  font-family:'Space Grotesk',sans-serif;font-size:17px;font-weight:700;
  display:flex;align-items:center;gap:8px;
}
.mobile-logo span{color:var(--cyan)}
.hamburger-btn{
  width:36px;height:36px;border-radius:10px;
  background:rgba(255,255,255,0.05);border:1px solid var(--border2);
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  gap:5px;cursor:pointer;transition:all 0.15s;
  -webkit-tap-highlight-color:transparent;
}
.hamburger-btn:hover{background:rgba(255,255,255,0.09)}
.hamburger-btn span{
  display:block;width:18px;height:2px;
  background:var(--text2);border-radius:2px;transition:all 0.2s;
}

/* ══ DRAWER ══════════════════════════════════════════════ */
.drawer-overlay{
  display:none;position:fixed;inset:0;z-index:190;
  background:rgba(0,0,0,0.65);backdrop-filter:blur(5px);
  -webkit-backdrop-filter:blur(5px);
}
.drawer{
  position:fixed;top:0;right:-280px;bottom:0;width:265px;z-index:195;
  background:linear-gradient(180deg,#06101f,#030810);
  border-left:1px solid var(--border);
  transition:right 0.28s cubic-bezier(.4,0,.2,1);
  display:flex;flex-direction:column;padding:20px 0;
  overflow-y:auto;
  box-shadow:-8px 0 40px rgba(0,0,0,0.6);
}
.drawer.open{right:0}
.drawer-header{
  padding:8px 20px 16px;border-bottom:1px solid var(--border);
  margin-bottom:8px;
  display:flex;align-items:center;justify-content:space-between;
}
.drawer-close{
  width:32px;height:32px;border-radius:8px;border:none;
  background:rgba(255,255,255,0.05);color:var(--text2);
  font-size:16px;cursor:pointer;transition:all 0.15s;
  display:flex;align-items:center;justify-content:center;
}
.drawer-close:hover{background:rgba(255,255,255,0.09);color:var(--text)}
.drawer-item{
  display:flex;align-items:center;gap:12px;
  padding:12px 20px;color:var(--text2);text-decoration:none;
  font-size:13.5px;font-weight:500;transition:all 0.12s;
  border-left:3px solid transparent;
}
.drawer-item svg{width:17px;height:17px;flex-shrink:0;opacity:0.65}
.drawer-item:hover{
  color:var(--text);
  background:rgba(255,255,255,0.04);
}
.drawer-item:hover svg{opacity:1}
.drawer-active{
  color:var(--blue)!important;
  border-left-color:var(--blue)!important;
  background:rgba(37,99,235,0.08)!important;
}
.drawer-active svg{opacity:1!important}

@media(max-width:960px){
  .mobile-nav{display:flex}
  .mobile-topbar{display:flex}
  .topbar{display:none}
  .page{margin-top:54px}
}

/* ══ GEN Z ANIMATIONS ═══════════════════════════════════ */

/* Page load — everything fades in */
@keyframes fadeUp{
  from{opacity:0;transform:translateY(18px)}
  to{opacity:1;transform:translateY(0)}
}
@keyframes fadeIn{
  from{opacity:0}to{opacity:1}
}
@keyframes slideInLeft{
  from{opacity:0;transform:translateX(-22px)}
  to{opacity:1;transform:translateX(0)}
}
@keyframes scaleIn{
  from{opacity:0;transform:scale(0.92)}
  to{opacity:1;transform:scale(1)}
}
@keyframes shimmer{
  0%{background-position:-200% center}
  100%{background-position:200% center}
}
@keyframes float{
  0%,100%{transform:translateY(0)}
  50%{transform:translateY(-6px)}
}
@keyframes glow-pulse{
  0%,100%{box-shadow:0 0 12px rgba(59,130,246,0.2)}
  50%{box-shadow:0 0 28px rgba(59,130,246,0.5),0 0 50px rgba(6,182,212,0.2)}
}
@keyframes border-glow{
  0%,100%{border-color:rgba(59,130,246,0.15)}
  50%{border-color:rgba(59,130,246,0.45)}
}
@keyframes count-up{
  from{opacity:0;transform:translateY(10px) scale(0.8)}
  to{opacity:1;transform:translateY(0) scale(1)}
}
@keyframes spin-slow{
  from{transform:rotate(0deg)}
  to{transform:rotate(360deg)}
}
@keyframes ripple-out{
  0%{transform:scale(0);opacity:1}
  100%{transform:scale(3);opacity:0}
}

/* ── Apply on page load ── */
.hero{animation:fadeUp 0.55s cubic-bezier(.34,1.2,.64,1) both}
.stats-row .stat:nth-child(1){animation:fadeUp 0.45s 0.08s cubic-bezier(.34,1.2,.64,1) both}
.stats-row .stat:nth-child(2){animation:fadeUp 0.45s 0.16s cubic-bezier(.34,1.2,.64,1) both}
.stats-row .stat:nth-child(3){animation:fadeUp 0.45s 0.24s cubic-bezier(.34,1.2,.64,1) both}
.stats-row .stat:nth-child(4){animation:fadeUp 0.45s 0.32s cubic-bezier(.34,1.2,.64,1) both}
.card{animation:fadeUp 0.5s 0.1s cubic-bezier(.34,1.1,.64,1) both}
.sidebar{animation:slideInLeft 0.4s cubic-bezier(.34,1.1,.64,1) both}
.topbar{animation:fadeIn 0.3s ease both}
.mobile-topbar{animation:fadeIn 0.3s ease both}
.mobile-nav{animation:fadeUp 0.35s 0.15s cubic-bezier(.34,1.1,.64,1) both}

/* ── Stat values pop in ── */
.stat-val{
  animation:count-up 0.5s 0.3s cubic-bezier(.34,1.4,.64,1) both;
  display:inline-block;
}

/* ── Logo floats gently ── */
.logo-icon{animation:float 4s ease-in-out infinite}

/* ── Active nav item glows ── */
.nav-active{animation:glow-pulse 3s ease-in-out infinite}

/* ── Hero card border breathes ── */
.hero{animation:fadeUp 0.55s cubic-bezier(.34,1.2,.64,1) both,
              border-glow 4s 1s ease-in-out infinite}

/* ── Student & gallery cards pop in sequence ── */
.student-card{animation:scaleIn 0.4s cubic-bezier(.34,1.2,.64,1) both}
.student-card:nth-child(1){animation-delay:0.05s}
.student-card:nth-child(2){animation-delay:0.10s}
.student-card:nth-child(3){animation-delay:0.15s}
.student-card:nth-child(4){animation-delay:0.20s}
.student-card:nth-child(5){animation-delay:0.25s}
.student-card:nth-child(6){animation-delay:0.30s}
.student-card:nth-child(n+7){animation-delay:0.35s}

.gallery-item{animation:scaleIn 0.4s cubic-bezier(.34,1.2,.64,1) both}
.gallery-item:nth-child(1){animation-delay:0.05s}
.gallery-item:nth-child(2){animation-delay:0.10s}
.gallery-item:nth-child(3){animation-delay:0.15s}
.gallery-item:nth-child(4){animation-delay:0.20s}
.gallery-item:nth-child(n+5){animation-delay:0.25s}

/* ── Login card entrance ── */
.login-card{animation:scaleIn 0.45s cubic-bezier(.34,1.3,.64,1) both}

/* ── Plan cards stagger ── */
.plan-card:nth-child(1){animation:fadeUp 0.45s 0.05s cubic-bezier(.34,1.2,.64,1) both}
.plan-card:nth-child(2){animation:fadeUp 0.45s 0.15s cubic-bezier(.34,1.2,.64,1) both}
.plan-card:nth-child(3){animation:fadeUp 0.45s 0.25s cubic-bezier(.34,1.2,.64,1) both}

/* ── Scan ring pulse ── */
.scan-ring{
  border-color:var(--cyan) !important;
  box-shadow:0 0 14px rgba(6,182,212,0.35);
}

/* ── Shimmer loading text ── */
.shimmer-text{
  background:linear-gradient(90deg,var(--text2) 0%,var(--cyan) 40%,var(--blue) 60%,var(--text2) 100%);
  background-size:200% auto;
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  animation:shimmer 3s linear infinite;
}

/* ── Glowing CTA button ── */
.btn-primary{
  animation:glow-pulse 3s 2s ease-in-out infinite;
}
.btn-primary:hover{animation:none}

/* ── Pill pop in ── */
.pill{animation:scaleIn 0.3s cubic-bezier(.34,1.4,.64,1) both}

/* ── Bottom nav items pop in sequence ── */
.mnav-item:nth-child(1){animation:fadeUp 0.3s 0.05s cubic-bezier(.34,1.3,.64,1) both}
.mnav-item:nth-child(2){animation:fadeUp 0.3s 0.10s cubic-bezier(.34,1.3,.64,1) both}
.mnav-item:nth-child(3){animation:fadeUp 0.3s 0.15s cubic-bezier(.34,1.3,.64,1) both}
.mnav-item:nth-child(4){animation:fadeUp 0.3s 0.20s cubic-bezier(.34,1.3,.64,1) both}
.mnav-item:nth-child(5){animation:fadeUp 0.3s 0.25s cubic-bezier(.34,1.3,.64,1) both}

/* ── Section tabs slide in ── */
.sec-tab{animation:fadeIn 0.4s ease both}
.sec-tab:nth-child(1){animation-delay:0.0s}
.sec-tab:nth-child(2){animation-delay:0.05s}
.sec-tab:nth-child(3){animation-delay:0.10s}
.sec-tab:nth-child(4){animation-delay:0.15s}
.sec-tab:nth-child(n+5){animation-delay:0.20s}

/* ── Table rows fade in ── */
tbody tr{animation:fadeIn 0.3s ease both}
tbody tr:nth-child(1){animation-delay:0.05s}
tbody tr:nth-child(2){animation-delay:0.08s}
tbody tr:nth-child(3){animation-delay:0.11s}
tbody tr:nth-child(4){animation-delay:0.14s}
tbody tr:nth-child(n+5){animation-delay:0.17s}

/* ── Alert slides in ── */
.alert{animation:slideInLeft 0.3s cubic-bezier(.34,1.2,.64,1) both !important}

/* ── Modal pop ── */
.expired-modal{animation:scaleIn 0.35s cubic-bezier(.34,1.4,.64,1) both}

/* ── Upgrade hero pulse ── */
.upgrade-hero{animation:fadeUp 0.5s cubic-bezier(.34,1.1,.64,1) both,
              border-glow 5s 1s ease-in-out infinite}

/* ── Section cards stagger ── */
.section-card{animation:scaleIn 0.4s cubic-bezier(.34,1.2,.64,1) both}
.section-grid .section-card:nth-child(1){animation-delay:0.04s}
.section-grid .section-card:nth-child(2){animation-delay:0.08s}
.section-grid .section-card:nth-child(3){animation-delay:0.12s}
.section-grid .section-card:nth-child(n+4){animation-delay:0.16s}

/* ── Tap ripple effect on buttons ── */
.btn{position:relative;overflow:hidden}
.btn::after{
  content:'';
  position:absolute;
  width:100px;height:100px;
  background:rgba(255,255,255,0.15);
  border-radius:50%;
  transform:scale(0);
  opacity:0;
  top:50%;left:50%;
  margin:-50px 0 0 -50px;
  pointer-events:none;
  transition:transform 0.4s ease,opacity 0.4s ease;
}
.btn:active::after{
  transform:scale(2.5);
  opacity:0;
  transition:0s;
}

/* ── Hover glow on stat cards ── */
.stat:hover{
  box-shadow:0 14px 40px rgba(0,0,0,0.4),0 0 20px rgba(59,130,246,0.08);
}
.s-blue:hover{box-shadow:0 14px 40px rgba(0,0,0,0.4),0 0 24px rgba(59,130,246,0.15)!important}
.s-green:hover{box-shadow:0 14px 40px rgba(0,0,0,0.4),0 0 24px rgba(16,185,129,0.15)!important}
.s-red:hover{box-shadow:0 14px 40px rgba(0,0,0,0.4),0 0 24px rgba(239,68,68,0.15)!important}
.s-amber:hover{box-shadow:0 14px 40px rgba(0,0,0,0.4),0 0 24px rgba(245,158,11,0.15)!important}

/* ── Neon glow on active bottom nav ── */
.mnav-active svg{
  filter:drop-shadow(0 0 6px rgba(59,130,246,0.7))!important;
}
.mnav-premium.mnav-active svg{
  filter:drop-shadow(0 0 6px rgba(245,158,11,0.7))!important;
}

/* ── Reduce motion for accessibility ── */
@media(prefers-reduced-motion:reduce){
  *{animation-duration:0.01ms!important;animation-iteration-count:1!important;transition-duration:0.01ms!important}
}

</style>
"""
