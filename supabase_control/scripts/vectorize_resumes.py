"""
Career Pilot 履歷向量化主程式
功能：
1. 從 Supabase 批次提取未向量化履歷（依說明書：structured_data / normalized_data）
2. 使用 OpenAI text-embedding-3-large 產生 1536 維向量
3. 寫入 Qdrant resume_vectors，並回寫 resume 表的 vector_id 與 is_embedded
4. 日誌寫入 logs/vectorization.log，含明確進度與成功/失敗筆數

流程／後端串接：
- 使用者上傳原始履歷後，後端可立即觸發本腳本只處理該筆：設 RESUME_IDS=<resume_id> 再執行（不問 confirm）。
- 未設 RESUME_IDS 時為批次模式（依 RESUME_LIMIT），適合 cron 或手動補跑。
- 職缺推薦時由 retriever 依使用者選擇用 resume_vectors 或 optimized_resume_vectors 做比對；職缺本身用 vectorize_jobs 批次即可。
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

# 日誌：寫入 supabase_control/logs/vectorization.log
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

# 本腳本預設只處理前 N 筆（可透過 RESUME_LIMIT 環境變數覆寫）
RESUME_LIMIT = int(os.getenv("RESUME_LIMIT", "10"))
# 後端觸發「指定履歷」向量化時可傳 RESUME_IDS=1,2,3，只處理這些 resume_id（仍限 is_embedded=False）
_RESUME_IDS_ENV = os.getenv("RESUME_IDS", "").strip()
RESUME_IDS = [int(x.strip()) for x in _RESUME_IDS_ENV.split(",") if x.strip().isdigit()] if _RESUME_IDS_ENV else None

# ============ 初始化客戶端 ============
openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
qdrant_client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
)


def _json_to_flat_text(obj: Any) -> str:
    """
    將履歷 JSON（structured_data / normalized_data）轉成單一可向量化字串。
    依說明書欄位語意，遞迴展開為可讀文字。
    """
    if obj is None:
        return ""
    if isinstance(obj, str):
        return obj.strip()
    if isinstance(obj, (int, float)):
        return str(obj)
    if isinstance(obj, list):
        parts = []
        for i, item in enumerate(obj):
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
    return str(obj).strip()


def prepare_resume_text(resume: Dict) -> str:
    """
    依說明書：向量化來源為 structured_data / normalized_data。
    優先使用 normalized_data（標準化後），若無或為空則用 structured_data。
    """
    normalized = resume.get("normalized_data")
    structured = resume.get("structured_data")

    # 優先使用 normalized_data
    if normalized is not None and (normalized if isinstance(normalized, str) else True):
        text = _json_to_flat_text(normalized)
        if text:
            if len(text) > settings.MAX_TEXT_LENGTH:
                text = text[: settings.MAX_TEXT_LENGTH]
                logger.warning(
                    "⚠️  resume_id %s 文本過長，已截斷至 %s 字元",
                    resume.get("resume_id"),
                    settings.MAX_TEXT_LENGTH,
                )
            return text.strip()

    # 其次使用 structured_data
    if structured is not None and (structured if isinstance(structured, str) else True):
        text = _json_to_flat_text(structured)
        if text:
            if len(text) > settings.MAX_TEXT_LENGTH:
                text = text[: settings.MAX_TEXT_LENGTH]
                logger.warning(
                    "⚠️  resume_id %s 文本過長，已截斷至 %s 字元",
                    resume.get("resume_id"),
                    settings.MAX_TEXT_LENGTH,
                )
            return text.strip()

    return ""


def prepare_resume_payload(resume: Dict) -> Dict:
    """準備寫入 Qdrant 的 payload（關聯鍵與篩選用）。"""
    return {
        "resume_id": resume["resume_id"],
        "user_id": resume.get("user_id"),
        "resume_type": resume.get("resume_type"),
    }


def get_embedding(text: str) -> List[float]:
    """
    調用 OpenAI Embedding API（text-embedding-3-large，1536 維）。
    """
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


def vectorize_resumes_batch(limit: int, offset: int = 0, resume_ids: Optional[List[int]] = None) -> tuple:
    """
    處理單一批次履歷向量化。

    Args:
        limit: 本批最多筆數（resume_ids 為 None 時使用）
        offset: 起始位置（resume_ids 為 None 時用於分頁）
        resume_ids: 若提供，只處理這些 resume_id（仍限 is_embedded=False），供後端「上傳後立即向量化」觸發

    Returns:
        (成功筆數, 失敗筆數, 跳過筆數)
    """
    # ========== Step 1: 從 Supabase 提取未向量化履歷 ==========
    try:
        q = (
            supabase.table("resume")
            .select(
                "resume_id, user_id, template_id, resume_type, structured_data, normalized_data"
            )
            .eq("is_embedded", False)
        )
        if resume_ids:
            q = q.in_("resume_id", resume_ids)
        else:
            q = q.range(offset, offset + limit - 1)
        response = q.execute()
        rows = response.data or []
    except Exception as e:
        logger.error("❌ Supabase 查詢履歷失敗 (offset=%s, resume_ids=%s): %s", offset, resume_ids, e)
        return (0, 0, 0)

    if not rows:
        return (0, 0, 0)

    success_count = 0
    fail_count = 0
    skip_count = 0
    points = []
    update_records = []

    for resume in rows:
        resume_id = resume["resume_id"]
        try:
            text = prepare_resume_text(resume)
            if not text:
                logger.warning("⚠️  resume_id %s: structured_data/normalized_data 為空，跳過", resume_id)
                skip_count += 1
                continue

            vector = get_embedding(text)
            vector_id = str(uuid.uuid4())

            points.append(
                PointStruct(
                    id=vector_id,
                    vector=vector,
                    payload=prepare_resume_payload(resume),
                )
            )
            update_records.append({"resume_id": resume_id, "vector_id": vector_id})
            success_count += 1
            time.sleep(settings.RATE_LIMIT_DELAY)

        except Exception as e:
            logger.error("❌ resume_id %s 處理失敗: %s", resume_id, e)
            fail_count += 1

    # ========== Step 2: 批次寫入 Qdrant ==========
    if points:
        try:
            qdrant_client.upsert(
                collection_name=settings.RESUME_COLLECTION,
                points=points,
            )
            logger.info("✅ Qdrant 寫入 %s 筆履歷向量", len(points))
        except Exception as e:
            logger.error("❌ Qdrant 履歷批次寫入失敗: %s", e)
            return (0, fail_count + len(update_records), skip_count)

    # ========== Step 3: 回寫 Supabase resume 表（vector_id & is_embedded）==========
    for record in update_records:
        try:
            supabase.table("resume").update({
                "vector_id": record["vector_id"],
                "is_embedded": True,
            }).eq("resume_id", record["resume_id"]).execute()
        except Exception as e:
            logger.error("❌ resume_id %s 回寫 Supabase 失敗: %s", record["resume_id"], e)
            success_count -= 1
            fail_count += 1

    return (success_count, fail_count, skip_count)


def main():
    """主流程：可依 RESUME_IDS 只處理指定履歷，或依 RESUME_LIMIT 批次處理未向量化履歷。"""
    logger.info("=" * 60)
    logger.info("Career Pilot 履歷向量化作業")
    logger.info("執行時間: %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("模型: %s，維度: %s", settings.EMBEDDING_MODEL, settings.EMBEDDING_DIMENSIONS)
    if RESUME_IDS:
        logger.info("模式: 指定 ID（RESUME_IDS=%s）", RESUME_IDS)
    else:
        logger.info("本輪處理筆數上限: %s", RESUME_LIMIT)
    logger.info("=" * 60)

    if RESUME_IDS:
        # 後端觸發：只處理指定 resume_id，不問 confirm、不跑進度條
        ok, fail, skip = vectorize_resumes_batch(limit=0, offset=0, resume_ids=RESUME_IDS)
        logger.info("指定 ID 模式完成：成功=%s, 失敗=%s, 跳過=%s", ok, fail, skip)
        return

    # ========== 批次模式：取得待處理總數 ==========
    try:
        count_response = (
            supabase.table("resume")
            .select("resume_id", count="exact")
            .eq("is_embedded", False)
            .execute()
        )
        total_pending = getattr(count_response, "count", None)
        if total_pending is None and hasattr(count_response, "data"):
            total_pending = len(count_response.data or [])
        if total_pending is None:
            total_pending = 0
    except Exception as e:
        logger.error("❌ 無法取得待處理履歷筆數: %s", e)
        return

    if total_pending == 0:
        logger.info("✅ 所有履歷已完成向量化，無待處理筆數")
        return

    run_limit = min(RESUME_LIMIT, total_pending)
    logger.info("📊 待處理履歷總數: %s，本輪將處理: %s 筆", total_pending, run_limit)

    confirm = input("\n是否繼續執行？(y/n): ")
    if confirm.lower() != "y":
        logger.info("❌ 使用者取消作業")
        return

    total_ok = 0
    total_fail = 0
    total_skip = 0
    offset = 0

    with tqdm(total=run_limit, desc="履歷向量化進度") as pbar:
        while total_ok + total_fail + total_skip < run_limit:
            batch_limit = min(settings.BATCH_SIZE, run_limit - (total_ok + total_fail + total_skip))
            ok, fail, skip = vectorize_resumes_batch(limit=batch_limit, offset=offset)
            total_ok += ok
            total_fail += fail
            total_skip += skip
            pbar.update(ok + fail + skip)
            offset += batch_limit
            logger.info(
                "📈 進度: 成功=%s, 失敗=%s, 跳過=%s (本批 成功=%s, 失敗=%s, 跳過=%s)",
                total_ok, total_fail, total_skip, ok, fail, skip,
            )
            if ok == 0 and fail == 0 and skip == 0:
                break

    logger.info("=" * 60)
    logger.info("🎉 本輪履歷向量化作業完成")
    logger.info("✅ 成功轉出並回寫: %s 筆（已寫入 Qdrant 並更新 resume.vector_id / resume.is_embedded）", total_ok)
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
