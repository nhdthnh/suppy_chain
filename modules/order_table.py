"""
modules/order_table.py
Bảng Pre-Order:
  - Date picker, vendor dropdown, deposit %
  - Bảng sản phẩm: barcode | description | qty | note | X
  - Unit price & total bỏ khỏi UI (VLOOKUP tự động trong Excel)
"""

import os
from datetime import date
import streamlit as st
import pandas as pd
from db.queries import query
from utils.excel import df_to_excel_bytes, timestamped_filename
from utils.styles import section_label, mono

_KEY           = "sc_order_items"
_VENDOR_KEY    = "sc_vendor_id"
_DATE_KEY      = "sc_po_date"
_DEPOSIT_KEY   = "sc_deposit_pct"

_HERE          = os.path.dirname(os.path.abspath(__file__))

def _get_vendor_template_dir(vendor_short_name: str) -> str | None:
    base = os.path.join(_HERE, "..", "templates", "Pre-Order")
    if not os.path.exists(base):
        return None
    for d in os.listdir(base):
        if d.lower() == vendor_short_name.lower() and os.path.isdir(os.path.join(base, d)):
            return os.path.join(base, d)
    return None


# ── State API ─────────────────────────────────────────────────

def _init() -> None:
    if _KEY not in st.session_state:
        st.session_state[_KEY] = []


def get_items() -> list[dict]:
    _init()
    return st.session_state[_KEY]


def add_product(barcode: str, description: str) -> None:
    _init()
    if not any(r["barcode"] == barcode for r in st.session_state[_KEY]):
        st.session_state[_KEY].append({
            "barcode":     barcode,
            "description": description,
            "quantity":    1,
            "note":        "",
        })


def remove_product(barcode: str) -> None:
    _init()
    st.session_state[_KEY] = [r for r in st.session_state[_KEY] if r["barcode"] != barcode]


def clear_all() -> None:
    st.session_state[_KEY] = []


# ── Vendor helpers ────────────────────────────────────────────

@st.cache_data(ttl=60)
def _load_vendors() -> pd.DataFrame:
    return query(
        "SELECT id, short_name, name, address, tel, bank_name, bank_address, "
        "swift_code, beneficiary_name, account_number, beneficiary_address "
        "FROM vendors WHERE is_active = 1 ORDER BY short_name"
    )


# ── Render ────────────────────────────────────────────────────

