"""
pages/view_templates.py
Trang xem trước các file Excel Templates.
"""

import os
import streamlit as st
import pandas as pd
from utils.styles import page_header, section_label


def _excel_to_html(filepath: str, sheet_name: str) -> str:
    from openpyxl import load_workbook
    from openpyxl.utils import get_column_letter
    import html as html_lib

    wb = load_workbook(filepath, data_only=True)
    if sheet_name not in wb.sheetnames:
        return "Sheet không tồn tại"
    ws = wb[sheet_name]

    # Map merged cells để tính rowspan, colspan
    merged = {}
    for mr in ws.merged_cells.ranges:
        min_row, min_col, max_row, max_col = mr.min_row, mr.min_col, mr.max_row, mr.max_col
        for r in range(min_row, max_row + 1):
            for c in range(min_col, max_col + 1):
                if r == min_row and c == min_col:
                    merged[(r, c)] = {
                        "rowspan": max_row - min_row + 1,
                        "colspan": max_col - min_col + 1
                    }
                else:
                    merged[(r, c)] = "slave"

    # Styles cho các thanh mục lục Excel (1, 2, 3, A, B, C)
    IDX_STYLE = (
        'background-color:#f8f9fa; text-align:center; font-weight:600; color:#444; '
        'border:1px solid #d1d5db; padding:3px 5px; font-family:sans-serif; font-size:0.68rem;'
    )

    html_code = '<table style="border-collapse:collapse; font-family:\'Segoe UI\',Arial,sans-serif;' \
                'font-size:0.78rem; border:1px solid #d1d5db; color:#222; background-color:#fff; width:max-content;">'
    
    # ── 1. Tạo hàng tiêu đề Cột (A, B, C...) ───────────────────
    html_code += '<tr>'
    html_code += f'<td style="{IDX_STYLE} border-bottom:2px solid #bbb; width:35px;"></td>' # Góc trái trên
    for c in range(1, ws.max_column + 1):
        letter = get_column_letter(c)
        # Tính toán chiều rộng gần đúng (excel width * 7-8 pixel)
        col_dim = ws.column_dimensions.get(letter)
        width = col_dim.width if col_dim and col_dim.width else 8.43
        w_px = int(width * 8.5)
        html_code += f'<td style="{IDX_STYLE} border-bottom:2px solid #bbb; width:{w_px}px; min-width:{w_px}px;">' \
                     f'{letter}</td>'
    html_code += '</tr>'

    # ── 2. Tạo dữ liệu các Hàng ───────────────────────────────
    for r in range(1, ws.max_row + 1):
        html_code += '<tr style="height:25px;">'
        
        # Mục lục dòng (1, 2, 3...)
        html_code += f'<td style="{IDX_STYLE} border-right:2px solid #bbb;">{r}</td>'

        for c in range(1, ws.max_column + 1):
            cell_key = (r, c)
            status = merged.get(cell_key)
            
            if status == "slave":
                continue
                
            cell = ws.cell(r, c)
            val  = cell.value if cell.value is not None else ""
            val  = html_lib.escape(str(val)) if val != "" else "&nbsp;"

            rowspan = 1
            colspan = 1
            if isinstance(status, dict):
                rowspan = status["rowspan"]
                colspan = status["colspan"]

            styles = ["border:1px solid #e2e8f0; padding:5px 8px;"]

            # 1. Background Fill
            if cell.fill and cell.fill.start_color:
                sc = cell.fill.start_color
                rgb = sc.rgb if hasattr(sc, 'rgb') and sc.rgb else None
                if rgb and isinstance(rgb, str) and rgb != "00000000":
                    if len(rgb) == 8: rgb = rgb[2:]
                    if rgb.upper() not in ["FFFFFF", "000000"]:
                        styles.append(f"background-color:#{rgb};")

            # 2. Font Styles
            if cell.font:
                if cell.font.bold: styles.append("font-weight:bold;")
                if cell.font.italic: styles.append("font-style:italic;")
                frgb = cell.font.color.rgb if cell.font.color and hasattr(cell.font.color, 'rgb') else None
                if frgb and isinstance(frgb, str) and frgb != "00000000":
                    if len(frgb) == 8: frgb = frgb[2:]
                    if frgb.upper() != "000000":
                         styles.append(f"color:#{frgb};")

            # 3. Alignment
            if cell.alignment:
                if cell.alignment.horizontal:
                    h = cell.alignment.horizontal
                    if h == 'centre': h = 'center'
                    styles.append(f"text-align:{h};")
                if cell.alignment.vertical:
                    v = cell.alignment.vertical
                    if v == 'centre': v = 'center'
                    styles.append(f"vertical-align:{v};")

            style_str = "".join(styles)
            r_attr = f' rowspan="{rowspan}"' if rowspan > 1 else ""
            c_attr = f' colspan="{colspan}"' if colspan > 1 else ""
            
            html_code += f'<td{r_attr}{c_attr} style="{style_str}">{val}</td>'
        html_code += '</tr>'
    html_code += '</table>'
    return html_code


