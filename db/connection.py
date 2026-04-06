"""
db/connection.py — MySQL connection management.

Sử dụng @st.cache_resource để cache connection object.
Tự động reconnect nếu bị mất kết nối.
"""

import streamlit as st
import mysql.connector


@st.cache_resource
def get_connection():
    """Tạo connection MySQL từ secrets, cache toàn bộ lifetime."""
    cfg = st.secrets["mysql"]
    return mysql.connector.connect(
        host=cfg["host"],
        port=int(cfg.get("port", 3306)),
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
    )


def ensure_connected():
    """Lấy connection, tự reconnect nếu bị mất."""
    conn = get_connection()
    if not conn.is_connected():
        conn.reconnect()
    return conn


def connection_status() -> tuple[bool, str]:
    """Kiểm tra trạng thái kết nối DB.

    Returns:
        (is_ok, label) — ví dụ: (True, "CONNECTED")
    """
    try:
        conn = get_connection()
        ok = conn.is_connected()
        return ok, "CONNECTED" if ok else "DISCONNECTED"
    except Exception:
        return False, "ERROR"
