"""pages/export_excel.py — Export MySQL ra Excel."""

import streamlit as st
from db.queries import list_tables, query
from utils.styles import page_header
from utils.excel import df_to_excel_bytes, multi_df_to_excel_bytes, timestamped_filename


def render() -> None:
    st.markdown(page_header("supply_chain / export", "EXPORT MySQL → EXCEL"), unsafe_allow_html=True)

    tables = list_tables()
    if not tables:
        st.warning("Không tìm thấy bảng nào.")
        return

    mode = st.radio("Chế độ", ["Xuất 1 bảng", "Xuất nhiều bảng", "SQL tùy chỉnh"], horizontal=True)

    if mode == "Xuất 1 bảng":
        tbl = st.selectbox("Bảng", tables)
        if st.button("▶ XUẤT"):
            with st.spinner("Đang tải…"):
                df = query(f"SELECT * FROM `{tbl}`")
            if not df.empty:
                fname = timestamped_filename(tbl)
                st.download_button(
                    f"⬇ Tải {fname}",
                    data=df_to_excel_bytes(df, tbl[:31]),
                    file_name=fname,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
                st.success(f"{len(df):,} dòng · {len(df.columns)} cột")

    elif mode == "Xuất nhiều bảng":
        selected = st.multiselect("Chọn bảng", tables, default=tables[:2])
        if st.button("▶ XUẤT TẤT CẢ") and selected:
            with st.spinner("Đang tải…"):
                sheets = {t: query(f"SELECT * FROM `{t}`") for t in selected}
            fname = timestamped_filename("supply_chain_export")
            st.download_button(
                f"⬇ Tải {fname}",
                data=multi_df_to_excel_bytes(sheets),
                file_name=fname,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            st.success(f"Đã đóng gói {len(selected)} bảng.")

    else:
        default_tbl = tables[0] if tables else "products"
        sql_input = st.text_area("SQL", value=f"SELECT * FROM `{default_tbl}` LIMIT 100", height=110)
        if st.button("▶ CHẠY & XUẤT"):
            with st.spinner("Đang thực thi…"):
                df = query(sql_input)
            if not df.empty:
                st.dataframe(df.head(20), width="stretch")
                st.markdown(
                    f'<span style="font-family:\'IBM Plex Mono\',monospace;font-size:0.7rem;color:#888;">'
                    f'{len(df):,} dòng</span>',
                    unsafe_allow_html=True,
                )
                fname = timestamped_filename("query_result")
                st.download_button(
                    "⬇ Tải kết quả (.xlsx)", data=df_to_excel_bytes(df),
                    file_name=fname,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
