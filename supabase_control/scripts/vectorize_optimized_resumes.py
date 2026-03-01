"""
Career Pilot 優化後履歷向量化主程式
功能：
1. 從 Supabase 批次提取未向量化的 resume_optimization（is_embedded = False）
2. 以 professional_summary、professional_experience、core_skills、projects、education、autobiography 組合成文本並向量化
3. 使用 OpenAI text-embedding-3-large 產生 1536 維向量，寫入 Qdrant optimized_resume_vectors
4. 回寫 resume_optimization 表的 vector_id 與 is_embedded
5. Payload 僅存：optimization_id, user_id, resume_id（篩選用），六個內容欄位不寫入 payload

流程／後端串接：
- 使用者使用履歷優化功能（每月次數由後端卡上限）、寫入 resume_optimization 後，後端可立即觸發本腳本只處理該筆：設 OPTIMIZATION_IDS=<optimization_id> 再執行（不問 confirm）。
- 未設 OPTIMIZATION_IDS 時為批次模式（依 OPTIMIZED_RESUME_LIMIT），適合 cron 或手動補跑。
"""

import os
import sys
import time
import uuid
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from openai import OpenAI
from supabase import create_client, Client
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from tqdm import tqdm

# 專案根目錄 = supabase_control（scripts 的上一層）
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import settings

LOG_FILE = PROJECT_ROOT / "logs" / "vectorization.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# 本腳本預設只處理前 N 筆（可透過 OPTIMIZED_RESUME_LIMIT 環境變數覆寫）
OPTIMIZED_RESUME_LIMIT = int(os.getenv("OPTIMIZED_RESUME_LIMIT", "10"))
# 後端觸發「指定優化結果」向量化時可傳 OPTIMIZATION_IDS=5,6,7，只處理這些 optimization_id（仍限 is_embedded=False）
_OPTIMIZATION_IDS_ENV = os.getenv("OPTIMIZATION_IDS", "").strip()
OPTIMIZATION_IDS = [int(x.strip()) for x in _OPTIMIZATION_IDS_ENV.split(",") if x.strip().isdigit()] if _OPTIMIZATION_IDS_ENV else None

# 向量化來源欄位（與 ERD RESUME_OPTIMIZATION 對應）
VECTOR_FIELDS = [
    "professional_summary",   # 專業摘要
    "professional_experience", # 工作經歷
    "core_skills",            # 核心技能
    "projects",               # 專案作品集
    "education",              # 學歷
    "autobiography",          # 自傳
]

openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
qdrant_client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
)


def _json_to_flat_text(obj: Any) -> str:
    """將 JSON/JSONB 轉成可向量化字串，遞迴展開。"""
    if obj is None:
        return ""
    if isinstance(obj, str):
        return obj.strip()
    if isinstance(obj, (int, float)):
        return str(obj)
    if isinstance(obj, list):
        parts = []
        for item in obj:
            part = _json_to_flat_text(item)
            if part:
                parts.append(part)
        return "\n".join(parts)
    if isinstance(obj, dict):
        parts = []
        for k, v in obj.items():
            if v is None or v == "":
                continue
            v_str = _json_to_flat_text(v)
            if v_str:
                parts.append(f"{k}: {v_str}")
        return "\n".join(parts)
    return str(obj).strip() if obj else ""


def prepare_optimized_resume_text(row: Dict) -> str:
    """
    依 ERD：向量化來源為 professional_summary, professional_experience, core_skills, projects, education, autobiography。
    依序拼接為單一文本。
    """
    parts = []
    for field in VECTOR_FIELDS:
        val = row.get(field)
        if val is None:
            continue
        text = _json_to_flat_text(val)
        if text:
            parts.append(text)
    combined = "\n\n".join(parts)
    if len(combined) > settings.MAX_TEXT_LENGTH:
        combined = combined[: settings.MAX_TEXT_LENGTH]
        logger.warning(
            "⚠️  optimization_id %s 文本過長，已截斷至 %s 字元",
            row.get("optimization_id"),
            settings.MAX_TEXT_LENGTH,
        )
    return combined.strip()


def prepare_payload(row: Dict) -> Dict:
    """
    準備寫入 Qdrant 的 payload，只放篩選用三欄：optimization_id, user_id, resume_id。
    六個向量化欄位僅用於組文本做 embedding，不寫入 payload。
    """
    return {
        "optimization_id": row["optimization_id"],
        "user_id": row["user_id"],
        "resume_id": row["resume_id"],
    }


def get_embedding(text: str) -> List[float]:
    """調用 OpenAI Embedding API（text-embedding-3-large，1536 維）。"""
    try:
        response = openai_client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=text,
            dimensions=settings.EMBEDDING_DIMENSIONS,
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error("❌ Embedding API 失敗: %s", e)
        raise


