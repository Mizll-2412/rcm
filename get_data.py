import pyodbc
import pandas as pd
import time
from datetime import datetime

# ===== Cấu hình kết nối Windows Authentication =====
server = r'ADMIN-PC\SQLEXPRESS01'
database = 'tinhnguyen_db'
driver = '{ODBC Driver 18 for SQL Server}'

conn_str = f"""
DRIVER={driver};
SERVER={server};
DATABASE={database};
Trusted_Connection=yes;
TrustServerCertificate=YES;
"""

# ===== Danh sách view và file CSV =====
views = {
    "vw_TinhNguyenVien_FullInfo": "TinhNguyenVien_FullInfo.csv",
    "vw_SuKien_FullInfo": "SuKien_FullInfo.csv"
}

# ===== Thời gian chờ giữa các lần sync (giây) =====
interval_minutes = 5
interval_seconds = interval_minutes * 60

# ===== Hàm lấy dữ liệu incremental =====
def sync_view(view_name, file_name, conn):
    try:
        # Lấy dữ liệu từ SQL
        df_new = pd.read_sql(f"SELECT * FROM {view_name}", conn)
        print(f"[{datetime.now()}] Lấy {len(df_new)} dòng từ view {view_name}")

        try:
            # Nếu file đã tồn tại, đọc dữ liệu cũ
            df_old = pd.read_csv(file_name, encoding='utf-8-sig')
            # Ghép dữ liệu mới với cũ, loại bỏ trùng lặp (theo tất cả các cột)
            df_combined = pd.concat([df_old, df_new]).drop_duplicates()
        except FileNotFoundError:
            # File chưa tồn tại, dùng dữ liệu mới
            df_combined = df_new

        # Ghi lại CSV
        df_combined.to_csv(file_name, index=False, encoding='utf-8-sig')
        print(f"Đã sync {len(df_combined)} dòng vào {file_name}")

    except Exception as e:
        print(f"Lỗi khi sync view {view_name}: {e}")

# ===== Chạy vòng lặp sync định kỳ =====
try:
    conn = pyodbc.connect(conn_str)
    print("Kết nối SQL Server thành công!")

    while True:
        for view_name, file_name in views.items():
            sync_view(view_name, file_name, conn)
        print(f"Đợi {interval_minutes} phút trước lần sync tiếp theo...\n")
        time.sleep(interval_seconds)

except KeyboardInterrupt:
    print("Dừng chương trình theo yêu cầu người dùng.")
except Exception as e:
    print("Lỗi kết nối hoặc chạy chương trình:", e)
finally:
    if 'conn' in locals():
        conn.close()
