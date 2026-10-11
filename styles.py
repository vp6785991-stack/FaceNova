# styles.py — FaceNova Premium Mobile App UI v5
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}

/* ══ TOKENS ════════════════════════════════════════════ */
:root{
  /* Dark premium base */
  --bg:        #0a0f1e;
  --surface:   #0d1526;
  --card:      #111827;
  --card2:     #1a2236;
  --border:    rgba(99,102,241,0.12);
  --border2:   rgba(99,102,241,0.22);
  --border3:   rgba(99,102,241,0.4);

  /* Brand colors */
  --blue:      #6366f1;
  --blue-d:    #4f46e5;
  --blue-l:    #818cf8;
  --cyan:      #06b6d4;
  --cyan-d:    #0891b2;
  --green:     #10b981;
  --green-l:   #34d399;
  --red:       #ef4444;
  --red-l:     #f87171;
  --amber:     #f59e0b;
  --amber-l:   #fbbf24;
  --purple:    #8b5cf6;
  --purple-l:  #a78bfa;
  --pink:      #ec4899;

  /* Text */
  --text:      #f1f5f9;
  --text2:     #94a3b8;
  --muted:     #4b5563;

  /* Glow effects */
  --glow-blue:   0 0 24px rgba(99,102,241,0.3);
  --glow-green:  0 0 24px rgba(16,185,129,0.3);
  --glow-red:    0 0 24px rgba(239,68,68,0.25);

  /* Layout */
  --sidebar-w: 260px;
  --radius:    16px;
  --radius-sm: 12px;
  --radius-xs: 8px;
  --t:         0.18s cubic-bezier(.4,0,.2,1);

  /* Shadows */
  --shadow-sm: 0 2px 8px rgba(0,0,0,0.3);
  --shadow:    0 4px 20px rgba(0,0,0,0.4);
  --shadow-lg: 0 8px 40px rgba(0,0,0,0.5);
}

/* ══ BASE ════════════════════════════════════════════ */
html{scroll-behavior:smooth}
body{
  font-family:'Inter',sans-serif;
  background:var(--bg);
  color:var(--text);
  min-height:100vh;display:flex;
  line-height:1.6;
  -webkit-font-smoothing:antialiased;
  -moz-osx-font-smoothing:grayscale;
  background-image:
    radial-gradient(ellipse 70% 50% at 50% -5%,rgba(99,102,241,0.08),transparent),
    radial-gradient(ellipse 50% 40% at 90% 90%,rgba(6,182,212,0.05),transparent);
}
::-webkit-scrollbar{width:4px;height:4px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:rgba(99,102,241,0.3);border-radius:10px}

/* ══ SIDEBAR ═════════════════════════════════════════ */
.sidebar{
  width:var(--sidebar-w);
  background:linear-gradient(180deg,#0d1526 0%,#080d18 100%);
  border-right:1px solid var(--border);
  display:flex;flex-direction:column;
  position:fixed;top:0;bottom:0;left:0;z-index:100;
  overflow:hidden;
  box-shadow:4px 0 32px rgba(0,0,0,0.4);
}
.sidebar::before{
  content:'';position:absolute;top:-60px;left:-60px;
  width:220px;height:220px;border-radius:50%;
  background:radial-gradient(circle,rgba(99,102,241,0.07),transparent 70%);
  pointer-events:none;
}
.sidebar-logo{
  padding:22px 20px 16px;
  border-bottom:1px solid var(--border);
  position:relative;z-index:1;
}
.logo-mark{display:flex;align-items:center;gap:12px}
.logo-icon{
  width:38px;height:38px;border-radius:11px;
  background:linear-gradient(135deg,#4f46e5,#06b6d4);
  display:flex;align-items:center;justify-content:center;
  font-size:18px;
  box-shadow:0 4px 16px rgba(79,70,229,0.5);
  flex-shrink:0;
  animation:logo-float 4s ease-in-out infinite;
}
@keyframes logo-float{
  0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}
}
.logo-text{
  font-family:'Space Grotesk',sans-serif;
  font-size:19px;font-weight:800;letter-spacing:-0.5px;
}
.logo-text span{
  background:linear-gradient(90deg,var(--blue-l),var(--cyan));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}
.logo-tag{font-size:9px;font-weight:700;letter-spacing:2px;color:var(--muted);text-transform:uppercase;margin-top:2px}
.sidebar-section{
  font-size:9px;font-weight:700;letter-spacing:2.2px;
  color:var(--muted);text-transform:uppercase;
  padding:20px 20px 6px;
}
.nav-item{
  display:flex;align-items:center;gap:11px;
  padding:9px 16px 9px 18px;
  color:var(--text2);text-decoration:none;
  font-size:13px;font-weight:500;
  transition:all var(--t);
  border-radius:12px;margin:1px 10px;
}
.nav-item svg{width:16px;height:16px;flex-shrink:0;opacity:0.5;transition:all var(--t)}
.nav-item:hover{color:var(--text);background:rgba(99,102,241,0.08)}
.nav-item:hover svg{opacity:1;transform:translateX(1px)}
.nav-active{
  color:#fff!important;
  background:linear-gradient(135deg,rgba(79,70,229,0.35),rgba(6,182,212,0.15))!important;
  border:1px solid rgba(99,102,241,0.25)!important;
  font-weight:600!important;
  box-shadow:0 4px 16px rgba(79,70,229,0.2);
}
.nav-active svg{opacity:1!important;filter:drop-shadow(0 0 4px rgba(99,102,241,0.6))}
.sidebar-footer{
  margin-top:auto;padding:14px 20px 18px;
  border-top:1px solid var(--border);
}
.status-dot{
  display:inline-block;width:7px;height:7px;
  background:var(--green);border-radius:50%;
  margin-right:8px;box-shadow:0 0 8px var(--green);
  animation:pulse-dot 2.5s infinite;
}
@keyframes pulse-dot{0%,100%{opacity:1;box-shadow:0 0 8px var(--green)}50%{opacity:0.4;box-shadow:none}}

/* ══ MAIN / TOPBAR ═══════════════════════════════════ */
.main{margin-left:var(--sidebar-w);flex:1;display:flex;flex-direction:column;min-height:100vh}
.topbar{
  height:58px;padding:0 24px;
  background:rgba(10,15,30,0.8);
  backdrop-filter:blur(24px) saturate(1.4);
  -webkit-backdrop-filter:blur(24px) saturate(1.4);
  border-bottom:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between;
  position:sticky;top:0;z-index:50;
}
.topbar-title{
  font-family:'Space Grotesk',sans-serif;
  font-size:15px;font-weight:700;letter-spacing:-0.2px;
}
.topbar-right{display:flex;align-items:center;gap:10px}
.tbadge{
  background:rgba(99,102,241,0.12);border:1px solid rgba(99,102,241,0.25);
  color:var(--blue-l);padding:4px 12px;border-radius:20px;
  font-size:11px;font-weight:700;letter-spacing:0.3px;
}
.page{padding:20px 24px;flex:1}

/* ══ STAT CARDS ══════════════════════════════════════ */
.stats-row{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px}
.stat{
  background:var(--card);border:1px solid var(--border);
  border-radius:var(--radius);padding:18px 16px;
  position:relative;overflow:hidden;
  transition:transform var(--t),box-shadow var(--t);
  animation:fadeUp 0.45s cubic-bezier(.34,1.2,.64,1) both;
}
.stat:nth-child(1){animation-delay:.05s}
.stat:nth-child(2){animation-delay:.10s}
.stat:nth-child(3){animation-delay:.15s}
.stat:nth-child(4){animation-delay:.20s}
.stat:hover{transform:translateY(-3px);box-shadow:var(--shadow-lg)}
.stat::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;border-radius:var(--radius) var(--radius) 0 0}
.stat::after{content:'';position:absolute;bottom:-20px;right:-20px;width:80px;height:80px;border-radius:50%;opacity:0.07}
.s-blue::before{background:linear-gradient(90deg,var(--blue-d),var(--cyan))}
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
  font-size:17px;margin-bottom:12px;
}
.stat-val{
  font-family:'Space Grotesk',sans-serif;
  font-size:32px;font-weight:800;line-height:1;margin-bottom:4px;
  letter-spacing:-1px;
  animation:count-up 0.6s cubic-bezier(.34,1.4,.64,1) both .2s;
}
.stat-lbl{font-size:11.5px;color:var(--text2);font-weight:500}

