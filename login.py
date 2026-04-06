"""
login.py — Authentication module.

Chức năng:
  · show_login_page()  — Render form đăng nhập
  · is_authenticated() — Check trạng thái đăng nhập
  · auto_login()       — Tự động login từ URL params (survive F5)
  · logout()           — Xóa session + URL params

Lưu trữ user: file log/log.xlsx, sheet "user"
Password: mã hóa SHA256
"""

import hashlib
from pathlib import Path

import pandas as pd
import streamlit as st

# Path tới file chứa user/password
LOG_FILE = Path(__file__).parent / "log" / "log.xlsx"


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def _hash_password(password: str) -> str:
    """Mã hóa password bằng SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


def _verify_login(username: str, password: str) -> bool:
    """Kiểm tra username + password với file log.xlsx.

    Returns:
        True nếu credentials đúng.
    """
    if not LOG_FILE.exists():
        st.error(f"Không tìm thấy file log.xlsx tại {LOG_FILE}")
        return False

    try:
        df = pd.read_excel(LOG_FILE, sheet_name="user")
        user_row = df[df["username"] == username]
        if user_row.empty:
            return False
        stored_hash = user_row.iloc[0]["password"]
        return stored_hash == _hash_password(password)
    except Exception as e:
        st.error(f"Lỗi khi đọc file log: {e}")
        return False


# ─────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────

def is_authenticated() -> bool:
    """Check xem user đã đăng nhập chưa."""
    return st.session_state.get("authenticated", False)


def auto_login() -> bool:
    """Tự động login từ URL params nếu có (survive F5).

    Returns:
        True nếu tự động đăng nhập thành công.
    """
    if is_authenticated():
        return False

    params = st.query_params
    if params.get("logged_in") == "true" and params.get("user"):
        st.session_state["authenticated"] = True
        st.session_state["username"] = params["user"]
        return True

    return False


def logout() -> None:
    """Đăng xuất: xóa session + URL params."""
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.query_params.clear()
    st.rerun()


def show_login_page() -> None:
    """Render form đăng nhập."""
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("# 🔐 Đăng nhập")
        st.markdown("### Supply Chain Management Tool")
        st.markdown("---")

        with st.form("login_form"):
            username = st.text_input(
                "👤 Tên đăng nhập", placeholder="Nhập username"
            )
            password = st.text_input(
                "🔑 Mật khẩu", type="password", placeholder="Nhập password"
            )
            submit = st.form_submit_button(
                "Đăng nhập", use_container_width=True
            )

            if submit:
                if not (username and password):
                    st.warning("⚠️ Vui lòng nhập đầy đủ thông tin!")
                elif _verify_login(username, password):
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username
                    st.query_params["logged_in"] = "true"
                    st.query_params["user"] = username
                    st.success("✅ Đăng nhập thành công!")
                    st.rerun()
                else:
                    st.error("❌ Sai tên đăng nhập hoặc mật khẩu!")

        st.markdown("---")
        st.caption("OQR CO. LTD. © 2024")
