"""
pages/import_excel.py — Import dữ liệu từ Excel vào MySQL.

Flow:
  1. Chọn bảng đích + upload file Excel
  2. Chọn sheet
  3. Preview 5 dòng đầu
  4. Mapping cột Excel → cột DB
  5. Thực hiện INSERT (có option IGNORE cho trùng khóa)
"""

import pandas as pd
import streamlit as st

from db.queries import list_tables, list_columns, executemany
from utils.styles import page_header, section_label, divider
from utils.excel import read_excel_sheet


def render() -> None:
    """Render trang Import Excel."""
    st.markdown(
        page_header("supply_chain / import", "IMPORT EXCEL → MySQL"),
        unsafe_allow_html=True,
    )

    # ── Bước 1: Chọn bảng đích & file upload ─────────────
    st.markdown(
        section_label("🗄", "BẢNG ĐÍCH & FILE"), unsafe_allow_html=True
    )

    c1, c2 = st.columns([1, 1])
    with c1:
        tables = list_tables()
        target = st.selectbox("Bảng đích", tables)
    with c2:
        uploaded = st.file_uploader(
            "File Excel (.xlsx / .xls)", type=["xlsx", "xls"]
        )

    if not (uploaded and target):
        st.info("💡 Chọn bảng đích và upload file Excel để tiếp tục cấu hình mapping.")
        return

    st.markdown(divider(), unsafe_allow_html=True)

    # ── Bước 2: Chọn sheet ───────────────────────────────
    xl = pd.ExcelFile(uploaded)
    c3, _ = st.columns([1, 2])
    with c3:
        sheet = st.selectbox("Sheet", xl.sheet_names)

    preview = read_excel_sheet(uploaded, sheet).head(5)

    st.markdown(
        section_label("👁", "PREVIEW 5 DÒNG ĐẦU"), unsafe_allow_html=True
    )
    st.dataframe(preview, use_container_width=True)
    st.markdown(divider(), unsafe_allow_html=True)

    # ── Bước 3: Mapping cột ──────────────────────────────
    st.markdown(
        section_label("🔗", "MAPPING CỘT EXCEL → DB"),
        unsafe_allow_html=True,
    )

    db_cols = list_columns(target)
    xls_cols = list(preview.columns)
    options = ["(bỏ qua)"] + db_cols
    grid = st.columns(min(len(xls_cols), 4))
    mapping: dict[str, str] = {}

    for i, xc in enumerate(xls_cols):
        with grid[i % 4]:
            default = xc if xc in db_cols else None
            idx = options.index(default) if default in options else 0
            mapping[xc] = st.selectbox(xc, options, index=idx, key=f"map_{i}")

    st.markdown(divider(), unsafe_allow_html=True)

    # ── Bước 4: Import ───────────────────────────────────
    st.markdown(
        section_label("⚡", "THỰC HIỆN IMPORT"), unsafe_allow_html=True
    )

    skip_dup = st.checkbox(
        "INSERT IGNORE — bỏ qua dòng trùng khóa chính",
        value=True,
    )

    if st.button("🚀 BẮT ĐẦU IMPORT", type="primary", use_container_width=True):
        full_df = read_excel_sheet(uploaded, sheet)
        active = {xc: dc for xc, dc in mapping.items() if dc != "(bỏ qua)"}

        if not active:
            st.error("Vui lòng map ít nhất 1 cột.")
            return

        import_df = full_df[list(active.keys())].rename(columns=active)
        import_df = import_df.dropna(subset=list(active.values()), how="all")
        import_df = import_df.where(import_df.notna(), None)

        cols_sql = ", ".join(f"`{c}`" for c in import_df.columns)
        placeholders = ", ".join(["%s"] * len(import_df.columns))
        verb = "INSERT IGNORE" if skip_dup else "INSERT"
        sql = f"{verb} INTO `{target}` ({cols_sql}) VALUES ({placeholders})"
        rows = [
            tuple(r) for r in import_df.itertuples(index=False, name=None)
        ]

        with st.spinner(f"Đang import {len(rows):,} dòng vào `{target}`…"):
            affected = executemany(sql, rows)

        st.success(
            f"✅ Hoàn tất — {affected:,} dòng đã ghi vào `{target}`"
        )
        st.cache_data.clear()
