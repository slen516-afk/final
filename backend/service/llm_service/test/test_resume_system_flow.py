import os
import sys
import json
from dotenv import load_dotenv

# 1. 環境設定與路徑導入，確保測試腳本能正確引用 src 模組
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

try:
    from src.core.agent_engine.manager import CareerAgentManager
except ImportError as e:
    print(f"❌ 模組導入失敗: {e}")
    sys.exit(1)

# 載入 .env 檔案
load_dotenv()

def test_resume_system_integration():
    """
    完整系統整合測試：從 CareerAgentManager 入口發送任務。
    驗證從 Manager 接收請求 -> 分發 Agent -> 工具抓取 Supabase 資料 -> 結構化輸出的完整流程。
    """
    print("" + "="*60)
    print("🚀 [系統整合測試] 履歷模組 (分析 & 優化) 完整閉環驗證")
    print("="*60)
    
    # 初始化總管理器
    # 建議使用支援結構化輸出的模型，例如 o3-mini 或 gpt-4o
    manager = CareerAgentManager()
    
    # 指定測試用的 user_id (請確保 Supabase 中 user_id='1' 有對應的 resume 與 career_survey 資料)

    # 前端傳入的 user_input
    task_type_str = "resume_analysis"
    user_input = {
        "user_id": 8
    }
    
    # ---------------------------------------------------------
    # PART 1: 履歷分析 (RESUME_ANALYSIS)
    # ---------------------------------------------------------
    print(f"[任務 1] 啟動『履歷深度分析』...")
    print(f"👉 目標用戶: {user_input}")
    
    
    try:
        # 執行任務
        analysis_result = manager.run_task(
            task_type_str=task_type_str,
            user_input=user_input
        )
        
        print("✅ [PART 1] 履歷分析任務執行成功！")
        print("-" * 30)
        # 輸出部分結果進行驗證
        print(f"🔹 診斷摘要: {analysis_result.get('candidate_positioning', '無內容')}")
        print(f"🔹 ATS 風險等級: {analysis_result.get('ats_risk_level', '未知')}")
        
    except Exception as e:
        print(f"❌ [PART 1] 履歷分析執行失敗: {str(e)}")
        # 若分析失敗，通常後續優化也會因缺乏分析結果而受阻，故中斷測試
        return

    # ---------------------------------------------------------
    # PART 2: 履歷優化 (RESUME_OPT)
    # ---------------------------------------------------------
    #優化任務輸入
    # task_type_str="resume_opt"
    # opt_input = {
    #     "user_id": 2
    # }
    
    # print(f"[任務 2] 啟動『履歷內容優化』...")
    # print(f"👉 目標用戶: {opt_input}")
    
    
    # try:
    #     # 執行任務
    #     opt_result = manager.run_task(
    #         task_type_str=task_type_str,
    #         user_input=opt_input
    #     )
        
    #     print("✅ [PART 2] 履歷優化任務執行成功！")
    #     print("-" * 30)
    #     # 輸出部分優化內容驗證
    #     print(f"🔹 優化成果預覽 (前 200 字):")
    #     # 假設優化結果存放在特定欄位，或直接回傳結構化履歷
    #     print(json.dumps(opt_result, indent=2, ensure_ascii=False)[:400] + "...")
        
    # except Exception as e:
    #     print(f"❌ [PART 2] 履歷優化執行失敗: {str(e)}")

    print("" + "="*60)
    print("💡 提示：您可以前往檢查 `logs/crewai_outputs/task_audit_trail.log`，看看 Agent 是否有留下稽核蹤跡！")
    print("✨ 系統整合測試結束")
    print("="*60)

if __name__ == "__main__":
    # 檢查是否有設定 OpenAI API Key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 錯誤: 找不到 OPENAI_API_KEY 環境變數。")
    else:
        test_resume_system_integration()
