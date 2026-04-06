"""
pages/about.py — Trang giới thiệu ứng dụng.
"""

import streamlit as st
from utils.styles import page_header


def render() -> None:
    """Render trang About."""
    st.markdown(
        page_header("SUPPLY_CHAIN / ABOUT", "VỀ ỨNG DỤNG NÀY"),
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        Ứng dụng **Supply Chain Management** được phát triển bởi
        **OQR CO. LTD.** để tối ưu hóa quy trình quản lý chuỗi cung ứng,
        lập đơn đặt hàng (Pre-Order), nhập/xuất dữ liệu từ định dạng Excel,
        và tổng hợp thông tin.

        **Các tính năng chính:**
        - 📋 **Lập Pre-Order**: Tạo đơn đặt hàng tự động xuất ra file Excel
          từ thư viện hệ thống.
        - 🗄 **Dữ liệu bảng**: Tra cứu dữ liệu trực tiếp từ Database.
        - ⬆ **Import Excel**: Hỗ trợ nạp hàng loạt dữ liệu mới.
        - ⬇ **Export Excel**: Xuất báo cáo cấu trúc tùy chỉnh.
        - 📄 **Xem Templates**: Quản lý sẵn mẫu PO và CI.

        ---
        *Phiên bản: 1.0*
        """,
        unsafe_allow_html=True,
    )
