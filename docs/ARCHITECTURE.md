# 🏗️ Kiến trúc ứng dụng — Supply Chain

## Tổng quan

Ứng dụng Streamlit single-page, sử dụng `st.sidebar` + `st.radio` để tạo navigation.
Dữ liệu lưu trong MySQL, xác thực qua file Excel (`log/log.xlsx`).

## Sơ đồ kiến trúc

```
┌──────────────────────────────────────────────────────────┐
│                        app.py                            │
│             (Entry point + Auth + Routing)                │
├──────────────┬───────────────────────────────────────────┤
│              │                                           │
│   login.py   │        components/sidebar.py              │
│   (Auth)     │        (Navigation → page_key)            │
│              │                                           │
├──────────────┴───────────────────────────────────────────┤
│                         PAGES                            │
│  ┌────────────┬────────────┬────────────┬──────────────┐ │
│  │ search_    │ data_      │ import_    │ export_      │ │
│  │ order.py   │ browser.py │ excel.py   │ excel.py     │ │
│  ├────────────┼────────────┼────────────┼──────────────┤ │
│  │ view_      │ about.py   │            │              │ │
│  │ templates  │            │            │              │ │
│  └────────────┴────────────┴────────────┴──────────────┘ │
├──────────────────────────────────────────────────────────┤
│                        MODULES                           │
│  ┌────────────────┬────────────────┬───────────────────┐ │
│  │ product_       │ order_         │ export_pre_       │ │
│  │ search.py      │ table.py       │ order.py          │ │
│  └────────────────┴────────────────┴───────────────────┘ │
├──────────────────────────────────────────────────────────┤
│  COMPONENTS         │  DB              │  UTILS          │
│  ┌────────────────┐ │  ┌────────────┐  │  ┌───────────┐ │
│  │ sidebar.py     │ │  │ connection │  │  │ styles.py │ │
│  │ filter.py      │ │  │ queries.py │  │  │ excel.py  │ │
│  └────────────────┘ │  └────────────┘  │  └───────────┘ │
└──────────────────────────────────────────────────────────┘
```

## Cấu trúc thư mục

```
supply_chain/
├── app.py                    # Entry point: config → auth → routing
├── login.py                  # Authentication: login/logout/auto-login
│
├── components/               # UI components tái sử dụng
│   ├── __init__.py
│   ├── sidebar.py            # Sidebar navigation (trả về page_key)
│   └── filter.py             # Bộ lọc bảng DB (auto-detect columns)
│
├── pages/                    # Các trang chính (mỗi file = 1 trang)
│   ├── search_order.py       # Lập Pre-Order
│   ├── data_browser.py       # Xem/sửa dữ liệu bảng
│   ├── import_excel.py       # Import Excel → MySQL
│   ├── export_excel.py       # Export MySQL → Excel
│   ├── view_templates.py     # Xem trước templates Excel
│   └── about.py              # Giới thiệu ứng dụng
│
├── modules/                  # Business logic modules
│   ├── product_search.py     # Tìm kiếm sản phẩm (multiselect)
│   ├── order_table.py        # Bảng đơn hàng + state management
│   └── export_pre_order.py   # Ghi sản phẩm vào template Excel
│
├── db/                       # Database layer
│   ├── connection.py         # MySQL connection + reconnect
│   └── queries.py            # Tất cả SQL queries (cached)
│
├── utils/                    # Utilities
│   ├── styles.py             # Global CSS + HTML helper functions
│   └── excel.py              # Excel read/write helpers
│
├── config/                   # Config files
│   ├── export_pre_order.json # Config template PO+CI sheets
│   └── export_po.json        # Config template PO sheets
│
├── templates/                # Excel templates
│   └── Pre-Order/
│       └── <VENDOR>/         # Mỗi vendor 1 folder
│           └── *.xlsx        # Template files
│
├── scripts/                  # One-time setup & admin scripts
│   ├── create_log_file.py    # Tạo log/log.xlsx ban đầu
│   ├── manage_users.py       # Quản lý user (CLI)
│   ├── setup_login.py        # Wizard cài đặt
│   ├── check_db_size.py      # Kiểm tra kích thước DB
│   ├── create_debt_tracking.py
│   ├── create_debt_triggers.py
│   ├── import_products_eng.py
│   └── leibu.xlsx
│
├── log/                      # User data (gitignored)
│   └── log.xlsx
│
├── docs/                     # Documentation
│   ├── README.md
│   ├── ARCHITECTURE.md       # (file này)
│   └── DEVELOPMENT.md
│
└── .streamlit/
    ├── config.toml           # Streamlit theme + server config
    └── secrets.toml          # MySQL credentials (gitignored)
```

## Data Flow

### 1. Request Flow

```
User → Browser
  → app.py (check auth)
    → login.py (nếu chưa auth → show login form)
    → sidebar.render() → page_key
    → PAGES[page_key].render()
      → db/queries.py → MySQL
      → utils/styles.py (HTML)
  → Browser (render)
```

### 2. Pre-Order Flow

```
search_order.py
  → product_search.render()
    → DB: SELECT barcode, description FROM products_eng
    → st.multiselect → user chọn sản phẩm
    → order_table.add_product()
  → order_table.render()
    → Hiển thị bảng: barcode | desc | qty | note
    → Export: export_pre_order.build_pre_order_bytes()
      → Load template .xlsx
      → Ghi data + formulas vào PO sheet + CI sheet
      → Trả về bytes → st.download_button
```

### 3. Import/Export Flow

```
import_excel.py
  → Upload .xlsx → chọn sheet → preview
  → Map cột Excel → cột DB
  → executemany(INSERT INTO ...) → MySQL

export_excel.py
  → [1 bảng] SELECT * → df_to_excel_bytes → download
  → [nhiều bảng] multi_df_to_excel_bytes → download
  → [SQL] query(user_sql) → preview → download
```

## Module Chi Tiết

### `components/sidebar.py`
- **Input**: Không có
- **Output**: `page_key` (string) — key của page được chọn
- **State**: `_sidebar_nav_idx` — index menu đang active
- **UI**: Logo + DB badge + radio menu + user info + logout

### `components/filter.py`
- **Input**: `key_prefix` (string)
- **Output**: `FilterResult` dataclass
- **Logic**: Auto-detect cột barcode/description dựa trên tên cột

### `modules/order_table.py`
- **State**: `sc_order_items` — list[dict] sản phẩm
- **State**: `sc_vendor_id`, `sc_po_date`, `sc_deposit_pct`
- **API**: `add_product()`, `remove_product()`, `clear_all()`, `get_items()`

### `modules/export_pre_order.py`
- **Input**: template bytes + items + date + vendor + deposit
- **Config**: `config/export_pre_order.json`
- **Output**: bytes file Excel hoàn chỉnh

### `db/queries.py`
- Cache TTL: schema=120s, count=30s, search=15s, page=20s
- `query()` → SELECT → DataFrame
- `execute()` → INSERT/UPDATE/DELETE → bool
- `executemany()` → batch INSERT → int

### `utils/styles.py`
- `GLOBAL_CSS` — CSS toàn cục inject 1 lần
- `HIDE_SIDEBAR_CSS` — CSS ẩn sidebar (trang login)
- HTML helpers: `page_header()`, `section_label()`, `metric_card()`, `mono()`, `divider()`, `badge()`
