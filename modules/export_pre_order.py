"""
modules/export_pre_order.py

Điền sản phẩm vào template Excel — sheet PO + sheet CI.
Sử dụng config/export_pre_order.json để render động và dễ bảo trì.
"""

import io
import os
import json
import copy
from datetime import date
from openpyxl import load_workbook

_HERE        = os.path.dirname(os.path.abspath(__file__))
_CONFIG_PATH = os.path.join(_HERE, "..", "config", "export_pre_order.json")

# ── Default Fallback Config ───────────────────────────────────
_DEFAULT_CONFIG = {
  "sheets": [
    {
      "name": "PO",
      "first_row": 15,
      "ref_row": 15,
      "fields": {
        "F2": { "type": "date", "format": "%d/%m/%Y" },
        "F3": { "type": "po_number" }
      },
      "columns": [
        { "col": 1, "type": "formula", "value": "=VLOOKUP(C{row}, 'master data'!$A:$B, 2, 0)" },
        { "col": 2, "type": "formula", "value": "=VLOOKUP(C{row}, 'master data'!$A:$C, 3, 0)" },
        { "col": 3, "type": "field", "value": "description" },
        { "col": 4, "type": "field", "value": "quantity", "cast": "int" },
        { "col": 5, "type": "formula", "value": "=VLOOKUP(C{row}, 'master data'!$A:$D, 4, 0)" },
        { "col": 6, "type": "formula", "value": "=D{row}*E{row}" },
        { "col": 7, "type": "field", "value": "note" }
      ],
      "totals": [
        { "col": 4, "formula": "=SUM(D{start}:D{end})" },
        { "col": 6, "formula": "=SUM(F{start}:F{end})" }
      ],
      "total_search_text": "TOTAL"
    },
    {
      "name": "CI",
      "first_row": 12,
      "ref_row": 12,
      "fields": {
        "E4": { "type": "date", "format": "%d/%m/%Y" }
      },
      "columns": [
        { "col": 1, "type": "formula", "value": "=VLOOKUP(C{row}, 'master data'!$A:$B, 2, 0)" },
        { "col": 2, "type": "formula", "value": "=VLOOKUP(C{row}, 'master data'!$A:$C, 3, 0)" },
        { "col": 3, "type": "field", "value": "description" },
        { "col": 4, "type": "field", "value": "quantity", "cast": "int" },
        { "col": 5, "type": "formula", "value": "=VLOOKUP(C{row}, 'master data'!$A:$D, 4, 0)" },
        { "col": 6, "type": "formula", "value": "=E{row}*D{row}" },
        { "col": 7, "type": "formula", "value": "=F{row}*{deposit_pct}%" }
      ],
      "totals": [
        { "col": 4, "formula": "=SUM(D{start}:D{end})" },
        { "col": 6, "formula": "=SUM(F{start}:F{end})" },
        { "col": 7, "formula": "=SUM(G{start}:G{end})" }
      ],
      "total_search_text": "TOTAL"
    }
  ]
}

def _load_config() -> dict:
    if os.path.exists(_CONFIG_PATH):
        try:
            with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return _DEFAULT_CONFIG


# ── Style helpers ─────────────────────────────────────────────

def _copy_cell_style(src, dst) -> None:
    if src.has_style:
        dst.font          = copy.copy(src.font)
        dst.border        = copy.copy(src.border)
        dst.fill          = copy.copy(src.fill)
        dst.number_format = src.number_format
        dst.alignment     = copy.copy(src.alignment)


def _copy_row_style(ws_src, src_row: int, ws_dst, dst_row: int, max_col: int = 10) -> None:
    for col in range(1, max_col + 1):
        _copy_cell_style(ws_src.cell(src_row, col), ws_dst.cell(dst_row, col))


def _safe_set(ws, row: int, col: int, value) -> None:
    c = ws.cell(row, col)
    if type(c).__name__ != "MergedCell":
        c.value = value


# ── Row helpers ───────────────────────────────────────────────

def _find_total_row(ws, first_row: int, search_text: str = "TOTAL") -> int:
    for r in range(first_row, ws.max_row + 5):
        if ws.cell(r, 1).value == search_text:
            return r
    return first_row + 4


def _hide_row(ws, row: int) -> None:
    ws.row_dimensions[row].height = 0
    ws.row_dimensions[row].hidden = True
    for col in range(1, 10):
        _safe_set(ws, row, col, None)