/* ══ PROGRESS BAR ════════════════════════════════════ */
.pbar-wrap{
  background:rgba(255,255,255,0.05);
  border-radius:20px;height:6px;overflow:hidden;
}
.pbar{height:100%;border-radius:20px;transition:width 1.2s cubic-bezier(.4,0,.2,1)}
.pbar-green{background:linear-gradient(90deg,var(--green),var(--green-l))}
.pbar-amber{background:linear-gradient(90deg,var(--amber),var(--amber-l))}
.pbar-red{background:linear-gradient(90deg,var(--red),var(--red-l))}
.pbar-blue{background:linear-gradient(90deg,var(--blue-d),var(--cyan))}

/* ══ CARDS ═══════════════════════════════════════════ */
.card{
  background:var(--card);border:1px solid var(--border);
  border-radius:var(--radius);padding:20px;
  transition:border-color var(--t),box-shadow var(--t);
  animation:fadeUp 0.45s 0.1s cubic-bezier(.34,1.1,.64,1) both;
}
.card:hover{border-color:var(--border2)}
.card-glass{
  background:rgba(13,21,38,0.6);
  backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);
  border:1px solid var(--border);
  border-radius:var(--radius);padding:20px;
}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.grid-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}
.sec-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px}
.sec-title{
  font-family:'Space Grotesk',sans-serif;
  font-size:15px;font-weight:700;letter-spacing:-0.2px;
}
.sec-sub{font-size:12px;color:var(--text2);margin-top:2px}

/* ══ TABLE ═══════════════════════════════════════════ */
.tbl-wrap{overflow-x:auto;border-radius:var(--radius-sm)}
table{width:100%;border-collapse:collapse;font-size:13px}
thead th{
  background:rgba(255,255,255,0.025);
  padding:10px 14px;text-align:left;
  font-size:9.5px;font-weight:700;letter-spacing:1.4px;
  text-transform:uppercase;color:var(--muted);
  border-bottom:1px solid var(--border);
}
tbody td{
  padding:12px 14px;border-bottom:1px solid rgba(255,255,255,0.035);
  transition:background var(--t);
}
tbody tr:hover td{background:rgba(99,102,241,0.04)}
tbody tr:last-child td{border-bottom:none}

/* ══ PILLS ═══════════════════════════════════════════ */
.pill{
  display:inline-flex;align-items:center;gap:4px;
  padding:3px 10px;border-radius:20px;
  font-size:11px;font-weight:600;letter-spacing:0.2px;
}
.pill-green{background:rgba(16,185,129,0.12);color:var(--green-l);border:1px solid rgba(16,185,129,0.2)}
.pill-red{background:rgba(239,68,68,0.12);color:var(--red-l);border:1px solid rgba(239,68,68,0.2)}
.pill-amber{background:rgba(245,158,11,0.12);color:var(--amber-l);border:1px solid rgba(245,158,11,0.2)}
.pill-blue{background:rgba(99,102,241,0.12);color:var(--blue-l);border:1px solid rgba(99,102,241,0.2)}
.pill-purple{background:rgba(139,92,246,0.12);color:var(--purple-l);border:1px solid rgba(139,92,246,0.2)}

