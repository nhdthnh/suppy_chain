"""
components/sidebar.py — Sidebar navigation component.

Features:
  · Logo với typography premium
  · Badge trạng thái kết nối DB real-time
  · Radio nav tùy chỉnh style cho routing
  · User profile + nút đăng xuất
"""

import streamlit as st
from datetime import datetime
from db.connection import connection_status


# ─────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────

NAV_ITEMS: list[tuple[str, str]] = [
    ("📋  PRE-ORDER",       "search_order"),
    ("🗄   DỮ LIỆU BẢNG",   "data_browser"),
    ("⬆   IMPORT EXCEL",   "import_excel"),
    ("⬇   EXPORT EXCEL",   "export_excel"),
    ("📄   XEM TEMPLATES",  "view_templates"),
    ("ℹ️   ABOUT",         "about"),
]

_NAV_KEY     = "_sidebar_nav_idx"
APP_VERSION  = "v2.5"


# ─────────────────────────────────────────────────────────────
# PRIVATE UI PIECES
# ─────────────────────────────────────────────────────────────

def _logo() -> None:
    """Render logo: tên app + tên công ty."""
    st.markdown(
        f'''
        <div style="margin-bottom:24px;">
            <div style="font-family:'Inter',sans-serif;font-weight:800;font-size:1.5rem;
                        color:#0f172a;display:flex;align-items:center;gap:8px;">
                <span style="background:#10b981;color:#fff;padding:4px 8px;
                             border-radius:8px;font-size:1.2rem;">🛒</span>
                CUNG ỨNG
            </div>
            <div style="font-family:'Inter',sans-serif;font-size:0.72rem;font-weight:600;
                        color:#64748b;letter-spacing:0.1em;text-transform:uppercase;
                        margin-top:4px;">
                OQR Co.Ltd · {APP_VERSION}
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )


def _connection_badge() -> None:
    """Render DB connection status badge."""
    is_ok, _ = connection_status()
    label  = "CONNECTED"     if is_ok else "DISCONNECTED"
    color  = "#059669"        if is_ok else "#dc2626"
    bg     = "#ecfdf5"        if is_ok else "#fef2f2"

    st.markdown(
        f'''
        <div style="font-family:'Inter',sans-serif;font-size:0.7rem;font-weight:700;
                    color:{color};background:{bg};border:1px solid rgba(0,0,0,0.04);
                    padding:4px 12px;border-radius:100px;display:inline-flex;
                    align-items:center;gap:6px;">
            <span>●</span> DB {label}
        </div>
        ''',
        unsafe_allow_html=True,
    )


def _user_info() -> None:
    """Render thông tin tài khoản hiện tại."""
    username = st.session_state.get("username", "User")
    st.markdown(
        f'''
        <div style="margin-bottom:12px;">
            <div style="font-family:'Inter',sans-serif;font-size:0.75rem;
                        font-weight:500;color:#64748b;">Tài khoản</div>
            <div style="font-family:'Inter',sans-serif;font-size:0.95rem;
                        font-weight:700;color:#0f172a;">{username}</div>
        </div>
        ''',
        unsafe_allow_html=True,
    )


def _version_stamp() -> None:
    """Render dấu phiên bản + thời gian."""
    now = datetime.now().strftime("%d/%m %H:%M")
    st.markdown(
        f'''
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;
                    color:#94a3b8;margin-top:16px;border-top:1px solid #f1f5f9;
                    padding-top:10px;">
            {APP_VERSION} ∙ {now}
        </div>
        ''',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────
# PUBLIC RENDERER
# ─────────────────────────────────────────────────────────────

def render() -> str:
    """Render sidebar và trả về page key đang active."""
    labels = [lbl for lbl, _ in NAV_ITEMS]
    keys   = [key for _, key in NAV_ITEMS]

    if _NAV_KEY not in st.session_state:
        st.session_state[_NAV_KEY] = 0

    with st.sidebar:
        _logo()
        _connection_badge()

        st.markdown('<div style="margin-top:24px;"></div>', unsafe_allow_html=True)

        selected = st.radio(
            "Navigation",
            labels,
            index=st.session_state[_NAV_KEY],
            label_visibility="collapsed",
            key="_sidebar_radio",
        )

        new_idx = labels.index(selected)
        st.session_state[_NAV_KEY] = new_idx

        st.markdown('<div style="margin-top:2.5rem;"></div>', unsafe_allow_html=True)

        _user_info()

        if st.button(
            "🚪 Đăng xuất",
            use_container_width=True,
            type="secondary",
            key="_logout_btn",
        ):
            st.session_state["authenticated"] = False
            st.session_state["username"] = None
            st.query_params.clear()
            st.rerun()

        _version_stamp()

    return keys[new_idx]
