"""Re:Learn UI - bold "graph paper" theme.

Drop-in replacement for ui.py. Works with the original app.py and with the
previous redesign (it exports every helper either one imports).
"""
import html
import re

import streamlit as st

try:
    from engine import DISPLAY_LABELS
except Exception:  # keep the UI usable even if engine changes
    DISPLAY_LABELS = {
        "distribute_first_only": "Only distributing to the first term",
        "ignore_minus_sign": "Losing the minus sign",
        "square_each_term": "Missing the middle term when squaring",
        "multiply_by_two": "Treating a square like multiplication by 2",
    }


CSS = """
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500..800&family=Figtree:wght@400;500;600;700&family=Fraunces:ital,opsz,wght@0,9..144,600..800;1,9..144,600..800&display=swap');

:root {
  --bg: #D6CCFF;
  --ink: #14112B;
  --cream: #FFFBEF;
  --yellow: #FFD23F;
  --coral: #FF6B4A;
  --mint: #74E8B5;
  --pink: #FFA6C9;
  --sky: #8EC9FF;
  --muted: #4B4670;
  --soft: #BDB4EE;
  --line: 2.5px solid var(--ink);
  --display: 'Bricolage Grotesque', 'Segoe UI', system-ui, sans-serif;
  --body: 'Figtree', 'Segoe UI', system-ui, sans-serif;
  --math: 'Fraunces', Georgia, 'Times New Roman', serif;
}

html { color-scheme: light; }
::selection { background: var(--yellow); color: var(--ink); }

/* ---------- canvas: lilac graph paper ---------- */
.stApp {
  background-color: var(--bg);
  background-image:
    linear-gradient(rgba(20,17,43,.07) 1px, transparent 1px),
    linear-gradient(90deg, rgba(20,17,43,.07) 1px, transparent 1px);
  background-size: 36px 36px;
  color: var(--ink);
  font-family: var(--body);
}
[data-testid="stAppViewContainer"], [data-testid="stMain"], .main { background: transparent; }
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer, .stDeployButton, [data-testid="stDecoration"] { display: none; }
.block-container, [data-testid="stMainBlockContainer"] { max-width: 1080px; padding: 2.5rem 2rem 5rem; }
[data-testid="stMainBlockContainer"]:has(.login-wrap) { max-width: 620px; }

/* ---------- type ---------- */
h1, h2, h3, h4 {
  font-family: var(--display); font-weight: 800; color: var(--ink);
  letter-spacing: -.025em; line-height: 1.08;
}
h2 { font-size: 2.3rem; }
h3 { font-size: 1.5rem; margin-top: 2.2rem; }
[data-testid="stHeaderActionElements"] { display: none; }
.stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stMarkdownContainer"] li { color: var(--ink); line-height: 1.65; }
[data-testid="stWidgetLabel"] p { color: var(--ink); font-weight: 600; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p { color: var(--muted); font-weight: 500; }
.muted { color: var(--muted); }
hr { border: 0; border-top: var(--line); opacity: 1; }
i, em { font-family: var(--math); }

/* ---------- sidebar ---------- */
section[data-testid="stSidebar"], section[data-testid="stSidebar"] > div { background: var(--ink); }
section[data-testid="stSidebar"] { border-right: 3px solid var(--ink); }
section[data-testid="stSidebar"] hr { border-top: 2px solid rgba(255,251,239,.16); }
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: var(--cream); }
.wordmark { display: flex; align-items: center; gap: .6rem; font-family: var(--display); font-weight: 800; font-size: 1.55rem; letter-spacing: -.02em; color: var(--cream); margin: .3rem 0 1.6rem; }
.wm-badge { display: inline-flex; align-items: center; justify-content: center; width: 2.1rem; height: 2.1rem; border-radius: 10px; background: var(--yellow); color: var(--ink); font-family: var(--math); font-size: 1.05rem; transform: rotate(-6deg); }
.profile-card { display: flex; align-items: center; gap: .8rem; }
.avatar { width: 2.6rem; height: 2.6rem; flex: none; border-radius: 50%; background: var(--pink); color: var(--ink); display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: .95rem; }
.profile-name { color: var(--cream); font-weight: 700; font-size: 1rem; }
.profile-id { color: var(--soft); font-size: .74rem; word-break: break-all; }

section[data-testid="stSidebar"] .stButton > button {
  width: 100%; min-height: 2.9rem; border-radius: 12px; box-shadow: none; transform: none;
  background: rgba(255,251,239,.08); border: 2px solid rgba(255,251,239,.28);
}
section[data-testid="stSidebar"] .stButton > button > div { justify-content: flex-start; width: 100%; }
section[data-testid="stSidebar"] .stButton > button p { color: var(--cream); font-weight: 600; text-align: left; }
section[data-testid="stSidebar"] .stButton > button:hover { background: rgba(255,210,63,.16); border-color: var(--yellow); transform: none; box-shadow: none; }
section[data-testid="stSidebar"] .stButton > button[kind="primary"],
section[data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-primary"] {
  background: var(--yellow); border-color: var(--yellow); box-shadow: 4px 4px 0 var(--coral);
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] p,
section[data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-primary"] p { color: var(--ink); font-weight: 800; }

/* sidebar open/close arrows: always visible, never hover-only */
[data-testid="stSidebarCollapseButton"], [data-testid="stSidebarCollapseButton"] *,
[data-testid="stExpandSidebarButton"], [data-testid="stExpandSidebarButton"] *,
[data-testid="stSidebarCollapsedControl"], [data-testid="stSidebarCollapsedControl"] * { opacity: 1 !important; visibility: visible !important; }
[data-testid="stSidebarCollapseButton"] button, [data-testid="stSidebarCollapseButton"] span,
[data-testid="stSidebarCollapseButton"] svg { color: var(--cream); fill: var(--cream); }
[data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapsedControl"] button {
  background: var(--yellow); border: var(--line); border-radius: 12px; box-shadow: 3px 3px 0 var(--ink);
}
[data-testid="stExpandSidebarButton"] *, [data-testid="stSidebarCollapsedControl"] button * { color: var(--ink); fill: var(--ink); }

/* ---------- buttons ---------- */
.stButton > button, .stFormSubmitButton > button {
  min-height: 3.1rem; border-radius: 12px; border: var(--line);
  background: var(--cream); color: var(--ink); box-shadow: 4px 4px 0 var(--ink);
  transition: transform .12s ease, box-shadow .12s ease, background .12s ease;
}
.stButton > button p, .stFormSubmitButton > button p { color: var(--ink); font-weight: 700; font-size: 1rem; }
.stButton > button:hover, .stFormSubmitButton > button:hover { transform: translate(-2px, -2px); box-shadow: 6px 6px 0 var(--ink); border-color: var(--ink); color: var(--ink); }
.stButton > button:active, .stFormSubmitButton > button:active { transform: translate(3px, 3px); box-shadow: 1px 1px 0 var(--ink); }
.stButton > button:focus:not(:active) { border-color: var(--ink); color: var(--ink); }
.stButton > button:focus-visible { outline: 3px solid var(--coral); outline-offset: 3px; }
.stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"],
.stFormSubmitButton > button[kind="primary"] { background: var(--yellow); }
.stButton > button[kind="primary"]:hover, .stButton > button[data-testid="stBaseButton-primary"]:hover { background: #FFDE6E; }
.stButton > button:disabled { opacity: .5; box-shadow: none; }

/* ---------- inputs ---------- */
div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="textarea"] { background: var(--cream) !important; border-radius: 12px; }
div[data-baseweb="input"] { border: var(--line); box-shadow: 4px 4px 0 var(--ink); }
div[data-baseweb="base-input"] { border: 0; }
div[data-baseweb="input"]:focus-within { box-shadow: 4px 4px 0 var(--coral); }
div[data-baseweb="input"] input { color: var(--ink) !important; -webkit-text-fill-color: var(--ink); font-size: 1.1rem; font-weight: 600; padding: .8rem 1rem; }
div[data-baseweb="input"] input::placeholder { color: #7C76A8; -webkit-text-fill-color: #7C76A8; opacity: 1; font-weight: 500; }

div[data-baseweb="select"] > div { background: var(--cream); border: var(--line); border-radius: 12px; box-shadow: 4px 4px 0 var(--ink); min-height: 3rem; }
div[data-baseweb="select"] * { color: var(--ink); font-weight: 600; }
div[data-baseweb="select"] svg { fill: var(--ink); }
div[data-baseweb="popover"] { background: transparent; }
div[data-baseweb="popover"] ul, div[data-baseweb="menu"] { background: var(--cream); border: var(--line); border-radius: 12px; }
div[data-baseweb="popover"] li, div[data-baseweb="popover"] li * { color: var(--ink); font-weight: 600; background: transparent; }
div[data-baseweb="popover"] li:hover, div[data-baseweb="popover"] li[aria-selected="true"] { background: var(--yellow); }

/* practice-mode radio -> big pills */
div[role="radiogroup"] { gap: .6rem; flex-wrap: wrap; }
label[data-baseweb="radio"] { background: var(--cream); border: var(--line); border-radius: 999px; padding: .5rem 1.2rem; box-shadow: 3px 3px 0 var(--ink); margin: 0 .2rem .6rem 0; cursor: pointer; }
label[data-baseweb="radio"] > div:first-child { display: none; }
label[data-baseweb="radio"] p { color: var(--ink); font-weight: 700; margin: 0; }
label[data-baseweb="radio"]:has(input:checked) { background: var(--ink); box-shadow: 3px 3px 0 var(--coral); }
label[data-baseweb="radio"]:has(input:checked) p { color: var(--yellow); }

/* alerts, code */
div[data-testid="stAlert"] { background: var(--cream); border: var(--line); border-radius: 14px; box-shadow: 4px 4px 0 var(--ink); }
div[data-testid="stAlert"] > div, div[data-testid="stAlert"] [data-baseweb="notification"] { background: transparent !important; }
div[data-testid="stAlert"] * { color: var(--ink); }
div[data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]) { background: var(--sky); }
div[data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) { background: var(--yellow); }
div[data-testid="stAlert"]:has([data-testid="stAlertContentError"]) { background: var(--pink); }
div[data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) { background: var(--mint); }
[data-testid="stCode"], .stCodeBlock { border: var(--line); border-radius: 12px; box-shadow: 4px 4px 0 var(--ink); background: var(--cream); }
[data-testid="stCode"] pre, [data-testid="stCode"] code { background: var(--cream) !important; color: var(--ink) !important; font-size: 1.25rem; font-weight: 700; }

/* ---------- login ---------- */
.login-wrap { text-align: center; margin: 5vh 0 2rem; }
.login-logo { width: 5.4rem; height: 5.4rem; margin: 0 auto 1.6rem; border-radius: 24px; background: var(--yellow); border: 3px solid var(--ink); box-shadow: 6px 6px 0 var(--ink); transform: rotate(-6deg); display: flex; align-items: center; justify-content: center; font-family: var(--math); font-weight: 800; font-size: 2.3rem; color: var(--ink); }
.login-title { font-family: var(--display); font-weight: 800; font-size: clamp(2.2rem, 6vw, 3.2rem); letter-spacing: -.035em; line-height: 1.05; margin-bottom: .8rem; }
.login-copy { color: var(--muted); max-width: 440px; margin: 0 auto; font-weight: 500; }

/* ---------- home hero ---------- */
.hero { display: grid; grid-template-columns: 1.25fr 1fr; gap: 3rem; align-items: center; padding: .5rem 0 2.5rem; }
.hero-title { font-family: var(--display); font-weight: 800; font-size: clamp(2.6rem, 5.6vw, 4.4rem); letter-spacing: -.04em; line-height: .98; margin-bottom: 1.2rem; }
.hero-subtitle { color: var(--muted); font-size: 1.12rem; font-weight: 500; max-width: 520px; line-height: 1.6; }
.mistake-card { background: var(--cream); border: var(--line); border-radius: 20px; box-shadow: 8px 8px 0 var(--ink); padding: 1.4rem; transform: rotate(2.2deg); }
.mc-q { font-family: var(--math); font-weight: 700; font-size: 2.4rem; text-align: center; padding: .5rem 0 .9rem; white-space: nowrap; }
.mc-row { display: flex; justify-content: space-between; align-items: center; border: var(--line); border-radius: 12px; padding: .7rem 1rem; margin-top: .7rem; font-weight: 700; font-size: .92rem; }
.mc-row b { font-family: var(--math); font-weight: 700; font-size: 1.45rem; white-space: nowrap; }
.mc-row.wrong { background: var(--pink); }
.mc-row.wrong b { text-decoration: line-through; text-decoration-thickness: 3px; }
.mc-row.right { background: var(--mint); }
.mc-note { margin-top: 1rem; text-align: center; color: var(--muted); font-weight: 600; font-size: .9rem; }

.topbar { margin: 0 0 1.6rem; }
.page-tag { display: inline-block; background: var(--ink); color: var(--yellow); font-weight: 700; font-size: .85rem; padding: .35rem 1rem; border-radius: 999px; box-shadow: 3px 3px 0 var(--coral); }

/* ---------- stat tiles ---------- */
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1.1rem; margin: .5rem 0 1rem; }
.stat { border: var(--line); border-radius: 16px; box-shadow: 4px 4px 0 var(--ink); padding: 1.1rem 1.3rem 1.2rem; }
.stat:nth-child(1) { background: var(--yellow); }
.stat:nth-child(2) { background: var(--mint); }
.stat:nth-child(3) { background: var(--pink); }
.stat:nth-child(4) { background: var(--sky); }
.stat:nth-child(5) { background: var(--cream); }
.stat b { display: block; font-family: var(--display); font-weight: 800; font-size: 2.9rem; letter-spacing: -.03em; line-height: 1; margin-bottom: .35rem; }
.stat span { font-weight: 700; font-size: .9rem; }

/* ---------- steps / feature cards ---------- */
.section-title { font-family: var(--display); font-weight: 800; font-size: 1.5rem; letter-spacing: -.025em; margin: 2.4rem 0 1rem; }
.steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.2rem; margin: 0 0 2.2rem; }
.step, .feature-card { background: var(--cream); border: var(--line); border-radius: 16px; box-shadow: 4px 4px 0 var(--ink); padding: 1.4rem; }
.step:nth-child(1) { background: var(--cream); }
.step:nth-child(2) { background: var(--cream); }
.step-n, .feature-number { display: inline-flex; align-items: center; justify-content: center; background: var(--ink); color: var(--yellow); font-weight: 800; font-size: .85rem; min-width: 2.1rem; height: 2.1rem; padding: 0 .55rem; border-radius: 999px; margin-bottom: .9rem; }
.step b { display: block; font-family: var(--display); font-weight: 800; font-size: 1.35rem; letter-spacing: -.02em; margin-bottom: .3rem; }
.step p, .feature-card p { margin: 0; color: var(--muted); font-size: .95rem; font-weight: 500; }
.stApp .step p { color: var(--muted); }
.feature-card h2, .feature-card h3 { margin: .2rem 0 .4rem; }

/* ---------- question + math ---------- */
.question-box { background: var(--ink); border: var(--line); border-radius: 22px; box-shadow: 8px 8px 0 var(--coral); padding: 2.6rem 1.5rem; text-align: center; margin: 1.2rem 0 2.2rem; }
.question-label { display: inline-block; background: var(--yellow); color: var(--ink); font-weight: 700; font-size: .8rem; padding: .25rem .9rem; border-radius: 999px; margin-bottom: 1.2rem; }
.question-text { font-family: var(--math); font-weight: 700; font-size: clamp(2.6rem, 8vw, 4.6rem); color: var(--cream); letter-spacing: .01em; line-height: 1.1; }
.question-text i { color: var(--yellow); }
.mini { color: var(--muted); font-weight: 700; font-size: .88rem; margin-bottom: .5rem; }
.math-chip { display: inline-block; font-family: var(--math); font-weight: 700; font-size: 2rem; background: var(--cream); border: var(--line); border-radius: 14px; box-shadow: 4px 4px 0 var(--ink); padding: .7rem 1.3rem; margin-bottom: 1.2rem; white-space: nowrap; }
div[data-testid="stColumn"]:first-child .math-chip, div[data-testid="column"]:first-child .math-chip { background: var(--pink); }
div[data-testid="stColumn"]:nth-child(2) .math-chip, div[data-testid="column"]:nth-child(2) .math-chip { background: var(--mint); }
.retest-q { display: flex; align-items: center; gap: 1rem; margin: 2rem 0 .6rem; font-family: var(--math); font-weight: 700; font-size: 2rem; white-space: nowrap; }
.retest-q span { display: inline-flex; align-items: center; justify-content: center; width: 2.3rem; height: 2.3rem; border-radius: 50%; background: var(--yellow); border: var(--line); font-family: var(--body); font-weight: 800; font-size: .95rem; }

/* ---------- feedback ---------- */
.wrong-banner { background: var(--pink); border: var(--line); border-radius: 16px; box-shadow: 5px 5px 0 var(--ink); padding: 1.2rem 1.6rem; margin: 1rem 0 1.8rem; }
.wrong-title { font-family: var(--display); font-weight: 800; font-size: 2.1rem; letter-spacing: -.03em; color: var(--ink); }
.wrong-subtitle { color: var(--ink); font-weight: 500; margin-top: .15rem; }
.diagnosis-card { background: var(--cream); border: var(--line); border-radius: 18px; box-shadow: 6px 6px 0 var(--ink); padding: 1.8rem; margin: 1.6rem 0 1.6rem; }
.eyebrow { display: inline-block; background: var(--ink); color: var(--yellow); font-weight: 700; font-size: .8rem; padding: .25rem .85rem; border-radius: 999px; margin-bottom: .6rem; }
.diagnosis-title { font-family: var(--display); font-weight: 800; font-size: 1.9rem; letter-spacing: -.03em; line-height: 1.1; margin: .2rem 0 .8rem; }
.diagnosis-text { color: #2C2850; line-height: 1.7; font-weight: 500; }
.conf { font-weight: 700; font-size: .9rem; margin: 0 0 2rem; }
.bar { height: 16px; border: var(--line); border-radius: 999px; background: var(--cream); margin-top: .5rem; overflow: hidden; }
.bar i { display: block; height: 100%; background: var(--coral); }

.result-card { background: var(--cream); border: var(--line); border-radius: 22px; box-shadow: 7px 7px 0 var(--ink); padding: 2.8rem 2rem; text-align: center; margin: 2rem 0; }
.result-card.success-card { background: var(--mint); }
.result-card.retry-card { background: var(--yellow); }
.result-card h2 { font-size: 2.7rem; margin: .4rem 0 .6rem; }
.stApp .result-card p { color: var(--ink); font-weight: 500; margin: 0; }
.success-icon { width: 4rem; height: 4rem; border-radius: 50%; background: var(--ink); color: var(--mint); display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; font-size: 1.7rem; font-weight: 800; }
.eyebrow.success-text { color: var(--mint); }

.progress-row { display: flex; align-items: center; justify-content: space-between; gap: 1rem; background: var(--cream); border: var(--line); border-radius: 14px; box-shadow: 4px 4px 0 var(--ink); padding: 1rem 1.3rem; margin: 1rem 0; font-weight: 700; }
.progress-percent { font-family: var(--display); font-weight: 800; font-size: 1.9rem; letter-spacing: -.03em; text-align: right; line-height: 1; }
.progress-percent small { display: block; font-family: var(--body); font-size: .75rem; font-weight: 700; color: var(--muted); letter-spacing: 0; margin-top: .25rem; }

@media (max-width: 760px) {
  .block-container, [data-testid="stMainBlockContainer"] { padding: 1.5rem 1rem 4rem; }
  .hero { grid-template-columns: 1fr; gap: 2rem; }
  .mistake-card { transform: none; }
  .steps { grid-template-columns: 1fr; }
  .result-card h2 { font-size: 2.1rem; }
}
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
"""


