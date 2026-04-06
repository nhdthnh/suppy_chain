"""
app.py — Entry point cho ứng dụng Supply Chain.

Flow:
  1. Config page (title, icon, layout)
  2. Inject global CSS
  3. Check authentication (cookie auto-login → login page)
  4. Render sidebar → route tới page tương ứng
"""

import streamlit as st
from utils.styles import GLOBAL_CSS, HIDE_SIDEBAR_CSS
from components import sidebar
from pages import (
    search_order,
    data_browser,
    import_excel,
    export_excel,
    view_templates,
    about,
)
import login


# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Cung Ứng · OQR",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# AUTHENTICATION
# ─────────────────────────────────────────────────────────────

# Thử auto-login từ URL params (survive F5)
if not login.is_authenticated():
    if login.auto_login():
        st.rerun()

# Nếu chưa đăng nhập → hiện login page, ẩn sidebar
if not login.is_authenticated():
    st.markdown(HIDE_SIDEBAR_CSS, unsafe_allow_html=True)
    login.show_login_page()
    st.stop()


# ─────────────────────────────────────────────────────────────
# ROUTING (sau khi đã đăng nhập)
# ─────────────────────────────────────────────────────────────

PAGES = {
    "search_order":   search_order,
    "data_browser":   data_browser,
    "import_excel":   import_excel,
    "export_excel":   export_excel,
    "view_templates": view_templates,
    "about":          about,
}

page_key = sidebar.render()
PAGES[page_key].render()
