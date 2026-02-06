"""
Career Pilot 職缺向量化主程式
功能：
1. 從 Supabase 批次提取未向量化職缺
2. 調用 OpenAI API 進行向量化
3. 寫入 Qdrant 並回寫 vector_id 到 Supabase
"""

import sys
import time
import uuid
import logging
from pathlib import Path
from typing import List, Dict
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

# 配置日誌（寫入專案根目錄下的 logs/）
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

# ============ 初始化客戶端 ============
openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
qdrant_client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
)

# ============ 核心函數 ============


def get_embedding(text: str) -> List[float]:
    """
    調用 OpenAI Embedding API

    Args:
        text: 待向量化的文本

    Returns:
        1536 維向量陣列

    Raises:
        Exception: API 調用失敗
    """
    try:
        response = openai_client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=text,
            dimensions=settings.EMBEDDING_DIMENSIONS,
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"❌ Embedding API 失敗: {e}")
        raise


def prepare_job_text(job: Dict) -> str:
    """
    準備職缺文本（符合 ERD 設計）

    Args:
        job: Supabase 查詢結果（單筆職缺）

    Returns:
        合併後的文本字串
    """
    title = job.get("job_title") or ""
    description = job.get("job_description") or ""
    requirements = job.get("requirements") or ""

    combined_text = f"{title}\n{description}\n{requirements}"

    if len(combined_text) > settings.MAX_TEXT_LENGTH:
        combined_text = combined_text[: settings.MAX_TEXT_LENGTH]
        logger.warning(
            f"⚠️  job_id {job['job_id']} 文本過長，已截斷至 {settings.MAX_TEXT_LENGTH} 字元"
        )

    return combined_text.strip()


def prepare_payload(job: Dict) -> Dict:
    """
    準備 Qdrant Payload（符合 ERD 設計，含薪資範圍）
    """
    return {
        "job_id": job["job_id"],
        "job_title": job.get("job_title"),
        "city": job.get("city"),
        "district": job.get("district"),
        "remote_option": job.get("remote_option"),
        "salary_min": job.get("salary_min"),
        "salary_max": job.get("salary_max"),
    }


def vectorize_batch(offset: int, limit: int = None) -> int:
    """
    處理單一批次

    Args:
        offset: 起始位置
        limit: 批次大小（預設使用 settings.BATCH_SIZE）

    Returns:
        成功處理的筆數
    """
    if limit is None:
        limit = settings.BATCH_SIZE

    # ========== Step 1: 從 Supabase 提取資料 ==========
    try:
        response = (
            supabase.table("job_posting")
            .select(
                "job_id, job_title, job_description, requirements, city, district, remote_option, salary_min, salary_max"
            )
            .eq("is_embedded", False)
            .range(offset, offset + limit - 1)
            .execute()
        )

        jobs = response.data
        if not jobs:
            return 0

    except Exception as e:
        logger.error(f"❌ Supabase 查詢失敗 (offset={offset}): {e}")
        return 0

    # ========== Step 2: 批次向量化與準備 Points ==========
    points = []
    update_records = []

    for job in jobs:
        job_id = job["job_id"]

        try:
            text = prepare_job_text(job)
            if not text:
                logger.warning(f"⚠️  job_id {job_id}: 文本為空，跳過")
                continue

            vector = get_embedding(text)
            vector_id = str(uuid.uuid4())

            points.append(
                PointStruct(
                    id=vector_id,
                    vector=vector,
                    payload=prepare_payload(job),
                )
            )

            update_records.append({
                "job_id": job_id,
                "vector_id": vector_id,
            })

            time.sleep(settings.RATE_LIMIT_DELAY)

        except Exception as e:
            logger.error(f"❌ job_id {job_id} 處理失敗: {e}")
            continue

    # ========== Step 3: 批次寫入 Qdrant ==========
    if points:
        try:
            qdrant_client.upsert(
                collection_name=settings.JOB_COLLECTION,
                points=points,
            )
            logger.info(f"✅ Qdrant 寫入 {len(points)} 筆")
        except Exception as e:
            logger.error(f"❌ Qdrant 批次寫入失敗: {e}")
            return 0

    # ========== Step 4: 批次更新 Supabase ==========
    success_count = 0
    for record in update_records:
        try:
            supabase.table("job_posting").update({
                "vector_id": record["vector_id"],
                "is_embedded": True,
            }).eq("job_id", record["job_id"]).execute()
            success_count += 1
        except Exception as e:
            logger.error(f"❌ job_id {record['job_id']} 回寫失敗: {e}")

    logger.info(f"✅ Supabase 更新 {success_count}/{len(update_records)} 筆")
    return success_count


