import json
import os
from dotenv import load_dotenv
from src.core.agent_engine.manager import CareerAgentManager

load_dotenv()

def test_entry_level_analysis():
    """
    測試無經驗者/轉職者的自動識別與分析流程。
    """
    print("====== TEST CASE: ENTRY LEVEL AUTO-DISPATCH ======")
    manager = CareerAgentManager(model_name="o3-mini")

    # 1. 模擬無經驗者/轉職者的問卷 (沒有 module_a)
    INPUT_CAREER_DATA = {
        "module_c": {
            "q16_current_level": "entry_level",
            "q17_target_role": "",
            "q18_industry": "software_service",
            "q19_search_status": "actively_looking"
        },
        "module_d": {
            "q20_values_top3": ["work_life_balance", "learning_culture"],
            "q22_career_type": "specialist"
        }
    }

    # 2. 模擬心理特質資料
    INPUT_TRAIT_DATA = {
        "trait_normalized_scores": {
            "structure": 70,
            "ambiguity": 80,
            "decision": 40,
            "learning": 90,
            "transfer": 95
        }
    }

    # 3. 模擬非技術背景的履歷 (行政助理轉職)
    RESUME_DATA = {
        "basics": {
            "name": "張小明",
            "summary": "擔任行政助理 3 年，擅長優化辦公室作業流程。目前正在自學 Python，希望能轉職為後端工程師。"
        },
        "work": [
            {
                "company": "某某貿易公司",
                "position": "行政助理",
                "highlights": ["優化採購流程，節省 15% 作業時間", "使用 Excel 進行庫存管理與自動化報表生成"]
            }
        ]
    }

    user_input = {
        "survey_json": json.dumps(INPUT_CAREER_DATA),
        "trait_json": json.dumps(INPUT_TRAIT_DATA),
        "resume_json": json.dumps(RESUME_DATA)
    }

    # 注意：這裡使用通用的 "career_analysis" 標籤
    print(">>> 正在發送通用分析請求...")
    result = manager.run_task("career_analysis", "user_entry_999", user_input)
    
    print("🎉 Analysis Result (Auto-Detected Entry Level):")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_entry_level_analysis()
