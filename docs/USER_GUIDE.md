# 📖 Hướng dẫn Sử dụng — Supply Chain Management v2.5

> **OQR Co. Ltd** · Ứng dụng quản lý chuỗi cung ứng  
> Cập nhật: 2025 · Phiên bản: v2.5

---

## Mục lục

1. [Tổng quan](#1-tổng-quan)
2. [Đăng nhập & Đăng xuất](#2-đăng-nhập--đăng-xuất)
3. [Lập Pre-Order](#3-lập-pre-order)
4. [Dữ liệu bảng (Data Browser)](#4-dữ-liệu-bảng-data-browser)
5. [Import Excel](#5-import-excel)
6. [Export Excel](#6-export-excel)
7. [Xem Templates](#7-xem-templates)
8. [Quản lý User (CLI)](#8-quản-lý-user-cli)
9. [Cấu hình Template Export](#9-cấu-hình-template-export)
10. [Xử lý sự cố thường gặp](#10-xử-lý-sự-cố-thường-gặp)

---

## 1. Tổng quan

**Supply Chain Management** là ứng dụng web nội bộ chạy trên Streamlit, kết nối trực tiếp tới MySQL. Giao diện gồm một **sidebar** điều hướng ở trái và vùng nội dung chính ở phải.

**Sidebar bao gồm:**
- Logo + badge trạng thái kết nối DB (CONNECTED / DISCONNECTED)
- Menu điều hướng 6 trang
- Thông tin tài khoản đang đăng nhập
- Nút **Đăng xuất**
- Dấu phiên bản + thời gian đồng bộ

---

## 2. Đăng nhập & Đăng xuất

### Đăng nhập

1. Mở trình duyệt, truy cập địa chỉ app (mặc định `http://localhost:8501`)
2. Nhập **Tên đăng nhập** và **Mật khẩu**
3. Nhấn **Đăng nhập**

> Thông tin xác thực được lưu trong `log/log.xlsx` (sheet `user`).  
> Password được mã hóa SHA-256, không lưu plain text.

### Đăng xuất

Nhấn nút **🚪 Đăng xuất** ở cuối sidebar.  
Phiên làm việc sẽ được xóa hoàn toàn.

### Tài khoản mặc định

| Username | Password |
|----------|----------|
| `root`   | `root`   |

> ⚠️ Thay đổi mật khẩu mặc định ngay sau khi cài đặt.

---

## 3. Lập Pre-Order

Trang **📋 PRE-ORDER** là tính năng cốt lõi: tạo đơn đặt hàng tự động và xuất ra file Excel (PO + CI).

### Bước 1 — Cấu hình thông tin PO

Điền vào 3 trường ở đầu trang:

| Trường | Mô tả |
|--------|--------|
| **Ngày đặt hàng** | Ngày trên file PO, định dạng DD/MM/YYYY |
| **Vendor** | Chọn nhà cung cấp (lấy từ bảng `vendors`) |
| **Template Excel** | File template tương ứng với vendor đã chọn |
| **Deposit (%)** | Tỷ lệ đặt cọc, ví dụ `70` → deposit = amount × 70% |

Sau khi chọn đủ, hệ thống hiển thị **số PO preview**, ví dụ:  
`NO. 0601_2025_OQR_LIEBU · Deposit: 70%`

### Bước 2 — Tìm kiếm & thêm sản phẩm

1. Gõ từ khóa (mã vạch hoặc tên) vào ô **TÌM KIẾM SẢN PHẨM**
2. Kết quả gợi ý hiển thị dạng `BARCODE | DESCRIPTION`
3. Click chọn sản phẩm → tự động thêm vào danh sách bên dưới
4. Ô tìm kiếm tự reset sau mỗi lần thêm

> Dữ liệu sản phẩm lấy từ bảng `products_eng` trong DB.

### Bước 3 — Chỉnh sửa danh sách

Trong bảng **DANH SÁCH SẢN PHẨM PRE-ORDER**:

| Cột | Chức năng |
|-----|-----------|
| **BARCODE** | Mã vạch (chỉ đọc) |
| **DESCRIPTION** | Tên sản phẩm (chỉ đọc) |
| **QTY** | Số lượng đặt — chỉnh sửa trực tiếp |
| **NOTE** | Ghi chú tự do |
| **✕** | Xóa dòng khỏi danh sách |

### Bước 4 — Xuất file

Sau khi có ít nhất 1 sản phẩm, 3 nút xuất hiện:

| Nút | Chức năng |
|-----|-----------|
| **▶ Chuẩn bị file Pre-Order** | Tạo file Excel (PO+CI) từ template + tự động lưu vào bảng `debt_tracking` |
| **⬇ Xuất Excel (plain)** | Xuất danh sách đơn giản không cần template |
| **🗑 Xóa tất cả** | Xóa toàn bộ danh sách, reset trạng thái |

**Quy trình "Chuẩn bị file Pre-Order":**
1. Nhấn nút → hệ thống đọc template, điền sản phẩm + công thức
2. Tự động tra giá từ sheet `master data` (ẩn) trong template
3. Lưu kết quả vào bảng `debt_tracking` (barcode, qty, giá, amount, deposit)
4. Nút chuyển thành **⬇ Tải Pre-Order (PO+CI)** → nhấn để download

> **Lưu ý:** Nếu giá không tìm thấy trong `master data`, amount = 0. Kiểm tra sheet `master data` trong template.

### Tên file xuất

Format: `DDMM_YYYY_OQR_<VENDOR>.xlsx`  
Ví dụ: `0601_2025_OQR_LIEBU.xlsx`

---

## 4. Dữ liệu bảng (Data Browser)

Trang **🗄 DỮ LIỆU BẢNG** cho phép xem và chỉnh sửa trực tiếp dữ liệu MySQL.

### Chọn bảng

Dùng dropdown **Chọn bảng** ở đầu trang. Sau khi chọn, 3 metric card hiển thị:
- **TỔNG DÒNG** — số dòng hiện có
- **SỐ CỘT** — số cột
- **BẢNG** — tên bảng

### Chỉnh sửa dữ liệu

Bảng Data Editor hỗ trợ:
- **Click vào cell** để sửa giá trị
- **Lazy load**: mặc định load 200 dòng đầu, nhấn **⬇ Load thêm** để tải thêm
- Hiển thị `X / Y dòng đang hiển thị` ở dưới bảng

### Thêm dòng mới

Nhấn **＋ Thêm dòng mới** → một dòng mới được thêm vào cuối bảng với ID tự động (MAX + 1).

### Lưu thay đổi

1. Nhấn **✔ Lưu vào Database** → xuất hiện hộp xác nhận
2. Nhấn **✔ Xác nhận** để ghi → hệ thống thực hiện INSERT/UPDATE/DELETE
3. Hoặc nhấn **✕ Hủy** để bỏ qua

> ⚠️ Hành động ghi không thể hoàn tác. Kiểm tra kỹ trước khi xác nhận.

### Xuất Excel

Nhấn **⬇ Xuất Excel (.xlsx)** → tải toàn bộ bảng ra file Excel có timestamp.

---

## 5. Import Excel

Trang **⬆ IMPORT EXCEL** nạp dữ liệu từ file `.xlsx` / `.xls` vào MySQL.

### Quy trình

**Bước 1 — Chọn bảng đích & upload file**
- Chọn bảng đích từ dropdown
- Upload file Excel (tối đa 50 MB)

**Bước 2 — Chọn sheet**
- Chọn sheet cần import từ danh sách sheet trong file

**Bước 3 — Preview**
- Hệ thống hiển thị 5 dòng đầu của sheet để kiểm tra

**Bước 4 — Mapping cột**
- Mỗi cột Excel hiển thị một dropdown để chọn cột DB tương ứng
- Chọn `(bỏ qua)` để bỏ cột đó
- Hệ thống tự động gợi ý cột cùng tên

**Bước 5 — Thực hiện Import**
- Tùy chọn **INSERT IGNORE** — bỏ qua dòng trùng khóa chính (khuyến nghị bật)
- Nhấn **🚀 BẮT ĐẦU IMPORT**
- Kết quả hiển thị số dòng đã ghi thành công

---

## 6. Export Excel

Trang **⬇ EXPORT EXCEL** xuất dữ liệu từ MySQL ra file Excel.

### 3 chế độ xuất

#### Xuất 1 bảng
1. Chọn bảng từ dropdown
2. Nhấn **▶ XUẤT BẢNG**
3. Nhấn **⬇ Tải file** để download

#### Xuất nhiều bảng
1. Chọn nhiều bảng từ multiselect
2. Nhấn **▶ XUẤT TẤT CẢ**
3. Download file Excel với mỗi bảng là 1 sheet

#### SQL tùy chỉnh
1. Nhập câu SQL vào textarea (mặc định `SELECT * FROM <bảng> LIMIT 100`)
2. Nhấn **▶ CHẠY & XUẤT**
3. Preview 20 dòng đầu hiển thị ngay
4. Nhấn **⬇ Tải kết quả** để download

> **Lưu ý:** Chỉ hỗ trợ câu `SELECT`. Không thực thi được `INSERT/UPDATE/DELETE` qua trang này.

---

## 7. Xem Templates

Trang **📄 XEM TEMPLATES** xem trước file Excel template ngay trong trình duyệt.

### Cách dùng

1. Chọn **Loại biểu mẫu** (thư mục con trong `templates/`)
2. Chọn **Vendor**
3. Chọn **File Template** (.xlsx)
4. Chọn **Sheet** cần xem
5. Nội dung hiển thị với đầy đủ màu sắc, font, merged cells

### Cấu trúc thư mục template

```
templates/
└── Pre-Order/
    ├── LIEBU/
    │   ├── template_v1.xlsx
    │   └── template_v2.xlsx
    └── <VENDOR_CODE>/
        └── *.xlsx
```

> Tên thư mục Vendor phải **khớp chính xác** (case-insensitive) với `short_name` trong bảng `vendors`.

---

## 8. Quản lý User (CLI)

Các script quản lý user nằm trong `scripts/manage_users.py`.

```bash
# Xem danh sách tất cả user
python scripts/manage_users.py list

# Thêm user mới
python scripts/manage_users.py add <username> <password>

# Đổi mật khẩu
python scripts/manage_users.py password <username> <new_password>

# Xóa user
python scripts/manage_users.py delete <username>
```

> File `log/log.xlsx` (sheet `user`) lưu: `username` + `password` (SHA-256 hash).

---

## 9. Cấu hình Template Export

File `config/export_pre_order.json` định nghĩa cách ghi dữ liệu vào các sheet PO và CI.

### Cấu trúc

```json
{
  "sheets": [
    {
      "name": "PO",
      "first_row": 15,
      "ref_row": 15,
      "fields": {
        "F2": {"type": "date", "format": "%d/%m/%Y"},
        "F3": {"type": "po_number"}
      },
      "columns": [
        {"col": 3, "type": "field", "value": "description"},
        {"col": 4, "type": "field", "value": "quantity", "cast": "int"},
        {"col": 5, "type": "formula", "value": "=VLOOKUP(C{row},'master data'!$A:$D,4,0)"},
        {"col": 6, "type": "formula", "value": "=D{row}*E{row}"}
      ],
      "totals": [
        {"col": 4, "formula": "=SUM(D{start}:D{end})"},
        {"col": 6, "formula": "=SUM(F{start}:F{end})"}
      ],
      "total_search_text": "TOTAL"
    }
  ]
}
```

### Các loại column

| `type` | Mô tả |
|--------|--------|
| `field` | Lấy từ item dict (`barcode`, `description`, `quantity`, `note`) |
| `formula` | Công thức Excel, `{row}` được thay bằng số dòng thực tế |

### Tra giá từ Master Data

Sheet `master data` (có thể bị ẩn trong Excel) cần có:
- **Cột A**: Tên sản phẩm (description)
- **Cột D**: Đơn giá

Hệ thống tra giá theo thứ tự ưu tiên:
1. Description (đã chuẩn hóa lowercase, bỏ ký tự đặc biệt)
2. Barcode
3. Description raw

---

## 10. Xử lý sự cố thường gặp

### ❌ DB DISCONNECTED trên sidebar

- Kiểm tra `.streamlit/secrets.toml` đúng host/port/user/password
- Kiểm tra MySQL server đang chạy
- Kiểm tra network/firewall cho phép kết nối

### ❌ Không tìm thấy vendor hoặc template

- Vendor chưa có trong bảng `vendors` (cột `is_active = 1`)
- Thư mục template chưa được tạo: `templates/Pre-Order/<VENDOR_SHORT_NAME>/`
- Tên thư mục không khớp `short_name`

### ❌ Giá = 0 khi xuất Pre-Order

- Sheet `master data` không tồn tại hoặc bị ẩn hoàn toàn (veryHidden)
- Tên sản phẩm trong master data không khớp với description
- Cột D (giá) trong master data trống hoặc không phải số

### ❌ Sai tên đăng nhập / mật khẩu

- Kiểm tra file `log/log.xlsx` có tồn tại không
- Chạy lại `python scripts/create_log_file.py` nếu file bị mất
- Xác minh username bằng `python scripts/manage_users.py list`

### ❌ Import Excel bị lỗi encoding

- Mở file Excel và lưu lại dưới dạng `.xlsx` (không phải `.xls` cũ)
- Kiểm tra cột mapping đúng kiểu dữ liệu với bảng đích

### ❌ Lỗi "Khóa chính bị trùng" khi lưu Data Browser

- Hệ thống phát hiện ID tự sinh bị trùng với dòng hiện có
- Reload trang để đồng bộ lại dữ liệu

---

## Phím tắt & Mẹo

| Tình huống | Gợi ý |
|-----------|--------|
| Tìm nhanh sản phẩm | Gõ 3-4 ký tự đầu barcode trong ô tìm kiếm |
| Reset ô tìm kiếm sau khi thêm | Tự động reset — không cần làm gì |
| Xem tất cả dòng DB | Nhấn Load thêm nhiều lần hoặc dùng Export Excel |
| Test SQL trước khi export | Dùng chế độ SQL tùy chỉnh trong Export Excel |
| Thêm vendor mới | Chèn trực tiếp vào bảng `vendors` qua Data Browser |

---

*© 2025 OQR Co. Ltd · Supply Chain Management · v2.5*
