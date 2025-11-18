import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import warnings
import re
warnings.filterwarnings('ignore')

df_volunteers = pd.read_csv('tinhnguyenvien.csv')

df_volunteers = df_volunteers.rename(columns={
    "Tuổi": "age",
    "Địa Điểm Sinh Sống": "location",
    "Kỹ năng bạn có": "skills",
    "Thời gian rảnh để tham gia tình nguyện": "time",
    "Lĩnh vực mà bạn quan tâm": "field"
})

df_volunteers = df_volunteers.dropna()

df_jobs = pd.read_csv('tochuc.csv')

df_jobs = df_jobs.rename(columns={
    "Tên hoạt động tình nguyện": "title",
    "Kỹ năng yêu cầu": "required_skills",
    "Lĩnh vực hoạt động": "field",
    "Thời gian thực hiện": "time",
    "Địa điểm": "location"
})

df_jobs = df_jobs.dropna()
print("=" * 60)
print("DATASET TÌNH NGUYỆN VIÊN:")
print(df_volunteers.head(1).to_string())
print("\n" + "=" * 60)
print("DATASET CÔNG VIỆC:")
print(df_jobs.head())


df_volunteers["combined_features"] = (
    df_volunteers["age"].astype(str) + " " +
    df_volunteers["skills"].apply(lambda x: re.sub(r'[/,]+', ' ', x)) + " " +
    df_volunteers["field"].apply(lambda x: re.sub(r'[/,]+', ' ', x)) + " " +
    df_volunteers["location"] + " " +
    df_volunteers["time"]
)

df_jobs["combined_features"] = (
    df_jobs["title"] + " " +
    df_jobs["required_skills"].apply(lambda x: re.sub(r'[/,]+', ' ', x)) + " " +
    df_jobs["field"].apply(lambda x: re.sub(r'[/,]+', ' ', x)) + " " +
    df_jobs["location"] + " " +
    df_jobs["time"]
)

# print("\n" + "=" * 60)
# print("ĐẶC TRƯNG KẾT HỢP (VOLUNTEERS):")
# for i, row in df_volunteers.head(5).iterrows():
#     print(f"{row['age']}: {row['combined_features']}")

# Khởi tạo TF-IDF Vectorizer với tiếng Việt
vectorizer = TfidfVectorizer(
    max_features=100,
    ngram_range=(1, 2),  # Sử dụng unigram và bigram
    min_df=1,
    stop_words=None
)

all_features = pd.concat([
    df_volunteers["combined_features"],
    df_jobs["combined_features"]
])

vectorizer.fit(all_features)

volunteers_tfidf = vectorizer.transform(df_volunteers["combined_features"])
jobs_tfidf = vectorizer.transform(df_jobs["combined_features"])

print("\n" + "=" * 60)
print("TF-IDF MATRIX SHAPE:")
print(f"Volunteers: {volunteers_tfidf.shape}")
print(f"Jobs: {jobs_tfidf.shape}")
print(f"\nVocabulary size: {len(vectorizer.vocabulary_)}")
print(f"Sample vocabulary: {list(vectorizer.vocabulary_.keys())[:10]}")
cosine_sim_matrix = cosine_similarity(volunteers_tfidf, jobs_tfidf)
similarity_df = pd.DataFrame(
    cosine_sim_matrix,
    index=df_volunteers["age"],
    columns=df_jobs["title"]
)

# print("\n" + "=" * 60)
# print("MA TRẬN COSINE SIMILARITY:")
# print(similarity_df.round(3).to_string())

def recommend_jobs_for_volunteer(vol_idx, top_k=3, threshold=0.1):
    if vol_idx >= len(similarity_df):
        return f"Chỉ số tình nguyện viên {vol_idx} không hợp lệ"
    
    scores = similarity_df.iloc[vol_idx, :]
    top_jobs = scores.sort_values(ascending=False)[:top_k]
    top_jobs = top_jobs[top_jobs >= threshold]
    
    result = pd.DataFrame({
        "Tên công việc": top_jobs.index,
        "Điểm phù hợp": (top_jobs.values * 100).round(1),
        "Mức độ": [
            "Rất phù hợp" if s > 0.7 else
            "Phù hợp" if s > 0.4 else
            "Có thể xem xét"
            for s in top_jobs.values
        ]
    })
    return result

def recommend_volunteers_for_job(job_title, top_k=3, threshold=0.1):
    if job_title not in similarity_df.columns:
        return f"Không tìm thấy công việc: {job_title}"
    scores = similarity_df[job_title]
    top_volunteers = scores.sort_values(ascending=False)[:top_k]
    
    # Lọc theo threshold
    top_volunteers = top_volunteers[top_volunteers >= threshold]
    result = pd.DataFrame({
        'Tình nguyện viên': top_volunteers.index,
        'Điểm phù hợp': (top_volunteers.values * 100).round(1),
        'Mức độ': ['Rất phù hợp' if s > 0.7 else 'Phù hợp' if s > 0.4 else 'Có thể xem xét' 
                   for s in top_volunteers.values]
    })
    
    return result