def render() -> None:
    st.markdown(page_header("supply_chain / templates", "XEM TEMPLATES EXCEL"), unsafe_allow_html=True)

    base = os.path.join(os.path.dirname(__file__), "..", "templates")
    if not os.path.exists(base):
        st.error("Thư mục `templates` không tồn tại.")
        return

    types = [d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d)) and not d.startswith(".")]
    if not types:
        st.warning("Không tìm thấy thư mục con nào trong `templates`.")
        return

    c1, c2 = st.columns([3, 7])
    with c1:
        selected_type = st.selectbox("📂 Loại Biểu mẫu", options=types, key="tmpl_type_select")

    type_path = os.path.join(base, selected_type)
    vendors = [d for d in os.listdir(type_path) if os.path.isdir(os.path.join(type_path, d)) and not d.startswith(".")]

    template_file = None

    with c2:
        if not vendors:
            st.info(f"Chưa có thư mục Vendor cho `{selected_type}`.")
        else:
            selected_vendor = st.selectbox("🏢 Vendor", options=vendors, key="tmpl_vendor_select")
            vendor_path = os.path.join(type_path, selected_vendor)
            files = [f for f in os.listdir(vendor_path) if f.endswith(".xlsx")]
            
            if not files:
                st.warning(f"Chưa có file `.xlsx` trong `templates/{selected_type}/{selected_vendor}`.")
            else:
                selected_file = st.selectbox("📄 File Template", options=files, key="tmpl_file_select")
                template_file = os.path.join(vendor_path, selected_file)

    st.markdown('<hr style="border:none;border-top:1px solid #e8e8e8;margin:0.8rem 0;">', unsafe_allow_html=True)

    if template_file:
        st.markdown(section_label("📊", f"BẢN XEM TRƯỚC: {os.path.basename(template_file)}"), unsafe_allow_html=True)
        try:
            from openpyxl import load_workbook
            wb_sheets = load_workbook(template_file, read_only=True).sheetnames
            
            if not wb_sheets:
                st.warning("File Excel này không có sheet nào.")
                return

            sc1, _ = st.columns([3, 7])
            with sc1:
                selected_sheet = st.selectbox("🔍 Chọn Sheet", options=wb_sheets, key="tmpl_sheet_select")

            with st.spinner("Đang kết xuất biểu mẫu…"):
                try:
                    import io
                    from xlsx2html import xlsx2html
                    
                    html_buf = io.StringIO()
                    xlsx2html(template_file, html_buf, sheet=selected_sheet)
                    html_view = html_buf.getvalue()
                    
                    style_override = (
                        "<style>"
                        "table { border-collapse: collapse !important; width: max-content !important; font-family: 'Segoe UI', Arial, sans-serif !important; font-size: 0.78rem !important; }"
                        "td { border: 1px solid #e2e8f0 !important; padding: 5px 8px !important; }"
                        "</style>"
                    )
                    html_view = style_override + html_view
                    
                except ImportError:
                    # Fallback về Render có Grid Index (A, B, C, 1, 2, 3) tôi viết ở trước
                    html_view = _excel_to_html(template_file, selected_sheet)

            st.markdown(
                f'<div style="overflow-x:auto; overflow-y:auto; max-height:600px; border:1px solid #f1f5f9;border-radius:6px; background-color:#fff; padding:10px;">'
                f'{html_view}</div>',
                unsafe_allow_html=True
            )
            
        except Exception as e:
            st.error(f"Lỗi đọc file Excel: {e}")
