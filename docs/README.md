# 📦 Supply Chain Management — OQR Co.Ltd

Ứng dụng Streamlit quản lý chuỗi cung ứng: lập đơn Pre-Order, quản lý dữ liệu bảng,
import/export Excel, và xem templates.

## 🚀 Cài đặt & Chạy

### 1. Cài dependencies

```bash
pip install streamlit pandas mysql-connector-python openpyxl
```

### 2. Cấu hình database

Tạo file `.streamlit/secrets.toml`:

```toml
[mysql]
host = "your-host"
port = 3306
user = "your-user"
password = "your-password"
database = "your-database"
```

### 3. Khởi tạo file đăng nhập

```bash
python scripts/create_log_file.py
```

Tạo file `log/log.xlsx` với user mặc định: `root / root`

### 4. Chạy ứng dụng

```bash
streamlit run app.py
```

---

## 🔑 Đăng nhập mặc định

| Username | Password |
|----------|----------|
| `root`   | `root`   |

---

## 👥 Quản lý user

```bash
# Xem danh sách user
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
| **Pre-Order** | Lập đơn đặt hàng, xuất file PO+CI theo template |
| **Dữ liệu bảng** | Xem, sửa trực tiếp dữ liệu trong DB |
| **Import Excel** | Nạp dữ liệu từ file Excel vào MySQL |
| **Export Excel** | Xuất bảng/query ra file Excel |
| **Xem Templates** | Xem trước các biểu mẫu Excel (PO, CI) |
| **About** | Thông tin ứng dụng |

---

## 📁 Cấu trúc dự án

Xem chi tiết tại [ARCHITECTURE.md](ARCHITECTURE.md).

---

## 🔒 Bảo mật

- Password mã hóa SHA256 (không lưu plain text)
- File `log/log.xlsx` nằm trong `.gitignore`
- Session-based authentication + URL params (survive F5)

---

*© 2024 OQR CO. LTD.*
