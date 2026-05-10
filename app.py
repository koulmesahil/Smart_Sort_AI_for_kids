import streamlit as st
import streamlit.components.v1 as components
import time
from datetime import datetime
import pandas as pd
import altair as alt
import json
import os
import uuid

# Import from our modules
from child_game import show_game_interface, init_game_state
from parent_dashboard import show_parent_dashboard
from utils import load_css, save_session_data
from game_data import FOOD_CATEGORIES, ADVANCED_CATEGORIES

# ---------------------------------------------------------------------------
# Page config — sidebar collapsed (and fully hidden via CSS)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="SmartSort Kids - Learn & Play!",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

load_css()


# ---------------------------------------------------------------------------
# Custom theme / CSS
# ---------------------------------------------------------------------------
def inject_custom_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&family=Nunito:wght@400;600;800&display=swap');

        html, body, [class*="css"]  { font-family: 'Nunito', sans-serif; }
        h1, h2, h3, h4 { font-family: 'Fredoka', sans-serif !important; letter-spacing: -0.5px; }

        .stApp {
            background:
              radial-gradient(circle at 10% 10%, rgba(255,182,193,0.45) 0%, transparent 40%),
              radial-gradient(circle at 90% 20%, rgba(168,230,255,0.45) 0%, transparent 40%),
              radial-gradient(circle at 50% 90%, rgba(255,234,167,0.55) 0%, transparent 45%),
              linear-gradient(135deg, #fff8f0 0%, #f0f7ff 100%);
            background-attachment: fixed;
        }

        /* Hide sidebar entirely */
        [data-testid="stSidebar"],
        section[data-testid="stSidebar"],
        [data-testid="collapsedControl"] { display: none !important; }
        #MainMenu, footer, header { visibility: hidden; }

        /* Section card */
        .section-card {
            background: white;
            border-radius: 28px;
            padding: 28px 28px 24px;
            margin: 14px 0;
            box-shadow: 0 8px 24px rgba(0,0,0,0.06);
        }

        /* Streamlit buttons (kept for forms below the cards) */
        .stButton > button {
            background: linear-gradient(135deg, #ff6b9d 0%, #ff8a3d 100%);
            color: white !important;
            border: none;
            border-radius: 50px;
            padding: 12px 28px;
            font-family: 'Fredoka', sans-serif;
            font-size: 18px;
            font-weight: 600;
            box-shadow: 0 5px 0 #d63384, 0 8px 18px rgba(214,51,132,0.28);
            transition: transform .12s, box-shadow .12s;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 7px 0 #d63384, 0 12px 22px rgba(214,51,132,0.36);
            color: white !important;
        }
        .stButton > button:active {
            transform: translateY(3px);
            box-shadow: 0 2px 0 #d63384, 0 3px 8px rgba(214,51,132,0.3);
        }
        button[kind="secondary"] {
            background: white !important;
            color: #6c5ce7 !important;
            box-shadow: 0 3px 0 #d6cffa, 0 4px 10px rgba(108,92,231,0.18) !important;
        }

        .age-badges .stButton > button {
            width: 64px;
            height: 64px;
            border-radius: 50% !important;
            padding: 0 !important;
            font-size: 22px !important;
            background: white !important;
            color: #2d3436 !important;
            box-shadow: 0 4px 0 #ffd6e0, 0 6px 14px rgba(255,107,157,0.18) !important;
        }
        .age-badges .stButton > button:hover { transform: translateY(-2px) scale(1.05); }

        .stTextInput > div > div > input {
            border-radius: 16px !important;
            border: 3px solid #ffd6e0 !important;
            padding: 12px 18px !important;
            font-family: 'Nunito', sans-serif !important;
            font-size: 18px !important;
            background: white !important;
        }
        .stTextInput > div > div > input:focus {
            border-color: #ff6b9d !important;
            box-shadow: 0 0 0 4px rgba(255,107,157,0.15) !important;
        }

        .center { text-align: center; }
        .small-muted { color:#7d7d8a; font-size: 14px; }
        .lock-emoji { text-align:center; font-size:64px; margin-top:-6px; }

        /* Floating bottom-right links replacing the sidebar info */
        .floating-links {
            position: fixed;
            bottom: 18px;
            right: 22px;
            display: flex;
            gap: 10px;
            z-index: 9999;
        }
        .floating-links a {
            background: rgba(255,255,255,0.92);
            backdrop-filter: blur(8px);
            padding: 8px 14px;
            border-radius: 999px;
            text-decoration: none;
            color: #2d3436;
            font-family: 'Nunito', sans-serif;
            font-weight: 700;
            font-size: 13px;
            box-shadow: 0 6px 18px rgba(0,0,0,0.10);
            transition: transform .15s, box-shadow .15s;
        }
        .floating-links a:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 22px rgba(0,0,0,0.14);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Hero (rendered inside an iframe via components.html so JS runs)
#
# Scene: a floating field of fruits & veggies drifts around the title.
# Cursor scatters them gently; clicking anywhere fires a big food explosion
# with physics (gravity, rotation, fade) plus a shockwave ring.
# ---------------------------------------------------------------------------
HERO_HTML = """
<!DOCTYPE html>
<html><head>
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { background: transparent; overflow: hidden; height: 100%; }

.hero-stage {
    position: relative;
    width: 100%;
    height: 400px;
    overflow: hidden;
    cursor: pointer;
}

/* Canvas background: floating dots */
.particles {
    position: absolute; top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none;
    z-index: 1;
}

/* Cursor glow halo */
.cursor-glow {
    position: absolute;
    width: 140px; height: 140px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255,107,157,0.40) 0%, rgba(108,92,231,0.18) 50%, transparent 75%);
    pointer-events: none;
    transform: translate(-50%, -50%);
    z-index: 2;
    opacity: 0;
    transition: opacity .25s;
    mix-blend-mode: screen;
}

/* Soft animated rainbow blob behind title */
.aura {
    position: absolute;
    top: 50%; left: 50%;
    width: 520px; height: 280px;
    margin: -140px 0 0 -260px;
    border-radius: 50%;
    background:
      radial-gradient(circle at 30% 50%, rgba(255,107,157,0.35) 0%, transparent 55%),
      radial-gradient(circle at 70% 50%, rgba(72,219,251,0.30) 0%, transparent 55%),
      radial-gradient(circle at 50% 50%, rgba(254,202,87,0.25) 0%, transparent 60%);
    filter: blur(8px);
    animation: pulse 5s ease-in-out infinite;
    z-index: 1;
}
@keyframes pulse {
    0%,100% { transform: scale(1)    rotate(0deg);  opacity: 0.85; }
    50%     { transform: scale(1.08) rotate(3deg);  opacity: 1; }
}

/* Floating food items (drifting around) */
.food-item {
    position: absolute;
    top: 0; left: 0;
    user-select: none;
    pointer-events: none;
    will-change: transform, opacity;
    filter: drop-shadow(0 5px 10px rgba(0,0,0,0.20));
}
.food-item.ambient { z-index: 2; }
.food-item.burst   { z-index: 7; }

/* Centered title block */
.hero-content {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    z-index: 5;
    pointer-events: none;
    width: 92%;
}
.hero-title {
    font-family: 'Fredoka', sans-serif;
    font-size: 68px;
    font-weight: 700;
    line-height: 1.05;
    background: linear-gradient(90deg, #ff6b9d, #feca57, #48dbfb, #1dd1a1, #ff6b9d);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shimmer 6s ease infinite, float 4s ease-in-out infinite;
    margin: 0 0 8px;
    filter: drop-shadow(0 6px 14px rgba(0,0,0,0.10));
    letter-spacing: -1px;
}
@keyframes shimmer {
    0%,100% { background-position: 0% 50%; }
    50%     { background-position: 100% 50%; }
}
@keyframes float {
    0%,100% { transform: translateY(0); }
    50%     { transform: translateY(-6px); }
}
.hero-subtitle {
    font-family: 'Fredoka', sans-serif;
    font-size: 19px;
    color: #6c5ce7;
    font-weight: 500;
    margin: 0;
}

/* Click-anywhere hint badge */
.click-hint {
    position: absolute;
    bottom: 14px; left: 50%;
    transform: translateX(-50%);
    background: rgba(255,255,255,0.85);
    backdrop-filter: blur(6px);
    color: #6c5ce7;
    font-family: 'Fredoka', sans-serif;
    font-weight: 600;
    font-size: 13px;
    padding: 7px 16px;
    border-radius: 999px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.10);
    z-index: 6;
    pointer-events: none;
    animation: hint-pulse 1.6s ease-in-out infinite;
    transition: opacity .4s;
}
@keyframes hint-pulse {
    0%,100% { transform: translateX(-50%) translateY(0); }
    50%     { transform: translateX(-50%) translateY(-4px); }
}

/* Click shockwave ring */
.click-ring {
    position: absolute;
    width: 30px; height: 30px;
    border: 4px solid rgba(255,107,157,0.85);
    border-radius: 50%;
    transform: translate(-50%, -50%) scale(0);
    pointer-events: none;
    z-index: 6;
    animation: ring-expand 0.7s cubic-bezier(.2,.8,.3,1) forwards;
}
@keyframes ring-expand {
    0%   { transform: translate(-50%, -50%) scale(0);   opacity: 1; }
    100% { transform: translate(-50%, -50%) scale(14);  opacity: 0; }
}
</style>
</head>
<body>
<div class='hero-stage' id='stage'>
    <canvas class='particles' id='particles'></canvas>
    <div class='aura'></div>
    <div class='cursor-glow' id='cursor-glow'></div>
    <div class='hero-content'>
        <h1 class='hero-title'>Know Your Food!</h1>
        <p class='hero-subtitle'>Learn about food groups through fun sorting games</p>
    </div>
    <div class='click-hint' id='click-hint'>👆 click anywhere — make it rain food!</div>
</div>
<script>
(function(){
    const stage      = document.getElementById('stage');
    const cursorGlow = document.getElementById('cursor-glow');
    const clickHint  = document.getElementById('click-hint');
    const canvas     = document.getElementById('particles');
    const ctx        = canvas.getContext('2d');

    const FOODS = [
        '🍎','🍌','🍊','🍇','🍓','🍉','🍒','🥭','🍑','🥝',
        '🍍','🍐','🥕','🥦','🌽','🍅','🥑','🥒','🫐','🥬',
        '🍆','🌶️','🥥','🍋','🥯','🥨'
    ];

    function resize() {
        canvas.width  = stage.clientWidth;
        canvas.height = stage.clientHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    // ---------- Background dot particles ----------
    const COLORS = ['#ff6b9d','#feca57','#48dbfb','#1dd1a1','#c8b6ff','#ff8a3d'];
    const dots = [];
    for (let i = 0; i < 40; i++) {
        dots.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * 0.35,
            vy: (Math.random() - 0.5) * 0.35,
            r: Math.random() * 3 + 1,
            color: COLORS[Math.floor(Math.random() * COLORS.length)],
            opacity: Math.random() * 0.45 + 0.2,
            phase: Math.random() * Math.PI * 2
        });
    }

    // ---------- Floating ambient food items ----------
    const ambient = [];
    function spawnAmbient(n) {
        for (let i = 0; i < n; i++) {
            const el = document.createElement('div');
            el.className = 'food-item ambient';
            el.textContent = FOODS[Math.floor(Math.random() * FOODS.length)];
            const size = 26 + Math.random() * 22;
            el.style.fontSize = size + 'px';
            stage.appendChild(el);
            ambient.push({
                el,
                x: Math.random() * (stage.clientWidth - 60) + 30,
                y: Math.random() * (stage.clientHeight - 60) + 30,
                vx: (Math.random() - 0.5) * 1.2,
                vy: (Math.random() - 0.5) * 1.2,
                rot: Math.random() * 360,
                rotV: (Math.random() - 0.5) * 1.2,
                size: size
            });
        }
    }
    spawnAmbient(14);

    // ---------- Click burst items ----------
    const burst = [];

    let mouseX = -9999, mouseY = -9999;
    let hintHidden = false;

    // ---------- Animation loop ----------
    function tick() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const t = Date.now() * 0.001;

        // Dots
        dots.forEach(p => {
            p.x += p.vx + Math.sin(t + p.phase) * 0.18;
            p.y += p.vy + Math.cos(t + p.phase) * 0.18;
            if (p.x < -10) p.x = canvas.width + 10;
            if (p.x > canvas.width + 10) p.x = -10;
            if (p.y < -10) p.y = canvas.height + 10;
            if (p.y > canvas.height + 10) p.y = -10;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = p.color;
            ctx.globalAlpha = p.opacity;
            ctx.fill();
        });
        ctx.globalAlpha = 1;

        // Ambient food drift
        const W = stage.clientWidth;
        const H = stage.clientHeight;
        ambient.forEach(it => {
            // Cursor repel
            if (mouseX > -100) {
                const dx = it.x - mouseX;
                const dy = it.y - mouseY;
                const d2 = dx*dx + dy*dy;
                if (d2 < 11000 && d2 > 1) {
                    const d = Math.sqrt(d2);
                    const f = (1 - d/Math.sqrt(11000)) * 0.9;
                    it.vx += (dx/d) * f;
                    it.vy += (dy/d) * f;
                }
            }
            it.x += it.vx;
            it.y += it.vy;
            it.rot += it.rotV;
            // friction so they settle into gentle drift
            it.vx *= 0.985;
            it.vy *= 0.985;
            // tiny random nudge
            if (Math.random() < 0.02) {
                it.vx += (Math.random() - 0.5) * 0.4;
                it.vy += (Math.random() - 0.5) * 0.4;
            }
            // cap velocity
            const sp = Math.hypot(it.vx, it.vy);
            const SP_MAX = 4;
            if (sp > SP_MAX) { it.vx = it.vx/sp*SP_MAX; it.vy = it.vy/sp*SP_MAX; }
            // soft bounce off edges
            const m = 24;
            if (it.x < m)        { it.x = m;        it.vx = Math.abs(it.vx) * 0.85; }
            if (it.x > W - m)    { it.x = W - m;    it.vx = -Math.abs(it.vx) * 0.85; }
            if (it.y < m)        { it.y = m;        it.vy = Math.abs(it.vy) * 0.85; }
            if (it.y > H - m)    { it.y = H - m;    it.vy = -Math.abs(it.vy) * 0.85; }
            it.el.style.transform =
                `translate(${it.x - it.size/2}px, ${it.y - it.size/2}px) rotate(${it.rot}deg)`;
        });

        // Burst items (with gravity, fade)
        for (let i = burst.length - 1; i >= 0; i--) {
            const it = burst[i];
            it.vy += 0.32;        // gravity
            it.vx *= 0.995;       // air drag
            it.x  += it.vx;
            it.y  += it.vy;
            it.rot += it.rotV;
            it.life -= 0.011;
            if (it.life <= 0 || it.y > H + 80) {
                it.el.remove();
                burst.splice(i, 1);
            } else {
                const sc = 0.7 + it.life * 0.4;
                it.el.style.transform =
                    `translate(${it.x - it.size/2}px, ${it.y - it.size/2}px) rotate(${it.rot}deg) scale(${sc})`;
                it.el.style.opacity = Math.min(1, it.life * 1.4);
            }
        }

        requestAnimationFrame(tick);
    }
    tick();

    // ---------- Cursor tracking ----------
    stage.addEventListener('mousemove', (e) => {
        const rect = stage.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;
        mouseX = mx; mouseY = my;
        cursorGlow.style.left    = mx + 'px';
        cursorGlow.style.top     = my + 'px';
        cursorGlow.style.opacity = '1';
    });
    stage.addEventListener('mouseleave', () => {
        cursorGlow.style.opacity = '0';
        mouseX = -9999; mouseY = -9999;
    });

    // ---------- Click → food explosion ----------
    function explode(cx, cy) {
        // Shockwave ring
        const ring = document.createElement('div');
        ring.className = 'click-ring';
        ring.style.left = cx + 'px';
        ring.style.top  = cy + 'px';
        stage.appendChild(ring);
        setTimeout(() => ring.remove(), 700);

        // Burst of fruits/veggies in all directions
        const N = 30;
        for (let i = 0; i < N; i++) {
            const angle = (Math.PI * 2 * i / N) + (Math.random() - 0.5) * 0.5;
            const speed = 5 + Math.random() * 9;
            const size  = 28 + Math.random() * 22;
            const el = document.createElement('div');
            el.className = 'food-item burst';
            el.textContent = FOODS[Math.floor(Math.random() * FOODS.length)];
            el.style.fontSize = size + 'px';
            stage.appendChild(el);
            burst.push({
                el,
                x: cx,
                y: cy,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed - 3,   // upward bias for arc
                rot: Math.random() * 360,
                rotV: (Math.random() - 0.5) * 28,
                life: 1,
                size: size
            });
        }

        // Also nudge ambient items outward — feels alive
        ambient.forEach(it => {
            const dx = it.x - cx;
            const dy = it.y - cy;
            const d  = Math.hypot(dx, dy) || 1;
            if (d < 220) {
                const f = (1 - d/220) * 6;
                it.vx += (dx/d) * f;
                it.vy += (dy/d) * f;
                it.rotV += (Math.random() - 0.5) * 6;
            }
        });
    }

    stage.addEventListener('click', (e) => {
        const rect = stage.getBoundingClientRect();
        explode(e.clientX - rect.left, e.clientY - rect.top);
        if (!hintHidden) {
            hintHidden = true;
            clickHint.style.opacity = '0';
            setTimeout(() => clickHint.remove(), 500);
        }
    });

    // First-load auto-burst so users see what's possible
    setTimeout(() => {
        explode(stage.clientWidth / 2, stage.clientHeight / 2);
    }, 700);
})();
</script>
</body></html>
"""


def show_hero():
    components.html(HERO_HTML, height=420, scrolling=False)


# ---------------------------------------------------------------------------
# Mode picker — the cards themselves are the click target.
# Anchor links update the URL with ?welcome_step=..., the app picks it up.
# ---------------------------------------------------------------------------
MODE_CARDS_HTML = """
<style>
.mode-cards-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 30px;
    max-width: 900px;
    margin: 8px auto 30px;
    padding: 0 20px;
}
.mode-card {
    display: block;
    text-decoration: none;
    border-radius: 28px;
    padding: 50px 30px 36px;
    text-align: center;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    transition: transform .3s cubic-bezier(.2,.9,.3,1.4), box-shadow .3s;
    border: 4px solid transparent;
    position: relative;
    overflow: hidden;
    cursor: pointer;
    color: #2d3436;
}
.mode-card::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.45) 0%, transparent 60%);
    transform: scale(0);
    transition: transform .55s ease;
    pointer-events: none;
}
.mode-card:hover {
    transform: translateY(-10px) scale(1.025);
    box-shadow: 0 25px 50px rgba(0,0,0,0.16);
}
.mode-card:hover::before { transform: scale(1); }
.mode-card:active { transform: translateY(-3px) scale(1.005); }

.mode-card-child  {
    background: linear-gradient(135deg, #ffeaa7 0%, #ffb8d1 100%);
    border-color: #ff6b9d;
}
.mode-card-parent {
    background: linear-gradient(135deg, #a8e6ff 0%, #c8b6ff 100%);
    border-color: #6c5ce7;
}

.mode-icon {
    font-size: 90px;
    display: block;
    margin-bottom: 14px;
    animation: wiggle 4s ease-in-out infinite;
    filter: drop-shadow(0 6px 12px rgba(0,0,0,0.16));
}
.mode-card:hover .mode-icon { animation: bouncing 0.6s ease-in-out infinite; }
@keyframes wiggle   { 0%,100% { transform: rotate(-6deg); } 50% { transform: rotate(6deg); } }
@keyframes bouncing { 0%,100% { transform: translateY(0)    rotate(-6deg); }
                      50%     { transform: translateY(-12px) rotate(6deg); } }

.mode-title {
    font-family: 'Fredoka', sans-serif;
    font-size: 36px;
    font-weight: 700;
    margin: 4px 0 6px;
    color: #2d3436;
    letter-spacing: -0.5px;
}
.mode-desc  {
    color: #4b4b4b;
    font-size: 17px;
    margin: 0;
    font-family: 'Nunito', sans-serif;
    font-weight: 600;
}
.mode-hint  {
    margin-top: 14px;
    font-size: 12px;
    color: rgba(45,52,54,0.55);
    font-family: 'Nunito', sans-serif;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}
</style>
<div class='mode-cards-row'>
    <a href='?welcome_step=child_form' target='_self' class='mode-card mode-card-child'>
        <span class='mode-icon'>👶</span>
        <h2 class='mode-title'>Child</h2>
        <p class='mode-desc'>Play games and learn about food!</p>
        <p class='mode-hint'>▸ Tap to start</p>
    </a>
    <a href='?welcome_step=parent_login' target='_self' class='mode-card mode-card-parent'>
        <span class='mode-icon'>👨‍👩‍👧</span>
        <h2 class='mode-title'>Parent</h2>
        <p class='mode-desc'>View progress and analytics</p>
        <p class='mode-hint'>▸ Tap to start</p>
    </a>
</div>
"""


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.page = 'welcome'
    st.session_state.mode = 'child'
    st.session_state.child_name = ''
    st.session_state.child_age = '5'
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.parent_password = None
    st.session_state.welcome_step = 'pick_mode'  # pick_mode | child_form | parent_login
    st.session_state.selected_age = '5'
    st.session_state.parent_authenticated = False

    init_game_state()


# Pull welcome_step from URL query params (set by clicking a mode card)
def consume_query_params():
    qp_step = st.query_params.get("welcome_step")
    if qp_step and qp_step in ("pick_mode", "child_form", "parent_login"):
        st.session_state.welcome_step = qp_step
        # Clean the URL so it doesn't stick on refresh / back-button weirdness
        try:
            st.query_params.clear()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# UI sections
# ---------------------------------------------------------------------------
def show_mode_picker():
    st.markdown(MODE_CARDS_HTML, unsafe_allow_html=True)


def show_child_form():
    if st.button("← Back", key="back_from_child", type="secondary"):
        st.session_state.welcome_step = 'pick_mode'
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 3, 1])
    with mid:
        #st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown(
            "<h2 class='center' style='color:#ff6b9d; margin-top:0;'>🎉 Let's Get Started!</h2>",
            unsafe_allow_html=True,
        )

        st.markdown("<h4 style='color:#4b89dc;'>👤 What's your name?</h4>", unsafe_allow_html=True)
        name = st.text_input(
            "Name",
            key="name_input",
            placeholder="Type your name here...",
            max_chars=15,
            label_visibility="collapsed",
        )

        st.markdown(
            "<h4 style='color:#4b89dc; margin-top:18px;'>🎂 How old are you?</h4>",
            unsafe_allow_html=True,
        )

        ages = ['3', '4', '5', '6', '7']
        st.markdown("<div class='age-badges'>", unsafe_allow_html=True)
        cols = st.columns(5)
        for i, a in enumerate(ages):
            with cols[i]:
                is_selected = st.session_state.selected_age == a
                label = f"✨{a}✨" if is_selected else a
                if st.button(label, key=f"age_{a}", use_container_width=True):
                    st.session_state.selected_age = a
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        use_voice = st.checkbox(
            "🔊 Enable Voice Features",
            value=False,
            help="Turn on speaking and listening",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Start Playing! 🚀", key="start_button", use_container_width=True):
            if name:
                st.session_state.child_name = name
                st.session_state.child_age = st.session_state.selected_age
                st.session_state.use_voice = use_voice
                st.session_state.mode = 'child'
                st.session_state.page = 'game'
                st.rerun()
            else:
                st.warning("⚠️ Please tell us your name first!")

        st.markdown("</div>", unsafe_allow_html=True)


def show_parent_login():
    if st.button("← Back", key="back_from_parent", type="secondary"):
        st.session_state.welcome_step = 'pick_mode'
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        #st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='lock-emoji'>🔒</div>", unsafe_allow_html=True)
        st.markdown(
            "<h2 class='center' style='color:#6c5ce7; margin-top:6px;'>Parent Access</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p class='center small-muted'>Enter the family password to peek at progress</p>",
            unsafe_allow_html=True,
        )

        if not st.session_state.parent_authenticated:
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter password...",
                help="Default password is 'parent123'",
                label_visibility="collapsed",
            )
            if st.button("Log In 🔓", key="parent_login", use_container_width=True):
                if password == "parent123":
                    st.session_state.parent_authenticated = True
                    st.session_state.mode = 'parent'
                    st.session_state.page = 'dashboard'
                    st.rerun()
                else:
                    st.error("❌ Incorrect password")
        else:
            st.success("✅ Authenticated as parent")
            if st.button("View Dashboard 📊", key="view_dashboard", use_container_width=True):
                st.session_state.mode = 'parent'
                st.session_state.page = 'dashboard'
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


