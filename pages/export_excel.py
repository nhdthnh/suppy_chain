"""
pages/export_excel.py — Export dữ liệu MySQL ra file Excel.

Chế độ xuất:
  1. Xuất 1 bảng
  2. Xuất nhiều bảng (multi-sheet)
  3. SQL tùy chỉnh → preview + download
"""

import streamlit as st

from db.queries import list_tables, query
from utils.styles import page_header, section_label
from utils.excel import (
    df_to_excel_bytes,
    multi_df_to_excel_bytes,
    timestamped_filename,
)


def render() -> None:
    """Render trang Export Excel."""
    st.markdown(
        page_header("supply_chain / export", "EXPORT MySQL → EXCEL"),
        unsafe_allow_html=True,
    )

    tables = list_tables()
    if not tables:
        st.warning("Không tìm thấy bảng nào.")
        return

    mode = st.radio(
        "Chế độ xuất",
        ["Xuất 1 bảng", "Xuất nhiều bảng", "SQL tùy chỉnh"],
        horizontal=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if mode == "Xuất 1 bảng":
        _render_single_table(tables)
    elif mode == "Xuất nhiều bảng":
        _render_multi_table(tables)
    else:
        _render_custom_sql(tables)


# ─────────────────────────────────────────────────────────────
# PRIVATE RENDER FUNCTIONS
# ─────────────────────────────────────────────────────────────

def _render_single_table(tables: list[str]) -> None:
    """Xuất 1 bảng ra Excel."""
    st.markdown(
        section_label("🗄", "CHỌN BẢNG"), unsafe_allow_html=True
    )
    tbl = st.selectbox("Bảng", tables, label_visibility="collapsed")

    if st.button("▶ XUẤT BẢNG", type="primary"):
        with st.spinner(f"Đang tải dữ liệu `{tbl}`…"):
            df = query(f"SELECT * FROM `{tbl}`")
        if df.empty:
            st.warning("Bảng trống.")
            return
        fname = timestamped_filename(tbl)
        st.success(f"✅ {len(df):,} dòng · {len(df.columns)} cột")
        st.download_button(
            f"⬇ Tải {fname}",
            data=df_to_excel_bytes(df, tbl[:31]),
            file_name=fname,
            mime="application/vnd.openxmlformats-officedocument"
                 ".spreadsheetml.sheet",
        )


def _render_multi_table(tables: list[str]) -> None:
    """Xuất nhiều bảng ra 1 file Excel (multi-sheet)."""
    st.markdown(
        section_label("📦", "CHỌN CÁC BẢNG"), unsafe_allow_html=True
    )
    selected = st.multiselect(
        "Bảng cần xuất",
        tables,
        default=tables[:2],
        label_visibility="collapsed",
    )

    if st.button("▶ XUẤT TẤT CẢ", type="primary") and selected:
        with st.spinner(f"Đang tải {len(selected)} bảng…"):
            sheets = {t: query(f"SELECT * FROM `{t}`") for t in selected}
        fname = timestamped_filename("supply_chain_export")
        st.success(f"✅ Đã đóng gói {len(selected)} bảng.")
        st.download_button(
            f"⬇ Tải {fname}",
            data=multi_df_to_excel_bytes(sheets),
            file_name=fname,
            mime="application/vnd.openxmlformats-officedocument"
                 ".spreadsheetml.sheet",
        )


def _render_custom_sql(tables: list[str]) -> None:
    """Chạy SQL tùy chỉnh, preview + xuất kết quả."""
    default_tbl = tables[0] if tables else "products"
    st.markdown(
        section_label("⌨️", "NHẬP CÂU SQL"), unsafe_allow_html=True
    )
    sql_input = st.text_area(
        "SQL query",
        value=f"SELECT * FROM `{default_tbl}` LIMIT 100",
        height=110,
        label_visibility="collapsed",
    )

    if st.button("▶ CHẠY & XUẤT", type="primary"):
        with st.spinner("Đang thực thi…"):
            df = query(sql_input)
        if df.empty:
            st.warning("Không có kết quả.")
            return

        st.markdown(
            section_label("👁", f"PREVIEW — {len(df):,} DÒNG"),
            unsafe_allow_html=True,
        )
        st.dataframe(df.head(20), use_container_width=True)

        fname = timestamped_filename("query_result")
        st.download_button(
            "⬇ Tải kết quả (.xlsx)",
            data=df_to_excel_bytes(df),
            file_name=fname,
            mime="application/vnd.openxmlformats-officedocument"
                 ".spreadsheetml.sheet",
        )