PAGE_TAGS = {
    "practice": "Practice",
    "answer": "Your question",
    "correct": "Result",
    "diagnosis": "Diagnosis",
    "retest": "Retest",
    "retry": "Retest",
    "resolved": "Result",
    "progress": "Progress",
}


def _html(markup):
    """Collapse to one line so Markdown never mistakes indented HTML for code."""
    st.markdown(re.sub(r"\s*\n\s*", " ", markup.strip()), unsafe_allow_html=True)


def label_name(label):
    return DISPLAY_LABELS.get(label, label)


def math_html(expr):
    s = html.escape(str(expr))
    s = re.sub(r"\^(\d+)", r"<sup>\1</sup>", s)
    s = re.sub(r"(?<![A-Za-z])x(?![A-Za-z])", "<i>x</i>", s)
    s = re.sub(r"\s*([+\-])\s*", r" \1 ", s).strip()
    return s.replace("-", "\u2212")


def apply_theme():
    st.markdown("<style>" + CSS + "</style>", unsafe_allow_html=True)


def render_login():
    _html(
        """
        <div class="login-wrap">
            <div class="login-logo">x&sup2;</div>
            <div class="login-title">Welcome to Re:Learn</div>
            <p class="login-copy">An algebra tutor that finds out why an answer went wrong,
            not just that it was wrong.</p>
        </div>
        """
    )
    st.markdown("### Create your learner profile")


