"""
建立 Qdrant collections：resume_vectors、job_vectors、optimized_resume_vectors（1536 維、COSINE）。
執行前請確保 .env 或 Erd/.env 已設定 QDRANT_URL、QDRANT_API_KEY。
建議執行順序：先跑本腳本建立 collections，再跑 vectorize_jobs.py / vectorize_resumes.py / vectorize_optimized_resumes.py。

optimized_resume_vectors 用途：
  職缺推薦時讓使用者選擇「優化前／優化後」履歷做向量比對，需對 RESUME_OPTIMIZATION 產出做向量化。
  Payload 建議結構（與 qdrant_retriever 篩選邏輯、RESUME_OPTIMIZATION 表對齊）：
    - 必填（篩選用）：optimization_id, user_id, resume_id
    - 向量化來源欄位（與 ERD RESUME_OPTIMIZATION 對應，可選存 payload 供顯示）：
      professional_summary（專業摘要）, professional_experience（工作經歷）,
      core_skills（核心技能）, projects（專案作品集）, education（學歷）, autobiography（自傳）
"""

import os
import sys
from pathlib import Path

# 專案根目錄 = supabase_control
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# 載入 .env（與原 qdrant.ipynb 一致）
for _path in [PROJECT_ROOT / "Erd" / ".env", PROJECT_ROOT / ".env"]:
    if _path.exists():
        load_dotenv(_path)
        break
else:
    load_dotenv()

QDRANT_URL = (os.getenv("QDRANT_URL") or "").strip()
QDRANT_API_KEY = (os.getenv("QDRANT_API_KEY") or "").strip()
if not QDRANT_URL or not QDRANT_API_KEY:
    raise ValueError("請在 .env 設定 QDRANT_URL 與 QDRANT_API_KEY")

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# 檢查現有 collections
collections = client.get_collections().collections
existing_names = [c.name for c in collections]

if "resume_vectors" not in existing_names:
    client.create_collection(
        collection_name="resume_vectors",
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
    )
    print("✅ resume_vectors 建立完成")
else:
    print("⚠️  resume_vectors 已存在")

if "job_vectors" not in existing_names:
    client.create_collection(
        collection_name="job_vectors",
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
    )
    print("✅ job_vectors 建立完成")
else:
    print("⚠️  job_vectors 已存在")

# 優化後履歷向量：職缺推薦時可選「優化後履歷」做比對
if "optimized_resume_vectors" not in existing_names:
    client.create_collection(
        collection_name="optimized_resume_vectors",
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
    )
    print("✅ optimized_resume_vectors 建立完成")
else:
    print("⚠️  optimized_resume_vectors 已存在")

print("目前 collections:", [c.name for c in client.get_collections().collections])
