"""
db/create_debt_triggers.py
Tạo trigger tự động tính total_qty và total_amount cho bảng debt_tracking.
Chạy: python db/create_debt_triggers.py
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

# ── Logic tính (giống hệt Excel) ─────────────────────────────
# total_amount = amount
#   - IF(preorder_pay_status='finished', preorder_amount, 0)
#   - IF(balance_pay_status ='finished', balance_due,     0)
#   - IF(payment_type       ='finished', amount,          0)
#
# total_qty = balance_qty - qty   (chênh lệch thực giao vs đặt hàng)
# -------------------------------------------------------------

_CALC_TOTAL_AMOUNT = """
    SET NEW.total_amount = NEW.amount
        - IF(NEW.preorder_pay_status = 'finished', COALESCE(NEW.preorder_amount, 0), 0)
        - IF(NEW.balance_pay_status  = 'finished', COALESCE(NEW.balance_due,     0), 0)
        - IF(NEW.payment_type        = 'finished', COALESCE(NEW.amount,           0), 0);
"""

_CALC_TOTAL_QTY = """
    IF NEW.balance_qty IS NOT NULL THEN
        SET NEW.total_qty = NEW.balance_qty - NEW.qty;
    ELSE
        SET NEW.total_qty = NULL;
    END IF;
"""

TRIGGER_INSERT = f"""
CREATE TRIGGER `trg_debt_calc_insert`
BEFORE INSERT ON `debt_tracking`
FOR EACH ROW
BEGIN
{_CALC_TOTAL_AMOUNT}
{_CALC_TOTAL_QTY}
END
"""

TRIGGER_UPDATE = f"""
CREATE TRIGGER `trg_debt_calc_update`
BEFORE UPDATE ON `debt_tracking`
FOR EACH ROW
BEGIN
{_CALC_TOTAL_AMOUNT}
{_CALC_TOTAL_QTY}
END
"""

RECALC_EXISTING = """
UPDATE `debt_tracking`
SET
    total_amount = amount
        - IF(preorder_pay_status = 'finished', COALESCE(preorder_amount, 0), 0)
        - IF(balance_pay_status  = 'finished', COALESCE(balance_due,     0), 0)
        - IF(payment_type        = 'finished', COALESCE(amount,          0), 0),
    total_qty = IF(
        balance_qty IS NOT NULL,
        balance_qty - qty,
        NULL
    )
"""


def run():
    conn = mysql.connector.connect(**DB_CONFIG)
    cur  = conn.cursor()

    # Drop triggers cũ nếu có
    for name in ["trg_debt_calc_insert", "trg_debt_calc_update"]:
        cur.execute(f"DROP TRIGGER IF EXISTS `{name}`")
        print(f"  Dropped (if existed): {name}")

    # Tạo triggers
    cur.execute(TRIGGER_INSERT)
    print("✅ Trigger BEFORE INSERT tạo thành công")

    cur.execute(TRIGGER_UPDATE)
    print("✅ Trigger BEFORE UPDATE tạo thành công")

    conn.commit()

    # Cập nhật dữ liệu cũ
    cur.execute(RECALC_EXISTING)
    conn.commit()
    print(f"✅ Đã recalculate {cur.rowcount} dòng hiện có")

    # Xác nhận
    cur.execute("SHOW TRIGGERS FROM `supply_chain` LIKE 'trg_debt%'")
    triggers = cur.fetchall()
    print(f"\n📋 Triggers hiện tại ({len(triggers)}):")
    for t in triggers:
        print(f"   {t[0]:35s} Event={t[1]:8s} Timing={t[2]}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    run()