def render_sidebar_profile(username, initials, user_id):
    _html(
        f"""
        <div class="wordmark"><span class="wm-badge">x&sup2;</span>Re:Learn</div>
        <div class="profile-card">
            <div class="avatar">{html.escape(str(initials))}</div>
            <div>
                <div class="profile-name">{html.escape(str(username))}</div>
                <div class="profile-id">{html.escape(str(user_id))}</div>
            </div>
        </div>
        """
    )


def render_header(username, initials):
    page = st.session_state.get("page", "home")

    if page != "home":
        tag = PAGE_TAGS.get(page, "Re:Learn")
        _html(f'<div class="topbar"><span class="page-tag">{tag}</span></div>')
        return

    _html(
        f"""
        <div class="hero">
            <div>
                <div class="hero-title">Learn from the mistake.</div>
                <div class="hero-subtitle">
                    Welcome back, {html.escape(str(username))}. Re:Learn finds the misconception
                    behind a wrong answer, explains it, and gives you practice that targets it.
                </div>
            </div>
            <div class="mistake-card" aria-hidden="true">
                <div class="mc-q">2(<i>x</i> + 3)</div>
                <div class="mc-row wrong"><span>You wrote</span><b>2<i>x</i> + 3</b></div>
                <div class="mc-row right"><span>Should be</span><b>2<i>x</i> + 6</b></div>
                <div class="mc-note">Only distributing to the first term</div>
            </div>
        </div>
        """
    )


