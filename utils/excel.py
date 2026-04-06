"""
utils/excel.py — Đọc/ghi Excel helpers.

Chức năng:
  · df_to_excel_bytes()       — DataFrame → Excel bytes (1 sheet)
  · multi_df_to_excel_bytes() — Dict[name, df] → Excel bytes (multi-sheet)
  · read_excel_sheet()        — Đọc 1 sheet từ file upload
  · timestamped_filename()    — Tạo tên file có timestamp
"""

import io
from datetime import datetime

import pandas as pd
import streamlit as st


@st.cache_data
def df_to_excel_bytes(
    df: pd.DataFrame, sheet_name: str = "data"
) -> bytes:
    """Convert DataFrame thành bytes Excel (1 sheet)."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name=sheet_name[:31])
    return buf.getvalue()


@st.cache_data
def multi_df_to_excel_bytes(
    sheets: dict[str, pd.DataFrame],
) -> bytes:
    """Convert nhiều DataFrame thành 1 file Excel (multi-sheet)."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        for name, df in sheets.items():
            df.to_excel(w, index=False, sheet_name=name[:31])
    return buf.getvalue()


def read_excel_sheet(file, sheet_name: str) -> pd.DataFrame:
    """Đọc 1 sheet từ uploaded file, drop dòng trống."""
    df = pd.read_excel(file, sheet_name=sheet_name, dtype=str)
    return df.dropna(how="all").reset_index(drop=True)


def timestamped_filename(prefix: str, ext: str = "xlsx") -> str:
    """Tạo tên file có timestamp, ví dụ: prefix_20260406_0952.xlsx"""
    return f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M')}.{ext}"
