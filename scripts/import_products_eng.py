"""
Import dữ liệu từ sheet 'cafein' trong file Excel vào MySQL.
- SKU được tạo từ cột DESCRIPTION (unique)
- Bỏ qua các dòng rỗng
- Dùng INSERT IGNORE để tránh trùng SKU
"""

import os
import pandas as pd
import mysql.connector
import re
import sys

# ── CẤU HÌNH ────────────────────────────────────────────────────────────────
# Resolve path tương đối so với thư mục chứa script (db/)
# → chạy từ bất kỳ thư mục nào đều tìm đúng file
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE  = os.path.join(_SCRIPT_DIR, "leibu.xlsx")
SHEET_NAME  = "Sheet1"

DB_CONFIG = {
    "host":     "192.168.1.119",
    "port":     3306,
    "user":     "root",           # <-- đổi username
    "password": "Oqr@18009413",  # <-- đổi password
    "database": "supply_chain",  # <-- đổi tên database
}

TABLE_NAME = "products_eng"
# ────────────────────────────────────────────────────────────────────────────


def make_sku(description: str) -> str:
    """Tạo SKU từ DESCRIPTION: viết hoa, bỏ ký tự đặc biệt, thay space bằng _"""
    s = str(description).upper().strip()
    s = re.sub(r"[^A-Z0-9\s]", "", s)
    s = re.sub(r"\s+", "_", s)
    return s[:100]  # giới hạn 100 ký tự


def create_table_sql() -> str:
    return f"""
CREATE TABLE IF NOT EXISTS `{TABLE_NAME}` (
    `id`          INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    `description` VARCHAR(500)    NOT NULL,
    `barcode`     VARCHAR(50)     DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uniq_barcode` (`barcode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""


def load_data(excel_file: str, sheet: str) -> pd.DataFrame:
    if not os.path.exists(excel_file):
        raise FileNotFoundError(f"Không tìm thấy file Excel: {excel_file}. Hãy chạy từ thư mục chứa file hoặc truyền đường dẫn đầy đủ.")

    # header nằm ở dòng index 1 (dòng số 2 trong Excel)
    df = pd.read_excel(excel_file, sheet_name=sheet, header=0, dtype=str)
    df.columns = [c.strip().upper() for c in df.columns]

    if "DESCRIPTION" not in df.columns:
        raise ValueError("Không tìm thấy cột 'DESCRIPTION' trong file Excel.")

    if "BARCODE" not in df.columns:
        df["BARCODE"] = None

    # Giữ đúng hai cột cần thiết
    df = df[["DESCRIPTION", "BARCODE"]].copy()

    # Bỏ dòng rỗng (DESCRIPTION phải có giá trị)
    df = df[df["DESCRIPTION"].notna() & (df["DESCRIPTION"].str.strip() != "")]
    df["BARCODE"] = df["BARCODE"].where(df["BARCODE"].notna(), None)

    return df.reset_index(drop=True)


def import_to_mysql(df: pd.DataFrame, config: dict) -> None:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    # Tạo bảng nếu chưa có
    cursor.execute(create_table_sql())
    conn.commit()

    insert_sql = f"""
        INSERT IGNORE INTO `{TABLE_NAME}` (description, barcode)
        VALUES (%s, %s)
    """

    rows = [
        (row["DESCRIPTION"].strip(), row["BARCODE"])
        for _, row in df.iterrows()
    ]

    cursor.executemany(insert_sql, rows)
    conn.commit()

    inserted = cursor.rowcount
    skipped  = len(rows) - inserted
    print(f"✅ Tổng dòng đọc từ Excel : {len(rows)}")
    print(f"   Đã insert thành công   : {inserted}")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        EXCEL_FILE = sys.argv[1]

    print(f"📂 Đọc file: {EXCEL_FILE}  |  sheet: {SHEET_NAME}")
    df = load_data(EXCEL_FILE, SHEET_NAME)
    df["SKU"] = df["DESCRIPTION"].apply(make_sku)
    print(f"   Số dòng hợp lệ: {len(df)}")
    print(df[["SKU", "DESCRIPTION", "BARCODE"]].head())

    print(f"\n🔗 Kết nối MySQL: {DB_CONFIG['host']}/{DB_CONFIG['database']}")
    import_to_mysql(df, DB_CONFIG)