def show_welcome_page():
    show_hero()
    step = st.session_state.get('welcome_step', 'pick_mode')
    if step == 'pick_mode':
        show_mode_picker()
    elif step == 'child_form':
        show_child_form()
    elif step == 'parent_login':
        show_parent_login()


def show_floating_links():
    st.markdown(
        """
        <div class='floating-links'>
            <a href="https://www.linkedin.com/in/sahilkoul123/" target="_blank">in · LinkedIn</a>
            <a href="https://koulmesahil.github.io/" target="_blank">⌘ GitHub</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    inject_custom_css()
    consume_query_params()

    # Top-right small mode-switch button (only when not on welcome)
    if st.session_state.page != 'welcome':
        col1, col2 = st.columns([9, 1])
        with col2:
            if st.session_state.mode == 'child':
                if st.button("👨‍👩‍👧", help="Switch to Parent Mode"):
                    st.session_state.page = 'welcome'
                    st.session_state.welcome_step = 'pick_mode'
                    st.rerun()
            else:
                if st.button("👶", help="Switch to Child Mode"):
                    st.session_state.page = 'welcome'
                    st.session_state.welcome_step = 'pick_mode'
                    st.rerun()

    # Routing
    if st.session_state.page == 'welcome':
        show_welcome_page()
    elif st.session_state.mode == 'child' and st.session_state.page == 'game':
        show_game_interface()
    elif st.session_state.mode == 'parent' and st.session_state.page == 'dashboard':
        if st.session_state.parent_authenticated:
            show_parent_dashboard()
        else:
            st.error("Authentication required")
            st.session_state.page = 'welcome'
            st.session_state.welcome_step = 'parent_login'
            st.rerun()
    else:
        show_welcome_page()

    show_floating_links()


if __name__ == "__main__":
    main()
