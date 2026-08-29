# styles.py — FaceNova UI Styles
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}

/* ══ DESIGN TOKENS ══════════════════════════════════════ */
:root{
  /* backgrounds */
  --bg:       #030712;
  --surface:  #060b14;
  --card:     #0a1120;
  --card2:    #0d1526;
  --border:   rgba(255,255,255,0.06);
  --border2:  rgba(255,255,255,0.10);

  /* brand */
  --blue:     #3b82f6;
  --blue-d:   #1d4ed8;
  --cyan:     #06b6d4;
  --green:    #10b981;
  --green-l:  #34d399;
  --red:      #ef4444;
  --red-l:    #f87171;
  --amber:    #f59e0b;
  --amber-l:  #fcd34d;
  --purple:   #8b5cf6;
  --purple-l: #a78bfa;
  --pink:     #ec4899;

  /* text */
  --text:     #f0f6ff;
  --text2:    #94a3b8;
  --muted:    #475569;

  /* glow */
  --glow-blue:   0 0 24px rgba(59,130,246,0.18);
  --glow-cyan:   0 0 24px rgba(6,182,212,0.18);
  --glow-green:  0 0 24px rgba(16,185,129,0.18);

  --sidebar-w:252px;
  --radius:16px;
  --radius-sm:10px;
  --transition:0.18s cubic-bezier(.4,0,.2,1);
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
  /* subtle noise */
  background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.025'/%3E%3C/svg%3E");
}

/* ══ SCROLLBAR ═══════════════════════════════════════════ */
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.1);border-radius:10px}
::-webkit-scrollbar-thumb:hover{background:rgba(255,255,255,0.18)}

/* ══ GLASSMORPHISM MIXIN ═════════════════════════════════ */
.glass{
  background:rgba(255,255,255,0.028);
  backdrop-filter:blur(20px) saturate(1.4);
  -webkit-backdrop-filter:blur(20px) saturate(1.4);
  border:1px solid var(--border2);
}