def _show_row(ws, row: int, height: float) -> None:
    ws.row_dimensions[row].height = height
    ws.row_dimensions[row].hidden = False


# ── Pass 1: chỉ insert nếu cần thêm rows ─────────────────────

def _structural_pass(tmpl: bytes, n: int, config: dict) -> bytes:
    wb = load_workbook(io.BytesIO(tmpl))
    sheets_cfg = config.get("sheets", [])

    for scfg in sheets_cfg: 
        sname = scfg["name"]
        first = scfg["first_row"]
        if sname not in wb.sheetnames:
            continue
        ws        = wb[sname]
        total_row = _find_total_row(ws, first, scfg.get("total_search_text", "TOTAL"))
        old_count = total_row - first
        diff      = n - old_count

        if diff > 0:
            for mr in [str(m) for m in ws.merged_cells.ranges if m.min_row >= first]:
                ws.merged_cells.remove(mr)
            ws.insert_rows(total_row, diff)

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ── Pass 2: ghi data ──────────────────────────────────────────

def _write_sheet(ws, ws_ref, items: list[dict], po_date: date, po_number: str, deposit_pct: float, cfg: dict) -> None:
    F          = cfg.get("first_row", 15)
    n          = len(items)
    total_text = cfg.get("total_search_text", "TOTAL")
    total_row  = _find_total_row(ws, F, total_text)

    # 1. Điền static fields (Date, PO number...)
    fields_cfg = cfg.get("fields", {})
    for cell_addr, fcfg in fields_cfg.items():
        type_ = fcfg.get("type")
        val = None
        if type_ == "date":
            fmt = fcfg.get("format", "%d/%m/%Y")
            val = po_date.strftime(fmt)
        elif type_ == "po_number":
            val = po_number
        if val is not None:
            ws[cell_addr] = val

    # 2. Clear toàn bộ vùng data
    for r in range(F, total_row):
        for col in range(1, 10):
            _safe_set(ws, r, col, None)

    # 3. Ghi sản phẩm
    ref_row = cfg.get("ref_row", F)
    data_h  = ws_ref.row_dimensions[ref_row].height or 47.25
    pct     = int(deposit_pct) if deposit_pct == int(deposit_pct) else deposit_pct

    for idx, item in enumerate(items):
        r = F + idx
        _show_row(ws, r, data_h)
        _copy_row_style(ws_ref, ref_row, ws, r)

        for col_cfg in cfg.get("columns", []):
            c_idx        = col_cfg["col"]
            type_        = col_cfg["type"]
            val_template = col_cfg.get("value", "")

            if type_ == "formula":
                try:
                    val = val_template.format(row=r, deposit_pct=pct)
                except Exception:
                    val = val_template
                ws.cell(r, c_idx).value = val
            elif type_ == "field":
                val  = item.get(val_template, "")
                cast = col_cfg.get("cast")
                if cast == "int":
                    try: val = int(val)
                    except: val = 0
                ws.cell(r, c_idx).value = val

    # 4. Ẩn rows thừa
    for r in range(F + n, total_row):
        _hide_row(ws, r)

    # 5. Cập nhật TOTAL formula
    for tcfg in cfg.get("totals", []):
        c_idx     = tcfg["col"]
        form_tmpl = tcfg["formula"]
        try:
            val = form_tmpl.format(start=F, end=F+n-1)
        except Exception:
            val = form_tmpl
        ws.cell(total_row, c_idx).value = val


# ── Public API ────────────────────────────────────────────────

def build_pre_order_bytes(
    template_bytes: bytes,
    items: list[dict],
    po_date: date,
    vendor: dict,
    deposit_pct: float = 70.0,
) -> bytes:
    if not items:
        return template_bytes

    dd, mm, yyyy = po_date.strftime("%d"), po_date.strftime("%m"), po_date.strftime("%Y")
    short     = (vendor.get("short_name") or vendor.get("name", "VENDOR")).strip()
    po_number = f"{dd}{mm}_{yyyy}_OQR_{short}"

    config   = _load_config()
    adjusted = _structural_pass(template_bytes, len(items), config)

    wb     = load_workbook(io.BytesIO(adjusted))
    wb_ref = load_workbook(io.BytesIO(template_bytes))

    for scfg in config.get("sheets", []):
        name = scfg["name"]
        if name in wb.sheetnames:
            _write_sheet(wb[name], wb_ref[name], items, po_date, po_number, deposit_pct, scfg)

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