def render_steps():
    _html(
        """
        <div class="section-title">How it works</div>
        <div class="steps">
            <div class="step"><span class="step-n">1</span><b>Practice</b>
                <p>Pick a question, generate one, or write your own.</p></div>
            <div class="step"><span class="step-n">2</span><b>Understand</b>
                <p>See the exact misconception behind a wrong answer.</p></div>
            <div class="step"><span class="step-n">3</span><b>Improve</b>
                <p>Prove it with three targeted retest questions.</p></div>
        </div>
        """
    )


def render_dashboard(stats, detailed=False):
    cells = [
        ("Attempts", stats.get("total", 0)),
        ("Accuracy", f"{stats.get('accuracy', 0)}%"),
        ("Correct", stats.get("correct", 0)),
        ("Resolved", stats.get("resolved", 0)),
    ]
    if detailed:
        cells.append(("Current streak", stats.get("streak", 0)))
    tiles = "".join(f'<div class="stat"><b>{v}</b><span>{k}</span></div>' for k, v in cells)
    _html(f'<div class="stats">{tiles}</div>')


def render_diagnosis(label, confidence, lesson):
    try:
        c = max(0, min(int(confidence), 100))
    except (TypeError, ValueError):
        c = 0
    _html(
        f"""
        <div class="diagnosis-card">
            <div class="eyebrow">What went wrong</div>
            <div class="diagnosis-title">{label_name(label)}</div>
            <div class="diagnosis-text">{lesson}</div>
        </div>
        <div class="conf">Model confidence: {c}%
            <div class="bar"><i style="width:{c}%"></i></div>
        </div>
        """
    )