/* ══ SIDEBAR ════════════════════════════════════════════ */
.sidebar{
  width:var(--sidebar-w);
  background:linear-gradient(180deg,#060c1a 0%,#04080f 100%);
  border-right:1px solid var(--border);
  display:flex;flex-direction:column;
  position:fixed;top:0;bottom:0;left:0;z-index:100;
  overflow:hidden;
}
.sidebar::before{
  content:'';position:absolute;top:-120px;left:-80px;
  width:300px;height:300px;border-radius:50%;
  background:radial-gradient(circle,rgba(59,130,246,0.08) 0%,transparent 70%);
  pointer-events:none;
}

.sidebar-logo{
  padding:22px 20px 18px;
  border-bottom:1px solid var(--border);
  position:relative;
}
.logo-mark{display:flex;align-items:center;gap:11px}
.logo-icon{
  width:38px;height:38px;border-radius:11px;
  background:linear-gradient(135deg,#2563eb,#06b6d4);
  display:flex;align-items:center;justify-content:center;
  font-size:18px;
  box-shadow:0 0 18px rgba(37,99,235,0.5),inset 0 1px 0 rgba(255,255,255,0.15);
}
.logo-text{font-family:'Space Grotesk',sans-serif;font-size:19px;font-weight:700;letter-spacing:-0.5px}
.logo-text span{
  background:linear-gradient(90deg,var(--cyan),var(--blue));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}
.logo-tag{font-size:10px;font-weight:600;letter-spacing:1.5px;
  color:var(--muted);text-transform:uppercase;margin-top:2px}

.sidebar-section{
  font-size:9.5px;font-weight:700;letter-spacing:2px;
  color:var(--muted);text-transform:uppercase;
  padding:18px 20px 7px;
}

.nav-item{
  display:flex;align-items:center;gap:11px;
  padding:9px 16px 9px 20px;
  color:var(--text2);text-decoration:none;
  font-size:13.5px;font-weight:500;
  transition:all var(--transition);
  border-left:2px solid transparent;
  margin:1px 8px 1px 0;
  border-radius:0 10px 10px 0;
  position:relative;
}
.nav-item svg{width:17px;height:17px;flex-shrink:0;transition:transform var(--transition)}
.nav-item:hover{
  color:var(--text);
  background:rgba(255,255,255,0.05);
  border-left-color:rgba(255,255,255,0.2);
}
.nav-item:hover svg{transform:translateX(1px)}
.nav-active{
  color:var(--blue)!important;
  background:linear-gradient(90deg,rgba(59,130,246,0.12),rgba(59,130,246,0.03))!important;
  border-left-color:var(--blue)!important;
  font-weight:600!important;
}
.nav-active::after{
  content:'';position:absolute;right:0;top:50%;transform:translateY(-50%);
  width:3px;height:60%;border-radius:2px 0 0 2px;
  background:var(--blue);opacity:0.5;
}

.sidebar-footer{
  margin-top:auto;
  padding:14px 20px 0;
  border-top:1px solid var(--border);
}
.status-dot{
  display:inline-block;width:7px;height:7px;
  background:var(--green);border-radius:50%;
  margin-right:8px;
  box-shadow:0 0 6px var(--green);
  animation:pulse-dot 2.5s infinite;
}
@keyframes pulse-dot{
  0%,100%{opacity:1;box-shadow:0 0 6px var(--green)}
  50%{opacity:0.5;box-shadow:0 0 2px var(--green)}
}

/* ══ TOPBAR ═════════════════════════════════════════════ */
.main{margin-left:var(--sidebar-w);flex:1;display:flex;flex-direction:column;min-height:100vh}
.topbar{
  height:60px;padding:0 30px;
  background:rgba(6,11,20,0.85);
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border-bottom:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between;
  position:sticky;top:0;z-index:50;
}
.topbar-title{
  font-family:'Space Grotesk',sans-serif;
  font-size:15.5px;font-weight:600;color:var(--text);
}
.topbar-right{display:flex;align-items:center;gap:12px}
.tbadge{
  background:linear-gradient(135deg,rgba(59,130,246,0.18),rgba(6,182,212,0.1));
  border:1px solid rgba(59,130,246,0.25);
  color:var(--blue);padding:4px 12px;
  border-radius:20px;font-size:11.5px;font-weight:700;
  letter-spacing:0.3px;
}
.page{padding:26px 30px;flex:1}

/* ══ STAT CARDS ═════════════════════════════════════════ */
.stats-row{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:22px}
.stat{
  background:var(--card);
  border:1px solid var(--border);
  border-radius:var(--radius);
  padding:20px;position:relative;overflow:hidden;
  transition:transform var(--transition),border-color var(--transition);
}
.stat:hover{transform:translateY(-2px);border-color:var(--border2)}
.stat::before{content:'';position:absolute;top:0;left:0;right:0;height:1.5px}
.stat::after{
  content:'';position:absolute;top:0;right:0;
  width:80px;height:80px;border-radius:50%;
  opacity:0.07;transform:translate(20px,-20px);
}
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
  width:36px;height:36px;border-radius:9px;
  display:flex;align-items:center;justify-content:center;
  font-size:16px;margin-bottom:12px;
}
.stat-val{
  font-family:'Space Grotesk',sans-serif;
  font-size:30px;font-weight:700;line-height:1;margin-bottom:3px;
  letter-spacing:-0.5px;
}
.stat-lbl{font-size:12px;color:var(--text2);font-weight:500}

/* ══ PROGRESS ════════════════════════════════════════════ */
.pbar-wrap{
  background:rgba(255,255,255,0.05);
  border-radius:20px;height:5px;overflow:hidden;
}
.pbar{height:100%;border-radius:20px;transition:width 0.8s cubic-bezier(.4,0,.2,1)}
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
}
.card:hover{border-color:var(--border2)}
.card-glass{
  background:rgba(10,17,32,0.6);
  backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);
  border:1px solid rgba(255,255,255,0.07);
  border-radius:var(--radius);padding:22px;
}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.grid-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}
.sec-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px}
.sec-title{
  font-family:'Space Grotesk',sans-serif;
  font-size:15px;font-weight:700;
}
.sec-sub{font-size:12px;color:var(--text2);margin-top:2px}

/* ══ TABLE ═══════════════════════════════════════════════ */
.tbl-wrap{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:13px}
thead th{
  background:rgba(255,255,255,0.03);
  padding:10px 14px;text-align:left;
  font-size:10px;font-weight:700;
  letter-spacing:1.2px;text-transform:uppercase;
  color:var(--muted);border-bottom:1px solid var(--border);
}
tbody td{padding:12px 14px;border-bottom:1px solid rgba(255,255,255,0.04)}
tbody tr:hover{background:rgba(255,255,255,0.025)}
tbody tr:last-child td{border-bottom:none}

/* ══ PILLS ═══════════════════════════════════════════════ */
.pill{
  display:inline-flex;align-items:center;gap:4px;
  padding:3px 10px;border-radius:20px;
  font-size:11.5px;font-weight:600;letter-spacing:0.2px;
}
.pill-green{background:rgba(16,185,129,0.12);color:var(--green-l);border:1px solid rgba(16,185,129,0.2)}
.pill-red{background:rgba(239,68,68,0.12);color:var(--red-l);border:1px solid rgba(239,68,68,0.2)}
.pill-amber{background:rgba(245,158,11,0.12);color:var(--amber-l);border:1px solid rgba(245,158,11,0.2)}
.pill-blue{background:rgba(59,130,246,0.12);color:var(--blue);border:1px solid rgba(59,130,246,0.2)}
.pill-purple{background:rgba(139,92,246,0.12);color:var(--purple-l);border:1px solid rgba(139,92,246,0.2)}