/* ══ BUTTONS ═════════════════════════════════════════ */
.btn{
  display:inline-flex;align-items:center;gap:7px;
  padding:9px 18px;border:none;border-radius:var(--radius-sm);
  font-size:13px;font-weight:600;cursor:pointer;
  transition:all var(--t);text-decoration:none;
  font-family:'Inter',sans-serif;
  position:relative;overflow:hidden;
  -webkit-tap-highlight-color:transparent;
}
.btn-primary{
  background:linear-gradient(135deg,#4f46e5,#7c3aed);color:#fff;
  box-shadow:0 4px 16px rgba(79,70,229,0.4);
}
.btn-primary:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(79,70,229,0.55)}
.btn-primary:active{transform:translateY(0)}
.btn-cyan{
  background:linear-gradient(135deg,#0891b2,#06b6d4);color:#fff;
  box-shadow:0 4px 16px rgba(6,182,212,0.35);
}
.btn-cyan:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(6,182,212,0.45)}
.btn-ghost{
  background:rgba(255,255,255,0.05);color:var(--text2);
  border:1px solid var(--border2);
}
.btn-ghost:hover{background:rgba(255,255,255,0.09);color:var(--text);transform:translateY(-1px)}
.btn-red{background:rgba(239,68,68,0.12);color:var(--red-l);border:1px solid rgba(239,68,68,0.2)}
.btn-red:hover{background:rgba(239,68,68,0.2);transform:translateY(-1px)}
.btn-green{
  background:linear-gradient(135deg,#059669,#047857);color:#fff;
  box-shadow:0 4px 14px rgba(5,150,105,0.35);
}
.btn-green:hover{transform:translateY(-2px);box-shadow:0 8px 22px rgba(16,185,129,0.45)}
.btn-sm{padding:6px 13px;font-size:12px}
.btn-xs{padding:4px 10px;font-size:11px;border-radius:7px}
/* ripple */
.btn::after{
  content:'';position:absolute;width:80px;height:80px;
  background:rgba(255,255,255,0.18);border-radius:50%;
  transform:scale(0);opacity:0;
  top:50%;left:50%;margin:-40px 0 0 -40px;pointer-events:none;
}
.btn:active::after{animation:ripple-btn .4s ease-out}
@keyframes ripple-btn{0%{transform:scale(0);opacity:1}100%{transform:scale(3);opacity:0}}

/* ══ FORMS ═══════════════════════════════════════════ */
.form-group{margin-bottom:16px}
label{
  display:block;font-size:11px;font-weight:700;
  color:var(--text2);margin-bottom:7px;
  letter-spacing:0.6px;text-transform:uppercase;
}
input[type=text],input[type=password],select,textarea{
  width:100%;background:rgba(255,255,255,0.04);
  border:1.5px solid var(--border2);border-radius:var(--radius-xs);
  padding:10px 13px;color:var(--text);font-size:13.5px;
  font-family:'Inter',sans-serif;transition:all var(--t);outline:none;
}
input[type=text]:focus,input[type=password]:focus,select:focus,textarea:focus{
  border-color:var(--blue-l);
  box-shadow:0 0 0 3px rgba(99,102,241,0.12);
  background:rgba(99,102,241,0.04);
}
input::placeholder{color:var(--muted)}
select option{background:#111827;color:var(--text)}
input[type=file]{
  width:100%;background:rgba(255,255,255,0.03);
  border:2px dashed rgba(99,102,241,0.25);
  border-radius:var(--radius-xs);padding:14px 13px;
  color:var(--text2);font-size:13px;font-family:'Inter',sans-serif;
  cursor:pointer;transition:all var(--t);
}
input[type=file]:hover{border-color:var(--blue-l);background:rgba(99,102,241,0.05)}

/* ══ ALERTS ══════════════════════════════════════════ */
.alert{
  padding:12px 16px;border-radius:var(--radius-xs);
  font-size:13px;margin-bottom:16px;
  display:flex;align-items:center;gap:9px;
  animation:slideIn .3s cubic-bezier(.34,1.3,.64,1);
}
@keyframes slideIn{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}
.alert-success{background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.2);color:var(--green-l)}
.alert-error{background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.2);color:var(--red-l)}
.alert-info{background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.2);color:var(--blue-l)}
.alert-warn{background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.2);color:var(--amber-l)}

/* ══ HERO BANNER ═════════════════════════════════════ */
.hero{
  border-radius:20px;padding:26px 28px;margin-bottom:20px;
  position:relative;overflow:hidden;
  background:linear-gradient(135deg,rgba(79,70,229,0.22) 0%,rgba(6,182,212,0.08) 50%,rgba(139,92,246,0.1) 100%);
  border:1px solid rgba(99,102,241,0.2);
  box-shadow:0 0 60px rgba(79,70,229,0.07);
  animation:fadeUp 0.5s cubic-bezier(.34,1.2,.64,1) both;
}
.hero::before{
  content:'';position:absolute;top:-60px;right:-40px;
  width:220px;height:220px;border-radius:50%;
  background:radial-gradient(circle,rgba(99,102,241,0.1),transparent 70%);
  pointer-events:none;
}
.hero h1{
  font-family:'Space Grotesk',sans-serif;
  font-size:22px;font-weight:800;margin-bottom:5px;
  letter-spacing:-0.5px;
}
.hero p{color:var(--text2);font-size:13.5px;line-height:1.6;word-break:break-word}
.hero-actions{
  margin-top:16px;display:flex;gap:9px;flex-wrap:wrap;width:100%;
}
.hero-actions .btn{flex:1;min-width:0;justify-content:center}

