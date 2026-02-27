import json
from src.core.agent_engine.manager import CareerAgentManager
from src.core.agent_engine.task_types import TaskType

# --- 1. Notebook 中的模擬職缺與履歷資料 ---

MOCK_RESUME = {
  "user_id": "mock_user_001",
  "profile": {
    "name": "陳轉職",
    "education": [
      {
        "level": "University",
        "major": "企業管理系",
        "school_type": "Private",
        "status": "Graduated"
      }
    ],
    "work_experience": [
      {
        "title": "數位行銷專員",
        "duration": "3 years",
        "description": "負責 FB 廣告投放，使用 Excel 進行數據分析，ROAS 提升 20%。"
      },
      {
        "title": "行政助理",
        "duration": "1 year",
        "description": "處理公司文書流程，影印文件與會議記錄。"
      }
    ],
    "skills": {
      "programming_languages": ["Python (自學3個月)"],
      "tools": ["Excel (VLOOKUP, Pivot Table)"],
      "languages": ["English (Reading/Writing: Medium)"]
    },
    "portfolio": [
      {
        "platform": "GitHub",
        "project_name": "Stock Crawler",
        "type": "Single .py file",
        "has_documentation": "false"
      }
    ],
    "autobiography": "您好，我是陳轉職，畢業於企管系。目前自學 Python 抓取基礎股票資訊。..."
  }
}

MOCK_PREFERENCES = {
    "target_role": "後端工程師",
    "interested_industry": "科技業",
    "salary_expectation": "50k 以上"
}

def test_resume_flow():
    manager = CareerAgentManager()
    
    # --- 階段 1: 履歷分析 ---
    print(">>> [啟動階段 1: 履歷分析] ...")
    analysis_inputs = {
        "survey_json": json.dumps(MOCK_PREFERENCES),
        "resume_json": json.dumps(MOCK_RESUME)
    }
    
    try:
        analysis_report = manager.run_task(
            task_type_str="resume_analysis",
            user_input=analysis_inputs
        )
        print("[分析結果摘要]:")
        print(f"風險等級: {analysis_report.get('ats_risk_level')}")
        print(f"核心弱點: {analysis_report.get('overall_weaknesses')[:2]}...")
        
        # --- 階段 2: 履歷優化 ---
        print(">>> [啟動階段 2: 履歷優化] ...")
        optimization_inputs = {
            "resume_json": json.dumps(MOCK_RESUME),
            "analysis_result": json.dumps(analysis_report) # 傳入上一步的分析結果
        }
        
        optimized_resume = manager.run_task(
            task_type_str="resume_opt",
            user_input=optimization_inputs
        )
        print("[優化結果摘要]:")
        print(f"專業總結: {optimized_resume.get('professional_summary')}")
        print(f"核心技能: {optimized_resume.get('core_skills')}")
        
    except Exception as e:
        print(f"測試失敗: {e}")

if __name__ == "__main__":
    test_resume_flow()
