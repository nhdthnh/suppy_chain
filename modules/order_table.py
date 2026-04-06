"""
modules/order_table.py — Bảng Pre-Order.

Chức năng:
  · Quản lý state danh sách sản phẩm (add/remove/clear)
  · UI: date picker, vendor dropdown, deposit %, template selector
  · UI: bảng sản phẩm (barcode, description, qty, note, delete)
  · Export: xuất file Pre-Order (PO+CI) hoặc plain Excel

State API:
  · add_product(barcode, description)
  · remove_product(barcode)
  · clear_all()
  · get_items() → list[dict]
"""

import os
from datetime import date

import pandas as pd
import streamlit as st

from db.queries import query
from utils.excel import df_to_excel_bytes
from utils.styles import section_label, mono, divider, metric_card, badge


# ─────────────────────────────────────────────────────────────
# CONSTANTS & SESSION KEYS
# ─────────────────────────────────────────────────────────────

_KEY = "sc_order_items"
_VENDOR_KEY = "sc_vendor_id"
_DATE_KEY = "sc_po_date"
_DEPOSIT_KEY = "sc_deposit_pct"
_HERE = os.path.dirname(os.path.abspath(__file__))


# ─────────────────────────────────────────────────────────────
# STATE API
# ─────────────────────────────────────────────────────────────

def _init() -> None:
    """Khởi tạo danh sách sản phẩm nếu chưa có."""
    if _KEY not in st.session_state:
        st.session_state[_KEY] = []


def get_items() -> list[dict]:
    """Lấy danh sách sản phẩm hiện tại."""
    _init()
    return st.session_state[_KEY]


def add_product(barcode: str, description: str) -> None:
    """Thêm sản phẩm (nếu chưa có barcode trùng)."""
    _init()
    if not any(r["barcode"] == barcode for r in st.session_state[_KEY]):
        st.session_state[_KEY].append({
            "barcode": barcode,
            "description": description,
            "quantity": 1,
            "note": "",
        })


def remove_product(barcode: str) -> None:
    """Xóa sản phẩm theo barcode."""
    _init()
    st.session_state[_KEY] = [
        r for r in st.session_state[_KEY] if r["barcode"] != barcode
    ]


def clear_all() -> None:
    """Xóa toàn bộ danh sách."""
    st.session_state[_KEY] = []


# ─────────────────────────────────────────────────────────────
# VENDOR HELPERS
# ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=120, show_spinner=False)
def _load_vendors() -> pd.DataFrame:
    """Load danh sách vendor active từ DB."""
    return query(
        "SELECT id, short_name, name, address, tel, bank_name, "
        "bank_address, swift_code, beneficiary_name, account_number, "
        "beneficiary_address "
        "FROM vendors WHERE is_active = 1 ORDER BY short_name"
    )


def _get_vendor_template_dir(vendor_short_name: str) -> str | None:
    """Tìm thư mục template cho vendor."""
    base = os.path.join(_HERE, "..", "templates", "Pre-Order")
    if not os.path.exists(base):
        return None
    for d in os.listdir(base):
        if (
            d.lower() == vendor_short_name.lower()
            and os.path.isdir(os.path.join(base, d))
        ):
            return os.path.join(base, d)
    return None


# ─────────────────────────────────────────────────────────────
# PRIVATE UI HELPERS
# ─────────────────────────────────────────────────────────────

