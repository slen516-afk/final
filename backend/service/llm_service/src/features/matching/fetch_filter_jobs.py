import os
import json
from dotenv import load_dotenv
from src.core.database.supabase_client import get_supabase_client

# 1. 載入環境變數 (確保你有 .env 檔案存放 URL 和 KEY)
load_dotenv()

from src.common.logger import setup_logger
logger = setup_logger()

class JobFilterTester:
    """
    用於測試 Supabase 硬篩選邏輯的獨立類別
    """
    def __init__(self):
        self.supabase = get_supabase_client()

    def fetch_filtered_jobs(self, filters: dict):
        """
        執行硬篩選 (Hard Filtering)
        """
        logger.info(f"正在執行篩選，條件: {json.dumps(filters, indent=2, ensure_ascii=False)}")
        
        # 初始化查詢
        # 注意: 請確保你的資料表名稱正確，這裡預設為 'jobs'
        query = self.supabase.table("job_posting").select("*")

        # --- A. 地點篩選 (Locations) ---
        # 邏輯：如果使用者選了 "Taipei"，我們要找出 location 欄位包含 "Taipei" 的職缺
        # 實作：使用 'in' 或是 'ilike' (模糊搜尋)。
        # 若資料庫欄位是標準化的 (如 'Taipei_City')，用 'in' 效能較好。
        # 這裡示範用 textSearch 或 ilike 來處理模糊匹配 (假設 filters['locations'] 是一個列表)
        
        if filters.get("city"):
            city = filters["city"]
            # Supabase (PostgREST) 的 'in' 語法通常用於精確匹配
            # 如果要模糊匹配多個地點，通常需要構建 'or' 語法字串，例如: "location.ilike.%Taipei%,location.ilike.%New Taipei%"
            # 簡化版：這裡假設資料庫欄位 'city' 是標準化的，直接用 'in'
            # 如果你的欄位是 'location' 且包含詳細地址，建議改用 .or_() 搭配 ilike
            
            # 方法一：精確匹配 (如果 DB 欄位是 City)
            # query = query.in_("city", locations) 
            
            # 方法二：模糊匹配 (比較通用，只要包含字串就算)
            # 語法格式： column.ilike.%value%
            or_condition = ",".join([f"city.ilike.%{city}%" for city in city])
            query = query.or_(or_condition)

        # --- B. 薪資篩選 (Salary Range Overlap) ---
        # 邏輯：找出「有交集」的區間
        # 公式：Job.min <= User.max AND Job.max >= User.min
        
        user_salary_min = filters.get("salary_min", 0)
        user_salary_max = filters.get("salary_max", 9999999) # 給一個極大值當預設

        # 條件 1: 職缺的最低薪資，不能高於使用者的最高期望 (否則職缺太貴/太高階，或是 User 預算太低)
        # 注意：這裡是指「職缺的下限」要小於等於「使用者的上限」
        query = query.lte("salary_min", user_salary_max)

        # 條件 2: 職缺的最高薪資，不能低於使用者的最低期望 (否則職缺太便宜，User 看不上)
        # 注意：這裡是指「職缺的上限」要大於等於「使用者的下限」
        query = query.gte("salary_max", user_salary_min)

        # --- 執行查詢 ---
        response = query.execute()
        
        return response.data

# --- 測試執行區 ---
if __name__ == "__main__":
    tester = JobFilterTester()

    # 模擬使用者輸入的篩選條件
    # 情境：使用者想找台北，薪水 50k - 100k 的工作
    user_filters = {
        "city": ["台北市"], # 支援多地點
        "salary_min": 50000,
        "salary_max": 100000
    }

    try:
        jobs = tester.fetch_filtered_jobs(user_filters)
        
        print(f"\n✅ 篩選完成，共找到 {len(jobs)} 筆職缺：")
        print("-" * 50)
        
        for job in jobs[:5]: # 只印出前 5 筆預覽
            # 假設 DB 欄位名稱如下，請依實際情況調整
            title = job.get('job_title', 'Unknown Title')
            loc = job.get('city', 'Unknown Location')
            s_min = job.get('salary_min')
            s_max = job.get('salary_max')
            # company = job.get('company', 'Unknown Company')
            
            # print(f"🏢 {company} | 💼 {title}")
            print(f"🏢 {title}")
            print(f"📍 {loc}")
            print(f"💰 {s_min} ~ {s_max}")
            
            # 驗證邏輯：檢查是否真的有交集
            is_match = (s_min <= user_filters['salary_max']) and (s_max >= user_filters['salary_min'])
            logger.info(f"驗證匹配: {'Pass' if is_match else 'FAIL'}")
            print("-" * 50)
            
    except Exception as e:
        logger.error(f"發生錯誤: {e}", exc_info=True)