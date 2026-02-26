import sys
import os
from pydantic import ValidationError

# 將 src 加入 Python 路徑，確保能 import 專案模組
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.features.matching.schemas import JobMatchResult, JobMatchingResponse

def test_matching_schema_validation():
    print("=== 開始測試職缺匹配 Schema 校驗 ===")

    # 1. 模擬從 CareerMatchingService.find_best_jobs 回傳的原始資料 (Mock Data)
    mock_raw_results = [
        {
            "job_id": "job_12345",
            "job_title": "AI 工程師",
            "company_name": "果凍科技",
            "industry": "軟體開發",
            "full_address": "台北市信義區...",
            "requirements": "Python | LangChain | Pydantic",
            "final_score": "92.5%",
            "ai_analysis": {
                "pros": ["技術契合度高"],
                "cons": ["缺乏 K8s 經驗"],
                "suggestion": "建議學習 Docker"
            },
            "source_url": "https://example.com/job/123"
        }
    ]

    print("--- 測試單筆職缺資料校驗 ---")
    try:
        # 嘗試將 mock 資料轉化為 Pydantic 模型
        for raw_job in mock_raw_results:
            validated_job = JobMatchResult(**raw_job)
            print(f"✅ [成功] 職缺 '{validated_job.job_title}' 通過校驗！")
    except ValidationError as e:
        print(f"❌ [失敗] 單筆職缺校驗未通過！錯誤資訊：{e}")
        return

    print("--- 測試完整 Response 列表校驗 ---")
    try:
        # 模擬整個 Response 結構
        full_response_data = {
            "results": mock_raw_results,
            "status": "success"
        }
        validated_response = JobMatchingResponse(**full_response_data)
        print(f"✅ [成功] 完整 Response (包含 {len(validated_response.results)} 筆職缺) 通過校驗！")
        
        # 驗證型別是否正確轉化
        assert isinstance(validated_response.results[0], JobMatchResult)
        print("✅ [成功] 資料型別自動轉化為 JobMatchResult 物件。")

    except ValidationError as e:
        print(f"❌ [失敗] 完整 Response 校驗未通過！錯誤資訊：{e}")
        return

    print("--- 測試故意噴錯 (測試嚴謹性) ---")
    bad_data = {"job_id": "fail_job"} # 缺了一堆必填欄位
    try:
        JobMatchResult(**bad_data)
        print("❌ [警報] 錯誤資料竟然通過了？這代表 Schema 定義太鬆！")
    except ValidationError:
        print("✅ [成功] 錯誤資料被正確攔截 (攔截成功)。")

    print("=== 所有 Schema 測試完畢，結構完全符合需求！ ===")

if __name__ == "__main__":
    test_matching_schema_validation()
