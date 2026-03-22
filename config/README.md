# Hướng dẫn Bàn giao: Cấu hình Xuất Excel Pre-order (PO & CI)

Để người dùng/khách hàng có thể thay đổi cấu trúc file Excel xuất ra mà **không cần sửa code Python**, hệ thống đã được tách rời logic Layout.

---

## 1. Cách 1: Sửa giao diện Excel trực tiếp (Rất khuyến khích)
Hệ thống sử dụng file template:
`templates/PRE ORDER_OQR_LIEBU (templates).xlsx`

Bạn có thể mở file này bằng Excel để:
* Thay đổi Logo, màu sắc, font chữ.
* Sửa text tĩnh (Seller Info, Buyer Info).
* Chỉnh sửa độ cao dòng, căn lề.
* Thêm sheet tính toán không liên quan trực tiếp đến bảng dữ liệu.

---

## 2. Cách 2: Sửa cấu trúc dữ liệu qua File JSON
File cấu hình: `config/export_po.json`

### 📄 Cấu trúc cơ bản:
```json
{
  "sheets": [
    {
      "name": "PO",                   // Tên Sheet trong Excel template
      "first_row": 15,                // Dòng đầu tiên bắt đầu ghi dữ liệu sản phẩm
      "ref_row": 15,                  // Dòng dùng để Copy Style (Border, Color) 
      "fields": {
        "F2": { "type": "date", "format": "%d/%m/%Y" }, // Điền Ngày vào ô F2
        "F3": { "type": "po_number" }                   // Điền PO# vào ô F3
      },
      "columns": [
        { "col": 1, "type": "formula", "value": "=VLOOKUP(C{row}, 'master data'!$A:$B, 2, 0)" },
        { "col": 3, "type": "field", "value": "description" }
      ],
      "totals": [
        { "col": 4, "formula": "=SUM(D{start}:D{end})" }
      ],
      "total_search_text": "TOTAL"    // Keyword để tìm dòng tổng số (ở cột 1)
    }
  ]
}
```

### 🔍 Giải thích về Loại cấu hình:
1. **Static Fields (`fields`)**:
   * Áp dụng để điền thông tin chung lên đầu bảng (Date, PO Number).
2. **Dynamic Product Table (`columns`)**:
   * `type: "field"`: Ghi dữ liệu từ table (`description`, `quantity`, `note`).
   * `type: "formula"`: Ghi công thức Excel tự động. Hỗ trợ biến `{row}` để thay bằng số dòng hiện tại.
3. **Total Calculation (`totals`)**:
   * Hỗ trợ biến `{start}` và `{end}` để sinh công thức tính SUM vùng dữ liệu tự động nở ra.

---

**💡 Biện pháp an toàn:** Nếu file JSON bị xóa hoặc cấu hình lỗi, code tự động **fallback** về cấu trúc mặc định chuẩn ban đầu. Hệ thống sẽ luôn hoạt động an toàn!
