"""
pages/data_browser.py — Xem, chỉnh sửa & xuất dữ liệu bảng.

Tính năng:
  · Chọn bảng → hiển thị metric cards (tổng dòng, số cột, tên bảng)
  · Data editor: sửa trực tiếp các cell
  · Thêm dòng mới với auto-increment ID
  · Áp dụng thay đổi (INSERT / UPDATE / DELETE) vào DB
  · Load thêm dòng (lazy pagination)
  · Xuất Excel toàn bộ bảng
"""

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from db.queries import (
    list_tables, count_rows, fetch_page,
    list_columns, query, execute,
)
from utils.styles import page_header, metric_card, section_label, divider
from utils.excel import df_to_excel_bytes, timestamped_filename


# ─────────────────────────────────────────────────────────────
# SCROLL HELPERS
# ─────────────────────────────────────────────────────────────

def _scroll_to_bottom() -> None:
    """Cuộn trang xuống cuối (dùng khi thêm dòng mới)."""
    components.html(
        """
        <script>
        setTimeout(() => {
            try {
                window.parent.scrollTo({
                    top: window.parent.document.body.scrollHeight,
                    behavior: 'smooth'
                });
            } catch(e) {
                window.scrollTo({
                    top: document.body.scrollHeight,
                    behavior: 'smooth'
                });
            }
        }, 150);
        </script>
        """,
        height=0,
    )


def _freeze_scroll_on_edit() -> None:
    """Giữ vị trí scroll khi user edit cell → rerun."""
    components.html(
        """
        <script>
        (function() {
            const WIN = window.parent;
            const KEY = 'sc_db_scroll_y';
            const saved = sessionStorage.getItem(KEY);
            if (saved !== null) {
                setTimeout(() => {
                    WIN.scrollTo({ top: parseInt(saved), behavior: 'instant' });
                    sessionStorage.removeItem(KEY);
                }, 60);
            }
            WIN.addEventListener('blur', () => {
                sessionStorage.setItem(KEY, String(WIN.scrollY));
            }, true);
        })();
        </script>
        """,
        height=0,
    )


# ─────────────────────────────────────────────────────────────
# DB HELPERS
# ─────────────────────────────────────────────────────────────

def _to_sql_param(v):
    """Convert giá trị Python → SQL param (None cho NaN/None)."""
    if v is None:
        return None
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    return v


def _next_auto_id(table: str, pk_col: str) -> int:
    """Lấy ID tiếp theo = MAX(pk_col) + 1."""
    df = query(f"SELECT MAX(`{pk_col}`) AS mx FROM `{table}`")
    if df.empty or pd.isna(df.iloc[0, 0]):
        return 1
    return int(df.iloc[0, 0]) + 1


def _is_numeric_col(series: pd.Series) -> bool:
    """Kiểm tra cột có phải numeric không."""
    try:
        pd.to_numeric(series.dropna())
        return True
    except (ValueError, TypeError):
        return False


def _apply_changes(
    table: str,
    original_df: pd.DataFrame,
    edited_df: pd.DataFrame,
) -> tuple[int, int, int]:
    """So sánh original vs edited → thực hiện INSERT/DELETE/UPDATE.

    Returns:
        (inserted, deleted, updated) counts
    """
    if original_df.empty and edited_df.empty:
        return 0, 0, 0

    cols = list(original_df.columns)
    pk = cols[0]

    if pk not in edited_df.columns:
        st.error(f"Không tìm thấy cột khóa chính '{pk}' trong dữ liệu.")
        return 0, 0, 0

    if original_df[pk].dropna().duplicated().any():
        st.error("Khóa chính bị trùng trong dữ liệu gốc.")
        return 0, 0, 0

    old_map = original_df.set_index(pk).to_dict(orient="index")
    new_map = {
        v: r
        for v, r in edited_df.set_index(pk).to_dict(orient="index").items()
        if pd.notna(v)
    }

    inserted = deleted = updated = 0

    # DELETE: dòng cũ không còn trong dữ liệu mới
    for pk_val in list(old_map.keys()):
        if pk_val not in new_map:
            sql = f"DELETE FROM `{table}` WHERE `{pk}` = %s"
            if execute(sql, (_to_sql_param(pk_val),)):
                deleted += 1

    # INSERT: dòng mới không có trong dữ liệu cũ
    for pk_val, row in new_map.items():
        if pk_val not in old_map:
            all_cols = [pk] + [c for c in cols if c != pk]
            col_names = ", ".join(f"`{c}`" for c in all_cols)
            placeholders = ", ".join(["%s"] * len(all_cols))
            values = [_to_sql_param(pk_val)] + [
                _to_sql_param(row.get(c)) for c in all_cols[1:]
            ]
            sql = f"INSERT INTO `{table}` ({col_names}) VALUES ({placeholders})"
            if execute(sql, tuple(values)):
                inserted += 1

    # UPDATE: dòng đã tồn tại nhưng có thay đổi
    for pk_val, row in new_map.items():
        if pk_val not in old_map:
            continue
        sets, params = [], []
        for c in cols:
            if c == pk:
                continue
            nv = _to_sql_param(row.get(c))
            ov = _to_sql_param(old_map[pk_val].get(c))
            if nv != ov:
                sets.append(f"`{c}` = %s")
                params.append(nv)
        if sets:
            params.append(_to_sql_param(pk_val))
            sql = f"UPDATE `{table}` SET {', '.join(sets)} WHERE `{pk}` = %s"
            if execute(sql, tuple(params)):
                updated += 1

    return inserted, deleted, updated