# print("\n" + "=" * 60)
# print("TEST 1: GỢI Ý CÔNG VIỆC CHO TÌNH NGUYỆN VIÊN:")
# print(recommend_jobs_for_volunteer(5, top_k=3))
# print(df_volunteers.loc[5])

# print("\n" + "=" * 60)
# print("TEST 2: GỢI Ý TÌNH NGUYỆN VIÊN CHO 'Dịch tài liệu tiếng Anh':")
# print(recommend_volunteers_for_job("Dọn dẹp rác", top_k=3))

def get_all_best_matches():
    """
    Tìm best match cho tất cả tình nguyện viên
    """
    results = []
    
    for volunteer in df_volunteers["name"]:
        best_job_idx = similarity_df.loc[volunteer, :].idxmax()
        best_score = similarity_df.loc[volunteer, best_job_idx]
        
        results.append({
            'Tình nguyện viên': volunteer,
            'Best Match': best_job_idx,
            'Điểm': f"{best_score*100:.1f}%"
        })
    
    return pd.DataFrame(results)

print("\n" + "=" * 60)
print("BEST MATCHES CHO TẤT CẢ TÌNH NGUYỆN VIÊN:")
print(get_all_best_matches().to_string())

class VolunteerJobMatcher:
    def __init__(self, weight_skills=0.4, weight_location=0.2, 
                 weight_time=0.2, weight_interest=0.2):
        self.weight_skills = weight_skills
        self.weight_location = weight_location
        self.weight_time = weight_time
        self.weight_interest = weight_interest
        
        # Separate vectorizers cho từng feature type
        self.skills_vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        self.location_vectorizer = TfidfVectorizer()
        self.time_vectorizer = TfidfVectorizer()
        self.interest_vectorizer = TfidfVectorizer()
        
    def fit(self, df_volunteers, df_jobs):
        # Fit skills
        all_skills = pd.concat([
            df_volunteers["skills"].apply(lambda x: x.replace(",", " ")),
            df_jobs["required_skills"].apply(lambda x: x.replace(",", " "))
        ])
        self.skills_vectorizer.fit(all_skills)
        
        # Fit location
        all_locations = pd.concat([df_volunteers["location"], df_jobs["location"]])
        self.location_vectorizer.fit(all_locations)
        
        # Fit time
        all_times = pd.concat([df_volunteers["availability"], df_jobs["time"]])
        self.time_vectorizer.fit(all_times)
        
        # Fit interests
        all_interests = pd.concat([df_volunteers["interests"], df_jobs["field"]])
        self.interest_vectorizer.fit(all_interests)
        
    def calculate_weighted_similarity(self, df_volunteers, df_jobs):
        """Tính weighted similarity với multiple features"""
        
        # Transform các features
        vol_skills = self.skills_vectorizer.transform(
            df_volunteers["skills"].apply(lambda x: x.replace(",", " "))
        )
        job_skills = self.skills_vectorizer.transform(
            df_jobs["required_skills"].apply(lambda x: x.replace(",", " "))
        )
        
        vol_location = self.location_vectorizer.transform(df_volunteers["location"])
        job_location = self.location_vectorizer.transform(df_jobs["location"])
        
        vol_time = self.time_vectorizer.transform(df_volunteers["availability"])
        job_time = self.time_vectorizer.transform(df_jobs["time"])
        
        vol_interest = self.interest_vectorizer.transform(df_volunteers["interests"])
        job_interest = self.interest_vectorizer.transform(df_jobs["field"])
        sim_skills = cosine_similarity(vol_skills, job_skills)
        sim_location = cosine_similarity(vol_location, job_location)
        sim_time = cosine_similarity(vol_time, job_time)
        sim_interest = cosine_similarity(vol_interest, job_interest)
        weighted_sim = (
            self.weight_skills * sim_skills +
            self.weight_location * sim_location +
            self.weight_time * sim_time +
            self.weight_interest * sim_interest
        )
        
        return weighted_sim

print("\n" + "=" * 60)
print("ADVANCED WEIGHTED MATCHING:")
matcher = VolunteerJobMatcher()
matcher.fit(df_volunteers, df_jobs)
weighted_sim = matcher.calculate_weighted_similarity(df_volunteers, df_jobs)

weighted_df = pd.DataFrame(
    weighted_sim,
    index=df_volunteers["age"],
    columns=df_jobs["title"]
)
print(weighted_df.round(3).to_string())

print("\n" + "=" * 60)
print("MODEL TRAINING HOÀN TẤT!")
print(f"Đã xử lý {len(df_volunteers)} tình nguyện viên")
print(f"Đã xử lý {len(df_jobs)} công việc") 
print(f"Vocabulary size: {len(vectorizer.vocabulary_)} terms")
print(f"Similarity matrix shape: {cosine_sim_matrix.shape}")