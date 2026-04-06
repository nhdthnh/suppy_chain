"""
pages/search_order.py — Trang lập đơn Pre-Order.

Flow:
  1. Header
  2. Auto-detect bảng products_eng → FilterResult
  3. Widget tìm kiếm sản phẩm (multiselect)
  4. Bảng đơn hàng (barcode, description, qty, note, export)
"""

import streamlit as st
from utils.styles import page_header, divider
from components import filter as sc_filter
from modules import product_search, order_table


def render() -> None:
    """Render trang lập Pre-Order."""
    st.markdown(
        page_header("supply_chain / pre-order", "LẬP PRE-ORDER"),
        unsafe_allow_html=True,
    )

    # 1. Filter cố định cho bảng products_eng
    filter_result = sc_filter.get_default_filter_result("products_eng")

    st.markdown(divider(), unsafe_allow_html=True)

    # 2. Tìm kiếm sản phẩm
    product_search.render(filter_result)

    st.markdown(divider("2px", "#e8e8e8", "1.4rem 0"), unsafe_allow_html=True)

    # 3. Bảng đơn hàng
    order_table.render()