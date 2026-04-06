"""
RUN THIS FIRST - Chạy file này trước khi start app
"""
print("=" * 60)
print("KHỞI TẠO HỆ THỐNG ĐĂNG NHẬP")
print("=" * 60)
print()

import subprocess
import sys
from pathlib import Path

# Kiểm tra file log.xlsx đã tồn tại chưa
log_file = Path(__file__).parent / "log" / "log.xlsx"

if log_file.exists():
    print(f"✅ File log.xlsx đã tồn tại: {log_file}")
    print()
    response = input("Bạn có muốn tạo lại file mới (sẽ reset về root/root)? (y/n): ")
    if response.lower() != 'y':
        print("❌ Đã hủy. Giữ nguyên file cũ.")
        print()
        print("Bạn có thể chạy app ngay:")
        print("  streamlit run app.py")
        print()
        sys.exit(0)

# Chạy script tạo log file
print()
print("Đang tạo file log.xlsx...")
subprocess.run([sys.executable, "create_log_file.py"])

print()
print("=" * 60)
print("✅ HOÀN TẤT!")
print("=" * 60)
print()
print("Bây giờ bạn có thể chạy app:")
print()
print("  streamlit run app.py")
print()
print("Thông tin đăng nhập mặc định:")
print("  Username: root")
print("  Password: root")
print()
print("Để quản lý user:")
print("  python manage_users.py list          # Xem danh sách")
print("  python manage_users.py add USER PASS # Thêm user")
print("  python manage_users.py password USER NEWPASS # Đổi password")
print()