/* ══ BUTTONS ═════════════════════════════════════════════ */
.btn{
  display:inline-flex;align-items:center;gap:7px;
  padding:9px 18px;border:none;border-radius:var(--radius-sm);
  font-size:13px;font-weight:600;cursor:pointer;
  transition:all var(--transition);
  text-decoration:none;font-family:'Inter',sans-serif;
  letter-spacing:0.1px;position:relative;overflow:hidden;
}
.btn::before{
  content:'';position:absolute;inset:0;
  background:linear-gradient(180deg,rgba(255,255,255,0.07) 0%,transparent 100%);
  pointer-events:none;border-radius:inherit;
}
.btn-primary{
  background:linear-gradient(135deg,#2563eb,#1d4ed8);
  color:white;
  box-shadow:0 1px 0 rgba(255,255,255,0.1) inset,0 4px 12px rgba(37,99,235,0.3);
}
.btn-primary:hover{
  background:linear-gradient(135deg,#3b82f6,#2563eb);
  transform:translateY(-1px);
  box-shadow:0 1px 0 rgba(255,255,255,0.1) inset,0 8px 20px rgba(37,99,235,0.4);
}
.btn-cyan{
  background:linear-gradient(135deg,#0891b2,#0e7490);
  color:white;
  box-shadow:0 1px 0 rgba(255,255,255,0.1) inset,0 4px 12px rgba(8,145,178,0.3);
}
.btn-cyan:hover{
  background:linear-gradient(135deg,#06b6d4,#0891b2);
  transform:translateY(-1px);
  box-shadow:0 1px 0 rgba(255,255,255,0.1) inset,0 8px 20px rgba(6,182,212,0.4);
}
.btn-ghost{
  background:rgba(255,255,255,0.05);
  color:var(--text2);
  border:1px solid var(--border2);
}
.btn-ghost:hover{background:rgba(255,255,255,0.09);color:var(--text);border-color:rgba(255,255,255,0.15)}
.btn-red{
  background:rgba(239,68,68,0.12);color:var(--red-l);
  border:1px solid rgba(239,68,68,0.22);
}
.btn-red:hover{background:rgba(239,68,68,0.22)}
.btn-green{
  background:linear-gradient(135deg,#059669,#047857);color:white;
  box-shadow:0 4px 12px rgba(5,150,105,0.3);
}
.btn-green:hover{transform:translateY(-1px);box-shadow:0 8px 20px rgba(16,185,129,0.4)}
.btn-sm{padding:6px 13px;font-size:12px}
.btn-xs{padding:4px 10px;font-size:11px}

/* ══ FORMS ═══════════════════════════════════════════════ */
.form-group{margin-bottom:15px}
label{
  display:block;font-size:12px;font-weight:600;
  color:var(--text2);margin-bottom:7px;letter-spacing:0.4px;text-transform:uppercase;
}
input[type=text],input[type=password],select,textarea{
  width:100%;
  background:rgba(255,255,255,0.04);
  border:1px solid var(--border2);
  border-radius:var(--radius-sm);
  padding:10px 13px;
  color:var(--text);font-size:13.5px;
  font-family:'Inter',sans-serif;
  transition:border-color var(--transition),box-shadow var(--transition);
  outline:none;
}
input[type=text]:focus,input[type=password]:focus,select:focus,textarea:focus{
  border-color:var(--blue);
  box-shadow:0 0 0 3px rgba(59,130,246,0.12);
  background:rgba(59,130,246,0.04);
}
select option{background:#0a1120;color:var(--text)}
input[type=file]{
  width:100%;
  background:rgba(255,255,255,0.03);
  border:1.5px dashed rgba(255,255,255,0.12);
  border-radius:var(--radius-sm);
  padding:14px 13px;color:var(--text2);
  font-size:13px;font-family:'Inter',sans-serif;
  cursor:pointer;transition:border-color var(--transition);
}
input[type=file]:hover{border-color:var(--blue)}

/* ══ ALERTS ══════════════════════════════════════════════ */
.alert{
  padding:12px 16px;border-radius:var(--radius-sm);
  font-size:13.5px;margin-bottom:16px;
  display:flex;align-items:center;gap:9px;
  animation:slide-in 0.2s ease;
}
@keyframes slide-in{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:none}}
.alert-success{background:rgba(16,185,129,0.09);border:1px solid rgba(16,185,129,0.22);color:var(--green-l)}
.alert-error{background:rgba(239,68,68,0.09);border:1px solid rgba(239,68,68,0.22);color:var(--red-l)}
.alert-info{background:rgba(59,130,246,0.09);border:1px solid rgba(59,130,246,0.22);color:var(--blue)}
.alert-warn{background:rgba(245,158,11,0.09);border:1px solid rgba(245,158,11,0.22);color:var(--amber-l)}

/* ══ HERO BANNER ═════════════════════════════════════════ */
.hero{
  border-radius:20px;padding:26px 30px;margin-bottom:22px;
  position:relative;overflow:hidden;
  background:linear-gradient(135deg,rgba(37,99,235,0.15) 0%,rgba(6,182,212,0.06) 50%,rgba(139,92,246,0.08) 100%);
  border:1px solid rgba(59,130,246,0.18);
}
.hero::before{
  content:'';position:absolute;top:-60px;right:-60px;
  width:220px;height:220px;border-radius:50%;
  background:radial-gradient(circle,rgba(59,130,246,0.12) 0%,transparent 70%);
}
.hero::after{
  content:'';position:absolute;bottom:-40px;left:30%;
  width:160px;height:160px;border-radius:50%;
  background:radial-gradient(circle,rgba(6,182,212,0.07) 0%,transparent 70%);
}
.hero h1{
  font-family:'Space Grotesk',sans-serif;
  font-size:23px;font-weight:800;margin-bottom:5px;
  letter-spacing:-0.5px;position:relative;z-index:1;
}
.hero p{color:var(--text2);font-size:13.5px;position:relative;z-index:1;line-height:1.5}
.hero-actions{margin-top:18px;display:flex;gap:10px;position:relative;z-index:1}

/* ══ LOG ITEMS ═══════════════════════════════════════════ */
.log-item{
  display:flex;align-items:center;gap:13px;
  padding:11px 0;border-bottom:1px solid rgba(255,255,255,0.04);
  transition:background var(--transition);
}
.log-item:last-child{border-bottom:none}
.log-avatar{
  width:36px;height:36px;border-radius:9px;flex-shrink:0;
  background:linear-gradient(135deg,var(--blue),var(--purple));
  display:flex;align-items:center;justify-content:center;
  font-weight:700;font-size:14px;
}
.log-info{flex:1}
.log-name{font-weight:600;font-size:13.5px}
.log-time{font-size:11.5px;color:var(--text2);margin-top:1px}

/* ══ STUDENT CARDS ═══════════════════════════════════════ */
.student-grid{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(188px,1fr));
  gap:13px;
}
.student-card{
  background:var(--card);
  border:1px solid var(--border);
  border-radius:var(--radius);
  padding:20px 16px 16px;
  text-align:center;
  transition:all var(--transition);
  position:relative;overflow:hidden;
}
.student-card::before{
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,0.1),transparent);
}
.student-card:hover{
  transform:translateY(-4px);
  border-color:rgba(59,130,246,0.25);
  box-shadow:0 12px 32px rgba(0,0,0,0.4);
}
.s-avatar{
  width:72px;height:72px;border-radius:50%;object-fit:cover;
  margin:0 auto 10px;
  border:2px solid var(--border2);
  box-shadow:0 0 0 4px rgba(255,255,255,0.03);
  transition:box-shadow var(--transition);
}
.student-card:hover .s-avatar{box-shadow:0 0 0 4px rgba(59,130,246,0.15)}
.s-avatar-placeholder{
  width:72px;height:72px;border-radius:50%;
  background:linear-gradient(135deg,var(--blue),var(--purple));
  display:flex;align-items:center;justify-content:center;
  font-size:24px;font-weight:700;
  margin:0 auto 10px;
  border:2px solid rgba(139,92,246,0.3);
}
.s-name{font-weight:700;font-size:13.5px;margin-bottom:3px}
.s-pct{font-family:'Space Grotesk',sans-serif;font-size:24px;font-weight:700}

/* ══ GALLERY ═════════════════════════════════════════════ */
.gallery-grid{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(195px,1fr));
  gap:13px;
}
.gallery-item{
  background:var(--card);border:1px solid var(--border);
  border-radius:var(--radius);overflow:hidden;
  transition:all var(--transition);
}
.gallery-item:hover{
  transform:translateY(-4px);
  border-color:rgba(59,130,246,0.2);
  box-shadow:0 12px 28px rgba(0,0,0,0.4);
}
.gallery-item img{width:100%;height:155px;object-fit:cover;display:block}
.gallery-item-info{padding:12px}
.gallery-item-name{font-size:13.5px;font-weight:700}
.gallery-item-stat{font-size:11.5px;color:var(--text2);margin-top:2px}

/* ══ CALENDAR ════════════════════════════════════════════ */
.cal-nav{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px}
.cal-month{font-family:'Space Grotesk',sans-serif;font-size:20px;font-weight:700}
.cal-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:5px}
.cal-dow{
  text-align:center;font-size:10.5px;font-weight:700;
  color:var(--muted);padding:6px 0;
  letter-spacing:0.8px;text-transform:uppercase;
}
.cal-cell{
  border-radius:var(--radius-sm);padding:9px 5px;text-align:center;
  min-height:60px;border:1px solid var(--border);
  background:rgba(255,255,255,0.015);
  cursor:pointer;transition:all var(--transition);
  position:relative;
}
.cal-cell:hover{background:rgba(255,255,255,0.05);border-color:var(--border2)}
.cal-cell.empty{opacity:0;pointer-events:none}
.cal-cell.today{border-color:rgba(59,130,246,0.4);background:rgba(59,130,246,0.07)}
.cal-cell.c-present{background:rgba(16,185,129,0.08);border-color:rgba(16,185,129,0.25)}
.cal-cell.c-absent{background:rgba(239,68,68,0.08);border-color:rgba(239,68,68,0.25)}
.cal-cell.c-partial{background:rgba(245,158,11,0.08);border-color:rgba(245,158,11,0.25)}
.cal-day-num{font-size:13px;font-weight:600;margin-bottom:4px}
.cal-dots{display:flex;gap:3px;justify-content:center;flex-wrap:wrap}
.dot{width:5px;height:5px;border-radius:50%}
.dot-g{background:var(--green)}
.dot-r{background:var(--red)}
.cal-legend{display:flex;gap:16px;align-items:center;margin-top:12px;font-size:12px;color:var(--text2)}
.leg-dot{width:9px;height:9px;border-radius:50%;display:inline-block;margin-right:5px}

