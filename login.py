"""
login.py — Authentication module.

Chức năng:
  · show_login_page()  — Render form đăng nhập
  · is_authenticated() — Kiểm tra trạng thái đăng nhập
  · auto_login()       — Tự động login từ URL params (survive F5)
  · logout()           — Xóa session + URL params

Lưu trữ user: log/log.xlsx  →  sheet "user"
Password: SHA-256
"""

import hashlib
from pathlib import Path

import pandas as pd
import streamlit as st

from components.sidebar import APP_VERSION

LOG_FILE = Path(__file__).parent / "log" / "log.xlsx"


# ─────────────────────────────────────────────────────────────
# INTERNAL HELPERS
# ─────────────────────────────────────────────────────────────

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _verify(username: str, password: str) -> bool:
    """Xác thực credentials với log.xlsx."""
    if not LOG_FILE.exists():
        st.error(f"Không tìm thấy file xác thực: {LOG_FILE}")
        return False
    try:
        df = pd.read_excel(LOG_FILE, sheet_name="user")
        row = df[df["username"] == username]
        if row.empty:
            return False
        return row.iloc[0]["password"] == _hash(password)
    except Exception as e:
        st.error(f"Lỗi đọc file đăng nhập: {e}")
        return False


# ─────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────

def is_authenticated() -> bool:
    return st.session_state.get("authenticated", False)


def auto_login() -> bool:
    """Tự động phục hồi phiên từ URL params (sau F5)."""
    if is_authenticated():
        return False
    params = st.query_params
    if params.get("logged_in") == "true" and params.get("user"):
        st.session_state["authenticated"] = True
        st.session_state["username"] = params["user"]
        return True
    return False


def logout() -> None:
    """Đăng xuất và xóa phiên."""
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.query_params.clear()
    st.rerun()


def show_login_page() -> None:
    """Render trang đăng nhập."""
    st.markdown(
        '''
        <div class="login-logo-box">🛒</div>
        <div class="login-title">Supply Chain</div>
        <div class="login-subtitle">OQR Co. Ltd — Hệ thống quản lý chuỗi cung ứng</div>
        ''',
        unsafe_allow_html=True,
    )

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input(
            "Tên đăng nhập",
            placeholder="Nhập username…",
        )
        password = st.text_input(
            "Mật khẩu",
            type="password",
            placeholder="Nhập password…",
        )
        submit = st.form_submit_button("Đăng nhập", use_container_width=True)

        if submit:
            if not username or not password:
                st.warning("Vui lòng nhập đầy đủ thông tin.")
            elif _verify(username, password):
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.query_params["logged_in"] = "true"
                st.query_params["user"] = username
                st.rerun()
            else:
                st.error("Sai tên đăng nhập hoặc mật khẩu.")

    st.markdown(
        f'<div class="login-footer">© 2025 OQR Co. Ltd · {APP_VERSION}</div>',
        unsafe_allow_html=True,
    )