def main():
    """主流程"""
    logger.info("=" * 60)
    logger.info("Career Pilot 職缺向量化作業")
    logger.info(f"執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    # ========== 計算待處理總數 ==========
    try:
        count_response = (
            supabase.table("job_posting")
            .select("job_id", count="exact")
            .eq("is_embedded", False)
            .execute()
        )
        total_jobs = getattr(count_response, "count", None)
        if total_jobs is None and hasattr(count_response, "data"):
            total_jobs = len(count_response.data)
        if total_jobs is None:
            total_jobs = 0
    except Exception as e:
        logger.error(f"❌ 無法取得待處理筆數: {e}")
        return

    if total_jobs == 0:
        logger.info("✅ 所有職缺已完成向量化")
        return

    # 本次最多處理筆數（MAX_BATCHES=1 時只跑 100 筆後自動停止）
    run_limit = (
        min(settings.MAX_BATCHES * settings.BATCH_SIZE, total_jobs)
        if settings.MAX_BATCHES > 0
        else total_jobs
    )
    num_batches_to_run = (
        settings.MAX_BATCHES if settings.MAX_BATCHES > 0 else (total_jobs + settings.BATCH_SIZE - 1) // settings.BATCH_SIZE
    )

    logger.info(f"📊 待處理職缺總數: {total_jobs}")
    logger.info(f"⚙️  批次大小: {settings.BATCH_SIZE}")
    if settings.MAX_BATCHES == 1:
        logger.info(f"🔹 模式: 單批試跑（本輪只處理 {run_limit} 筆，完成後自動終止）")
    elif settings.MAX_BATCHES > 0:
        logger.info(f"🔹 模式: 本輪最多跑 {num_batches_to_run} 批（共 {run_limit} 筆）")
    else:
        logger.info("🔹 模式: 跑完全部")

    estimated_cost = (run_limit * 600 * 0.13) / 1_000_000
    logger.info(f"💰 本輪預估成本: ${estimated_cost:.2f} USD")

    confirm = input("\n是否繼續執行？(y/n): ")
    if confirm.lower() != "y":
        logger.info("❌ 使用者取消作業")
        return

    # ========== 批次處理（可依 MAX_BATCHES 只跑 1 批或跑完全部）==========
    total_processed = 0
    offset = 0
    batch_count = 0

    with tqdm(total=run_limit, desc="向量化進度") as pbar:
        while total_processed < run_limit:
            processed = vectorize_batch(offset, settings.BATCH_SIZE)

            if processed == 0:
                logger.warning(f"⚠️  offset {offset} 處理失敗，嘗試跳過...")
                offset += settings.BATCH_SIZE
                continue

            total_processed += processed
            offset += settings.BATCH_SIZE
            batch_count += 1
            pbar.update(processed)

            logger.info(
                f"📈 進度: {total_processed}/{run_limit} ({total_processed / run_limit * 100:.1f}%)"
            )

            # 只跑單批時，跑完 100 筆就結束
            if settings.MAX_BATCHES > 0 and batch_count >= settings.MAX_BATCHES:
                logger.info(f"🔹 已跑完 {settings.MAX_BATCHES} 批，依設定自動終止")
                break

    logger.info("=" * 60)
    logger.info("🎉 本輪向量化作業完成！")
    logger.info(f"✅ 成功處理: {total_processed} 筆（已寫入 Qdrant 並回寫 Supabase vector_id / is_embedded）")
    if run_limit < total_jobs and settings.MAX_BATCHES > 0:
        logger.info(f"📌 尚有 {total_jobs - total_processed} 筆未處理，確認無誤後可設 MAX_BATCHES=0 跑完全部")
    logger.info("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("\n⚠️  使用者中斷作業")
    except Exception as e:
        logger.error(f"❌ 未預期錯誤: {e}", exc_info=True)
