"""
modules/product_search.py — Tìm kiếm sản phẩm dạng dropdown multiselect.

Chức năng:
  · Load toàn bộ barcode | description từ DB
  · Hiển thị multiselect dropdown
  · Khi user chọn → thêm vào order_table
"""

import streamlit as st
from db.queries import query
from components.filter import FilterResult
from modules import order_table
from utils.styles import section_label


# ─────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=120, show_spinner=False)
def _load_product_options(
    tables: list[str],
    bc_cols: dict,
    dsc_cols: dict,
) -> list[str]:
    """Tải toàn bộ barcode | description từ các bảng đã chọn.

    Returns:
        List các chuỗi dạng "BARCODE | DESCRIPTION" hoặc "BARCODE"
    """
    items: list[str] = []
    seen: set[str] = set()

    for tbl in tables:
        bc_col = bc_cols.get(tbl)
        dsc_col = dsc_cols.get(tbl)
        if not bc_col:
            continue

        sql = f"SELECT `{bc_col}`"
        if dsc_col:
            sql += f", `{dsc_col}`"
        sql += f" FROM `{tbl}` LIMIT 35000"

        try:
            df = query(sql)
            if df.empty:
                continue
            for _, row in df.iterrows():
                bc = str(row[bc_col]).strip()
                desc = (
                    str(row[dsc_col]).strip()
                    if dsc_col and dsc_col in df.columns
                    else ""
                )
                if bc and bc not in seen:
                    items.append(f"{bc} | {desc}" if desc else bc)
                    seen.add(bc)
        except Exception:
            continue

    return items


# ─────────────────────────────────────────────────────────────
# RENDER
# ─────────────────────────────────────────────────────────────

def render(filter_result: FilterResult) -> None:
    """Render multiselect dropdown tìm & thêm sản phẩm vào đơn hàng."""
    st.markdown(
        section_label("🔍", "TÌM KIẾM SẢN PHẨM"), unsafe_allow_html=True
    )

    if not filter_result.is_ready:
        st.caption("Vui lòng chọn ít nhất 1 bảng ở bộ lọc phía trên.")
        return

    options = _load_product_options(
        filter_result.selected_tables,
        filter_result.barcode_cols,
        filter_result.desc_cols,
    )

    if not options:
        st.warning("Không có dữ liệu sản phẩm.")
        return

    # Counter để reset multiselect sau khi thêm sản phẩm
    if "search_idx" not in st.session_state:
        st.session_state.search_idx = 0

    selected_items = st.multiselect(
        label="SẢN PHẨM",
        options=options,
        placeholder="Gõ mã hoặc tên để tìm kiếm…",
        key=f"search_items_{st.session_state.search_idx}",
    )

    if selected_items:
        for item in selected_items:
            if " | " in item:
                bc, desc = item.split(" | ", 1)
            else:
                bc, desc = item, ""
            order_table.add_product(bc, desc)

        st.session_state.search_idx += 1
        st.rerun()