/* ══ STREAK BADGE ════════════════════════════════════════ */
.streak{
  display:inline-flex;align-items:center;gap:4px;
  background:rgba(245,158,11,0.12);
  border:1px solid rgba(245,158,11,0.2);
  color:var(--amber-l);border-radius:20px;
  padding:3px 9px;font-size:11.5px;font-weight:700;
}

/* ══ SCAN RING ═══════════════════════════════════════════ */
.scan-wrap{position:relative;display:inline-block}
.scan-ring{
  position:absolute;inset:-14px;border-radius:50%;
  border:1.5px solid var(--cyan);opacity:0;
  animation:ring 2.8s ease-in-out infinite;
}
.scan-ring:nth-child(2){animation-delay:0.9s}
.scan-ring:nth-child(3){animation-delay:1.8s}
@keyframes ring{
  0%{transform:scale(0.82);opacity:0.9}
  100%{transform:scale(1.18);opacity:0}
}
video{border-radius:var(--radius);display:block}

/* ══ SECTION TABS ════════════════════════════════════════ */
.sec-tabs{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:20px}
.sec-tab{
  padding:6px 16px;border-radius:20px;font-size:12.5px;font-weight:600;
  text-decoration:none;border:1px solid var(--border2);
  color:var(--text2);background:rgba(255,255,255,0.03);
  transition:all var(--transition);
}
.sec-tab:hover{background:rgba(255,255,255,0.07);color:var(--text)}
.sec-tab-active{
  background:rgba(59,130,246,0.14)!important;
  border-color:rgba(59,130,246,0.35)!important;
  color:var(--blue)!important;
}
.sec-tab-all{background:rgba(139,92,246,0.08);border-color:rgba(139,92,246,0.2);color:var(--purple-l)}
.sec-tab-all.sec-tab-active{background:rgba(139,92,246,0.18)!important;color:var(--purple-l)!important}
.sec-badge{
  display:inline-block;padding:2px 9px;border-radius:6px;
  font-size:10.5px;font-weight:700;letter-spacing:0.5px;
  background:rgba(59,130,246,0.12);color:var(--blue);
  border:1px solid rgba(59,130,246,0.2);
}

