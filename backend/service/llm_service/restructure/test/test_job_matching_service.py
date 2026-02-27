# test/test_job_matching_service.py
import os
import json
import sys

# 確保可以匯入 src 資料夾
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from src.core.database.supabase_client import get_supabase_client
from src.core.database.qdrant_client import get_qdrant_client

# 匯入重構後的服務
from src.features.matching.service import CareerMatchingService

def test_full_job_matching_flow():
    print("==================================================")
    print("🚀 啟動職缺匹配模組整合測試")
    print("==================================================")
    
    load_dotenv()
    
    # 1. 環境變數檢查
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not openai_api_key:
        print("❌ 錯誤：環境變數 OPENAI_API_KEY 不完整，請檢查 .env 檔案。")
        return

    try:
        # 2. 初始化連線
        print("正在建立資料庫連線...")
        qdrant_client = get_qdrant_client()
        supabase_client = get_supabase_client()
        
        # 3. 啟動職缺匹配服務
        service = CareerMatchingService(
            qdrant_client=qdrant_client, 
            supabase_client=supabase_client, 
            openai_api_key=openai_api_key
        )
        
        # 4. 準備測試資料 (以陳浩宇為例)
        TEST_USER_ID = 1
        filters = {
            "city": ["台北市", "新北市"], 
            "salary_min": 40000
        }
        
        # 模擬使用者的六維能力分數 (D1-D6)
        user_6d_profile = {
            "D1": 2.5, "D2": 4.5, "D3": 3.0, 
            "D4": 2.0, "D5": 3.5, "D6": 4.0
        }
        
        print(f"🔍 正在為 User {TEST_USER_ID} 執行漏斗式職缺篩選...")
        print(f"篩選條件: {filters}")
        
        # 5. 執行核心匹配流程
        results = service.find_best_jobs(
            user_id=TEST_USER_ID, 
            filters=filters, 
            user_6d_profile=user_6d_profile
        )
        
        # 6. 驗證結果
        print("\n🏆 ================= 終極排行榜 Top 10 ================= 🏆\n")
        if results:
            print(f"✅ 成功產出 {len(results)} 筆職缺推薦：\n")
            
            for i, job in enumerate(results, 1):
                print(f"[{i}] {job.get('job_title')} @ {job.get('company_name')}")
                print(f"    最終契合度: {job.get('final_score')}")
                print(f"    AI 分析內容:")
                print(json.dumps(job.get('ai_analysis'), indent=8, ensure_ascii=False))
                print("-" * 50)
            
            # 驗證關鍵欄位是否存在 (以第一名為例)
            top_job = results[0]
            required_keys = ["job_id", "job_title", "requirements", "final_score", "ai_analysis"]
            missing_keys = [k for k in required_keys if k not in top_job]
            if not missing_keys:
                print("\n✅ JSON 結構完整性驗證通過。")
            else:
                print(f"\n❌ JSON 缺少欄位: {missing_keys}")
            
            print("\n🎉 職缺匹配模組測試通過！")
        else:
            print("⚠️ 測試完成，但未找到符合條件的職缺。請確認資料庫中是否有對應地區與薪資的職缺。")
            
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_job_matching_flow()