def render() -> None:
    _init()

    # ── THÔNG TIN PRE-ORDER ───────────────────────────────────
    st.markdown(section_label("⚙", "THÔNG TIN PRE-ORDER"), unsafe_allow_html=True)

    cfg1, cfg2, cfg3 = st.columns([2, 2, 1.5])

    with cfg1:
        po_date = st.date_input(
            "📅 Ngày đặt hàng",
            value=st.session_state.get(_DATE_KEY, date.today()),
            key=_DATE_KEY,
            format="DD/MM/YYYY",
        )

    vendor_row = None
    short      = "VENDOR"
    template_path = None

    with cfg2:
        vendors_df = _load_vendors()
        if vendors_df.empty:
            st.warning("Chưa có vendor — thêm vào bảng vendors.")
        else:
            options  = vendors_df["short_name"].tolist()
            sel_idx  = st.session_state.get(_VENDOR_KEY, 0)
            selected = st.selectbox(
                "🏢 Vendor",
                options=options,
                index=min(sel_idx, len(options) - 1),
                key="_vendor_select",
            )
            st.session_state[_VENDOR_KEY] = options.index(selected)
            vendor_row = vendors_df[vendors_df["short_name"] == selected].iloc[0]
            short      = (vendor_row.get("short_name") or "VENDOR").strip()

            v_dir = _get_vendor_template_dir(short)
            templates_list = []
            if v_dir:
                templates_list = [f for f in os.listdir(v_dir) if f.endswith(".xlsx")]
            
            if templates_list:
                sel_tmpl = st.selectbox(
                    "📋 Template Excel",
                    options=templates_list,
                    key=f"sc_tmpl_{short}",
                )
                if sel_tmpl:
                    template_path = os.path.join(v_dir, sel_tmpl)
            else:
                st.caption(f"⚠️ Chưa có file template trong `templates/Pre-Order/{short}`")

    with cfg3:
        deposit_pct = st.number_input(
            "💰 Deposit (%)",
            min_value=0.0, max_value=100.0,
            value=float(st.session_state.get(_DEPOSIT_KEY, 70.0)),
            step=5.0, format="%.0f",
            key=_DEPOSIT_KEY,
            help="Ví dụ: 70 → Deposit = Amount × 70%",
        )

    # PO number preview
    if vendor_row is not None:
        dd, mm, yyyy = po_date.strftime("%d"), po_date.strftime("%m"), po_date.strftime("%Y")
        po_preview = f"{dd}{mm}_{yyyy}_OQR_{short}"
        st.markdown(
            mono(f"NO. {po_preview}  ·  Deposit: {int(deposit_pct)}%", size="0.72rem", color="#555"),
            unsafe_allow_html=True,
        )

    st.markdown('<hr style="border:none;border-top:1px solid #e8e8e8;margin:0.8rem 0;">', unsafe_allow_html=True)

    # ── DANH SÁCH SẢN PHẨM ───────────────────────────────────
    st.markdown(section_label("📋", "DANH SÁCH SẢN PHẨM PRE-ORDER"), unsafe_allow_html=True)

    items = st.session_state[_KEY]

    if not items:
        st.markdown(
            mono("Chưa có sản phẩm — tìm kiếm và click để thêm vào pre-order.", color="#bbb"),
            unsafe_allow_html=True,
        )
    else:
        _render_header()
        st.markdown(
            '<hr style="border:none;border-top:1px solid #e0e0e0;margin:0.2rem 0 0.5rem;">',
            unsafe_allow_html=True,
        )

        to_remove = None

        for idx, item in enumerate(items):
            c_bc, c_desc, c_qty, c_note, c_del = st.columns([1.8, 5.0, 1.2, 2.8, 0.4])
            wkey = _widget_key(item, idx)

            with c_bc:
                st.markdown(mono(item["barcode"], size="0.72rem", color="#555"), unsafe_allow_html=True)

            with c_desc:
                st.markdown(
                    f'<span style="font-size:0.8rem;color:#111;line-height:1.3;">'
                    f'{item["description"]}</span>',
                    unsafe_allow_html=True,
                )

            with c_qty:
                qty = st.number_input(
                    "qty", min_value=0, value=int(item["quantity"]),
                    step=1, key=f"qty_{wkey}", label_visibility="collapsed",
                )
                item["quantity"] = qty

            with c_note:
                note = st.text_input(
                    "note", value=item.get("note", ""),
                    placeholder="Ghi chú…",
                    key=f"note_{wkey}", label_visibility="collapsed",
                )
                item["note"] = note

            with c_del:
                if st.button("✕", key=f"del_{wkey}", help="Xóa"):
                    to_remove = item["barcode"]

        if to_remove:
            remove_product(to_remove)
            st.rerun()

        # Footer
        st.markdown(
            '<hr style="border:none;border-top:2px solid #111;margin:0.4rem 0;">',
            unsafe_allow_html=True,
        )
        st.markdown(mono(f"{len(items)} SẢN PHẨM", size="0.68rem"), unsafe_allow_html=True)

    # ── Export buttons ────────────────────────────────────────
    if items:
        dd, mm, yyyy = po_date.strftime("%d"), po_date.strftime("%m"), po_date.strftime("%Y")
        po_number    = f"{dd}{mm}_{yyyy}_OQR_{short}"

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        b1, b2, b3, _ = st.columns([2.2, 1.8, 1.4, 4.6])

        with b1:
            # ── Lazy Generation cho Excel Template ────────────────
            current_params = (str(items), po_date, short, deposit_pct, template_path)
            
            if "sc_po_bytes" not in st.session_state:
                st.session_state["sc_po_bytes"] = None
                st.session_state["sc_po_params"] = None

            # Hủy cache nếu bất kỳ input nào thay đổi
            if st.session_state["sc_po_params"] != current_params:
                st.session_state["sc_po_bytes"] = None

            if st.session_state["sc_po_bytes"] is None:
                if template_path is None:
                    st.caption("⚠️ Tài file: Chọn template để tiếp tục")
                elif st.button("▶ Chuẩn bị file Pre-Order", help="Bấm để tạo file trước khi tải"):
                    with st.spinner("Đang dựng Excel…"):
                        b = _build_pre_order_template_bytes(
                            template_path,
                            items, po_date,
                            vendor_row.to_dict() if vendor_row is not None else {},
                            deposit_pct,
                        )
                        if b:
                            st.session_state["sc_po_bytes"] = b
                            st.session_state["sc_po_params"] = current_params
                            st.rerun()
                        else:
                            st.caption("⚠ Lỗi tạo file")
            else:
                st.download_button(
                    "⬇ Tải Pre-Order (PO+CI)",
                    data=st.session_state["sc_po_bytes"],
                    file_name=f"{po_number}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )


        with b2:
            st.download_button(
                "⬇ Xuất Excel (plain)",
                data=df_to_excel_bytes(_build_plain_df(items), "PreOrder"),
                file_name=f"plain_{po_number}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )


        with b3:
            if st.button("🗑 Xóa tất cả"):
                clear_all()
                st.rerun()


# ── Private helpers ───────────────────────────────────────────

def _render_header() -> None:
    cols = st.columns([1.8, 5.0, 1.2, 2.8, 0.4])
    for col, lbl in zip(cols, ["BARCODE", "DESCRIPTION", "QTY", "NOTE", ""]):
        col.markdown(mono(lbl, size="0.6rem"), unsafe_allow_html=True)


def _widget_key(item: dict, idx: int) -> str:
    safe = "".join(c if c.isalnum() else "_" for c in str(item["barcode"]))
    return f"{safe}_{idx}"


def _build_plain_df(items: list[dict]) -> pd.DataFrame:
    rows = [{
        "Barcode":     r["barcode"],
        "Description": r["description"],
        "Quantity":    r["quantity"],
        "Note":        r.get("note", ""),
    } for r in items]
    return pd.DataFrame(rows)


def _build_pre_order_template_bytes(
    template_path: str,
    items: list[dict],
    po_date: date,
    vendor: dict,
    deposit_pct: float,
) -> bytes | None:
    if template_path is None or not os.path.exists(template_path):
        return None
    try:
        from modules.export_pre_order import build_pre_order_bytes
        with open(template_path, "rb") as f:
            tmpl = f.read()
        return build_pre_order_bytes(tmpl, items, po_date, vendor, deposit_pct)
    except Exception as e:
        st.error(f"Lỗi xuất Pre-Order: {e}")
        return None