/* ══ SECTION OVERVIEW ════════════════════════════════════ */
.section-card{
  background:var(--card);border:1px solid var(--border);
  border-radius:var(--radius);padding:20px;
  transition:all var(--transition);
  cursor:pointer;text-decoration:none;display:block;
  position:relative;overflow:hidden;
}
.section-card::before{
  content:'';position:absolute;inset:0;
  background:linear-gradient(135deg,rgba(255,255,255,0.02) 0%,transparent 60%);
  pointer-events:none;
}
.section-card:hover{transform:translateY(-4px);box-shadow:0 16px 40px rgba(0,0,0,0.5)}
.section-card-name{font-family:'Space Grotesk',sans-serif;font-size:24px;font-weight:800;margin-bottom:3px}
.section-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:13px}

/* ══ PROFILE IMAGE ═══════════════════════════════════════ */
.profile-avatar-wrap{
  position:relative;width:110px;height:110px;
  margin:0 auto 14px;cursor:pointer;
}
.profile-avatar-wrap img,
.profile-avatar-wrap .avatar-placeholder{
  width:110px;height:110px;border-radius:50%;object-fit:cover;
  border:2.5px solid var(--border2);display:block;
  transition:filter var(--transition);
  box-shadow:0 0 0 4px rgba(255,255,255,0.03);
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
  background:rgba(59,130,246,0.12);
  border:1px solid rgba(59,130,246,0.25);
  color:var(--blue);cursor:pointer;
  transition:all var(--transition);margin-top:4px;
}
.profile-upload-btn:hover{background:rgba(59,130,246,0.22)}
.profile-preview{
  width:110px;height:110px;border-radius:50%;object-fit:cover;
  border:2.5px solid var(--cyan);display:none;margin:0 auto 8px;
}