# ─────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────

_PFX = "db_browser_"


def _k(suffix: str) -> str:
    """Tạo session state key với prefix."""
    return _PFX + suffix


def _init_state(table: str, chunk: int) -> None:
    """Khởi tạo session state khi đổi bảng."""
    if st.session_state.get(_k("table")) != table:
        st.session_state[_k("table")] = table
        st.session_state[_k("load_rows")] = chunk
        st.session_state[_k("df")] = pd.DataFrame()
        st.session_state[_k("confirm")] = False
        st.session_state[_k("scroll_down")] = False


def _reload(table: str) -> None:
    """Reload dữ liệu từ DB."""
    n = st.session_state[_k("load_rows")]
    st.session_state[_k("df")] = fetch_page(table, limit=n, offset=0)


# ─────────────────────────────────────────────────────────────
# RENDER
# ─────────────────────────────────────────────────────────────

def render() -> None:
    """Render trang Data Browser."""
    st.markdown(
        page_header("supply_chain / tables", "DỮ LIỆU BẢNG"),
        unsafe_allow_html=True,
    )

    tables = list_tables()
    if not tables:
        st.warning("Không tìm thấy bảng nào.")
        return

    selected = st.selectbox("Chọn bảng", tables)
    if not selected:
        return

    CHUNK = 200
    _init_state(selected, CHUNK)

    if st.session_state[_k("df")].empty:
        _reload(selected)

    total = count_rows(selected)
    cols = list_columns(selected)

    # ── Metrics ───────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(metric_card("TỔNG DÒNG", f"{total:,}"), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card("SỐ CỘT", str(len(cols))), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card("BẢNG", selected), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    current_df: pd.DataFrame = st.session_state[_k("df")]
    _freeze_scroll_on_edit()

    # ── Data Editor ───────────────────────────────────────
    st.markdown(
        section_label("✏️", "CHỈNH SỬA TRỰC TIẾP"),
        unsafe_allow_html=True,
    )

    edited_df = st.data_editor(
        current_df,
        use_container_width=True,
        num_rows="fixed",
        key=f"de_{selected}",
    )

    row_count = len(edited_df)
    st.caption(f"{row_count:,} / {total:,} dòng đang hiển thị")

    # ── Load thêm ─────────────────────────────────────────
    if row_count < total:
        st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
        if st.button(f"⬇ Load thêm {CHUNK} dòng", key="load_more", type="secondary", use_container_width=True):
            st.session_state[_k("load_rows")] += CHUNK
            _reload(selected)
            st.rerun()

    # ── Quick Actions ─────────────────────────────────────
    st.markdown(divider(), unsafe_allow_html=True)
    st.markdown(section_label("🛠️", "BẢNG ĐIỀU KHIỂN"), unsafe_allow_html=True)
    
    col_add, col_save, col_export = st.columns(3)

    # 1. Thêm dòng
    with col_add:
        pk_col = current_df.columns[0] if not current_df.empty else None
        numeric_pk = pk_col and _is_numeric_col(current_df[pk_col])
        if pk_col:
            if st.button("＋ Thêm dòng mới", key="add_row", use_container_width=True):
                auto_id = _next_auto_id(selected, pk_col) if numeric_pk else ""
                new_row = {c: None for c in current_df.columns}
                new_row[pk_col] = auto_id
                st.session_state[_k("df")] = pd.concat(
                    [current_df, pd.DataFrame([new_row])],
                    ignore_index=True,
                )
                st.session_state[_k("scroll_down")] = True
                st.rerun()

    # 2. Ghi DB
    with col_save:
        if st.button("✔ Lưu vào Database", key="apply_changes", type="primary", use_container_width=True):
            st.session_state[_k("confirm")] = True

    # 3. Xuất Excel
    with col_export:
        full_df = query(f"SELECT * FROM `{selected}`")
        st.download_button(
            f"⬇ Xuất Excel (.xlsx)",
            data=df_to_excel_bytes(full_df, selected[:31]),
            file_name=timestamped_filename(selected),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    if st.session_state.get(_k("confirm"), False):
        st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
        st.warning("⚠️ Xác nhận ghi thay đổi xuống database? Hành động không thể hoàn tác.")
        
        col_ok, col_cancel, _ = st.columns([1.2, 1, 8])
        if col_ok.button("✔ Xác nhận", key="confirm_ok", type="primary"):
            orig = st.session_state[_k("df")]
            ins, dels, upd = _apply_changes(selected, orig, edited_df)
            st.success(f"✅ Hoàn tất: +{ins} thêm  ·  −{dels} xóa  ·  ~{upd} sửa")
            st.session_state[_k("confirm")] = False
            _reload(selected)
            st.rerun()

        if col_cancel.button("✕ Hủy", key="confirm_cancel"):
            st.session_state[_k("confirm")] = False
            st.rerun()

    if st.session_state.get(_k("scroll_down"), False):
        _scroll_to_bottom()
        st.session_state[_k("scroll_down")] = False