/* ══ APP-STYLE SCAN PAGE ═════════════════════════════ */
.scan-app-wrap{
  display:flex;flex-direction:column;align-items:center;
  gap:0;max-width:480px;margin:0 auto;
}
.scan-viewfinder{
  width:100%;aspect-ratio:3/4;max-height:60vh;
  background:#000;border-radius:24px;overflow:hidden;
  position:relative;
  box-shadow:0 0 0 3px rgba(99,102,241,0.3),0 24px 60px rgba(0,0,0,0.6);
}
.scan-viewfinder video{
  width:100%;height:100%;object-fit:cover;display:block;
}
/* Animated scan corners */
.vf-corner{position:absolute;width:28px;height:28px;z-index:10}
.vf-tl{top:14px;left:14px;border-top:3px solid var(--cyan);border-left:3px solid var(--cyan);border-radius:6px 0 0 0;animation:corner-glow 2s ease-in-out infinite}
.vf-tr{top:14px;right:14px;border-top:3px solid var(--cyan);border-right:3px solid var(--cyan);border-radius:0 6px 0 0;animation:corner-glow 2s ease-in-out infinite .25s}
.vf-bl{bottom:14px;left:14px;border-bottom:3px solid var(--cyan);border-left:3px solid var(--cyan);border-radius:0 0 0 6px;animation:corner-glow 2s ease-in-out infinite .5s}
.vf-br{bottom:14px;right:14px;border-bottom:3px solid var(--cyan);border-right:3px solid var(--cyan);border-radius:0 0 6px 0;animation:corner-glow 2s ease-in-out infinite .75s}
@keyframes corner-glow{
  0%,100%{opacity:0.7;box-shadow:none}
  50%{opacity:1;box-shadow:0 0 12px rgba(6,182,212,0.6)}
}
/* Scan beam */
.vf-beam{
  position:absolute;left:0;right:0;height:2px;z-index:9;
  background:linear-gradient(90deg,transparent,rgba(6,182,212,0.9),transparent);
  box-shadow:0 0 16px rgba(6,182,212,0.7);
  animation:beam-scan 2.5s ease-in-out infinite;
}
@keyframes beam-scan{
  0%{top:10%;opacity:0}5%{opacity:1}95%{opacity:1}100%{top:90%;opacity:0}
}
/* Face target ring */
.vf-face-ring{
  position:absolute;top:50%;left:50%;
  transform:translate(-50%,-52%);
  width:160px;height:180px;border-radius:50%;
  border:2px solid rgba(6,182,212,0.35);
  z-index:9;
  animation:face-ring-pulse 2.5s ease-in-out infinite;
}
.vf-face-ring::before{
  content:'';position:absolute;inset:-10px;
  border-radius:50%;border:1px solid rgba(6,182,212,0.15);
  animation:face-ring-pulse 2.5s ease-in-out infinite .5s;
}
@keyframes face-ring-pulse{
  0%,100%{border-color:rgba(6,182,212,0.35);transform:translate(-50%,-52%) scale(1)}
  50%{border-color:rgba(6,182,212,0.7);transform:translate(-50%,-52%) scale(1.03)}
}
/* Live badge inside viewfinder */
.vf-live-badge{
  position:absolute;top:14px;left:50%;transform:translateX(-50%);
  background:rgba(0,0,0,0.55);backdrop-filter:blur(8px);
  border:1px solid rgba(16,185,129,0.4);
  border-radius:20px;padding:4px 12px;
  font-size:11px;font-weight:700;color:var(--green-l);
  display:flex;align-items:center;gap:5px;z-index:10;
}
.vf-live-dot{
  width:6px;height:6px;border-radius:50%;
  background:var(--green);box-shadow:0 0 6px var(--green);
  animation:pulse-dot 1.5s infinite;
}
/* instruction overlay at bottom of viewfinder */
.vf-instruction{
  position:absolute;bottom:0;left:0;right:0;
  background:linear-gradient(0deg,rgba(0,0,0,0.7),transparent);
  padding:24px 16px 16px;text-align:center;z-index:10;
}
.vf-instruction p{font-size:13px;color:rgba(255,255,255,0.85);font-weight:500}
/* Scan button */
.scan-btn-wrap{
  width:100%;padding:16px 0 4px;
}
.scan-btn-main{
  width:100%;padding:16px;border-radius:var(--radius);
  font-size:16px;font-weight:700;
  background:linear-gradient(135deg,#0891b2,#06b6d4);color:#fff;
  border:none;cursor:pointer;
  display:flex;align-items:center;justify-content:center;gap:10px;
  box-shadow:0 6px 24px rgba(6,182,212,0.4);
  transition:all var(--t);font-family:'Inter',sans-serif;
  position:relative;overflow:hidden;
  -webkit-tap-highlight-color:transparent;
}
.scan-btn-main:hover{transform:translateY(-2px);box-shadow:0 10px 30px rgba(6,182,212,0.5)}
.scan-btn-main:active{transform:scale(0.97)}

/* Result card — shown after scan */
.scan-result-card{
  width:100%;background:var(--card);
  border:1px solid var(--border2);border-radius:var(--radius);
  padding:20px;margin-top:16px;
  animation:scaleIn 0.35s cubic-bezier(.34,1.3,.64,1) both;
}
.scan-result-avatar{
  width:72px;height:72px;border-radius:50%;
  object-fit:cover;margin:0 auto 12px;display:block;
  border:3px solid var(--green);
  box-shadow:0 0 20px rgba(16,185,129,0.4);
}
.scan-result-avatar-placeholder{
  width:72px;height:72px;border-radius:50%;
  background:linear-gradient(135deg,var(--blue-d),var(--purple));
  display:flex;align-items:center;justify-content:center;
  font-size:26px;font-weight:800;color:#fff;
  margin:0 auto 12px;
  border:3px solid var(--border2);
}
.scan-result-name{
  font-family:'Space Grotesk',sans-serif;
  font-size:20px;font-weight:800;text-align:center;
  margin-bottom:4px;
}
.scan-result-status{
  display:flex;align-items:center;justify-content:center;
  gap:6px;margin-bottom:16px;
}

/* ══ ENROLL PAGE — APP STYLE ══════════════════════════ */
.enroll-app{max-width:520px;margin:0 auto}
.enroll-hero{
  background:linear-gradient(135deg,rgba(79,70,229,0.2),rgba(6,182,212,0.08));
  border:1px solid rgba(99,102,241,0.2);
  border-radius:var(--radius);padding:20px;
  margin-bottom:20px;display:flex;align-items:center;gap:16px;
  animation:fadeUp 0.4s cubic-bezier(.34,1.2,.64,1) both;
}
.enroll-hero-icon{
  width:52px;height:52px;border-radius:14px;flex-shrink:0;
  background:linear-gradient(135deg,var(--blue-d),var(--purple));
  display:flex;align-items:center;justify-content:center;
  font-size:22px;box-shadow:0 4px 16px rgba(79,70,229,0.4);
}
.enroll-hero h2{
  font-family:'Space Grotesk',sans-serif;
  font-size:17px;font-weight:700;margin-bottom:3px;
}
.enroll-hero p{font-size:12.5px;color:var(--text2);line-height:1.5}
.enroll-step{
  display:flex;gap:12px;align-items:flex-start;
  background:var(--card);border:1px solid var(--border);
  border-radius:var(--radius-sm);padding:14px;margin-bottom:12px;
}
.enroll-step-num{
  width:28px;height:28px;border-radius:8px;flex-shrink:0;
  background:linear-gradient(135deg,var(--blue-d),var(--cyan));
  display:flex;align-items:center;justify-content:center;
  font-size:12px;font-weight:700;color:#fff;
  box-shadow:0 2px 8px rgba(79,70,229,0.35);
}
.enroll-step h4{font-size:13.5px;font-weight:600;margin-bottom:2px}
.enroll-step p{font-size:12px;color:var(--text2);line-height:1.5}

/* ══ STUDENT CARDS ════════════════════════════════════ */
.student-grid{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(165px,1fr));
  gap:12px;
}
.student-card{
  background:var(--card);border:1px solid var(--border);
  border-radius:var(--radius);padding:20px 14px 16px;
  text-align:center;transition:all var(--t);
  position:relative;overflow:hidden;
  animation:scaleIn 0.35s cubic-bezier(.34,1.2,.64,1) both;
}
.student-card:nth-child(1){animation-delay:.04s}
.student-card:nth-child(2){animation-delay:.08s}
.student-card:nth-child(3){animation-delay:.12s}
.student-card:nth-child(4){animation-delay:.16s}
.student-card:nth-child(n+5){animation-delay:.20s}
.student-card::before{
  content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,var(--blue-d),var(--purple));
  opacity:0;transition:opacity var(--t);
}
.student-card:hover{transform:translateY(-4px);border-color:var(--border2);box-shadow:0 12px 32px rgba(0,0,0,0.4)}
.student-card:hover::before{opacity:1}
.s-avatar{
  width:68px;height:68px;border-radius:50%;object-fit:cover;
  margin:0 auto 10px;border:2.5px solid var(--border2);
  transition:all var(--t);box-shadow:var(--shadow-sm);
}
.student-card:hover .s-avatar{border-color:var(--blue-l);box-shadow:0 0 16px rgba(99,102,241,0.3)}
.s-avatar-placeholder{
  width:68px;height:68px;border-radius:50%;
  background:linear-gradient(135deg,var(--blue-d),var(--purple));
  display:flex;align-items:center;justify-content:center;
  font-size:22px;font-weight:800;color:#fff;
  margin:0 auto 10px;box-shadow:0 4px 14px rgba(79,70,229,0.3);
}
.s-name{font-weight:700;font-size:13px;margin-bottom:3px;letter-spacing:-0.1px}
.s-pct{
  font-family:'Space Grotesk',sans-serif;
  font-size:22px;font-weight:800;
}