/* ══ TEACHER DASHBOARD ═══════════════════════════════════ */
.td-hero{
  border-radius:20px;padding:26px 30px;margin-bottom:20px;
  position:relative;overflow:hidden;
  background:linear-gradient(135deg,
    rgba(37,99,235,0.18) 0%,
    rgba(139,92,246,0.1) 50%,
    rgba(6,182,212,0.08) 100%);
  border:1px solid rgba(59,130,246,0.2);
}
.td-hero::before{
  content:'';position:absolute;top:-80px;right:-60px;
  width:280px;height:280px;border-radius:50%;
  background:radial-gradient(circle,rgba(139,92,246,0.12) 0%,transparent 70%);
}
.td-hero::after{
  content:'👨‍🏫';
  position:absolute;right:28px;top:50%;transform:translateY(-50%);
  font-size:72px;opacity:0.1;
}
.td-hero h1{
  font-family:'Space Grotesk',sans-serif;
  font-size:24px;font-weight:800;margin-bottom:5px;
  letter-spacing:-0.5px;position:relative;z-index:1;
}
.td-hero p{color:var(--text2);font-size:13.5px;position:relative;z-index:1}

/* table row risk coloring */
.risk-high td:first-child{border-left:2.5px solid var(--red)!important}
.risk-mid  td:first-child{border-left:2.5px solid var(--amber)!important}
.risk-ok   td:first-child{border-left:2.5px solid var(--green)!important}

.absent-chip{
  display:inline-flex;align-items:center;gap:7px;
  background:rgba(239,68,68,0.08);
  border:1px solid rgba(239,68,68,0.2);
  border-radius:10px;padding:7px 12px;margin:4px;
  transition:background var(--transition);
}
.absent-chip:hover{background:rgba(239,68,68,0.14)}
.absent-chip-avatar{
  width:26px;height:26px;border-radius:50%;
  background:linear-gradient(135deg,var(--red),#f87171);
  display:flex;align-items:center;justify-content:center;
  font-size:11px;font-weight:700;flex-shrink:0;
}
.qa-grid{display:grid;grid-template-columns:1fr 1fr;gap:9px}
.qa-btn{
  display:flex;align-items:center;gap:10px;padding:12px 14px;
  background:rgba(255,255,255,0.03);border:1px solid var(--border);
  border-radius:var(--radius-sm);text-decoration:none;color:var(--text);
  font-size:13px;font-weight:600;transition:all var(--transition);
}
.qa-btn:hover{background:rgba(255,255,255,0.07);border-color:var(--border2);transform:translateY(-1px)}
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
  padding:11px 15px;border-radius:var(--radius-sm);
  font-size:13px;display:flex;align-items:center;gap:8px;margin-bottom:9px;
}
.notice-warn{background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.2);color:var(--amber-l)}
.notice-red{background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);color:var(--red-l)}

