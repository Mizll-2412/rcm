import pandas as pd
df = pd.read_csv("data\\Thu Thập Dữ Liệu Tình Nguyện (Câu trả lời) - Câu trả lời biểu mẫu 1.csv")
df.columns = df.columns.str.strip()
df = df.iloc[:, 1:-1] # bỏ cột đầu tiên và cột cuối cùng
start_col = "Họ Tên"
end_col = "Lĩnh vực mà bạn quan tâm"
cols = df.columns.tolist()
start_idx = cols.index(start_col)
end_idx = cols.index(end_col)
df_tnv = df.iloc[:, start_idx:end_idx+1]  # tình nguyện viên
df_tc = pd.concat([df.iloc[:, :start_idx], df.iloc[:, end_idx+1:]], axis=1)  # tổ chức
if "Họ Tên" in df_tnv.columns:
    df_tnv = df_tnv.drop(columns=["Họ Tên"])
drop_cols_tc = [c for c in ["Bạn là ai", "Mô tả công việc"] if c in df_tc.columns]
df_tc = df_tc.drop(columns=drop_cols_tc)
df_tnv = df_tnv.drop_duplicates()
df_tc = df_tc.drop_duplicates()
df_tnv.to_csv("tinhnguyenvien.csv", index=False)
df_tc.to_csv("tochuc.csv", index=False)

print("Đã tách, lọc cột, và loại bỏ trùng thành công: tinhnguyenvien.csv & tochuc.csv")