/* ══ GALLERY ══════════════════════════════════════════ */
.gallery-grid{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(180px,1fr));
  gap:12px;
}
.gallery-item{
  background:var(--card);border:1px solid var(--border);
  border-radius:var(--radius);overflow:hidden;
  transition:all var(--t);
  animation:scaleIn 0.35s cubic-bezier(.34,1.2,.64,1) both;
}
.gallery-item:hover{transform:translateY(-4px);border-color:var(--border2);box-shadow:0 12px 32px rgba(0,0,0,0.4)}
.gallery-item img{width:100%;height:150px;object-fit:cover;display:block;transition:filter var(--t)}
.gallery-item:hover img{filter:brightness(1.08)}
.gallery-item-info{padding:10px 12px}
.gallery-item-name{font-size:13px;font-weight:700}
.gallery-item-stat{font-size:11.5px;color:var(--text2);margin-top:2px}

/* ══ CALENDAR ════════════════════════════════════════ */
.cal-nav{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px}
.cal-month{font-family:'Space Grotesk',sans-serif;font-size:20px;font-weight:800}
.cal-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:4px}
.cal-dow{text-align:center;font-size:10px;font-weight:700;color:var(--muted);padding:6px 0;letter-spacing:1px;text-transform:uppercase}
.cal-cell{
  border-radius:var(--radius-xs);padding:8px 4px;
  text-align:center;min-height:52px;
  border:1px solid transparent;
  background:rgba(255,255,255,0.02);
  cursor:pointer;transition:all var(--t);
}
.cal-cell:hover{background:rgba(255,255,255,0.04);border-color:var(--border)}
.cal-cell.empty{opacity:0;pointer-events:none}
.cal-cell.today{border-color:rgba(99,102,241,0.4);background:rgba(99,102,241,0.06)}
.cal-cell.c-present{background:rgba(16,185,129,0.07);border-color:rgba(16,185,129,0.22)}
.cal-cell.c-absent{background:rgba(239,68,68,0.07);border-color:rgba(239,68,68,0.22)}
.cal-cell.c-partial{background:rgba(245,158,11,0.07);border-color:rgba(245,158,11,0.22)}
.cal-day-num{font-size:12px;font-weight:600;margin-bottom:3px}
.cal-dots{display:flex;gap:3px;justify-content:center}
.dot{width:5px;height:5px;border-radius:50%}
.dot-g{background:var(--green)}.dot-r{background:var(--red)}
.cal-legend{display:flex;gap:14px;align-items:center;margin-top:14px;font-size:12px;color:var(--text2);flex-wrap:wrap}
.leg-dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:5px}

/* ══ SCAN RING (legacy fallback) ═════════════════════ */
.scan-wrap{position:relative;display:inline-block}
.scan-ring{
  position:absolute;inset:-14px;border-radius:50%;
  border:1.5px solid var(--cyan);opacity:0;
  animation:ring 2.8s ease-in-out infinite;
}
.scan-ring:nth-child(2){animation-delay:.93s}
.scan-ring:nth-child(3){animation-delay:1.86s}
@keyframes ring{0%{transform:scale(0.82);opacity:0.85}100%{transform:scale(1.25);opacity:0}}
video{border-radius:var(--radius);display:block}

/* ══ SECTION TABS ════════════════════════════════════ */
.sec-tabs{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:20px}
.sec-tab{
  padding:6px 15px;border-radius:20px;font-size:12.5px;font-weight:600;
  text-decoration:none;border:1px solid var(--border2);
  color:var(--text2);background:rgba(255,255,255,0.03);
  transition:all var(--t);
}
.sec-tab:hover{background:rgba(255,255,255,0.07);color:var(--text)}
.sec-tab-active{
  background:rgba(79,70,229,0.18)!important;
  border-color:rgba(99,102,241,0.4)!important;
  color:var(--blue-l)!important;
  box-shadow:0 0 12px rgba(79,70,229,0.15);
}
.sec-badge{
  display:inline-block;padding:2px 9px;border-radius:6px;
  font-size:10px;font-weight:700;
  background:rgba(99,102,241,0.12);color:var(--blue-l);
  border:1px solid rgba(99,102,241,0.2);
}

/* ══ SECTION CARDS ═══════════════════════════════════ */
.section-card{
  background:var(--card);border:1px solid var(--border);
  border-radius:var(--radius);padding:20px;
  transition:all var(--t);cursor:pointer;
  text-decoration:none;display:block;
  animation:scaleIn 0.35s cubic-bezier(.34,1.2,.64,1) both;
}
.section-card:hover{transform:translateY(-4px);border-color:var(--border2);box-shadow:0 12px 32px rgba(0,0,0,0.4)}
.section-card-name{
  font-family:'Space Grotesk',sans-serif;
  font-size:24px;font-weight:800;margin-bottom:3px;
}
.section-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px}

