"""
Script khởi tạo file log.xlsx với user mặc định root/root
"""
import pandas as pd
from pathlib import Path
import hashlib

def hash_password(password: str) -> str:
    """Mã hóa password bằng SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

# Đường dẫn file
LOG_DIR = Path(__file__).parent / "log"
LOG_FILE = LOG_DIR / "log.xlsx"

# Tạo folder nếu chưa có
LOG_DIR.mkdir(exist_ok=True)

# Tạo DataFrame với user mặc định
data = {
    'username': ['root'],
    'password': [hash_password('root')]  # Mã hóa password
}

df = pd.DataFrame(data)

# Lưu vào Excel
with pd.ExcelWriter(LOG_FILE, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='user', index=False)

print(f"✅ Đã tạo file {LOG_FILE}")
print(f"📝 User mặc định: root / root")
print(f"🔐 Password đã được mã hóa SHA256")
