"""db/queries.py — Toàn bộ câu SQL dùng chung."""

import pandas as pd
import streamlit as st
import warnings
from mysql.connector import Error
from db.connection import ensure_connected


# ── Generic ───────────────────────────────────────────────────

def query(sql: str, params=None) -> pd.DataFrame:
    try:
        conn = ensure_connected()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return pd.read_sql(sql, conn, params=params)
    except Error as e:
        st.error(f"DB error: {e}")
        return pd.DataFrame()


def execute(sql: str, params=None) -> bool:
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


# ── Schema ────────────────────────────────────────────────────

@st.cache_data(ttl=60)
def list_tables() -> list[str]:
    df = query("SHOW TABLES")
    return df.iloc[:, 0].tolist() if not df.empty else []


@st.cache_data(ttl=60)
def list_columns(table: str) -> list[str]:
    df = query(f"SHOW COLUMNS FROM `{table}`")
    return df["Field"].tolist() if not df.empty else []


@st.cache_data(ttl=30)
def count_rows(table: str) -> int:
    df = query(f"SELECT COUNT(*) AS n FROM `{table}`")
    return int(df.iloc[0, 0]) if not df.empty else 0


# ── Search ────────────────────────────────────────────────────

@st.cache_data(ttl=20)
def search_products(table: str, keyword: str, search_cols: list[str], limit: int = 50) -> pd.DataFrame:
    if not keyword.strip() or not search_cols:
        return pd.DataFrame()
    where  = " OR ".join([f"`{c}` LIKE %s" for c in search_cols])
    params = tuple(f"%{keyword}%" for _ in search_cols)
    return query(f"SELECT * FROM `{table}` WHERE {where} LIMIT {limit}", params)


@st.cache_data(ttl=30)
def fetch_page(table: str, limit: int = 100, offset: int = 0) -> pd.DataFrame:
    return query(f"SELECT * FROM `{table}` LIMIT {limit} OFFSET {offset}")