/* ══ PROFILE IMAGE ════════════════════════════════════ */
.profile-avatar-wrap{position:relative;width:110px;height:110px;margin:0 auto 14px;cursor:pointer}
.profile-avatar-wrap img,.profile-avatar-wrap .avatar-placeholder{
  width:110px;height:110px;border-radius:50%;object-fit:cover;
  border:2.5px solid var(--border2);display:block;
  transition:all var(--t);
  box-shadow:0 4px 20px rgba(0,0,0,0.4);
}
.profile-avatar-wrap .avatar-placeholder{
  background:linear-gradient(135deg,var(--blue-d),var(--purple));
  display:flex;align-items:center;justify-content:center;
  font-size:36px;font-weight:800;color:#fff;
}
.profile-avatar-wrap:hover img,.profile-avatar-wrap:hover .avatar-placeholder{filter:brightness(0.55)}
.profile-avatar-overlay{
  position:absolute;inset:0;border-radius:50%;
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  opacity:0;transition:opacity var(--t);pointer-events:none;gap:3px;
}
.profile-avatar-wrap:hover .profile-avatar-overlay{opacity:1}
.profile-avatar-overlay span{font-size:20px}
.profile-avatar-overlay small{font-size:10.5px;font-weight:700;color:#fff}
.profile-upload-btn{
  display:inline-flex;align-items:center;gap:6px;
  padding:6px 15px;border-radius:20px;font-size:12px;font-weight:600;
  background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.22);
  color:var(--blue-l);cursor:pointer;transition:all var(--t);margin-top:4px;
}
.profile-upload-btn:hover{background:rgba(99,102,241,0.2)}
.profile-preview{
  width:110px;height:110px;border-radius:50%;object-fit:cover;
  border:2.5px solid var(--cyan);display:none;margin:0 auto 8px;
  box-shadow:0 0 16px rgba(6,182,212,0.3);
}

/* ══ TEACHER DASHBOARD ════════════════════════════════ */
.td-hero{
  border-radius:20px;padding:24px 28px;margin-bottom:20px;
  position:relative;overflow:hidden;
  background:linear-gradient(135deg,rgba(79,70,229,0.22) 0%,rgba(139,92,246,0.1) 50%,rgba(6,182,212,0.08) 100%);
  border:1px solid rgba(99,102,241,0.2);
  animation:fadeUp 0.5s cubic-bezier(.34,1.2,.64,1) both;
}
.td-hero::before{
  content:'';position:absolute;top:-60px;right:-40px;
  width:220px;height:220px;border-radius:50%;
  background:radial-gradient(circle,rgba(139,92,246,0.1),transparent 70%);
  pointer-events:none;
}
.td-hero::after{
  content:'👨‍🏫';position:absolute;right:28px;top:50%;
  transform:translateY(-50%);font-size:68px;opacity:0.08;
}
.td-hero h1{
  font-family:'Space Grotesk',sans-serif;
  font-size:22px;font-weight:800;margin-bottom:5px;letter-spacing:-0.5px;
}
.td-hero p{color:var(--text2);font-size:13.5px;line-height:1.6}
.risk-high td:first-child{border-left:2.5px solid var(--red-l)!important}
.risk-mid  td:first-child{border-left:2.5px solid var(--amber-l)!important}
.risk-ok   td:first-child{border-left:2.5px solid var(--green-l)!important}
.absent-chip{
  display:inline-flex;align-items:center;gap:7px;
  background:rgba(239,68,68,0.07);border:1px solid rgba(239,68,68,0.18);
  border-radius:10px;padding:7px 12px;margin:4px;transition:all var(--t);
}
.absent-chip:hover{background:rgba(239,68,68,0.13);transform:translateY(-1px)}
.absent-chip-avatar{
  width:26px;height:26px;border-radius:50%;
  background:linear-gradient(135deg,var(--red),#f87171);
  display:flex;align-items:center;justify-content:center;
  font-size:11px;font-weight:700;color:#fff;flex-shrink:0;
}
.qa-grid{display:grid;grid-template-columns:1fr 1fr;gap:9px}
.qa-btn{
  display:flex;align-items:center;gap:10px;padding:12px 14px;
  background:rgba(255,255,255,0.03);border:1px solid var(--border);
  border-radius:var(--radius-sm);text-decoration:none;color:var(--text);
  font-size:13px;font-weight:600;transition:all var(--t);
}
.qa-btn:hover{background:rgba(255,255,255,0.065);border-color:var(--border2);transform:translateY(-2px)}
.qa-btn-icon{
  width:32px;height:32px;border-radius:8px;
  display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0;
}
.ring-wrap{position:relative;width:110px;height:110px;margin:0 auto 8px}
.ring-wrap svg{transform:rotate(-90deg)}
.ring-val{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;flex-direction:column;text-align:center}
.ring-num{font-family:'Space Grotesk',sans-serif;font-size:22px;font-weight:800}
.ring-lbl{font-size:10px;color:var(--text2);margin-top:1px}
.notice{padding:11px 15px;border-radius:var(--radius-xs);font-size:13px;display:flex;align-items:center;gap:8px;margin-bottom:9px}
.notice-warn{background:rgba(245,158,11,0.07);border:1px solid rgba(245,158,11,0.18);color:var(--amber-l)}

/* ══ SUBSCRIPTION ════════════════════════════════════ */
.upgrade-hero{
  border-radius:22px;padding:44px 36px;text-align:center;
  background:linear-gradient(145deg,#06101f,#080e1d,#0b1224);
  border:1px solid rgba(99,102,241,0.15);
  position:relative;overflow:hidden;margin-bottom:28px;
  box-shadow:0 0 80px rgba(79,70,229,0.07);
  animation:fadeUp 0.5s cubic-bezier(.34,1.1,.64,1) both;
}
.upgrade-hero::before{
  content:'';position:absolute;top:-100px;left:50%;transform:translateX(-50%);
  width:500px;height:300px;border-radius:50%;
  background:radial-gradient(ellipse,rgba(79,70,229,0.1),transparent 70%);
  pointer-events:none;
}
.upgrade-hero h1{
  font-family:'Space Grotesk',sans-serif;
  font-size:clamp(26px,4vw,36px);font-weight:800;letter-spacing:-1.5px;
  background:linear-gradient(135deg,#eef4ff,#94a3b8);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  position:relative;z-index:1;margin-bottom:12px;
}
.upgrade-hero p{color:var(--text2);font-size:14px;position:relative;z-index:1;line-height:1.7}
.plan-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:24px}
.plan-card{
  background:linear-gradient(160deg,rgba(10,18,34,0.95),rgba(6,12,24,0.98));
  border:1px solid var(--border2);border-radius:20px;padding:26px 20px;
  text-align:center;position:relative;overflow:hidden;
  transition:all var(--t);
  animation:fadeUp 0.45s cubic-bezier(.34,1.2,.64,1) both;
}
.plan-card:nth-child(1){animation-delay:.05s}
.plan-card:nth-child(2){animation-delay:.12s}
.plan-card:nth-child(3){animation-delay:.19s}
.plan-card:hover{transform:translateY(-6px);box-shadow:0 20px 50px rgba(0,0,0,0.5);border-color:var(--border3)}
.plan-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px}
.plan-monthly::before{background:linear-gradient(90deg,var(--blue-d),var(--cyan))}
.plan-yearly::before{background:linear-gradient(90deg,var(--purple),var(--pink))}
.plan-5year::before{background:linear-gradient(90deg,var(--amber),var(--green))}
.plan-popular{border-color:rgba(139,92,246,0.35)!important;box-shadow:0 0 30px rgba(139,92,246,0.08)!important}
.plan-badge{
  position:absolute;top:14px;right:14px;
  background:linear-gradient(135deg,var(--purple),var(--pink));
  color:#fff;padding:3px 11px;border-radius:20px;font-size:10.5px;font-weight:700;
  box-shadow:0 2px 8px rgba(139,92,246,0.4);
}
.plan-icon{font-size:36px;margin-bottom:12px}
.plan-name{font-family:'Space Grotesk',sans-serif;font-size:16px;font-weight:700;margin-bottom:8px}
.plan-price{
  font-family:'Space Grotesk',sans-serif;
  font-size:36px;font-weight:800;letter-spacing:-1px;
  margin-bottom:4px;line-height:1;
}
.plan-period{font-size:12px;color:var(--text2);margin-bottom:18px}
.plan-features{
  list-style:none;text-align:left;margin-bottom:22px;
  display:flex;flex-direction:column;gap:8px;
}
.plan-features li{
  display:flex;align-items:center;gap:9px;
  font-size:13px;color:var(--text2);
}
.plan-features li::before{content:"✓";color:var(--green);font-weight:700;flex-shrink:0;font-size:11px}

/* ══ EXPIRED OVERLAY ══════════════════════════════════ */
.expired-overlay{
  position:fixed;inset:0;z-index:9999;
  background:rgba(3,7,18,0.92);
  backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);
  display:flex;align-items:center;justify-content:center;
}
.expired-modal{
  background:var(--card2);border:1px solid rgba(239,68,68,0.25);
  border-radius:22px;padding:44px 38px;max-width:460px;width:90%;
  text-align:center;position:relative;overflow:hidden;
  box-shadow:0 32px 80px rgba(0,0,0,0.7);
  animation:scaleIn 0.3s cubic-bezier(.34,1.4,.64,1) both;
}
.expired-modal::before{
  content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,var(--red),var(--purple),var(--blue-d));
}
.lock-icon{font-size:56px;margin-bottom:16px;display:block}
.expired-title{
  font-family:'Space Grotesk',sans-serif;font-size:22px;font-weight:800;
  color:var(--red-l);margin-bottom:10px;
}
.expired-sub{color:var(--text2);font-size:14px;line-height:1.7;margin-bottom:24px}

