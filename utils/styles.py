"""
utils/styles.py — Modern Premium UI Design System.

Design Tokens:
- Typography: Inter (UI/Text), JetBrains Mono (Codes)
- Color Palette:
    - Primary: #10b981 (Emerald-500)
    - Text Main: #0f172a (Slate-900)
    - Surface: #f8fafc (Slate-50)
- Accents: Low-alpha shadows, subtle border glows
"""

# ─────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ═══════════════════════════════════════════════════════════
   1. BASE TYPOGRAPHY & SMOOTHING
   ═══════════════════════════════════════════════════════════ */

:root {
    --primary: #10b981;
    --primary-hover: #059669;
    --text-main: #0f172a;
    --text-muted: #64748b;
    --bg-surface: #f8fafc;
    --border-subtle: rgba(226, 232, 240, 0.8);
}

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* ═══════════════════════════════════════════════════════════
   2. MAIN CONTENT LAYOUT
   ═══════════════════════════════════════════════════════════ */

.main .block-container {
    padding: 3rem 4rem !important;
    max-width: 1300px !important;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}

/* ═══════════════════════════════════════════════════════════
   3. SIDEBAR UPGRADE
   ═══════════════════════════════════════════════════════════ */

section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid var(--border-subtle) !important;
    box-shadow: 2px 0 10px rgba(15, 23, 42, 0.02) !important;
}

section[data-testid="stSidebar"] > div:first-child {
    padding: 1.5rem 1.2rem !important;
}

/* Radio nav menu as Pills */
section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 8px !important;
}

section[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] {
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    padding: 0.65rem 1rem !important;
    border-radius: 12px !important;
    color: #475569 !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    border: 1px solid transparent !important;
}

/* Hover state */
section[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:hover {
    background: #f1f5f9 !important;
    color: var(--text-main) !important;
}

/* Active state with pill effect and left accent */
section[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:has(input:checked) {
    background: #f0fdf4 !important;
    border: 1px solid rgba(16, 185, 129, 0.2) !important;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.08) !important;
}

section[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:has(input:checked) p,
section[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:has(input:checked) span {
    color: #065f46 !important;
    font-weight: 600 !important;
}

/* ═══════════════════════════════════════════════════════════
   4. PREMIUM PAGE HEADER
   ═══════════════════════════════════════════════════════════ */

.page-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--primary);
    background: #ecfdf5;
    padding: 4px 10px;
    border-radius: 6px;
    display: inline-block;
    margin-bottom: 0.75rem;
}

.page-title {
    font-size: 2.25rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: var(--text-main);
    margin-bottom: 2rem;
}

/* ═══════════════════════════════════════════════════════════
   5. MODERN METRIC CARD
   ═══════════════════════════════════════════════════════════ */

.metric-card {
    background: #ffffff;
    border: 1px solid var(--border-subtle);
    padding: 1.5rem;
    border-radius: 16px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 
                0 2px 4px -1px rgba(0, 0, 0, 0.03);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    border-left: 4px solid var(--primary);
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.08);
}

.metric-label {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
}

.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-main);
}

/* ═══════════════════════════════════════════════════════════
   6. TABLES & INPUTS
   ═══════════════════════════════════════════════════════════ */

/* Table refinements */
div[data-testid="stDataFrame"] table,
div[data-testid="stDataEditor"] table {
    border-radius: 8px !important;
    overflow: hidden !important;
}

/* Modern Inputs */
.stTextInput input, .stSelectbox [role="combobox"] {
    border-radius: 10px !important;
    border: 1px solid #e2e8f0 !important;
    padding: 0.75rem !important;
}

/* ═══════════════════════════════════════════════════════════
   7. HIDE DEFAULTS
   ═══════════════════════════════════════════════════════════ */

[data-testid="stSidebarNav"], 
[data-testid="stSidebarNavItems"], 
[data-testid="stSidebarNavLink"],
.stDeployButton, #MainMenu, footer {
    display: none !important;
}

[data-testid="stCollapsedControl"] {
    display: flex !important;
}

</style>
"""

HIDE_SIDEBAR_CSS = """
<style>
    [data-testid="stSidebar"], [data-testid="stCollapsedControl"] { display: none !important; }
    .main .block-container { max-width: 800px !important; padding-top: 6rem !important; }
</style>
"""

# ─────────────────────────────────────────────────────────────
# HTML HELPERS
# ─────────────────────────────────────────────────────────────

def page_header(tag: str, title: str) -> str:
    """Enhanced page header."""
    return f'''
    <div class="page-tag">{tag}</div>
    <div class="page-title">{title}</div>
    '''

def metric_card(label: str, value: str) -> str:
    """Premium Metric Card."""
    return f'''
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    '''

def section_label(icon: str, text: str) -> str:
    """Sleek section label."""
    return f'''
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:1rem; 
                font-size:0.9rem; font-weight:700; color:#334155; text-transform:uppercase; letter-spacing:0.02em;">
        <span>{icon}</span>
        <span>{text}</span>
    </div>
    '''

def divider(margin: str = "2rem 0") -> str:
    """Refined divider."""
    return f'<hr style="border:none; border-top:1px solid #f1f5f9; margin:{margin};" />'

def badge(text: str, is_active: bool = True) -> str:
    """Modern Badge."""
    color = "#10b981" if is_active else "#94a3b8"
    bg = "#ecfdf5" if is_active else "#f1f5f9"
    return f'''
    <span style="font-size:0.75rem; font-weight:600; color:{color}; background:{bg}; 
                 padding:4px 12px; border-radius:100px; border:1px solid rgba(0,0,0,0.02);">
        {text}
    </span>
    '''
