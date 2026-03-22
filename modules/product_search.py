"""
modules/product_search.py
Tìm kiếm sản phẩm dạng dropdown multiselect.
"""

import streamlit as st
import pandas as pd
from db.queries import query
from components.filter import FilterResult
from modules import order_table
from utils.styles import section_label


@st.cache_data(ttl=120)
def _load_products_options(tables: list[str], bc_cols: dict, dsc_cols: dict) -> list[str]:
    """Tải toàn bộ barcode | description từ các bảng được chọn."""
    items = []
    seen = set()
    for tbl in tables:
        bc_col  = bc_cols.get(tbl)
        dsc_col = dsc_cols.get(tbl)
        if not bc_col:
            continue
            
        sql = f"SELECT `{bc_col}`"
        if dsc_col:
            sql += f", `{dsc_col}`"
        sql += f" FROM `{tbl}` LIMIT 35000"  # Guard cho memory
        
        try:
            df = query(sql)
            if df.empty:
                continue
                
            for _, r in df.iterrows():
                bc   = str(r[bc_col]).strip()
                desc = str(r[dsc_col]).strip() if dsc_col and dsc_col in df.columns else ""
                if bc and bc not in seen:
                    items.append(f"{bc} | {desc}" if desc else bc)
                    seen.add(bc)
        except Exception:
            continue # Bỏ qua lỗi bảng lỗi
            
    return items


def render(filter_result: FilterResult) -> None:
    """
    Render multiselect dropdown để gõ mã & click chọn thêm vào đơn hàng.
    """
    st.markdown(section_label("🔍", "TÌM KIẾM"), unsafe_allow_html=True)

    if not filter_result.is_ready:
        st.caption("Vui lòng chọn ít nhất 1 bảng ở bộ lọc phía trên.")
        return

    # ── 1. Caching load options ───────────────────────────────
    options = _load_products_options(
        filter_result.selected_tables,
        filter_result.barcode_cols,
        filter_result.desc_cols
    )

    if not options:
        st.warning("Không có dữ liệu sản phẩm.")
        return

    # ── 2. Render dropdown ─────────────────────────────────────
    if "search_idx" not in st.session_state:
        st.session_state.search_idx = 0

    sc1, sc2 = st.columns([1.5, 8.5])
    with sc1:
        st.markdown(
            '<div style="font-style:normal;font-family:\'IBM Plex Sans\',sans-serif;'
            'font-weight:500;font-size:0.82rem;color:#444;margin-top:0.42rem;">SẢN PHẨM</div>',
            unsafe_allow_html=True,
        )
    with sc2:
        selected_items = st.multiselect(
            label="search_items",
            options=options,
            placeholder="Gõ mã hoặc tên để tìm kiếm…",
            key=f"search_items_{st.session_state.search_idx}",
            label_visibility="collapsed",
        )



    # ── 3. Thêm vào đơn hàng & Reset widget ──────────────────
    if selected_items:
        for item in selected_items:
            if " | " in item:
                bc, desc = item.split(" | ", 1)
            else:
                bc, desc = item, ""
            # Thêm sản phẩm
            order_table.add_product(bc, desc)
            
        st.session_state.search_idx += 1  # Đổi key để widget rỗng lại
        st.rerun()
