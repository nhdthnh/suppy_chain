"""
db/create_debt_tracking.py
Tạo bảng debt_tracking (CÔNG NỢ) và view v_debt_summary.
Chạy: python db/create_debt_tracking.py
"""

import os
import mysql.connector

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

DB_CONFIG = {
    "host":     "192.168.1.119",
    "port":     3306,
    "user":     "root",
    "password": "Oqr@18009413",
    "database": "supply_chain",
}

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS `debt_tracking` (
    `id`                    INT UNSIGNED    NOT NULL AUTO_INCREMENT,

    `status`                ENUM('pending','finished')
                            NOT NULL DEFAULT 'pending',

    -- Product
    `barcode`               VARCHAR(50)     NOT NULL,
    `description`           VARCHAR(500)    NOT NULL,
    `qty`                   INT             NOT NULL DEFAULT 0,
    `unit_price`            BIGINT          NOT NULL DEFAULT 0,
    `amount`                BIGINT          NOT NULL DEFAULT 0,

    -- Payment type
    `payment_type`          VARCHAR(50)     DEFAULT NULL,

    -- 70% Pre-order
    `preorder_no`           VARCHAR(100)    DEFAULT NULL,
    `preorder_amount`       BIGINT          DEFAULT NULL,
    `preorder_pay_status`   ENUM('pending','finished') DEFAULT NULL,

    -- 30% / Balance
    `po_no`                 VARCHAR(100)    DEFAULT NULL,
    `balance_qty`           INT             DEFAULT NULL,
    `balance_due`           BIGINT          DEFAULT NULL,
    `balance_pay_status`    ENUM('pending','finished') DEFAULT NULL,

    -- Total balance
    `total_qty`             INT             DEFAULT NULL,
    `total_amount`          BIGINT          DEFAULT NULL,

    -- References
    `vendor_id`             INT UNSIGNED    DEFAULT NULL,
    `note`                  TEXT            DEFAULT NULL,
    `created_at`            TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    `updated_at`            TIMESTAMP       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (`id`),
    INDEX `idx_barcode`     (`barcode`),
    INDEX `idx_preorder_no` (`preorder_no`),
    INDEX `idx_po_no`       (`po_no`),
    INDEX `idx_status`      (`status`),
    INDEX `idx_vendor`      (`vendor_id`),

    CONSTRAINT `fk_debt_vendor`
        FOREIGN KEY (`vendor_id`) REFERENCES `vendors` (`id`)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
  COMMENT='Theo dõi công nợ — CÔNG NỢ';
"""

CREATE_VIEW = """
CREATE OR REPLACE VIEW `v_debt_summary` AS
SELECT
    d.id,
    d.status,
    d.barcode,
    d.description,
    d.preorder_no,
    d.po_no,
    d.qty                                               AS ordered_qty,
    d.amount                                            AS ordered_amount,
    d.preorder_amount                                   AS paid_70,
    d.balance_due                                       AS paid_balance,
    COALESCE(d.preorder_amount,0)
        + COALESCE(d.balance_due,0)                     AS total_paid,
    d.amount
        - COALESCE(d.preorder_amount,0)
        - COALESCE(d.balance_due,0)                     AS remaining,
    d.preorder_pay_status,
    d.balance_pay_status,
    v.short_name                                        AS vendor,
    d.updated_at
FROM debt_tracking d
LEFT JOIN vendors v ON d.vendor_id = v.id;
"""


def run():
    conn = mysql.connector.connect(**DB_CONFIG)
    cur  = conn.cursor()

    cur.execute(CREATE_TABLE)
    conn.commit()
    print("✅ Bảng debt_tracking đã tạo")

    # cur.execute(CREATE_VIEW)
    # conn.commit()
    # print("✅ View v_debt_summary đã tạo")

    cur.execute("SELECT COUNT(*) FROM debt_tracking")
    print(f"📋 Số dòng hiện tại: {cur.fetchone()[0]}")

    cur.execute("SHOW COLUMNS FROM debt_tracking")
    cols = cur.fetchall()
    print(f"\n📐 Cấu trúc bảng ({len(cols)} cột):")
    for col in cols:
        print(f"   {col[0]:25s} {col[1]:30s} null={col[2]} default={col[4]}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    run()