import pandas as pd
import sys
import json
from model_3 import recommend_jobs_for_volunteer, df_jobs, df_volunteers

maTNV = sys.argv[1]  
vol_index = df_volunteers.index[df_volunteers['MaTNV'] == int(maTNV)][0]

results = recommend_jobs_for_volunteer(vol_index, top_k=5)

output = []
for _, row in results.iterrows():
    job_id = row["Job ID"]
    job_info = df_jobs[df_jobs["MaSuKien"] == job_id].iloc[0]

    output.append({
        "maSuKien": int(job_id),
        "tenSuKien": job_info["title"],
        "diaChi": job_info["location"],
        "diemPhuHop": float(row["Similarity (%)"]) / 100
    })

print(json.dumps(output, ensure_ascii=False))
