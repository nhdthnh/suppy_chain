import os

filepath = "u:\\supply_chain\\modules\\order_table.py"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Chunk 1: Helpers
old_helper = """_HERE          = os.path.dirname(os.path.abspath(__file__))
_TEMPLATE_PATH = os.path.join(_HERE, "..", "templates", "PRE ORDER_OQR_LIEBU (templates).xlsx")"""

new_helper = """_HERE          = os.path.dirname(os.path.abspath(__file__))

def _get_vendor_template_dir(vendor_short_name: str) -> str | None:
    base = os.path.join(_HERE, "..", "templates", "Pre-Order")
    if not os.path.exists(base):
        return None
    for d in os.listdir(base):
        if d.lower() == vendor_short_name.lower() and os.path.isdir(os.path.join(base, d)):
            return os.path.join(base, d)
    return None"""

content = content.replace(old_helper, new_helper)

# Chunk 2: render() Vendor select selectbox dropdown
old_vendor = """    vendor_row = None
    short      = "VENDOR"

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
            short      = (vendor_row.get("short_name") or "VENDOR").strip()"""

new_vendor = """    vendor_row = None
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
                st.caption(f"⚠️ Chưa có file template trong `templates/Pre-Order/{short}`")"""

content = content.replace(old_vendor, new_vendor)

# Chunk 3: current_params
content = content.replace(
    "current_params = (str(items), po_date, short, deposit_pct)",
    "current_params = (str(items), po_date, short, deposit_pct, template_path)"
)

# Chunk 4: build button
old_btn = """            if st.session_state["sc_po_bytes"] is None:
                if st.button("▶ Chuẩn bị file PO+CI", help="Bấm để tạo file trước khi tải"):
                    with st.spinner("Đang dựng Excel…"):
                        b = _build_po_template_bytes(
                            items, po_date,
                            vendor_row.to_dict() if vendor_row is not None else {},
                            deposit_pct,
                        )
                        if b:
                            st.session_state["sc_po_bytes"] = b
                            st.session_state["sc_po_params"] = current_params
                            st.rerun()
                        else:
                            st.caption("⚠ Lỗi tạo file")"""

new_btn = """            if st.session_state["sc_po_bytes"] is None:
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
                            st.caption("⚠ Lỗi tạo file")"""

content = content.replace(old_btn, new_btn)

# Chunk 5: build func
old_func = """def _build_po_template_bytes(
    items: list[dict],
    po_date: date,
    vendor: dict,
    deposit_pct: float,
) -> bytes | None:
    if not os.path.exists(_TEMPLATE_PATH):
        return None
    try:
        from modules.export_po import build_po_bytes
        with open(_TEMPLATE_PATH, "rb") as f:
            tmpl = f.read()
        return build_po_bytes(tmpl, items, po_date, vendor, deposit_pct)
    except Exception as e:
        st.error(f"Lỗi xuất PO: {e}")
        return None"""

new_func = """def _build_pre_order_template_bytes(
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
        return None"""

content = content.replace(old_func, new_func)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied successfully!")
