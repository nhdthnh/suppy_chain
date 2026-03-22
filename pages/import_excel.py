"""pages/import_excel.py — Import Excel vào MySQL."""

import streamlit as st
import pandas as pd
from db.queries import list_tables, list_columns, executemany
from utils.styles import page_header
from utils.excel import read_excel_sheet


def render() -> None:
    st.markdown(page_header("supply_chain / import", "IMPORT EXCEL → MySQL"), unsafe_allow_html=True)

    tables   = list_tables()
    target   = st.selectbox("Bảng đích", tables)
    uploaded = st.file_uploader("Chọn file .xlsx / .xls", type=["xlsx", "xls"])

    if not (uploaded and target):
        return

    xl    = pd.ExcelFile(uploaded)
    sheet = st.selectbox("Sheet", xl.sheet_names)

    preview = read_excel_sheet(uploaded, sheet).head(5)
    st.markdown("**Preview 5 dòng:**")
    st.dataframe(preview, width="stretch")

    db_cols  = list_columns(target)
    xls_cols = list(preview.columns)
    options  = ["(bỏ qua)"] + db_cols
    grid     = st.columns(min(len(xls_cols), 4))
    mapping: dict[str, str] = {}

    st.markdown("**Mapping cột Excel → DB:**")
    for i, xc in enumerate(xls_cols):
        with grid[i % 4]:
            default = xc if xc in db_cols else None
            idx = options.index(default) if default in options else 0
            mapping[xc] = st.selectbox(xc, options, index=idx, key=f"map_{i}")

    skip_dup = st.checkbox("INSERT IGNORE (bỏ qua trùng key)", value=True)

    if st.button("▶ BẮT ĐẦU IMPORT"):
        full_df  = read_excel_sheet(uploaded, sheet)
        active   = {xc: dc for xc, dc in mapping.items() if dc != "(bỏ qua)"}

        if not active:
            st.error("Vui lòng map ít nhất 1 cột.")
            return

        import_df = full_df[list(active.keys())].rename(columns=active)
        import_df = import_df.dropna(subset=list(active.values()), how="all")
        import_df = import_df.where(import_df.notna(), None)

        cols_sql     = ", ".join(f"`{c}`" for c in import_df.columns)
        placeholders = ", ".join(["%s"] * len(import_df.columns))
        verb         = "INSERT IGNORE" if skip_dup else "INSERT"
        sql          = f"{verb} INTO `{target}` ({cols_sql}) VALUES ({placeholders})"
        rows         = [tuple(r) for r in import_df.itertuples(index=False, name=None)]

        with st.spinner("Đang import…"):
            affected = executemany(sql, rows)

        st.success(f"✅ Xong — {affected} dòng ghi vào `{target}`")
        st.cache_data.clear()
