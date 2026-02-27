import sys
from pathlib import Path
from typing import List, Dict, Any

from qdrant_client import QdrantClient
from supabase import create_client, Client

# ===== 專案根目錄與環境載入 =====
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import settings  # 使用你現有的 settings

# ===== 常數設定 =====
BATCH_SIZE = 150  # 依照規劃文件
TABLE_NAME = "job_posting"


def init_clients() -> tuple[Client, QdrantClient]:
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    qdrant = QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
    )
    return supabase, qdrant


def fetch_jobs_batch(
    supabase: Client,
    offset: int,
    limit: int,
) -> List[Dict[str, Any]]:
    """
    從 job_posting 抓出需要同步的一批職缺。

    這裡先做「全量已貼標職缺」：
    - vector_id IS NOT NULL（已向量化，有 Qdrant 點）
    - is_labeled = TRUE（已貼標，有 D1–D6）
    """
    resp = (
        supabase.table(TABLE_NAME)
        .select(
            "job_id, vector_id, is_labeled, "
            "role_type, role_name, "
            "d1_frontend, d2_backend, d3_devops, d4_ai_data, d5_quality, d6_soft_skills"
        )
        .not_.is_("vector_id", "null")
        .eq("is_labeled", True)
        .order("job_id")
        .range(offset, offset + limit - 1)
        .execute()
    )
    return resp.data or []


def build_payload(job: Dict[str, Any]) -> Dict[str, Any]:
    """從 DB 資料組出要寫入 Qdrant 的 payload 子集。"""
    return {
        "is_labeled": job.get("is_labeled", False),
        "role_type": job.get("role_type"),
        "role_name": job.get("role_name"),
        "d1_frontend": job.get("d1_frontend"),
        "d2_backend": job.get("d2_backend"),
        "d3_devops": job.get("d3_devops"),
        "d4_ai_data": job.get("d4_ai_data"),
        "d5_quality": job.get("d5_quality"),
        "d6_soft_skills": job.get("d6_soft_skills"),
    }


def sync_batch(qdrant: QdrantClient, jobs: List[Dict[str, Any]]) -> int:
    """
    對一批職缺執行 Qdrant payload 更新。

    注意：這裡為簡單、直觀，採「一筆一個 set_payload 呼叫」，
    但在 DB 端仍然是 150 筆一批抓，之後如果需要再優化成更粗粒度的 batch。
    """
    updated = 0

    for job in jobs:
        vector_id = job.get("vector_id")
        if not vector_id:
            continue

        payload = build_payload(job)

        try:
            qdrant.set_payload(
                collection_name=settings.JOB_COLLECTION,
                payload=payload,
                points=[vector_id],
            )
            updated += 1
        except Exception as e:
            print(f"❌ job_id={job['job_id']} / vector_id={vector_id} set_payload 失敗: {e}")

    return updated


def main() -> None:
    supabase, qdrant = init_clients()

    # 先算出總筆數，讓你有感覺這次會跑多久
    count_resp = (
        supabase.table(TABLE_NAME)
        .select("job_id", count="exact")
        .not_.is_("vector_id", "null")
        .eq("is_labeled", True)
        .execute()
    )
    total = getattr(count_resp, "count", None)
    if total is None and hasattr(count_resp, "data"):
        total = len(count_resp.data)
    if total is None:
        total = 0

    print(f"📊 需要同步的職缺（已向量化且已貼標）總數: {total}")
    if total == 0:
        print("✅ 沒有需要同步的資料，結束。")
        return

    confirm = input("是否開始執行全量同步到 Qdrant？(y/n): ")
    if confirm.lower() != "y":
        print("❌ 使用者取消作業")
        return

    offset = 0
    total_updated = 0
    batch_index = 0

    while offset < total:
        jobs = fetch_jobs_batch(supabase, offset=offset, limit=BATCH_SIZE)
        if not jobs:
            break

        batch_index += 1
        print(f"\n=== 處理批次 {batch_index}（offset={offset}, 批次大小={len(jobs)}）===")

        updated = sync_batch(qdrant, jobs)
        total_updated += updated

        print(f"✅ 本批成功更新 {updated}/{len(jobs)} 筆")
        offset += BATCH_SIZE

    print("\n=== 全量同步完成 ===")
    print(f"🎉 總共成功更新 {total_updated}/{total} 筆職缺的 Qdrant payload")


if __name__ == "__main__":
    main()