def vectorize_optimized_resumes_batch(limit: int, optimization_ids: Optional[List[int]] = None) -> tuple:
    """
    處理單一批次優化後履歷向量化（每次撈「下一批」未嵌入，不依賴 offset）。
    optimization_ids: 若提供，只處理這些 optimization_id（仍限 is_embedded=False），供後端「優化完成後立即向量化」觸發。
    Returns:
        (成功筆數, 失敗筆數, 跳過筆數)
    """
    try:
        q = (
            supabase.table("resume_optimization")
            .select(
                "optimization_id, resume_id, user_id, "
                "professional_summary, professional_experience, core_skills, "
                "projects, education, autobiography"
            )
            .eq("is_embedded", False)
        )
        if optimization_ids:
            q = q.in_("optimization_id", optimization_ids)
        else:
            q = q.order("optimization_id").limit(limit)
        response = q.execute()
        rows = response.data or []
    except Exception as e:
        logger.error("❌ Supabase 查詢 resume_optimization 失敗: %s", e)
        return (0, 0, 0)

    if not rows:
        return (0, 0, 0)

    success_count = 0
    fail_count = 0
    skip_count = 0
    points = []
    update_records = []

    for row in rows:
        optimization_id = row["optimization_id"]
        try:
            text = prepare_optimized_resume_text(row)
            if not text:
                logger.warning(
                    "⚠️  optimization_id %s: 六個向量化欄位皆為空，跳過",
                    optimization_id,
                )
                skip_count += 1
                continue

            vector = get_embedding(text)
            vector_id = str(uuid.uuid4())

            points.append(
                PointStruct(
                    id=vector_id,
                    vector=vector,
                    payload=prepare_payload(row),
                )
            )
            update_records.append({
                "optimization_id": optimization_id,
                "vector_id": vector_id,
            })
            success_count += 1
            time.sleep(settings.RATE_LIMIT_DELAY)

        except Exception as e:
            logger.error("❌ optimization_id %s 處理失敗: %s", optimization_id, e)
            fail_count += 1

    if points:
        try:
            qdrant_client.upsert(
                collection_name=settings.OPTIMIZED_RESUME_COLLECTION,
                points=points,
            )
            logger.info("✅ Qdrant 寫入 %s 筆優化後履歷向量", len(points))
        except Exception as e:
            logger.error("❌ Qdrant 優化後履歷批次寫入失敗: %s", e)
            return (0, fail_count + len(update_records), skip_count)

    for record in update_records:
        try:
            supabase.table("resume_optimization").update({
                "vector_id": record["vector_id"],
                "is_embedded": True,
            }).eq("optimization_id", record["optimization_id"]).execute()
        except Exception as e:
            logger.error(
                "❌ optimization_id %s 回寫 Supabase 失敗: %s",
                record["optimization_id"],
                e,
            )
            success_count -= 1
            fail_count += 1

    return (success_count, fail_count, skip_count)


def main():
    """主流程：可依 OPTIMIZATION_IDS 只處理指定優化結果，或依 OPTIMIZED_RESUME_LIMIT 批次處理。"""
    logger.info("=" * 60)
    logger.info("Career Pilot 優化後履歷向量化作業")
    logger.info("執行時間: %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("模型: %s，維度: %s", settings.EMBEDDING_MODEL, settings.EMBEDDING_DIMENSIONS)
    logger.info("Collection: %s", settings.OPTIMIZED_RESUME_COLLECTION)
    if OPTIMIZATION_IDS:
        logger.info("模式: 指定 ID（OPTIMIZATION_IDS=%s）", OPTIMIZATION_IDS)
    else:
        logger.info("本輪處理筆數上限: %s", OPTIMIZED_RESUME_LIMIT)
    logger.info("=" * 60)

    if OPTIMIZATION_IDS:
        # 後端觸發：只處理指定 optimization_id（優化完成、扣完每月次數後呼叫），不問 confirm
        ok, fail, skip = vectorize_optimized_resumes_batch(limit=0, optimization_ids=OPTIMIZATION_IDS)
        logger.info("指定 ID 模式完成：成功=%s, 失敗=%s, 跳過=%s", ok, fail, skip)
        return

    try:
        count_response = (
            supabase.table("resume_optimization")
            .select("optimization_id", count="exact")
            .eq("is_embedded", False)
            .execute()
        )
        total_pending = getattr(count_response, "count", None)
        if total_pending is None and hasattr(count_response, "data"):
            total_pending = len(count_response.data or [])
        if total_pending is None:
            total_pending = 0
    except Exception as e:
        logger.error("❌ 無法取得待處理優化後履歷筆數: %s", e)
        return

    if total_pending == 0:
        logger.info("✅ 所有優化後履歷已完成向量化，無待處理筆數")
        return

    run_limit = min(OPTIMIZED_RESUME_LIMIT, total_pending)
    logger.info("📊 待處理優化後履歷總數: %s，本輪將處理: %s 筆", total_pending, run_limit)

    confirm = input("\n是否繼續執行？(y/n): ")
    if confirm.lower() != "y":
        logger.info("❌ 使用者取消作業")
        return

    total_ok = 0
    total_fail = 0
    total_skip = 0

    with tqdm(total=run_limit, desc="優化後履歷向量化進度") as pbar:
        while total_ok + total_fail + total_skip < run_limit:
            batch_limit = min(
                settings.BATCH_SIZE,
                run_limit - (total_ok + total_fail + total_skip),
            )
            ok, fail, skip = vectorize_optimized_resumes_batch(limit=batch_limit)
            total_ok += ok
            total_fail += fail
            total_skip += skip
            pbar.update(ok + fail + skip)
            logger.info(
                "📈 進度: 成功=%s, 失敗=%s, 跳過=%s (本批 成功=%s, 失敗=%s, 跳過=%s)",
                total_ok, total_fail, total_skip, ok, fail, skip,
            )
            if ok == 0 and fail == 0 and skip == 0:
                break

    logger.info("=" * 60)
    logger.info("🎉 本輪優化後履歷向量化作業完成")
    logger.info(
        "✅ 成功轉出並回寫: %s 筆（已寫入 Qdrant 並更新 resume_optimization.vector_id / is_embedded）",
        total_ok,
    )
    logger.info("❌ 失敗: %s 筆", total_fail)
    logger.info("⚠️  跳過（無有效文本）: %s 筆", total_skip)
    logger.info("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("\n⚠️  使用者中斷作業")
    except Exception as e:
        logger.error("❌ 未預期錯誤: %s", e, exc_info=True)