/* ══ STREAK ══════════════════════════════════════════ */
.streak{
  display:inline-flex;align-items:center;gap:4px;
  background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.2);
  color:var(--amber-l);border-radius:20px;
  padding:3px 9px;font-size:11.5px;font-weight:700;
}

/* ══ DEV TABLE ════════════════════════════════════════ */
.dev-table td,.dev-table th{padding:10px 14px;border-bottom:1px solid var(--border);font-size:13px}
.dev-table th{font-size:9.5px;letter-spacing:1.2px;text-transform:uppercase;color:var(--muted)}

/* ══ ANIMATIONS ══════════════════════════════════════ */
@keyframes fadeUp{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
@keyframes scaleIn{from{opacity:0;transform:scale(0.9)}to{opacity:1;transform:scale(1)}}
@keyframes count-up{from{opacity:0;transform:translateY(8px) scale(0.85)}to{opacity:1;transform:none}}
@keyframes shimmer{0%{background-position:-200% center}100%{background-position:200% center}}

.login-wrap{
  min-height:100vh;width:100%;
  display:flex;align-items:center;justify-content:center;
  background:var(--bg);
  background-image:
    radial-gradient(ellipse 70% 60% at 50% 0%,rgba(79,70,229,0.1),transparent),
    radial-gradient(ellipse 40% 40% at 80% 80%,rgba(139,92,246,0.06),transparent);
  padding:20px;
}
.login-card{
  background:rgba(13,21,38,0.7);
  backdrop-filter:blur(40px) saturate(1.4);
  -webkit-backdrop-filter:blur(40px) saturate(1.4);
  border:1px solid rgba(255,255,255,0.08);
  border-radius:24px;padding:40px 34px;
  width:100%;max-width:420px;
  box-shadow:0 40px 100px rgba(0,0,0,0.6),0 0 0 1px rgba(255,255,255,0.04) inset;
  position:relative;overflow:hidden;
  animation:scaleIn 0.45s cubic-bezier(.34,1.3,.64,1) both;
}
.login-card::before{
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(99,102,241,0.6),rgba(6,182,212,0.4),transparent);
}
.login-logo{text-align:center;margin-bottom:28px}
.login-logo-icon{
  width:62px;height:62px;border-radius:17px;margin:0 auto 14px;
  background:linear-gradient(135deg,#4f46e5,#06b6d4);
  display:flex;align-items:center;justify-content:center;font-size:26px;
  box-shadow:0 8px 28px rgba(79,70,229,0.45);
}
.login-title{
  font-family:'Space Grotesk',sans-serif;
  font-size:22px;font-weight:800;letter-spacing:-0.5px;margin-bottom:4px;
}
.login-sub{font-size:13px;color:var(--text2)}

/* ══ LOG ITEMS ════════════════════════════════════════ */
.log-item{
  display:flex;align-items:center;gap:12px;
  padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.035);
  transition:all var(--t);
}
.log-item:last-child{border-bottom:none}
.log-item:hover{padding-left:4px}
.log-avatar{
  width:35px;height:35px;border-radius:9px;flex-shrink:0;
  background:linear-gradient(135deg,var(--blue-d),var(--purple));
  display:flex;align-items:center;justify-content:center;
  font-weight:700;font-size:13px;color:#fff;
  box-shadow:0 2px 8px rgba(79,70,229,0.3);
}
.log-info{flex:1}
.log-name{font-weight:600;font-size:13.5px}
.log-time{font-size:11px;color:var(--text2);margin-top:1px}

