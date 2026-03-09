import os
import json
from unittest.mock import patch
from src.core.agent_engine.manager import CareerAgentManager
from src.common.logger import setup_logger

# 加入 Logger
logger = setup_logger()

def test_project_recommendation_flow():
    """
    測試 Side Project 推薦模組的完整執行流程。
    """
    manager = CareerAgentManager()
    
    # 改變：只需傳入 user_id，移除 hardcoded 的 skill_gap_result
    user_id = "3"
    user_input = {
        "user_id": user_id
    }
    
    print(f">>> 啟動 Side Project 推薦測試 (user_id={user_id})...")
    
    try:
        # 攔截 (Mock) ProjectRecHandler.process，確保不會真的寫入 Supabase
        with patch('src.core.agent_engine.result_handlers.ProjectRecHandler.process') as mock_process:
            final_result = manager.run_task(
                task_type_str="project_rec",
                user_input=user_input
            )
            print("\n[攔截資料庫寫入] 測試中已阻止寫入 DB")
        
        # 驗證結構是否正確
        assert final_result is not None, "回傳結果為空"
        assert "project_name" in final_result, "缺少 project_name"
        assert "tech_stack" in final_result, "缺少 tech_stack"
        assert "project_phases" in final_result, "缺少 project_phases"
        assert len(final_result["project_phases"]) >= 3, "至少要有三個階段"
        
        print("\n================ 測試成功 ==================")
        print(f"✅ 推薦專案名稱: {final_result.get('project_name')}")
        print("================ 詳細輸出結果 ==============")
        print(json.dumps(final_result, indent=2, ensure_ascii=False))
        print("============================================")
        print("\n💡 提示：您可以前往檢查 `logs/crewai_outputs/task_audit_trail.log`，看看 Agent 是否有留下稽核蹤跡！")
        
    except Exception as e:
        # [修復] 將原本單純的 print 改為 logger.error，這樣錯誤才會進 log
        logger.error(f"測試過程中發生錯誤: {e}", exc_info=True)
        print(f"❌ Side Project 推薦流程執行失敗: {e}")

if __name__ == "__main__":
    # 若直接執行此檔案，則運行測試
    test_project_recommendation_flow()
