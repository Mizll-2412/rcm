import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import warnings
warnings.filterwarnings('ignore')



# Tạo DataFrame
df_volunteers = pd.read_csv('data\\tinhnguyenvien.csv')
df_jobs = pd.read_csv('data\\tochuc.csv')

df_volunteers = df_volunteers.rename(columns={
    "Tuổi": "age",
    "Địa Điểm Sinh Sống": "location",
    "Kỹ năng bạn có": "skills",
    "Thời gian rảnh để tham gia tình nguyện": "time",
    "Lĩnh vực mà bạn quan tâm": "field"
})
df_jobs = df_jobs.rename(columns={
    "Tên hoạt động tình nguyện": "title",
    "Kỹ năng yêu cầu": "required_skills",
    "Địa điểm": "location",
    "Thời gian thực hiện": "time",
    "Lĩnh vực hoạt động": "field"
})
# LÀM SẠCH DỮ LIỆU
df_volunteers = df_volunteers.dropna(subset=["skills", "field", "location", "time"])
df_jobs = df_jobs.dropna(subset=["required_skills", "field", "location", "time"])

df_volunteers["name"] = [f"Volunteer_{i+1}" for i in range(len(df_volunteers))]
df_jobs["id"] = [f"Job_{i+1}" for i in range(len(df_jobs))]

# Làm sạch ký tự và chữ hoa
def clean_text(x):
    if isinstance(x, str):
        return re.sub(r'[/,]+', ' ', x).lower().strip()
    return ""

for col in ["skills", "field", "location", "time"]:
    df_volunteers[col] = df_volunteers[col].apply(clean_text)

for col in ["required_skills", "field", "location", "time"]:
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

for col in ["skills", "field", "location", "time"]:
    df_volunteers[col] = df_volunteers[col].apply(normalize_text)
for col in ["required_skills", "field", "location", "time"]:
    df_jobs[col] = df_jobs[col].apply(normalize_text)


df_volunteers["combined_features"] = (
    df_volunteers["skills"] + " " +
    df_volunteers["field"] + " " +
    df_volunteers["location"] + " " +
    df_volunteers["time"]
)

df_jobs["combined_features"] = (
    df_jobs["title"]+ " " +
    df_jobs["required_skills"] + " " +
    df_jobs["field"] + " " +
    df_jobs["location"] + " " +
    df_jobs["time"]
)

# Khởi tạo TF-IDF Vectorizer với tiếng Việt
vectorizer = TfidfVectorizer(
    max_features=100,
    ngram_range=(1, 2),  # Sử dụng unigram và bigram
    min_df=1,
    stop_words=None  # Có thể thêm stop words tiếng Việt
)

# Kết hợp tất cả features để fit vectorizer
all_features = pd.concat([
    df_volunteers["combined_features"],
    df_jobs["combined_features"]
])

# Fit vectorizer với tất cả dữ liệu
vectorizer.fit(all_features)

# Transform riêng cho volunteers và jobs
volunteers_tfidf = vectorizer.transform(df_volunteers["combined_features"])
jobs_tfidf = vectorizer.transform(df_jobs["combined_features"])

print("\n" + "=" * 60)
print("TF-IDF MATRIX SHAPE:")
print(f"Volunteers: {volunteers_tfidf.shape}")
print(f"Jobs: {jobs_tfidf.shape}")
print(f"\nVocabulary size: {len(vectorizer.vocabulary_)}")
print(f"Sample vocabulary: {list(vectorizer.vocabulary_.keys())[:10]}")

# ==================== PHẦN 4: TÍNH TOÁN SIMILARITY ====================

# Tính cosine similarity giữa volunteers và jobs
cosine_sim_matrix = cosine_similarity(volunteers_tfidf, jobs_tfidf)

# Tạo DataFrame để dễ visualize
similarity_df = pd.DataFrame(
    cosine_sim_matrix,
    index=df_volunteers["name"],
    columns=df_jobs["title"]
)

print("\n" + "=" * 60)
print("MA TRẬN COSINE SIMILARITY:")
print(similarity_df.round(3).to_string())

# ==================== PHẦN 5: HÀM RECOMMENDATION ====================

