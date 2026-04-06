# 🏗️ Kiến trúc ứng dụng — Supply Chain v2.5

## Tổng quan

Ứng dụng Streamlit single-page, dùng `st.sidebar` + `st.radio` để điều hướng.  
Dữ liệu lưu trong MySQL, xác thực qua file Excel (`log/log.xlsx`).

---

## Sơ đồ kiến trúc

```
┌──────────────────────────────────────────────────────────┐
│                        app.py                            │
│             (Entry point · Auth · Routing)               │
├──────────────┬───────────────────────────────────────────┤
│  login.py    │       components/sidebar.py               │
│  (Auth)      │       (Navigation → page_key)             │
├──────────────┴───────────────────────────────────────────┤
│                         PAGES                            │
│  search_order · data_browser · import_excel              │
│  export_excel · view_templates · about                   │
├──────────────────────────────────────────────────────────┤
│                       MODULES                            │
│  product_search · order_table · export_pre_order         │
├──────────────────────────────────────────────────────────┤
│  COMPONENTS       │  DB                │  UTILS          │
│  sidebar.py       │  connection.py     │  styles.py      │
│  filter.py        │  queries.py        │  excel.py       │
└──────────────────────────────────────────────────────────┘
```

---

## Cấu trúc thư mục

```
supply_chain/
├── app.py                    # Entry point: config → auth → routing
├── login.py                  # Authentication: login / logout / auto-login
│
├── components/
│   ├── __init__.py
│   ├── sidebar.py            # Sidebar + APP_VERSION constant
│   └── filter.py             # Bộ lọc bảng DB (auto-detect columns)
│
├── pages/
│   ├── search_order.py       # Lập Pre-Order
│   ├── data_browser.py       # Xem/sửa dữ liệu bảng
│   ├── import_excel.py       # Import Excel → MySQL
│   ├── export_excel.py       # Export MySQL → Excel
│   ├── view_templates.py     # Xem trước templates Excel
│   └── about.py              # Thông tin ứng dụng + changelog
│
├── modules/
│   ├── product_search.py     # Tìm kiếm sản phẩm (multiselect)
│   ├── order_table.py        # Bảng đơn hàng + state management
│   └── export_pre_order.py   # Ghi sản phẩm vào template Excel
│
├── db/
│   ├── connection.py         # MySQL connection + cache + reconnect
│   └── queries.py            # Tất cả SQL queries (cached)
│
├── utils/
│   ├── styles.py             # GLOBAL_CSS + HTML helper functions
│   └── excel.py              # Excel read/write helpers
│
├── config/
│   ├── export_pre_order.json # Config sheet PO + CI
│   └── export_po.json        # Config sheet PO only
│
├── templates/
│   └── Pre-Order/
│       └── <VENDOR>/         # Mỗi vendor 1 folder (khớp short_name)
│           └── *.xlsx
│
├── scripts/
│   ├── create_log_file.py    # Tạo log/log.xlsx ban đầu
│   ├── manage_users.py       # Quản lý user (CLI)
│   ├── setup_login.py        # Wizard cài đặt
│   ├── check_db_size.py      # Kiểm tra kích thước DB
│   ├── create_debt_tracking.py
│   ├── create_debt_triggers.py
│   ├── import_products_eng.py
│   └── debug/                # Scripts debug (không dùng trong production)
│       ├── check_sheets.py
│       ├── check_sheets_fast.py
│       ├── check_template_v4.py
│       └── debug_template_pd.py
│
├── log/                      # Gitignored
│   └── log.xlsx
│
├── docs/
│   ├── README.md
│   ├── USER_GUIDE.md         # Hướng dẫn sử dụng đầy đủ
│   ├── ARCHITECTURE.md       # File này
│   └── DEVELOPMENT.md
│
└── .streamlit/
    ├── config.toml           # Theme + server config
    └── secrets.toml          # MySQL credentials (gitignored)
```

---

## Data Flow

### Request Flow

```
User → Browser
  → app.py (check auth)
    → login.py          ← nếu chưa auth → show login form
    → sidebar.render()  → page_key
    → PAGES[page_key].render()
      → db/queries.py   → MySQL
      → utils/styles.py (HTML helpers)
  → Browser (render)
```

### Pre-Order Flow

```
search_order.py
  → product_search.render(filter_result)
      → DB: SELECT barcode, description FROM products_eng
      → st.multiselect → user chọn → order_table.add_product()
  → order_table.render()
      → _render_order_info()   → date / vendor / template / deposit
      → _render_product_list() → barcode | desc | qty | note | delete
      → _render_export_buttons()
          → _build_pre_order_bytes()
              → export_pre_order.build_pre_order_bytes()
                  → structural pass (insert rows)
                  → data pass (ghi formulas + fields)
                  → sync pass (đọc master data → price_map)
              → _save_to_db(sync_data, po_number, vendor_id)
          → st.download_button
```

### Import / Export Flow

```
import_excel.py
  → Upload .xlsx → chọn sheet → preview 5 dòng
  → Mapping cột Excel → cột DB
  → executemany(INSERT [IGNORE] INTO ...) → MySQL

export_excel.py
  → Xuất 1 bảng   : SELECT * → df_to_excel_bytes → download
  → Xuất nhiều    : multi_df_to_excel_bytes → download
  → SQL tùy chỉnh : query(sql) → preview → download
```

---

## Quản lý phiên bản (Version)

Version được định nghĩa **một nơi duy nhất**:

```python
# components/sidebar.py
APP_VERSION = "v2.5"
```

Được import vào `login.py` và `pages/about.py`:

```python
from components.sidebar import APP_VERSION
```

---

## Cache Strategy

| Hàm | TTL | Lý do |
|-----|-----|-------|
| `list_tables()` | 120s | Schema ít thay đổi |
| `list_columns()` | 120s | Schema ít thay đổi |
| `count_rows()` | 30s | Cần tương đối fresh |
| `fetch_page()` | 20s | Dữ liệu thay đổi thường |
| `search_products()` | 15s | Cần near-realtime |
| `_load_product_options()` | 120s | Load lần đầu tốn kém |
| `_load_vendors()` | 120s | Vendor ít thay đổi |

---

## Module Chi Tiết

### `components/sidebar.py`
- **Xuất**: `APP_VERSION` (string) — nguồn sự thật duy nhất cho version
- **Output**: `page_key` — key page đang active
- **State**: `_sidebar_nav_idx`

### `components/filter.py`
- **Output**: `FilterResult` dataclass
- **Logic**: Auto-detect cột barcode/description theo danh sách ứng viên

### `modules/order_table.py`
- **State keys**: `sc_order_items`, `sc_vendor_id`, `sc_po_date`, `sc_deposit_pct`
- **Public API**: `add_product()`, `remove_product()`, `clear_all()`, `get_items()`

### `modules/export_pre_order.py`
- **Config**: `config/export_pre_order.json`
- **Pass 1**: Structural — thêm row nếu cần
- **Pass 2**: Data — ghi fields + formulas
- **Pass 3**: Sync — đọc `master data` sheet (kể cả ẩn) qua zipfile XML

### `db/queries.py`
- `query()` → SELECT → DataFrame
- `execute()` → DML → bool
- `executemany()` → batch INSERT → int (rowcount)