/* ══ RESPONSIVE ══════════════════════════════════════ */
@media(max-width:768px){.plan-grid{grid-template-columns:1fr}}
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
  .hero{padding:16px}
  .hero h1{font-size:18px}
  .login-card{padding:32px 20px;border-radius:20px}
  .stat-val{font-size:26px}
  video{width:100%!important;max-width:100%}
  .scan-wrap{width:100%}
  .tbl-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch}
  table{min-width:400px}
  .sec-tabs{overflow-x:auto;flex-wrap:nowrap;padding-bottom:6px}
  .sec-tab{flex-shrink:0}
  .upgrade-hero{padding:28px 18px}
  .upgrade-hero h1{font-size:24px}
  .qa-grid{grid-template-columns:1fr}
  .scan-viewfinder{aspect-ratio:1/1;max-height:75vw}
}

/* ══ MOBILE BOTTOM NAV ════════════════════════════════ */
.mobile-nav{
  display:none;
  position:fixed;bottom:0;left:0;right:0;
  height:66px;
  background:rgba(8,12,22,0.97);
  backdrop-filter:blur(24px) saturate(1.3);
  -webkit-backdrop-filter:blur(24px) saturate(1.3);
  border-top:1px solid rgba(99,102,241,0.12);
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
  transition:all .15s cubic-bezier(.4,0,.2,1);
  -webkit-tap-highlight-color:transparent;
  animation:fadeUp .3s cubic-bezier(.34,1.3,.64,1) both;
}
.mnav-item:nth-child(1){animation-delay:.04s}
.mnav-item:nth-child(2){animation-delay:.08s}
.mnav-item:nth-child(3){animation-delay:.12s}
.mnav-item:nth-child(4){animation-delay:.16s}
.mnav-item:nth-child(5){animation-delay:.20s}
.mnav-item svg{width:21px;height:21px;flex-shrink:0;transition:all .15s}
.mnav-item:active{transform:scale(0.88)}
.mnav-active{color:var(--blue-l)!important;background:rgba(99,102,241,0.1)}
.mnav-active svg{transform:scale(1.12);filter:drop-shadow(0 0 5px rgba(99,102,241,0.6))}
.mnav-active::before{
  content:'';position:absolute;top:-6px;left:50%;transform:translateX(-50%);
  width:22px;height:2.5px;border-radius:2px;
  background:linear-gradient(90deg,var(--blue-d),var(--cyan));
  box-shadow:0 0 8px var(--blue-d);
}
.mnav-item{position:relative}
.mnav-premium{color:rgba(245,158,11,0.6)!important}
.mnav-premium.mnav-active{color:var(--amber-l)!important;background:rgba(245,158,11,0.09)}
.mnav-premium.mnav-active svg{filter:drop-shadow(0 0 5px rgba(245,158,11,0.5))}
.mnav-premium.mnav-active::before{background:linear-gradient(90deg,var(--amber),var(--amber-l))}

/* ══ MOBILE TOPBAR ════════════════════════════════════ */
.mobile-topbar{
  display:none;position:fixed;top:0;left:0;right:0;z-index:150;
  height:54px;padding:0 16px;
  background:rgba(8,12,22,0.96);
  backdrop-filter:blur(24px) saturate(1.3);
  -webkit-backdrop-filter:blur(24px) saturate(1.3);
  border-bottom:1px solid var(--border);
  align-items:center;justify-content:space-between;
  box-shadow:0 4px 20px rgba(0,0,0,0.4);
}
.mobile-logo{
  font-family:'Space Grotesk',sans-serif;font-size:17px;font-weight:800;
  display:flex;align-items:center;gap:8px;
}
.mobile-logo span{
  background:linear-gradient(90deg,var(--blue-l),var(--cyan));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}
.hamburger-btn{
  width:36px;height:36px;border-radius:10px;
  background:rgba(255,255,255,0.05);border:1px solid var(--border2);
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  gap:5px;cursor:pointer;transition:all .15s;
  -webkit-tap-highlight-color:transparent;
}
.hamburger-btn:hover{background:rgba(255,255,255,0.09)}
.hamburger-btn span{display:block;width:18px;height:2px;background:var(--text2);border-radius:2px}

/* ══ DRAWER ══════════════════════════════════════════ */
.drawer-overlay{
  display:none;position:fixed;inset:0;z-index:190;
  background:rgba(0,0,0,0.65);backdrop-filter:blur(5px);-webkit-backdrop-filter:blur(5px);
}
.drawer{
  position:fixed;top:0;right:-280px;bottom:0;width:265px;z-index:195;
  background:linear-gradient(180deg,#0d1526,#080d18);
  border-left:1px solid var(--border);
  transition:right .28s cubic-bezier(.4,0,.2,1);
  display:flex;flex-direction:column;padding:20px 0;
  overflow-y:auto;box-shadow:-8px 0 40px rgba(0,0,0,0.6);
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
  font-size:16px;cursor:pointer;transition:all .15s;
  display:flex;align-items:center;justify-content:center;
}
.drawer-close:hover{background:rgba(255,255,255,0.09);color:var(--text)}
.drawer-item{
  display:flex;align-items:center;gap:12px;
  padding:12px 20px;color:var(--text2);text-decoration:none;
  font-size:13.5px;font-weight:500;transition:all .12s;
  border-left:3px solid transparent;
}
.drawer-item svg{width:17px;height:17px;flex-shrink:0;opacity:0.55}
.drawer-item:hover{color:var(--text);background:rgba(255,255,255,0.04)}
.drawer-item:hover svg{opacity:1}
.drawer-active{
  color:var(--blue-l)!important;
  border-left-color:var(--blue-l)!important;
  background:rgba(99,102,241,0.08)!important;font-weight:600!important;
}
.drawer-active svg{opacity:1!important}

@media(max-width:960px){
  .mobile-nav{display:flex}
  .mobile-topbar{display:flex}
  .topbar{display:none}
  .page{margin-top:54px}
}
@media(prefers-reduced-motion:reduce){
  *{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important}
}
</style>
"""
