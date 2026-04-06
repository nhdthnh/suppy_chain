"""
utils/styles.py — Design System cho Supply Chain App.

Design Tokens:
  · Font UI   : Inter (400 / 500 / 600 / 700 / 800)
  · Font Mono : JetBrains Mono (400 / 500)
  · Primary   : #10b981  (Emerald-500)
  · Text Main : #0f172a  (Slate-900)
  · Surface   : #f8fafc  (Slate-50)
  · Border    : rgba(226, 232, 240, 0.8)
"""

# ─────────────────────────────────────────────────────────────
# GLOBAL CSS — Inject vào app.py một lần duy nhất
# ─────────────────────────────────────────────────────────────

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ══════════════════════════════════════════════════════════
   BASE
   ══════════════════════════════════════════════════════════ */
:root {
    --primary       : #10b981;
    --primary-hover : #059669;
    --primary-light : #ecfdf5;
    --primary-dark  : #065f46;
    --text-main     : #0f172a;
    --text-sub      : #334155;
    --text-muted    : #64748b;
    --bg-surface    : #f8fafc;
    --border        : rgba(226, 232, 240, 0.8);
    --shadow-sm     : 0 1px 3px rgba(15,23,42,.06), 0 1px 2px rgba(15,23,42,.04);
    --shadow-md     : 0 4px 6px -1px rgba(15,23,42,.07), 0 2px 4px -1px rgba(15,23,42,.04);
    --shadow-lg     : 0 10px 15px -3px rgba(15,23,42,.08), 0 4px 6px -2px rgba(15,23,42,.04);
    --radius-sm     : 8px;
    --radius-md     : 12px;
    --radius-lg     : 16px;
    --radius-xl     : 20px;
}

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* ══════════════════════════════════════════════════════════
   MAIN LAYOUT
   ══════════════════════════════════════════════════════════ */
.main .block-container {
    padding: 2.5rem 3.5rem !important;
    max-width: 1320px !important;
}

header[data-testid="stHeader"] { background: transparent !important; }