def _render_header() -> None:
    """Render header row với style mới."""
    st.markdown(
        '''
        <div style="background: #f8fafc; padding: 12px; border-radius: 8px; 
                    border: 1px solid #e2e8f0; margin-bottom: 8px;">
            <div style="display: grid; grid-template-columns: 1.8fr 5fr 1.2fr 2.8fr 0.4fr; gap: 10px;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #64748b; letter-spacing: 0.05em;">BARCODE</div>
                <div style="font-size: 0.75rem; font-weight: 700; color: #64748b; letter-spacing: 0.05em;">DESCRIPTION</div>
                <div style="font-size: 0.75rem; font-weight: 700; color: #64748b; letter-spacing: 0.05em;">QTY</div>
                <div style="font-size: 0.75rem; font-weight: 700; color: #64748b; letter-spacing: 0.05em;">NOTE</div>
                <div></div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )


def _widget_key(item: dict, idx: int) -> str:
    """Tạo unique key cho widget dựa trên barcode + index."""
    safe = "".join(c if c.isalnum() else "_" for c in str(item["barcode"]))
    return f"{safe}_{idx}"


def _build_plain_df(items: list[dict]) -> pd.DataFrame:
    """Convert danh sách sản phẩm thành DataFrame đơn giản."""
    return pd.DataFrame([{
        "Barcode": r["barcode"],
        "Description": r["description"],
        "Quantity": r["quantity"],
        "Note": r.get("note", ""),
    } for r in items])


def _build_pre_order_bytes(
    template_path: str,
    items: list[dict],
    po_date: date,
    vendor: dict,
    deposit_pct: float,
) -> bytes | None:
    """Tạo file Excel Pre-Order từ template.

    Returns:
        bytes của file Excel hoặc None nếu lỗi.
    """
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


# ─────────────────────────────────────────────────────────────
# RENDER — THÔNG TIN PRE-ORDER
# ─────────────────────────────────────────────────────────────

def _render_order_info() -> tuple:
    """Render phần thông tin PO: date, vendor, deposit, template.

    Returns:
        (po_date, vendor_row, short, deposit_pct, template_path)
    """
    st.markdown(
        section_label("⚙", "THÔNG TIN PRE-ORDER"), unsafe_allow_html=True
    )

    cfg1, cfg2, cfg3 = st.columns([2, 2, 1.5])

    # Date picker
    with cfg1:
        po_date = st.date_input(
            "📅 Ngày đặt hàng",
            value=st.session_state.get(_DATE_KEY, date.today()),
            key=_DATE_KEY,
            format="DD/MM/YYYY",
        )

    vendor_row = None
    short = "VENDOR"
    template_path = None

    # Vendor selector + template selector
    with cfg2:
        vendors_df = _load_vendors()
        if vendors_df.empty:
            st.warning("Chưa có vendor — thêm vào bảng vendors.")
        else:
            options = vendors_df["short_name"].tolist()
            sel_idx = st.session_state.get(_VENDOR_KEY, 0)
            selected = st.selectbox(
                "🏢 Vendor",
                options=options,
                index=min(sel_idx, len(options) - 1),
                key="_vendor_select",
            )
            st.session_state[_VENDOR_KEY] = options.index(selected)
            vendor_row = vendors_df[
                vendors_df["short_name"] == selected
            ].iloc[0]
            short = (vendor_row.get("short_name") or "VENDOR").strip()

            v_dir = _get_vendor_template_dir(short)
            templates_list = (
                [f for f in os.listdir(v_dir) if f.endswith(".xlsx")]
                if v_dir
                else []
            )

            if templates_list:
                sel_tmpl = st.selectbox(
                    "📋 Template Excel",
                    options=templates_list,
                    key=f"sc_tmpl_{short}",
                )
                if sel_tmpl:
                    template_path = os.path.join(v_dir, sel_tmpl)
            else:
                st.caption(
                    f"⚠️ Chưa có file template trong "
                    f"`templates/Pre-Order/{short}`"
                )

    # Deposit input
    with cfg3:
        deposit_pct = st.number_input(
            "💰 Deposit (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(st.session_state.get(_DEPOSIT_KEY, 70.0)),
            step=5.0,
            format="%.0f",
            key=_DEPOSIT_KEY,
            help="Ví dụ: 70 → Deposit = Amount × 70%",
        )

    # PO number preview
    if vendor_row is not None:
        dd = po_date.strftime("%d")
        mm = po_date.strftime("%m")
        yyyy = po_date.strftime("%Y")
        po_preview = f"{dd}{mm}_{yyyy}_OQR_{short}"
        st.markdown(
            mono(
                f"NO. {po_preview}  ·  Deposit: {int(deposit_pct)}%",
                size="0.9rem",
                color="#666",
            ),
            unsafe_allow_html=True,
        )

    return po_date, vendor_row, short, deposit_pct, template_path


def _render_summary(items: list[dict], vendor_short: str, deposit: float) -> None:
    """Hiển thị tóm tắt bằng các metric cards cao cấp."""
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(metric_card("SẢN PHẨM", str(len(items))), unsafe_allow_html=True)
    with m2:
        st.markdown(metric_card("VENDOR", vendor_short), unsafe_allow_html=True)
    with m3:
        st.markdown(metric_card("DEPOSIT", f"{int(deposit)}%"), unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# RENDER — DANH SÁCH SẢN PHẨM
# ─────────────────────────────────────────────────────────────

def _render_product_list(items: list[dict]) -> None:
    """Render danh sách sản phẩm (hoặc placeholder nếu trống)."""
    st.markdown(
        section_label("📋", "DANH SÁCH SẢN PHẨM PRE-ORDER"),
        unsafe_allow_html=True,
    )

    if not items:
        st.info("Chưa có sản phẩm — tìm kiếm và click để thêm vào danh sách.")
        return

    _render_header()

    to_remove = None

    for idx, item in enumerate(items):
        c_bc, c_desc, c_qty, c_note, c_del = st.columns(
            [1.8, 5.0, 1.2, 2.8, 0.4]
        )
        wkey = _widget_key(item, idx)

        with c_bc:
            st.markdown(
                mono(item["barcode"], size="0.95rem", color="#444"),
                unsafe_allow_html=True,
            )

        with c_desc:
            st.markdown(
                f'<span style="font-family:\'Source Sans\',sans-serif;'
                f'font-size:1.05rem;font-weight:500;line-height:1.35;">'
                f'{item["description"]}</span>',
                unsafe_allow_html=True,
            )

        with c_qty:
            qty = st.number_input(
                "qty",
                min_value=0,
                value=int(item["quantity"]),
                step=1,
                key=f"qty_{wkey}",
                label_visibility="collapsed",
            )
            item["quantity"] = qty

        with c_note:
            note = st.text_input(
                "note",
                value=item.get("note", ""),
                placeholder="Ghi chú…",
                key=f"note_{wkey}",
                label_visibility="collapsed",
            )
            item["note"] = note

        with c_del:
            if st.button("✕", key=f"del_{wkey}", help="Xóa dòng", type="secondary"):
                to_remove = item["barcode"]
        
        # Subtle divider between items
        st.markdown('<div style="border-bottom: 1px solid #f1f5f9; margin: 4px 0;"></div>', unsafe_allow_html=True)

    if to_remove:
        remove_product(to_remove)
        st.rerun()

    st.markdown(f'<div style="margin-top: 12px;">{badge(f"TOTAL: {len(items)} ITEMS", True)}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# RENDER — EXPORT BUTTONS
# ─────────────────────────────────────────────────────────────

def _render_export_buttons(
    items: list[dict],
    po_date: date,
    short: str,
    deposit_pct: float,
    template_path: str | None,
    vendor_row,
) -> None:
    """Render các nút export: Pre-Order (PO+CI), Plain Excel, Xóa tất cả."""
    dd = po_date.strftime("%d")
    mm = po_date.strftime("%m")
    yyyy = po_date.strftime("%Y")
    po_number = f"{dd}{mm}_{yyyy}_OQR_{short}"

    st.markdown(
        "<div style='height:10px'></div>", unsafe_allow_html=True
    )
    b1, b2, b3, _ = st.columns([2.2, 1.8, 1.4, 4.6])

    # ── Pre-Order (PO+CI) ────────────────────────────────
    with b1:
        current_params = (
            str(items), po_date, short, deposit_pct, template_path
        )

        if "sc_po_bytes" not in st.session_state:
            st.session_state["sc_po_bytes"] = None
            st.session_state["sc_po_params"] = None

        if st.session_state["sc_po_params"] != current_params:
            st.session_state["sc_po_bytes"] = None

        if st.session_state["sc_po_bytes"] is None:
            if template_path is None:
                st.caption("⚠️ Chọn template để tiếp tục")
            elif st.button(
                "▶ Chuẩn bị file Pre-Order",
                help="Tạo file trước khi tải",
            ):
                with st.spinner("Đang dựng Excel…"):
                    b = _build_pre_order_bytes(
                        template_path,
                        items,
                        po_date,
                        vendor_row.to_dict()
                        if vendor_row is not None
                        else {},
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
                mime="application/vnd.openxmlformats-officedocument"
                     ".spreadsheetml.sheet",
            )

    # ── Plain Excel ───────────────────────────────────────
    with b2:
        st.download_button(
            "⬇ Xuất Excel (plain)",
            data=df_to_excel_bytes(
                _build_plain_df(items), "PreOrder"
            ),
            file_name=f"plain_{po_number}.xlsx",
            mime="application/vnd.openxmlformats-officedocument"
                 ".spreadsheetml.sheet",
        )

    # ── Xóa tất cả ───────────────────────────────────────
    with b3:
        if st.button("🗑 Xóa tất cả"):
            clear_all()
            st.rerun()


# ─────────────────────────────────────────────────────────────
# PUBLIC RENDER
# ─────────────────────────────────────────────────────────────

def render() -> None:
    """Render toàn bộ section bảng Pre-Order."""
    _init()

    # 1. Thông tin PO
    po_date, vendor_row, short, deposit_pct, template_path = (
        _render_order_info()
    )

    st.markdown(divider(), unsafe_allow_html=True)
    
    # 2. Summary Metrics
    items = st.session_state[_KEY]
    _render_summary(items, short, deposit_pct)
    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)

    # 3. Danh sách sản phẩm
    _render_product_list(items)

    # 4. Export buttons (chỉ hiện khi có sản phẩm)
    if items:
        _render_export_buttons(
            items, po_date, short, deposit_pct, template_path, vendor_row
        )
