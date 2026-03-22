"""db/connection.py — Cache kết nối MySQL."""

import streamlit as st
import mysql.connector


@st.cache_resource
def get_connection():
    cfg = st.secrets["mysql"]
    return mysql.connector.connect(
        host=cfg["host"],
        port=int(cfg.get("port", 3306)),
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
    )


def ensure_connected():
    conn = get_connection()
    if not conn.is_connected():
        conn.reconnect()
    return conn


def connection_status() -> tuple[bool, str]:
    try:
        conn = get_connection()
        ok = conn.is_connected()
        return ok, "CONNECTED" if ok else "DISCONNECTED"
    except Exception:
        return False, "ERROR"
