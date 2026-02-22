import os
import random
from typing import List
from dotenv import load_dotenv
from supabase import create_client, Client

# 引用主程式 (確保 run_labeling_test.py 在同一層目錄)
from run_labeling_test import process_specific_jobs

# ==========================================
# 1. 初始化 Supabase
# ==========================================
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# 2. 隨機選號函數 (大池子撈取法)
# ==========================================
def get_random_unprocessed_ids(batch_size=10, pool_size=100) -> List[int]:
    """
    從資料庫中撈取未處理的職缺，並隨機選出 batch_size 筆。
    :param batch_size: 最終要貼標的筆數 (例如 10)
    :param pool_size: 候選池大小 (例如 100)，越大隨機性越高
    """
    print(f"🎲 正在從資料庫撈取未處理的候選名單 (Pool Size: {pool_size})...")
    
    # 步驟 A: 從資料庫撈取 pool_size 筆「未貼標」的 ID
    # 注意：這裡只抓 id 欄位，減少傳輸量
    response = supabase.table("job_posting")\
        .select("job_id")\
        .is_("d1_frontend", "null")\
        .limit(pool_size)\
        .execute()
    
    candidates = [item['job_id'] for item in response.data]
    
    if not candidates:
        print("🎉 恭喜！資料庫中所有職缺都已經貼標完成，沒有未處理的資料了。")
        return []

    print(f"✅ 撈取到 {len(candidates)} 筆候選資料。")

    # 步驟 B: Python 端進行隨機抽樣
    # 如果候選數量少於我们要的數量，就全拿；否則就隨機抽
    if len(candidates) <= batch_size:
        print(f"⚠️ 候選數量少於 {batch_size}，將處理剩餘的所有資料。")
        selected_ids = candidates
    else:
        selected_ids = random.sample(candidates, batch_size)
        print(f"✂️ 已從中隨機抽出 {len(selected_ids)} 筆進行測試。")

    return selected_ids

# ==========================================
# 3. 主程式執行
# ==========================================
if __name__ == "__main__":
    # 1. 取得隨機 ID
    random_ids = get_random_unprocessed_ids(batch_size=10)
    
    # 2. 如果有 ID，就執行貼標
    if random_ids:
        print(f"🚀 目標 ID: {random_ids}")
        print("="*50)
        # 呼叫主程式進行分析
        process_specific_jobs(random_ids, table_name="job_posting")
    else:
        print("❌ 無任務需執行。")