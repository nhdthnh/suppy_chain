# Hướng dẫn Bàn giao: Cấu hình Xuất Excel Pre-order (Đa Vendor & Low-Code)

Để chuẩn bị cho việc bảo trì tối ưu và bàn giao dự án, hệ thống xuất file Excel đã được nâng cấp để **hoàn toàn tự động quét template** và **hiệu chỉnh qua file cấu hình JSON**.

---

## 📂 1. Cấu trúc thư mục Templates mới
Các file Excel template hiện được gom nhóm theo cây phân cấp:
```text
templates
├── Pre-Order                 # Thư mục chứa mẫu Đặt hàng
│   └── Liebu                 # Folder riêng cho Vendor Liebu
│       └── PRE ORDER_OQR_LIEBU (templates).xlsx
└── Purchase-Order            # Thư mục chứa mẫu Mua hàng (Mở rộng sau này)
```

### 🧠 Cách hoạt động trên Giao diện:
* Khi chọn Vendor (Ví dụ: `Liebu`), hệ thống tự động quét folder `templates/Pre-Order/Liebu/`.
* Nếu có file Excel (`.xlsx`), ứng dụng tự sinh một dropdown **"📋 Template Excel"** cho phép người dùng kích chọn layout mong muốn dễ dàng.

---

## 🔧 2. Tùy biến Nội dung Low-Code (Không cần Sửa Python)

Bạn có 2 cách để chỉnh sửa file Excel khi bàn giao cho khách hàng:

### 📗 Cách A: Sửa giao diện trực tiếp trên Excel (Khuyến khích)
Bạn mở file Excel trong `templates/Pre-Order/Liebu/...` lên để:
* Thay đổi Logo, màu sắc, font chữ.
* Sửa text tĩnh (Ví dụ: thông tin Seller Info, Buyer Info).
* Thêm sheet tính toán phụ đi kèm.

---

### 📘 Cách B: Sửa cấu trúc dữ liệu qua File JSON
File cấu hình: `config/export_pre_order.json`

**Ví dụ:**
```json
{
  "sheets": [
    {
      "name": "PO",                   // Tên Sheet trong Excel template
      "first_row": 15,                // Dòng bắt đầu ghi sản phẩm
      "ref_row": 15,                  // Dòng dùng để Copy Style
      "fields": {
        "F2": { "type": "date", "format": "%d/%m/%Y" }, // Ghi Ngày vào F2
        "F3": { "type": "po_number" }                   // Ghi PO# vào F3
      },
      "columns": [
        { "col": 1, "type": "formula", "value": "=VLOOKUP(C{row}, 'master data'!$A:$B, 2, 0)" },
        { "col": 3, "type": "field", "value": "description" }
      ],
      "totals": [
        { "col": 4, "formula": "=SUM(D{start}:D{end})" }
      ],
      "total_search_text": "TOTAL"    // Tìm dòng "TOTAL" ở cột 1 để chốt bảng
    }
  ]
}
```

### 🔍 Giải thích Biến sử dụng trong Formula:
* `{row}`: Số dòng hiện tại (Ví dụ: D{row} sẽ tự nở ra D15, D16,...).
* `{start}` và `{end}`: Điểm đầu và điểm cuối của bảng sản phẩm, hỗ trợ sinh công thức `=SUM(D{start}:D{end})` nở ra động theo số lượng mặt hàng.

---

> [!TIP]
> **Biện pháp an toàn Code:** Nếu file JSON cấu hình bị xóa hoặc lỗi, hệ thống sẽ tự động sử dụng **cấu hình mặc định (Fallback)** trong Python để đảm bảo file Excel xuất ra luôn chính xác tuyệt đối!