/* ══════════════════════════════════════════════════════════
   SIDEBAR
   ══════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid var(--border) !important;
    box-shadow: 2px 0 12px rgba(15,23,42,.03) !important;
}
section[data-testid="stSidebar"] > div:first-child {
    padding: 1.5rem 1.25rem !important;
}

/* Nav Pills */
section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 4px !important;
    display: flex !important;
    flex-direction: column !important;
}
section[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] {
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    padding: 0.6rem 0.9rem !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-muted) !important;
    transition: all .18s ease !important;
    border: 1px solid transparent !important;
    cursor: pointer !important;
}
section[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:hover {
    background: #f1f5f9 !important;
    color: var(--text-sub) !important;
}
section[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:has(input:checked) {
    background: var(--primary-light) !important;
    border-color: rgba(16,185,129,.25) !important;
    box-shadow: 0 2px 8px rgba(16,185,129,.1) !important;
}
section[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:has(input:checked) p,
section[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:has(input:checked) span {
    color: var(--primary-dark) !important;
    font-weight: 600 !important;
}

/* Radio dot — ẩn */
section[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] > div:first-child:not(:last-child) {
    display: none !important;
}

/* ══════════════════════════════════════════════════════════
   PAGE HEADER
   ══════════════════════════════════════════════════════════ */
.page-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    font-weight: 500;
    color: var(--primary);
    background: var(--primary-light);
    padding: 3px 10px;
    border-radius: 6px;
    display: inline-block;
    margin-bottom: 0.6rem;
    letter-spacing: .03em;
}
.page-title {
    font-size: 2.1rem;
    font-weight: 800;
    letter-spacing: -0.025em;
    color: var(--text-main);
    margin-bottom: 1.75rem;
    line-height: 1.15;
}

/* ══════════════════════════════════════════════════════════
   METRIC CARD
   ══════════════════════════════════════════════════════════ */
.metric-card {
    background: #ffffff;
    border: 1px solid var(--border);
    padding: 1.35rem 1.5rem;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
    border-left: 3px solid var(--primary);
    transition: transform .2s ease, box-shadow .2s ease;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}
.metric-label {
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: .07em;
    margin-bottom: .4rem;
}
.metric-value {
    font-size: 1.85rem;
    font-weight: 700;
    color: var(--text-main);
    line-height: 1.1;
}

/* ══════════════════════════════════════════════════════════
   FORM INPUTS
   ══════════════════════════════════════════════════════════ */
.stTextInput input,
.stTextArea textarea,
.stSelectbox [role="combobox"] {
    border-radius: var(--radius-sm) !important;
    border: 1px solid #e2e8f0 !important;
    font-size: 0.9rem !important;
    transition: border-color .15s ease, box-shadow .15s ease !important;
}
.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(16,185,129,.12) !important;
}

/* ══════════════════════════════════════════════════════════
   BUTTONS
   ══════════════════════════════════════════════════════════ */
.stButton button[kind="primary"] {
    background: var(--primary) !important;
    border-color: var(--primary) !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    transition: background .15s ease, transform .1s ease !important;
}
.stButton button[kind="primary"]:hover {
    background: var(--primary-hover) !important;
    transform: translateY(-1px) !important;
}
.stButton button[kind="secondary"] {
    border-radius: var(--radius-sm) !important;
}

/* ══════════════════════════════════════════════════════════
   DATAFRAME / TABLE
   ══════════════════════════════════════════════════════════ */
div[data-testid="stDataFrame"] table,
div[data-testid="stDataEditor"] table {
    border-radius: var(--radius-sm) !important;
    overflow: hidden !important;
    font-size: 0.875rem !important;
}

/* ══════════════════════════════════════════════════════════
   HIDE STREAMLIT DEFAULTS
   ══════════════════════════════════════════════════════════ */
[data-testid="stSidebarNav"],
[data-testid="stSidebarNavItems"],
[data-testid="stSidebarNavLink"],
.stDeployButton, #MainMenu, footer {
    display: none !important;
}
[data-testid="stCollapsedControl"] { display: flex !important; }

/* ══════════════════════════════════════════════════════════
   LOGIN PAGE
   ══════════════════════════════════════════════════════════ */
.login-logo-box {
    background: var(--primary);
    color: #fff;
    width: 52px; height: 52px;
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.6rem;
    margin: 0 auto 1.25rem auto;
    box-shadow: 0 8px 24px rgba(16,185,129,.35);
}
.login-title {
    font-size: 1.6rem;
    font-weight: 800;
    color: var(--text-main);
    text-align: center;
    letter-spacing: -.02em;
    margin-bottom: 4px;
}
.login-subtitle {
    font-size: 0.85rem;
    color: var(--text-muted);
    text-align: center;
    margin-bottom: 1.75rem;
}
.login-footer {
    font-size: 0.72rem;
    color: #94a3b8;
    text-align: center;
    margin-top: 1.5rem;
}

</style>
"""

# ─────────────────────────────────────────────────────────────
# HIDE SIDEBAR CSS — dùng cho trang login
# ─────────────────────────────────────────────────────────────

HIDE_SIDEBAR_CSS = """
<style>
    [data-testid="stSidebar"],
    [data-testid="stCollapsedControl"] { display: none !important; }
    .main .block-container {
        max-width: 460px !important;
        padding: 5rem 2rem 2rem !important;
    }
</style>
"""


# ─────────────────────────────────────────────────────────────
# HTML HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────

def page_header(tag: str, title: str) -> str:
    """Render page tag + tiêu đề lớn."""
    return (
        f'<div class="page-tag">{tag}</div>'
        f'<div class="page-title">{title}</div>'
    )


def metric_card(label: str, value: str) -> str:
    """Metric card với border-left emerald."""
    return (
        f'<div class="metric-card">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>'
        f'</div>'
    )


def section_label(icon: str, text: str) -> str:
    """Section separator với icon + label chữ hoa."""
    return (
        '<div style="display:flex;align-items:center;gap:8px;'
        'margin-bottom:.85rem;font-size:.8rem;font-weight:700;'
        'color:#334155;text-transform:uppercase;letter-spacing:.06em;">'
        f'<span>{icon}</span><span>{text}</span></div>'
    )


def divider(
    height: str = "1px",
    color: str = "#f1f5f9",
    margin: str = "1.75rem 0",
) -> str:
    """Đường kẻ ngang tinh tế."""
    return (
        f'<hr style="border:none;border-top:{height} solid {color};'
        f'margin:{margin};" />'
    )


def badge(text: str, is_active: bool = True) -> str:
    """Pill badge — xanh khi active, xám khi không."""
    color = "#10b981" if is_active else "#94a3b8"
    bg    = "#ecfdf5" if is_active else "#f1f5f9"
    return (
        f'<span style="font-size:.72rem;font-weight:700;color:{color};'
        f'background:{bg};padding:3px 11px;border-radius:100px;">'
        f'{text}</span>'
    )


def mono(text: str, size: str = "0.88rem", color: str = "#64748b") -> str:
    """Inline monospace text với JetBrains Mono."""
    return (
        f'<span style="font-family:\'JetBrains Mono\',monospace;'
        f'font-size:{size};color:{color};">{text}</span>'
    )
