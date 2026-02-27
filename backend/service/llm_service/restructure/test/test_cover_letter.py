import os
import json
import pytest
from src.core.agent_engine.manager import CareerAgentManager
from src.core.agent_engine.task_types import TaskType

# 模擬優化後的履歷 (Optimization Resume) - 來自 Notebook 範例
MOCK_OPTIMIZATION_RESUME = {
    'professional_summary': '具備三年數位行銷經驗，擅長數據分析與廣告成效優化，成功提升廣告投資報酬率 (ROAS) 20%。對程式設計充滿熱情，自學 Python 並完成股票資訊爬蟲專案，渴望將行銷邏輯思維與程式技能結合，轉職成為初級助理工程師或軟體開發實習生。',
    'professional_experience': [
        '數位行銷專員 (3 年) - 負責 Facebook 廣告的策略規劃與投放，並透過 Excel 進行廣告數據的深入分析與成效追蹤。成功將廣告投資報酬率 (ROAS) 提升 20%，有效優化行銷預算效益。',
        '行政助理 (1 年) - 負責處理公司日常行政事務與文書流程，包含文件歸檔、資料整理、會議記錄撰寫與跨部門協調。確保辦公室運作順暢，提升行政效率。'
    ],
    'core_skills': ['Python', 'Excel', '數據分析', 'Git', 'SQL', 'RESTful API'],
    'projects': [
        '股票資訊爬蟲 (Stock Crawler): 基於 Python 開發，自動化抓取特定網站的股票基本資訊，展現基礎網頁資料擷取與處理能力。未來規劃加入資料儲存與視覺化功能。'
    ],
    'education': [
        '大學：企業管理學系 (私立大學，已畢業)',
        '高中：普通科 (公立高中，已畢業)'
    ]
}

def test_cover_letter_flow():
    """
    測試求職推薦信模組的完整執行流程。
    """
    manager = CareerAgentManager(model_name="o3-mini")
    
    # 注意：inputs 的 key 必須與 Task 中的 {optimize_resume} 與 {job_id} 對齊
    user_input = {
        "user_id": "test_user_cover_letter",
        "optimize_resume": MOCK_OPTIMIZATION_RESUME,
        "job_id": 46 # 嚮樂科技 - 軟體設計工程師
    }
    
    print(">>> 啟動 Cover Letter 推薦測試...")
    
    try:
        final_result = manager.run_task(
            task_type_str="cover_letter",
            user_input=user_input,
        )
        
        # 驗證結構是否正確
        assert "subject" in final_result
        assert "content" in final_result
        
        print("[測試成功] 求職信生成成功！")
        print("[主旨]:", final_result["subject"])
        print("-" * 30)
        print("[正文內容]:")
        print(final_result["content"])
        
    except Exception as e:
        pytest.fail(f"Cover Letter 流程執行失敗: {e}")

if __name__ == "__main__":
    test_cover_letter_flow()
