# 🛠️ Hướng dẫn phát triển — Supply Chain

## Convention chung

### Code style
- **Docstring**: Mỗi file phải có module-level docstring giải thích chức năng
- **Functions**: Mỗi function có docstring ngắn gồm Args + Returns
- **Constants**: Đặt ở đầu file, UPPER_SNAKE_CASE
- **Private**: Hàm private bắt đầu bằng `_`
- **Type hints**: Luôn dùng type hints cho function signatures

### Tổ chức file
- `pages/` — Mỗi file = 1 trang, có hàm `render()` public
- `modules/` — Business logic phức tạp, tái sử dụng
- `components/` — UI widgets tái sử dụng
- `utils/` — Pure utility functions
- `db/` — Database operations only
- `scripts/` — One-time scripts, KHÔNG import trong app

---

## Thêm page mới

### 1. Tạo file trong `pages/`

```python
"""pages/new_page.py — Mô tả trang."""

import streamlit as st
from utils.styles import page_header


def render() -> None:
    """Render trang."""
    st.markdown(
        page_header("supply_chain / new", "TIÊU ĐỀ TRANG"),
        unsafe_allow_html=True,
    )
    # ... UI code
```

### 2. Thêm vào sidebar navigation

Sửa `components/sidebar.py`:

```python
NAV_ITEMS: list[tuple[str, str]] = [
    # ... existing items
    ("🆕  NEW PAGE",  "new_page"),   # ← thêm dòng này
]
```

### 3. Đăng ký trong `app.py`

```python
from pages import new_page  # ← thêm import

PAGES = {
    # ... existing pages
    "new_page": new_page,   # ← thêm mapping
}
```

---

## Thêm vendor template

### 1. Tạo thư mục

```
templates/Pre-Order/<VENDOR_SHORT_NAME>/
```

Tên thư mục phải khớp với `short_name` trong bảng `vendors` (case-insensitive).

### 2. Đặt file template

Copy file `.xlsx` template vào thư mục vừa tạo. File template cần có:
- Sheet "PO" với row TOTAL ở cột 1
- Sheet "CI" với row TOTAL ở cột 1
- Sheet "master data" chứa bảng VLOOKUP
- Cấu trúc theo `config/export_pre_order.json`

### 3. Tùy chỉnh config (nếu cần)

Nếu template mới có cấu trúc khác, sửa `config/export_pre_order.json`:

```json
{
  "sheets": [
    {
      "name": "PO",
      "first_row": 15,          // Row đầu tiên chứa data
      "ref_row": 15,            // Row tham chiếu style
      "total_search_text": "TOTAL",
      "fields": { ... },
      "columns": [ ... ],
      "totals": [ ... ]
    }
  ]
}
```

---

## Database

### Thêm SQL query mới

Thêm vào `db/queries.py` với cache phù hợp:

```python
@st.cache_data(ttl=60, show_spinner=False)
def my_new_query(param: str) -> pd.DataFrame:
    """Mô tả query."""
    return query("SELECT ... WHERE col = %s", (param,))
```

### Cache TTL guide

| Loại data | TTL | Lý do |
|-----------|-----|-------|
| Schema (tables, columns) | 120s | Rất ít thay đổi |
| Count rows | 30s | Thay đổi khi import |
| Search results | 15s | User cần data mới |
| Page data | 20s | Cân bằng speed/freshness |

---

## CSS Styling

### Thêm style mới

Thêm CSS vào `GLOBAL_CSS` trong `utils/styles.py`:

```python
GLOBAL_CSS = """
<style>
/* ... existing CSS ... */

/* ═══ MY NEW SECTION ═══ */
.my-new-class {
    font-size: 1rem;
    color: var(--text-color, #111);
}
</style>
"""
```

### HTML helpers

Thêm helper function mới trong `utils/styles.py`:

```python
def my_helper(text: str) -> str:
    """Render my custom element."""
    return f'<div class="my-new-class">{text}</div>'
```

Sử dụng:
```python
from utils.styles import my_helper
st.markdown(my_helper("Hello"), unsafe_allow_html=True)
```

---

## Troubleshooting

### App không chạy
1. Kiểm tra `.streamlit/secrets.toml` có đúng credentials
2. Kiểm tra `log/log.xlsx` tồn tại (chạy `python scripts/create_log_file.py`)
3. Kiểm tra MySQL server đang chạy

### Sidebar bị lỗi UI
- KHÔNG thêm `width` cứng cho sidebar
- KHÔNG dùng `position: absolute` trong sidebar
- Dùng flex-grow spacer thay vì absolute positioning

### Cache không refresh
```python
st.cache_data.clear()  # Clear tất cả cache
```

### Import lỗi
- Kiểm tra mapping cột có đúng không
- Kiểm tra data type phù hợp với schema DB
- Dùng INSERT IGNORE để skip trùng khóa