/* ══ LOGIN ═══════════════════════════════════════════════ */
.login-wrap{
  min-height:100vh;display:flex;align-items:center;justify-content:center;
  background:radial-gradient(ellipse at 35% 40%,rgba(37,99,235,0.14) 0%,transparent 55%),
             radial-gradient(ellipse at 75% 75%,rgba(139,92,246,0.1) 0%,transparent 50%),
             var(--bg);
}
.login-card{
  background:rgba(10,17,32,0.85);
  backdrop-filter:blur(30px);-webkit-backdrop-filter:blur(30px);
  border:1px solid rgba(255,255,255,0.08);
  border-radius:22px;padding:42px 40px;width:100%;max-width:400px;
  position:relative;overflow:hidden;
  box-shadow:0 32px 80px rgba(0,0,0,0.6);
}
.login-card::before{
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(59,130,246,0.6),rgba(6,182,212,0.4),transparent);
}
.login-card::after{
  content:'';position:absolute;top:-100px;right:-60px;
  width:220px;height:220px;border-radius:50%;
  background:radial-gradient(circle,rgba(59,130,246,0.08) 0%,transparent 70%);
  pointer-events:none;
}
.login-logo{text-align:center;margin-bottom:28px}
.login-logo-icon{
  width:62px;height:62px;
  background:linear-gradient(135deg,#2563eb,#06b6d4);
  border-radius:18px;display:flex;align-items:center;justify-content:center;
  font-size:28px;margin:0 auto 12px;
  box-shadow:0 0 28px rgba(37,99,235,0.4),inset 0 1px 0 rgba(255,255,255,0.15);
}
.login-title{font-family:'Space Grotesk',sans-serif;font-size:22px;font-weight:700}
.login-sub{color:var(--text2);font-size:13px;margin-top:3px}




/* ══ SUBSCRIPTION MODULE ═══════════════════════════════ */
.upgrade-hero{
  border-radius:22px;padding:50px 40px;text-align:center;
  background:linear-gradient(135deg,#0a0f1e 0%,#0d1526 40%,#10172a 100%);
  border:1px solid rgba(59,130,246,0.2);
  position:relative;overflow:hidden;margin-bottom:28px;
}
.upgrade-hero::before{
  content:'';position:absolute;top:-100px;left:50%;transform:translateX(-50%);
  width:500px;height:300px;border-radius:50%;
  background:radial-gradient(ellipse,rgba(59,130,246,0.12) 0%,transparent 70%);
}
.upgrade-hero::after{
  content:'';position:absolute;bottom:-80px;right:-60px;
  width:280px;height:280px;border-radius:50%;
  background:radial-gradient(circle,rgba(139,92,246,0.1) 0%,transparent 70%);
}
.upgrade-hero h1{
  font-family:'Space Grotesk',sans-serif;
  font-size:36px;font-weight:800;letter-spacing:-1px;
  position:relative;z-index:1;margin-bottom:12px;
  background:linear-gradient(135deg,#f0f6ff,#94a3b8);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}
.upgrade-hero p{color:var(--text2);font-size:15px;position:relative;z-index:1;line-height:1.6}

.plan-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-bottom:28px}
.plan-card{
  background:var(--card);border:1px solid var(--border);border-radius:20px;
  padding:28px 24px;text-align:center;position:relative;overflow:hidden;
  transition:all var(--transition);
}
.plan-card:hover{transform:translateY(-6px);box-shadow:0 20px 50px rgba(0,0,0,0.5)}
.plan-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px}
.plan-monthly::before{background:linear-gradient(90deg,var(--blue),var(--cyan))}
.plan-yearly::before{background:linear-gradient(90deg,var(--purple),var(--pink))}
.plan-5year::before{background:linear-gradient(90deg,var(--amber),var(--green))}
.plan-popular{border-color:rgba(139,92,246,0.4)!important;box-shadow:0 0 30px rgba(139,92,246,0.1)}
.plan-badge{
  position:absolute;top:16px;right:16px;
  background:linear-gradient(135deg,var(--purple),var(--pink));
  color:white;padding:3px 12px;border-radius:20px;font-size:11px;font-weight:700;
}
.plan-icon{font-size:40px;margin-bottom:14px}
.plan-name{font-family:'Space Grotesk',sans-serif;font-size:17px;font-weight:700;margin-bottom:8px}
.plan-price{
  font-family:'Space Grotesk',sans-serif;
  font-size:40px;font-weight:800;letter-spacing:-1px;
  margin-bottom:4px;line-height:1;
}
.plan-period{font-size:13px;color:var(--text2);margin-bottom:20px}
.plan-features{
  list-style:none;text-align:left;margin-bottom:24px;
  display:flex;flex-direction:column;gap:10px;
}
.plan-features li{
  display:flex;align-items:center;gap:10px;
  font-size:13.5px;color:var(--text2);
}
.plan-features li::before{content:"✓";color:var(--green);font-weight:700;flex-shrink:0}

.expired-overlay{
  position:fixed;inset:0;z-index:9999;
  background:rgba(3,7,18,0.92);
  backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);
  display:flex;align-items:center;justify-content:center;
}
.expired-modal{
  background:var(--card2);border:1px solid rgba(239,68,68,0.3);
  border-radius:24px;padding:48px 42px;max-width:480px;width:90%;
  text-align:center;position:relative;overflow:hidden;
  box-shadow:0 32px 80px rgba(0,0,0,0.7);
  animation:modal-in 0.3s cubic-bezier(.34,1.56,.64,1);
}
@keyframes modal-in{from{opacity:0;transform:scale(0.85)}to{opacity:1;transform:none}}
.expired-modal::before{
  content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,var(--red),var(--purple),var(--blue));
}
.lock-icon{font-size:60px;margin-bottom:18px;display:block}
.expired-title{
  font-family:'Space Grotesk',sans-serif;font-size:24px;font-weight:800;
  color:var(--red-l);margin-bottom:10px;
}
.expired-sub{color:var(--text2);font-size:14px;line-height:1.6;margin-bottom:26px}

