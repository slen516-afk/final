"""
驗證 Supabase 與 Qdrant 同步狀態
"""

import sys
from pathlib import Path

from supabase import create_client
from qdrant_client import QdrantClient

# 專案根目錄 = supabase_control
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import settings

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
qdrant = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)

print("=" * 60)
print("Supabase ↔ Qdrant 同步驗證")
print("=" * 60)

# ========== 1. 統計資料 ==========
supabase_total = (
    supabase.table("job_posting").select("job_id", count="exact").execute().count
)
supabase_embedded = (
    supabase.table("job_posting")
    .select("job_id", count="exact")
    .eq("is_embedded", True)
    .execute()
    .count
)

qdrant_info = qdrant.get_collection(settings.JOB_COLLECTION)

print(f"\n📊 資料統計:")
print(f"  Supabase 總職缺數: {supabase_total}")
if supabase_total and supabase_total > 0:
    print(
        f"  Supabase 已向量化: {supabase_embedded} ({supabase_embedded / supabase_total * 100:.1f}%)"
    )
else:
    print(f"  Supabase 已向量化: {supabase_embedded}")
print(f"  Qdrant 向量總數:   {qdrant_info.points_count}")

# ========== 2. 一致性檢查 ==========
if supabase_embedded != qdrant_info.points_count:
    print(f"\n⚠️  警告：資料不一致！")
    print(f"  差異: {abs(supabase_embedded - qdrant_info.points_count)} 筆")
else:
    print(f"\n✅ 資料一致")

# ========== 3. 抽查驗證（含薪資欄位） ==========
print(f"\n🔍 抽查驗證 (隨機 5 筆):")
samples = (
    supabase.table("job_posting")
    .select("job_id, vector_id, job_title, salary_min, salary_max")
    .eq("is_embedded", True)
    .limit(5)
    .execute()
)

for i, sample in enumerate(samples.data or [], 1):
    try:
        point = qdrant.retrieve(
            collection_name=settings.JOB_COLLECTION,
            ids=[sample["vector_id"]],
        )

        if point:
            payload = point[0].payload
            payload_job_id = payload.get("job_id")
            payload_salary = (
                f"{payload.get('salary_min', 'N/A')} - {payload.get('salary_max', 'N/A')}"
            )

            match = "✅" if payload_job_id == sample["job_id"] else "❌"
            vid = sample.get("vector_id") or ""
            vid_short = vid[:8] + "..." if len(vid) > 8 else vid
            print(
                f"  {i}. job_id={sample['job_id']} | vector_id={vid_short} | 薪資: {payload_salary} {match}"
            )
        else:
            print(f"  {i}. job_id={sample['job_id']} ❌ Qdrant 找不到對應 Point")

    except Exception as e:
        print(f"  {i}. job_id={sample['job_id']} ❌ 錯誤: {e}")

if not (samples.data and len(samples.data) > 0):
    print("  （尚無已向量化資料可抽查）")

print("=" * 60)
