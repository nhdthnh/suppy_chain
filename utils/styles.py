"""utils/styles.py — CSS toàn cục + HTML helpers."""

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0d0d0d !important;
    border-right: 1px solid #1c1c1c;
}
section[data-testid="stSidebar"] > div { padding-top: 1.5rem; }
section[data-testid="stSidebar"] * { color: #c8c8c8 !important; }
section[data-testid="stSidebar"] hr { border-color: #262626 !important; }

/* Nav radio buttons */
section[data-testid="stSidebar"] .stRadio > div {
    gap: 0 !important;
}
section[data-testid="stSidebar"] .stRadio label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.06em;
    padding: 0.55rem 0.8rem !important;
    border-radius: 0 !important;
    display: block;
    width: 100%;
    transition: background 0.15s;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    background: #1a1a1a !important;
}
/* hide the radio dot */
section[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] > div:first-child {
    display: none !important;
}

/* ── Page header ── */
.page-tag {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.2em;
    color: #aaa;
    text-transform: uppercase;
    margin-bottom: 0.1rem;
}
.page-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.5rem;
    font-weight: 600;
    color: #111;
    border-bottom: 2px solid #111;
    padding-bottom: 0.5rem;
    margin-bottom: 1.6rem;
}

/* ── Section label ── */
.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.14em;
    color: #999;
    text-transform: uppercase;
    margin-bottom: 0.6rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

/* ── Metric card ── */
.metric-card {
    border: 1px solid #e4e4e4;
    padding: 0.85rem 1.1rem;
    background: #fafafa;
}
.metric-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.16em;
    color: #aaa;
    text-transform: uppercase;
}
.metric-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.65rem;
    font-weight: 600;
    color: #111;
    line-height: 1.2;
}

/* ── Suggestion buttons ── */
div[data-testid="stButton"] > button[kind="secondary"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.78rem !important;
    text-align: left !important;
    border-radius: 0 !important;
    border: 1px solid #e8e8e8 !important;
    background: #fff !important;
    color: #222 !important;
    padding: 0.45rem 0.9rem !important;
    margin-bottom: 2px !important;
    transition: background 0.1s !important;
    justify-content: flex-start !important;
}
div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: #f4f4f4 !important;
    border-color: #ccc !important;
}

/* ── Primary buttons ── */
.stButton > button[kind="primary"],
.stButton > button {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.06em;
    border-radius: 0 !important;
    border: 1px solid #111 !important;
    background: #111 !important;
    color: #fff !important;
}
.stButton > button:hover { background: #333 !important; }

.stDownloadButton > button {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.06em;
    border-radius: 0 !important;
    border: 1px solid #111 !important;
    background: #fff !important;
    color: #111 !important;
}
.stDownloadButton > button:hover { background: #f0f0f0 !important; }

/* ── Inputs ── */
.stTextInput > div > div > input {
    border-radius: 0 !important;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    border: 1px solid #d0d0d0 !important;
}
.stTextInput > div > div > input:focus {
    border-color: #111 !important;
    box-shadow: none !important;
}
.stNumberInput > div > div > input {
    border-radius: 0 !important;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
}
.stMultiSelect > div > div {
    border-radius: 0 !important;
    font-size: 0.82rem;
}
.stSelectbox > div > div {
    border-radius: 0 !important;
    font-size: 0.82rem;
}

/* ── Table ── */
div[data-testid="stDataFrame"] { border: 1px solid #e4e4e4; }

/* ── Divider ── */
.sc-divider {
    border: none;
    border-top: 1px solid #e8e8e8;
    margin: 1.2rem 0;
}

/* ── Hide Default Multipage Nav ── */
[data-testid="stSidebarNavLink"], [data-testid="stSidebarNav"] {
    display: none !important;
}
</style>
"""


# ── HTML helpers ──────────────────────────────────────────────

def page_header(tag: str, title: str) -> str:
    return (
        f'<div class="page-tag">{tag}</div>'
        f'<div class="page-title">{title}</div>'
    )


def section_label(icon: str, text: str) -> str:
    return f'<div class="section-label">{icon} {text}</div>'


def metric_card(label: str, value: str) -> str:
    return (
        f'<div class="metric-card">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>'
        f'</div>'
    )


def mono(text: str, size: str = "0.72rem", color: str = "#888") -> str:
    return (
        f'<span style="font-family:\'IBM Plex Mono\',monospace;'
        f'font-size:{size};color:{color};">{text}</span>'
    )


def divider(height: str = "1px", color: str = "#e8e8e8", margin: str = "1rem 0") -> str:
    return f'<hr class="sc-divider" style="height:{height};border-top:1px solid {color};margin:{margin};" />'