def recommend_jobs_for_volunteer(volunteer_name, top_k=3, threshold=0.1):
    """
    Gợi ý top K công việc phù hợp nhất cho một tình nguyện viên
    
    Parameters:
    - volunteer_name: Tên tình nguyện viên
    - top_k: Số lượng gợi ý
    - threshold: Ngưỡng similarity tối thiểu
    """
    if volunteer_name not in similarity_df.index:
        return f"Không tìm thấy tình nguyện viên: {volunteer_name}"
    
    # Lấy scores cho volunteer
    scores = similarity_df.loc[volunteer_name, :]
    
    # Sort và lấy top K
    top_jobs = scores.sort_values(ascending=False)[:top_k]
    
    # Lọc theo threshold
    top_jobs = top_jobs[top_jobs >= threshold]
    
    # Format kết quả
    result = pd.DataFrame({
        'Công việc': top_jobs.index,
        'Điểm phù hợp': (top_jobs.values * 100).round(1),
        'Mức độ': ['Rất phù hợp' if s > 0.7 else 'Phù hợp' if s > 0.4 else 'Có thể xem xét' 
                   for s in top_jobs.values]
    })
    
    return result

def recommend_volunteers_for_job(job_title, top_k=3, threshold=0.1):
    """
    Gợi ý top K tình nguyện viên phù hợp nhất cho một công việc
    
    Parameters:
    - job_title: Tên công việc
    - top_k: Số lượng gợi ý
    - threshold: Ngưỡng similarity tối thiểu
    """
    if job_title not in similarity_df.columns:
        return f"Không tìm thấy công việc: {job_title}"
    
    # Lấy scores cho job
    scores = similarity_df[job_title]
    
    # Sort và lấy top K
    top_volunteers = scores.sort_values(ascending=False)[:top_k]
    
    # Lọc theo threshold
    top_volunteers = top_volunteers[top_volunteers >= threshold]
    
    # Format kết quả
    result = pd.DataFrame({
        'Tình nguyện viên': top_volunteers.index,
        'Điểm phù hợp': (top_volunteers.values * 100).round(1),
        'Mức độ': ['Rất phù hợp' if s > 0.7 else 'Phù hợp' if s > 0.4 else 'Có thể xem xét' 
                   for s in top_volunteers.values]
    })
    
    return result

# ==================== PHẦN 6: TEST RECOMMENDATIONS ====================

print("\n" + "=" * 60)
print("TEST 1: GỢI Ý CÔNG VIỆC CHO TÌNH NGUYỆN VIÊN 'An':")
print(recommend_jobs_for_volunteer("An", top_k=3))

print("\n" + "=" * 60)
print("TEST 2: GỢI Ý TÌNH NGUYỆN VIÊN CHO 'Dịch tài liệu tiếng Anh':")
print(recommend_volunteers_for_job("Dịch tài liệu tiếng Anh", top_k=3))

# ==================== PHẦN 7: BATCH RECOMMENDATIONS ====================

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

# ==================== PHẦN 8: ADVANCED FEATURES ====================

class VolunteerJobMatcher:
    """
    Class chứa model matching nâng cao với multiple features
    """
    
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
        """Fit các vectorizers với dữ liệu"""
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
        
        # Tính similarity cho từng feature
        sim_skills = cosine_similarity(vol_skills, job_skills)
        sim_location = cosine_similarity(vol_location, job_location)
        sim_time = cosine_similarity(vol_time, job_time)
        sim_interest = cosine_similarity(vol_interest, job_interest)
        
        # Weighted average
        weighted_sim = (
            self.weight_skills * sim_skills +
            self.weight_location * sim_location +
            self.weight_time * sim_time +
            self.weight_interest * sim_interest
        )
        
        return weighted_sim

# Test advanced matcher
print("\n" + "=" * 60)
print("ADVANCED WEIGHTED MATCHING:")
matcher = VolunteerJobMatcher()
matcher.fit(df_volunteers, df_jobs)
weighted_sim = matcher.calculate_weighted_similarity(df_volunteers, df_jobs)

weighted_df = pd.DataFrame(
    weighted_sim,
    index=df_volunteers["name"],
    columns=df_jobs["title"]
)
print(weighted_df.round(3).to_string())

print("\n" + "=" * 60)
print("MODEL TRAINING HOÀN TẤT!")
print(f"✅ Đã xử lý {len(df_volunteers)} tình nguyện viên")
print(f"✅ Đã xử lý {len(df_jobs)} công việc") 
print(f"✅ Vocabulary size: {len(vectorizer.vocabulary_)} terms")
print(f"✅ Similarity matrix shape: {cosine_sim_matrix.shape}")