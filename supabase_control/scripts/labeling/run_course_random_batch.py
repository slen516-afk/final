"""
課程隨機批次貼標：從 course 表中撈取「未貼標」(role_type 為 null) 的課程，
隨機抽樣後呼叫 run_course_labeling_test 進行六大職類 (A-F) 貼標。

使用方式：在 supabase_control 目錄下執行
  python scripts/labeling/run_course_random_batch.py
可調整下方 batch_size、pool_size。
"""

import os
import random
import sys
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from supabase import create_client, Client

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from run_course_labeling_test import process_specific_courses

# ==========================================
# 1. 初始化 Supabase
# ==========================================
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# 2. 隨機選取未貼標課程 ID
# ==========================================
def get_random_unprocessed_course_ids(
    batch_size: int = 500,
    pool_size: int = 1000,
    table_name: str = "course",
) -> List[int]:
    """
    從 course 表撈取 role_type 為 null 的課程，隨機選出 batch_size 筆。
    """
    print(f"🎲 正在從 {table_name} 撈取未貼標課程 (Pool Size: {pool_size})...")

    response = (
        supabase.table(table_name)
        .select("course_id")
        .is_("role_type", "null")
        .limit(pool_size)
        .execute()
    )

    candidates = [item["course_id"] for item in (response.data or [])]

    if not candidates:
        print("🎉 資料庫中所有課程皆已貼標，沒有未處理的資料。")
        return []

    print(f"✅ 撈取到 {len(candidates)} 筆候選課程。")

    if len(candidates) <= batch_size:
        print(f"⚠️ 候選數量少於 {batch_size}，將處理剩餘全部。")
        selected_ids = candidates
    else:
        selected_ids = random.sample(candidates, batch_size)
        print(f"✂️ 已隨機抽出 {len(selected_ids)} 筆進行貼標。")

    return selected_ids

# ==========================================
# 3. 主程式
# ==========================================
if __name__ == "__main__":
    random_ids = get_random_unprocessed_course_ids(batch_size=500, pool_size=1000)

    if random_ids:
        print(f"🚀 目標 course_id 數量: {len(random_ids)}")
        print("=" * 50)
        process_specific_courses(random_ids, table_name="course")
    else:
        print("❌ 無需執行的任務。")
