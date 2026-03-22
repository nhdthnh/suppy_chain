"""
components/sidebar.py
Sidebar navigation độc lập.
render() → trả về page key để app.py route.
"""

import streamlit as st
from datetime import datetime
from db.connection import connection_status

NAV_ITEMS: list[tuple[str, str]] = [
    ("📋  PRE-ORDER",      "search_order"),
    ("🗄   DỮ LIỆU BẢNG",  "data_browser"),
    ("⬆   IMPORT EXCEL",  "import_excel"),
    ("⬇   EXPORT EXCEL",  "export_excel"),
    ("📄   XEM TEMPLATES", "view_templates"),
]


def _logo() -> None:
    st.markdown(
        '<div style="font-family:\'IBM Plex Mono\',monospace;font-weight:600;'
        'font-size:0.95rem;letter-spacing:0.08em;color:#e0e0e0;padding:0 0.2rem 0.2rem;">'
        '📦 SUPPLY CHAIN</div>',
        unsafe_allow_html=True,
    )


def _connection_badge() -> None:
    is_ok, label = connection_status()
    color = "#22c55e" if is_ok else "#ef4444"
    st.markdown(
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.65rem;'
        f'letter-spacing:0.12em;color:{color};padding:0 0.2rem;">● {label}</div>',
        unsafe_allow_html=True,
    )


def _footer() -> None:
    st.markdown(
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.55rem;'
        f'color:#3a3a3a;padding:0.2rem;">'
        f'supply_chain · {datetime.now().strftime("%d/%m/%Y %H:%M")}</div>',
        unsafe_allow_html=True,
    )


def render() -> str:
    """Render sidebar, trả về key của page được chọn."""
    labels = [lbl for lbl, _ in NAV_ITEMS]
    keys   = [key for _, key in NAV_ITEMS]

    with st.sidebar:
        _logo()
        st.markdown('<hr style="border-color:#1e1e1e;margin:0.7rem 0;">', unsafe_allow_html=True)
        _connection_badge()
        st.markdown('<hr style="border-color:#1e1e1e;margin:0.7rem 0;">', unsafe_allow_html=True)

        selected = st.radio("nav", labels, index=0, label_visibility="collapsed")

        st.markdown('<hr style="border-color:#1e1e1e;margin:0.7rem 0;">', unsafe_allow_html=True)
        _footer()

    return keys[labels.index(selected)]