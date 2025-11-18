import pandas as pd
import numpy as np
import re
import warnings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

warnings.filterwarnings('ignore')

df_volunteers = pd.read_csv('TinhNguyenVien_FullInfo.csv')
df_jobs = pd.read_csv('SuKien_FullInfo.csv')

# ĐỔI TÊN CỘT

df_volunteers = df_volunteers.rename(columns={
    "DiaChi": "location",
    "KyNangList": "skills",
    "LinhVucList": "field"
})
df_jobs = df_jobs.rename(columns={
    "TenSuKien": "title",
    "KyNangList": "required_skills",
    "DiaChi": "location",
    "LinhVucList": "field"
})
# LÀM SẠCH DỮ LIỆU
df_volunteers = df_volunteers.dropna(subset=["skills", "field", "location"])
df_jobs = df_jobs.dropna(subset=["title","required_skills", "field", "location"])

# df_volunteers["name"] = [f"Volunteer_{i+1}" for i in range(len(df_volunteers))]
# df_jobs["id"] = [f"Job_{i+1}" for i in range(len(df_jobs))]

# Làm sạch ký tự và chữ hoa
def clean_text(x):
    if isinstance(x, str):
        return re.sub(r'[/,]+', ' ', x).lower().strip()
    return ""

for col in ["skills", "field", "location"]:
    df_volunteers[col] = df_volunteers[col].apply(clean_text)

for col in ["title", "required_skills", "field", "location"]:
    df_jobs[col] = df_jobs[col].apply(clean_text)

def normalize_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    mapping = {
        "cntt": "công nghệ thông tin",
        "it": "công nghệ thông tin",
        "online": "trực tuyến",
        "tp hcm": "hồ chí minh",
        "hn": "hà nội"
    }
    for k, v in mapping.items():
        text = text.replace(k, v)
    return text

for col in ["skills", "field", "location"]:
    df_volunteers[col] = df_volunteers[col].apply(normalize_text)
for col in ["title", "required_skills", "field", "location"]:
    df_jobs[col] = df_jobs[col].apply(normalize_text)
# KẾT HỢP ĐẶC TRƯNG

df_volunteers["combined_features"] = (
    df_volunteers["skills"] + " " +
    df_volunteers["field"] + " " +
    df_volunteers["location"]
    )

df_jobs["combined_features"] = (
    df_jobs["title"]+ " " +
    df_jobs["required_skills"] + " " +
    df_jobs["field"] + " " +
    df_jobs["location"] 
)

# TF-IDF & COSINE SIMILARITY

def compute_similarity(vol_series, job_series, weight=1.0):
    vectorizer = TfidfVectorizer()
    combined = pd.concat([vol_series.fillna(''), job_series.fillna('')])
    tfidf_matrix = vectorizer.fit_transform(combined)
    n_vol = len(vol_series)
    sim = cosine_similarity(tfidf_matrix[:n_vol], tfidf_matrix[n_vol:])
    return sim * weight

W_SKILL = 0.45
W_FIELD = 0.4
W_LOCATION = 0.15

sim_skills = compute_similarity(df_volunteers["skills"], df_jobs["required_skills"], W_SKILL)
sim_field = compute_similarity(df_volunteers["field"], df_jobs["field"], W_FIELD)
sim_location = compute_similarity(df_volunteers["location"], df_jobs["location"], W_LOCATION)

similarity_matrix = sim_skills + sim_field + sim_location
similarity_df = pd.DataFrame(similarity_matrix, index=df_volunteers["MaTNV"], columns=df_jobs["MaSuKien"])

# HÀM GỢI Ý

def recommend_jobs_for_volunteer(vol_idx, top_k=3, threshold=0.1):
    if vol_idx >= len(similarity_df):
        return f"Chỉ số tình nguyện viên {vol_idx} không hợp lệ."
    
    scores = similarity_df.iloc[vol_idx, :]
    top_jobs = scores.sort_values(ascending=False).head(top_k)
    top_jobs = top_jobs[top_jobs >= threshold]
    
    result = pd.DataFrame({
        "Job ID": top_jobs.index,
        "Similarity (%)": (top_jobs.values * 100).round(1),
        "Match Level": [
            "Rất phù hợp" if s > 0.7 else
            "Phù hợp" if s > 0.4 else
            "Có thể xem xét"
            for s in top_jobs.values
        ]
    })
    return result

def recommend_volunteers_for_job(job_id, top_k=3, threshold=0.1):
    if job_id not in similarity_df.columns:
        return f"Không tìm thấy công việc: {job_id}"
    
    scores = similarity_df[job_id]
    top_volunteers = scores.sort_values(ascending=False).head(top_k)
    top_volunteers = top_volunteers[top_volunteers >= threshold]
    
    result = pd.DataFrame({
        "Volunteer": top_volunteers.index,
        "Similarity (%)": (top_volunteers.values * 100).round(1),
        "Match Level": [
            "Rất phù hợp" if s > 0.7 else
            "Phù hợp" if s > 0.4 else
            "Có thể xem xét"
            for s in top_volunteers.values
        ]
    })
    return result

def show_volunteer_info(vol_idx):
    print(df_volunteers.iloc[vol_idx])

def show_job_info(job_id):
    job_row = df_jobs.loc[df_jobs["MaSuKien"] == job_id]
    if not job_row.empty:
        print(job_row.iloc[0][["MaSuKien", "title", "required_skills", "field", "location"]])
    else:
        print(f"Không tìm thấy thông tin công việc {job_id}")

# GỢI Ý CHO TOÀN BỘ DANH SÁCH

def get_all_best_matches():
    results = []
    for volunteer in similarity_df.index:
        best_job = similarity_df.loc[volunteer, :].idxmax()
        best_score = similarity_df.loc[volunteer, best_job]
        results.append({
            "Volunteer": volunteer,
            "Best Job": best_job,
            "Score (%)": f"{best_score * 100:.1f}"
        })
    return pd.DataFrame(results)


# CHẠY THỬ

print("\n" + "="*70)
print(" TEST GỢI Ý CHO Volunteer_5:")
print(recommend_jobs_for_volunteer(4, top_k=3))

print("\nThông tin tình nguyện viên:")
show_volunteer_info(4)

print("\nChi tiết các công việc được gợi ý:")
for job in recommend_jobs_for_volunteer(4, top_k=3)["Job ID"]:
    show_job_info(job)
    print("-" * 50)

print("\n" + "="*70)
print(" TEST GỢI Ý CHO Job_2:")
print(recommend_volunteers_for_job(2, top_k=3))

print("\nThông tin công việc:")
show_job_info(2)

print("\nChi tiết các tình nguyện viên phù hợp:")
for vol in recommend_volunteers_for_job(2, top_k=3)["Volunteer"]:
    show_volunteer_info(int(vol) - 1)
    print("-" * 50)

# print("\n" + "=" * 70)
# print("BEST MATCHES:")
# print(get_all_best_matches().head(10).to_string(index=False))

print("\n" + "=" * 70)
print("MODEL TRAINING HOÀN TẤT!")
print(f"Đã xử lý {len(df_volunteers)} tình nguyện viên và {len(df_jobs)} công việc.")
