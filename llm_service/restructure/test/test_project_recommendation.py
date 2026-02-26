import os
import json
# import pytest
from src.core.agent_engine.manager import CareerAgentManager
from src.core.agent_engine.task_types import TaskType

# 模擬缺口分析 (Skill Gap Analysis) - 來自 Notebook 範例
MOCK_SKILL_GAP_ANALYSIS = {
    'strengths': [
        '數據分析與商業邏輯思維', 
        '強烈自主學習動機與實踐力', 
        '跨領域溝通與協調能力'
    ], 
    'weaknesses': [
        '缺乏核心後端技術棧實戰經驗 (如後端框架、API 設計、資料庫、雲端服務、容器化技術)', 
        '缺乏版本控制系統 (Git) 協作經驗', 
        '缺乏軟體測試與部署概念', 
        '缺乏軟體開發生命週期 (SDLC) 實務經驗', 
        '缺乏團隊協作開發經驗', 
        '缺乏後端工程師職位常見關鍵字 (如後端框架、資料庫、雲端服務等)'
    ], 
    'match_score': 25
}

def test_project_recommendation_flow():
    """
    測試 Side Project 推薦模組的完整執行流程。
    """
    manager = CareerAgentManager(model_name="o3-mini") # 使用專題建議的模型
    
    user_input = {
        "user_id": "test_user_001",
        "skill_gap_result": MOCK_SKILL_GAP_ANALYSIS
    }
    
    print(">>> 啟動 Side Project 推薦測試...")
    
    try:
        final_result = manager.run_task(
            task_type_str="project_rec",
            user_input=user_input,
        )
        
        # 驗證結構是否正確 (由 manager.py 中的 qa_task 強制輸出)
        assert "project_name" in final_result
        assert "tech_stack" in final_result
        assert "project_phases" in final_result
        assert len(final_result["project_phases"]) >= 3 # 至少要有三個階段
        
        print("[測試成功] 推薦專案名稱:", final_result["project_name"])
        print("技術棧:", final_result["tech_stack"])
        print("詳細輸出結果:")
        print(json.dumps(final_result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        pytest.fail(f"Side Project 推薦流程執行失敗: {e}")

if __name__ == "__main__":
    # 若直接執行此檔案，則運行測試
    test_project_recommendation_flow()
