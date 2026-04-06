"""
db/queries.py — Tất cả câu SQL dùng chung.

Cache strategy:
  · list_tables / list_columns : TTL 120s (ít thay đổi)
  · count_rows                 : TTL 30s
  · search_products            : TTL 15s
  · fetch_page                 : TTL 20s
  · show_spinner=False         : tránh flash UI khi cache hit
"""

import warnings

import pandas as pd
import streamlit as st
from mysql.connector import Error

from db.connection import ensure_connected


# ─────────────────────────────────────────────────────────────
# GENERIC QUERY / EXECUTE
# ─────────────────────────────────────────────────────────────

def query(sql: str, params=None) -> pd.DataFrame:
    """Chạy SELECT query, trả về DataFrame."""
    try:
        conn = ensure_connected()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return pd.read_sql(sql, conn, params=params)
    except Error as e:
        st.error(f"DB error: {e}")
        return pd.DataFrame()


def execute(sql: str, params=None) -> bool:
    """Chạy INSERT/UPDATE/DELETE, trả về True nếu thành công."""
    try:
        conn = ensure_connected()
        cur = conn.cursor()
        cur.execute(sql, params or ())
        conn.commit()
        cur.close()
        return True
    except Error as e:
        st.error(f"DB error: {e}")
        return False


def executemany(sql: str, data: list) -> int:
    """Chạy batch INSERT, trả về số dòng affected."""
    try:
        conn = ensure_connected()
        cur = conn.cursor()
        cur.executemany(sql, data)
        conn.commit()
        n = cur.rowcount
        cur.close()
        return n
    except Error as e:
        st.error(f"DB error: {e}")
        return 0


# ─────────────────────────────────────────────────────────────
# SCHEMA
# ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=120, show_spinner=False)
def list_tables() -> list[str]:
    """Danh sách bảng — cache 2 phút."""
    df = query("SHOW TABLES")
    return df.iloc[:, 0].tolist() if not df.empty else []


@st.cache_data(ttl=120, show_spinner=False)
def list_columns(table: str) -> list[str]:
    """Danh sách cột — cache 2 phút."""
    df = query(f"SHOW COLUMNS FROM `{table}`")
    return df["Field"].tolist() if not df.empty else []


@st.cache_data(ttl=30, show_spinner=False)
def count_rows(table: str) -> int:
    """Đếm dòng — cache 30 giây."""
    df = query(f"SELECT COUNT(*) AS n FROM `{table}`")
    return int(df.iloc[0, 0]) if not df.empty else 0


# ─────────────────────────────────────────────────────────────
# SEARCH
# ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=15, show_spinner=False)
def search_products(
    table: str,
    keyword: str,
    search_cols: list[str],
    limit: int = 50,
) -> pd.DataFrame:
    """Tìm kiếm sản phẩm theo keyword — cache 15 giây."""
    if not keyword.strip() or not search_cols:
        return pd.DataFrame()
    where = " OR ".join([f"`{c}` LIKE %s" for c in search_cols])
    params = tuple(f"%{keyword}%" for _ in search_cols)
    return query(
        f"SELECT * FROM `{table}` WHERE {where} LIMIT {limit}", params
    )


# ─────────────────────────────────────────────────────────────
# PAGINATION
# ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=20, show_spinner=False)
def fetch_page(
    table: str, limit: int = 100, offset: int = 0
) -> pd.DataFrame:
    """Lấy trang dữ liệu — cache 20 giây."""
    return query(f"SELECT * FROM `{table}` LIMIT {limit} OFFSET {offset}")
