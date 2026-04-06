# 📦 Supply Chain Management — OQR Co.Ltd

Ứng dụng **Streamlit** quản lý chuỗi cung ứng: lập đơn Pre-Order, quản lý dữ liệu bảng MySQL, import/export Excel và xem templates.

> **Phiên bản hiện tại: v2.5**  
> Tài liệu chi tiết: [`docs/USER_GUIDE.md`](USER_GUIDE.md) · [`docs/ARCHITECTURE.md`](ARCHITECTURE.md)

---

## 🚀 Cài đặt & Chạy nhanh

### 1. Cài dependencies

```bash
pip install streamlit pandas mysql-connector-python openpyxl
# Tùy chọn: xem template đẹp hơn
pip install xlsx2html
```

### 2. Cấu hình database

Tạo file `.streamlit/secrets.toml`:

```toml
[mysql]
host     = "your-host"
port     = 3306
user     = "your-user"
password = "your-password"
database = "your-database"
```

### 3. Khởi tạo file đăng nhập

```bash
python scripts/create_log_file.py
```

Tạo `log/log.xlsx` với user mặc định: `root / root`

### 4. Chạy ứng dụng

```bash
streamlit run app.py
```

---

## 🔑 Tài khoản mặc định

| Username | Password |
|----------|----------|
| `root`   | `root`   |

> **Đổi ngay sau lần đầu đăng nhập** bằng `scripts/manage_users.py`

---

## 👥 Quản lý user (CLI)

```bash
# Xem danh sách
python scripts/manage_users.py list

# Thêm user mới
python scripts/manage_users.py add <username> <password>

# Đổi password
python scripts/manage_users.py password <username> <new_pass>

# Xóa user
python scripts/manage_users.py delete <username>
```

---

## 📋 Tính năng chính

| Trang | Mô tả |
|-------|--------|
| **📋 Pre-Order** | Lập đơn, xuất file PO+CI theo template, tự động sync DB |
| **🗄 Dữ liệu bảng** | Xem, sửa trực tiếp dữ liệu MySQL (INSERT/UPDATE/DELETE) |
| **⬆ Import Excel** | Nạp dữ liệu từ .xlsx vào MySQL với column mapping |
| **⬇ Export Excel** | Xuất bảng / multi-sheet / SQL tùy chỉnh ra Excel |
| **📄 Xem Templates** | Preview biểu mẫu Excel PO, CI theo Vendor |
| **ℹ About** | Thông tin phiên bản, changelog, tech stack |

---

## 📁 Cấu trúc thư mục

```
supply_chain/
├── app.py              # Entry point
├── login.py            # Authentication
├── components/         # UI components (sidebar, filter)
├── pages/              # Các trang chính
├── modules/            # Business logic
├── db/                 # Database layer
├── utils/              # Styles & Excel helpers
├── config/             # JSON config cho template export
├── templates/          # Template Excel theo Vendor
├── scripts/            # Admin & setup scripts
├── log/                # User data (gitignored)
└── docs/               # Tài liệu
```

Chi tiết đầy đủ tại [ARCHITECTURE.md](ARCHITECTURE.md).

---

## 🔒 Bảo mật

- Password mã hóa **SHA-256** (không lưu plain text)
- `log/log.xlsx` nằm trong `.gitignore`
- Session-based authentication + URL params (survive F5)

---

## 📖 Tài liệu đầy đủ

Xem **[USER_GUIDE.md](USER_GUIDE.md)** để biết hướng dẫn sử dụng từng tính năng.

---

*© 2025 OQR Co. Ltd · v2.5*
