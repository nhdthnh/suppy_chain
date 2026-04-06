"""
Script quản lý user: thêm, xóa, đổi password, xem danh sách
"""
import pandas as pd
import hashlib
from pathlib import Path
import sys

LOG_FILE = Path(__file__).parent / "log" / "log.xlsx"

def hash_password(password: str) -> str:
    """Mã hóa password bằng SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def list_users():
    """Hiển thị danh sách user"""
    if not LOG_FILE.exists():
        print(f"❌ File {LOG_FILE} không tồn tại!")
        return
    
    df = pd.read_excel(LOG_FILE, sheet_name='user')
    print("\n📋 DANH SÁCH USER:")
    print("=" * 50)
    for idx, row in df.iterrows():
        print(f"{idx + 1}. {row['username']}")
    print("=" * 50)
    print(f"Tổng: {len(df)} user\n")

def add_user(username: str, password: str):
    """Thêm user mới"""
    if not LOG_FILE.exists():
        print(f"❌ File {LOG_FILE} không tồn tại! Chạy create_log_file.py trước.")
        return
    
    df = pd.read_excel(LOG_FILE, sheet_name='user')
    
    # Kiểm tra user đã tồn tại
    if username in df['username'].values:
        print(f"❌ User '{username}' đã tồn tại!")
        return
    
    # Thêm user mới
    new_row = pd.DataFrame({
        'username': [username],
        'password': [hash_password(password)]
    })
    
    df = pd.concat([df, new_row], ignore_index=True)
    
    # Lưu lại
    with pd.ExcelWriter(LOG_FILE, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='user', index=False)
    
    print(f"✅ Đã thêm user '{username}'")
    print(f"🔐 Password: {password} (đã được mã hóa)")

def delete_user(username: str):
    """Xóa user"""
    if not LOG_FILE.exists():
        print(f"❌ File {LOG_FILE} không tồn tại!")
        return
    
    df = pd.read_excel(LOG_FILE, sheet_name='user')
    
    # Kiểm tra user tồn tại
    if username not in df['username'].values:
        print(f"❌ User '{username}' không tồn tại!")
        return
    
    # Không cho xóa root
    if username == 'root':
        confirm = input("⚠️  Bạn đang xóa user ROOT! Tiếp tục? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Đã hủy!")
            return
    
    # Xóa user
    df = df[df['username'] != username]
    
    # Lưu lại
    with pd.ExcelWriter(LOG_FILE, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='user', index=False)
    
    print(f"✅ Đã xóa user '{username}'")

def change_password(username: str, new_password: str):
    """Đổi password"""
    if not LOG_FILE.exists():
        print(f"❌ File {LOG_FILE} không tồn tại!")
        return
    
    df = pd.read_excel(LOG_FILE, sheet_name='user')
    
    # Kiểm tra user tồn tại
    if username not in df['username'].values:
        print(f"❌ User '{username}' không tồn tại!")
        return
    
    # Cập nhật password
    df.loc[df['username'] == username, 'password'] = hash_password(new_password)
    
    # Lưu lại
    with pd.ExcelWriter(LOG_FILE, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='user', index=False)
    
    print(f"✅ Đã đổi password cho user '{username}'")
    print(f"🔐 Password mới: {new_password} (đã được mã hóa)")

def show_help():
    """Hiển thị hướng dẫn"""
    print("""
📖 USER MANAGER - Quản lý user Supply Chain Tool

Cách sử dụng:
  python manage_users.py list                           # Xem danh sách user
  python manage_users.py add <username> <password>      # Thêm user mới
  python manage_users.py delete <username>              # Xóa user
  python manage_users.py password <username> <new_pass> # Đổi password

Ví dụ:
  python manage_users.py list
  python manage_users.py add admin admin123
  python manage_users.py delete olduser
  python manage_users.py password root newpass123
    """)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    if command == "list":
        list_users()
    
    elif command == "add":
        if len(sys.argv) != 4:
            print("❌ Sai cú pháp! Dùng: python manage_users.py add <username> <password>")
            sys.exit(1)
        add_user(sys.argv[2], sys.argv[3])
    
    elif command == "delete":
        if len(sys.argv) != 3:
            print("❌ Sai cú pháp! Dùng: python manage_users.py delete <username>")
            sys.exit(1)
        delete_user(sys.argv[2])
    
    elif command == "password":
        if len(sys.argv) != 4:
            print("❌ Sai cú pháp! Dùng: python manage_users.py password <username> <new_password>")
            sys.exit(1)
        change_password(sys.argv[2], sys.argv[3])
    
    else:
        print(f"❌ Lệnh không hợp lệ: {command}")
        show_help()
        sys.exit(1)
