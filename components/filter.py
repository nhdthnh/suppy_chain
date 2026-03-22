"""
components/filter.py
Bộ lọc bảng + tự phát hiện cột barcode / description.
Trả về FilterResult để các module khác dùng.
"""

from dataclasses import dataclass, field
import streamlit as st
from db.queries import list_tables, list_columns


# ── Cột ưu tiên tự detect ────────────────────────────────────
_BARCODE_CANDIDATES  = ["barcode", "bar_code", "ean", "upc", "code", "ma_vach"]
_DESC_CANDIDATES     = ["description", "name", "product_name", "title", "ten", "mo_ta", "ten_sp"]


@dataclass
class FilterResult:
    selected_tables: list[str]       = field(default_factory=list)
    barcode_cols:    dict[str, str]   = field(default_factory=dict)   # table → col
    desc_cols:       dict[str, str]   = field(default_factory=dict)   # table → col
    all_columns:     list[str]        = field(default_factory=list)   # union tất cả cột

    @property
    def is_ready(self) -> bool:
        return bool(self.selected_tables)


def _detect(columns: list[str], candidates: list[str]) -> str | None:
    lower = {c.lower(): c for c in columns}
    for cand in candidates:
        if cand.lower() in lower:
            return lower[cand.lower()]
    return None


def get_default_filter_result(table_name: str) -> FilterResult:
    """
    Tạo FilterResult cứng cho một bảng không cần giao diện người dùng.
    """
    cols = list_columns(table_name)
    if not cols:
        return FilterResult()
        
    bc  = _detect(cols, _BARCODE_CANDIDATES)
    dsc = _detect(cols, _DESC_CANDIDATES)
    
    barcode_cols = {table_name: bc} if bc else {}
    desc_cols    = {table_name: dsc} if dsc else {}
    
    return FilterResult(
        selected_tables=[table_name],
        barcode_cols=barcode_cols,
        desc_cols=desc_cols,
        all_columns=cols,
    )


def render(key_prefix: str = "filter") -> FilterResult:
    """
    Hiển thị multiselect chọn bảng, tự detect cột barcode/description.
    Trả về FilterResult.
    """
    tables = list_tables()
    if not tables:
        st.warning("Không tìm thấy bảng nào trong database.")
        return FilterResult()

    c1, c2 = st.columns([1.5, 8.5])
    with c1:
        st.markdown(
            '<div style="font-style:normal;font-family:\'IBM Plex Sans\',sans-serif;'
            'font-weight:500;font-size:0.82rem;color:#444;margin-top:0.45rem;">BẢNG</div>',
            unsafe_allow_html=True,
        )
    with c2:
        selected_tables: list[str] = st.multiselect(
            label="Bảng",
            options=tables,
            default=tables[:1],
            placeholder="Chọn bảng…",
            key=f"{key_prefix}_tables",
            label_visibility="collapsed",
        )

    if not selected_tables:
        return FilterResult()

    # ── Detect cột cho từng bảng ─────────────────────────────
    barcode_cols: dict[str, str] = {}
    desc_cols:    dict[str, str] = {}
    seen_cols: set[str]          = set()
    all_columns: list[str]       = []

    for tbl in selected_tables:
        cols = list_columns(tbl)
        bc  = _detect(cols, _BARCODE_CANDIDATES)
        dsc = _detect(cols, _DESC_CANDIDATES)
        if bc:
            barcode_cols[tbl] = bc
        if dsc:
            desc_cols[tbl] = dsc
        for c in cols:
            if c not in seen_cols:
                all_columns.append(c)
                seen_cols.add(c)

    # ── Info nhỏ về mapping đã detect ────────────────────────
    with st.expander("ℹ Cột được nhận diện", expanded=False):
        for tbl in selected_tables:
            bc_label  = barcode_cols.get(tbl, "—")
            dsc_label = desc_cols.get(tbl, "—")
            st.markdown(
                f'<span style="font-family:\'IBM Plex Mono\',monospace;font-size:0.72rem;">'
                f'<b>{tbl}</b> → barcode: <code>{bc_label}</code> · '
                f'description: <code>{dsc_label}</code></span>',
                unsafe_allow_html=True,
            )

    return FilterResult(
        selected_tables=selected_tables,
        barcode_cols=barcode_cols,
        desc_cols=desc_cols,
        all_columns=all_columns,
    )