/* dev panel */
.dev-table td,.dev-table th{padding:10px 14px;border-bottom:1px solid var(--border);font-size:13px}
.dev-table th{font-size:10px;letter-spacing:1px;text-transform:uppercase;color:var(--muted)}

@media(max-width:768px){.plan-grid{grid-template-columns:1fr}}

/* ══ RESPONSIVE ══════════════════════════════════════════ */
@media(max-width:960px){
  .sidebar{display:none}
  .main{margin-left:0}
  .stats-row{grid-template-columns:1fr 1fr}
  .grid-2,.grid-3{grid-template-columns:1fr}
  .main{padding-bottom:70px}
}
@media(max-width:560px){
  .page{padding:14px}
  .stats-row{grid-template-columns:1fr 1fr}
  .hero{padding:18px}
  .hero h1{font-size:19px}
  .login-card{padding:30px 22px}
}

/* ══ MOBILE BOTTOM NAV ═══════════════════════════════════ */
.mobile-nav{
  display:none;
  position:fixed;bottom:0;left:0;right:0;
  height:64px;
  background:rgba(6,11,20,0.97);
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border-top:1px solid rgba(255,255,255,0.08);
  z-index:200;
  padding:0 4px;
  padding-bottom:env(safe-area-inset-bottom);
}
.mobile-nav-inner{
  display:flex;align-items:stretch;height:100%;
}
.mnav-item{
  flex:1;display:flex;flex-direction:column;
  align-items:center;justify-content:center;
  text-decoration:none;color:var(--muted);
  font-size:10px;font-weight:600;gap:3px;
  border-radius:12px;margin:6px 2px;
  transition:all 0.15s;
  letter-spacing:0.2px;
  position:relative;
}
.mnav-item svg{width:20px;height:20px;flex-shrink:0}
.mnav-item:hover,.mnav-active{color:var(--blue)!important}
.mnav-active{background:rgba(59,130,246,0.1)}
.mnav-active::before{
  content:'';position:absolute;top:-6px;left:50%;transform:translateX(-50%);
  width:24px;height:2px;border-radius:2px;background:var(--blue);
}
.mnav-premium{color:var(--amber-l)!important}
.mnav-premium.mnav-active{background:rgba(245,158,11,0.1)}
.mnav-premium.mnav-active::before{background:var(--amber)}

/* hamburger / more menu */
.mobile-topbar{
  display:none;position:fixed;top:0;left:0;right:0;z-index:150;
  height:52px;padding:0 16px;
  background:rgba(6,11,20,0.97);
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border-bottom:1px solid rgba(255,255,255,0.07);
  align-items:center;justify-content:space-between;
}
.mobile-logo{
  font-family:'Space Grotesk',sans-serif;font-size:17px;font-weight:700;
  display:flex;align-items:center;gap:8px;
}
.mobile-logo span{color:var(--cyan)}
.hamburger-btn{
  width:36px;height:36px;border-radius:10px;
  background:rgba(255,255,255,0.06);border:1px solid var(--border);
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  gap:5px;cursor:pointer;
}
.hamburger-btn span{
  display:block;width:18px;height:2px;
  background:var(--text2);border-radius:2px;
  transition:all 0.2s;
}
.drawer-overlay{
  display:none;position:fixed;inset:0;z-index:190;
  background:rgba(0,0,0,0.6);backdrop-filter:blur(4px);
}
.drawer{
  position:fixed;top:0;right:-280px;bottom:0;width:260px;z-index:195;
  background:var(--surface);border-left:1px solid var(--border);
  transition:right 0.25s cubic-bezier(.4,0,.2,1);
  display:flex;flex-direction:column;padding:20px 0;
  overflow-y:auto;
}
.drawer.open{right:0}
.drawer-header{
  padding:8px 20px 16px;border-bottom:1px solid var(--border);margin-bottom:8px;
  display:flex;align-items:center;justify-content:space-between;
}
.drawer-close{
  width:32px;height:32px;border-radius:8px;border:none;
  background:rgba(255,255,255,0.06);color:var(--text);
  font-size:16px;cursor:pointer;
}
.drawer-item{
  display:flex;align-items:center;gap:12px;
  padding:12px 20px;color:var(--text2);text-decoration:none;
  font-size:14px;font-weight:500;transition:all 0.12s;
  border-left:3px solid transparent;
}
.drawer-item svg{width:17px;height:17px;flex-shrink:0}
.drawer-item:hover{color:var(--text);background:rgba(255,255,255,0.04)}
.drawer-active{color:var(--blue)!important;border-left-color:var(--blue)!important;
  background:rgba(59,130,246,0.08)!important}

@media(max-width:960px){
  .mobile-nav{display:flex}
  .mobile-topbar{display:flex}
  .topbar{display:none}
  .page{margin-top:52px}
}
</style>
"""

