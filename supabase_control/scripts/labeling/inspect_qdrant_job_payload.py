import sys
from pathlib import Path

from qdrant_client import QdrantClient, models

# 用途：依 job_id 檢查 Qdrant 中對應點的 payload。
# 使用方式（在專案根目錄 supabase_control 下執行）：
#   python .\scripts\labeling\inspect_qdrant_job_payload.py <job_id>
# 範例：
#   python .\scripts\labeling\inspect_qdrant_job_payload.py 29621

# 專案根目錄 = supabase_control
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import settings


def inspect_job(job_id: int) -> None:
    """依 job_id 從 Qdrant 抓出對應點並印出 payload。"""
    client = QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
    )

    points, next_page = client.scroll(
        collection_name=settings.JOB_COLLECTION,
        scroll_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="job_id",
                    match=models.MatchValue(value=job_id),
                )
            ]
        ),
        limit=1,
        with_payload=True,
    )

    if not points:
        print(f"⚠️ Qdrant 中找不到 job_id={job_id} 的點（可能尚未向量化或 payload 無此欄位）。")
        return

    point = points[0]
    print(f"Point ID: {point.id}")
    print(f"job_id: {job_id}")
    print("Payload:")
    print(point.payload)


def main() -> None:
    if len(sys.argv) < 2:
        print("用法: python inspect_qdrant_job_payload.py <job_id>")
        sys.exit(1)

    try:
        job_id = int(sys.argv[1])
    except ValueError:
        print("❌ job_id 必須是整數")
        sys.exit(1)

    inspect_job(job_id)


if __name__ == "__main__":
    main()

