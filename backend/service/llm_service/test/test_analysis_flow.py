import json
import os
from dotenv import load_dotenv
from src.core.agent_engine.manager import CareerAgentManager

load_dotenv()

# ==========================================
# 假資料定義區 (Mock Data)
# ==========================================

def get_experienced_mock_data():
    """回傳有經驗者的問卷與特質假資料 (履歷將由 Manager 透過 user_id 從 DB 撈取)"""
    survey_data = {
    "module_a": {
        "q5_devops": "docker_basic",
        "q8_domain": "Social Media, Content Management",
        "q3_backend": "crud_api",
        "q6_ai_data": "api_consumer",
        "q2_frontend": "framework_spa",
        "q4_database": [
        "nosql_document"
        ],
        "q7_security": "owasp_basic",
        "q1_languages": [
        {
            "name": "JavaScript",
            "score": 4
        },
        {
            "name": "HTML/CSS",
            "score": 4
        },
        {
            "name": "SQL",
            "score": 3
        }
        ]
    },
    "module_b": {
        "q14_process": "agile_scrum",
        "q15_english": "slow_reading",
        "q13_learning": "hoarding",
        "q10_tech_choice": "popularity",
        "q12_code_review": "style_check",
        "q9_troubleshoot": "log_search",
        "q11_communication": "alternative_solution"
    },
    "module_c": {
        "q18_industry": "startup",
        "q17_target_role": "fullstack",
        "q16_current_level": "junior",
        "q19_search_status": "active_urgent"
    },
    "module_d": {
        "q21_pressure": "accept_immediately",
        "q20_values_top3": [
        "technical_growth",
        "team_culture",
        "financial_reward"
        ],
        "q22_career_type": "generalist",
        "q23_learning_style": [
        "video_courses",
        "hands_on_projects"
        ]
    }
    }

    trait_data = {
    "trait_created_at": "2026-03-04 11:03:00Z",
    "trait_raw_scores": {
        "decision": 3,
        "learning": 5,
        "transfer": 3,
        "ambiguity": 5,
        "structure": 0
    },
    "primary_archetype": "AMBIGUITY_NAVIGATOR",
    "trait_raw_responses": {
        "Q1": "B",
        "Q2": "C",
        "Q3": "A",
        "Q4": "A",
        "Q5": "B",
        "Q6": "A",
        "Q7": "A",
        "Q8": "B",
        "Q9": "A",
        "Q10": "C"
    },
    "secondary_archetypes": [
        "LEARNING_ACCELERATOR"
    ],
    "trait_normalized_scores": {
        "decision": 57,
        "learning": 70,
        "transfer": 57,
        "ambiguity": 100,
        "structure": 0
    }
    }
    
    return survey_data, trait_data


def get_entry_level_mock_data():
    """回傳無經驗者的問卷與特質假資料 (履歷將由 Manager 透過 user_id 從 DB 撈取)"""
    survey_data = {
    "module_a": {
        "q5_devops": "ftp_git_pull",
        "q8_domain": "無",
        "q3_backend": "script_only",
        "q6_ai_data": "api_only",
        "q2_frontend": "no_experience",
        "q4_database": [],
        "q7_security": "framework_default",
        "q1_languages": []
    },
    "module_b": {
        "q14_process": "no_process",
        "q15_english": "translate_dependent",
        "q13_learning": "fixed_schedule",
        "q10_tech_choice": "popular_stars",
        "q12_code_review": "formalism",
        "q9_troubleshoot": "log_search",
        "q11_communication": "direct_reject"
    },
    "module_c": {
        "q18_industry": "software_house",
        "q17_target_role": "backend",
        "q16_current_level": "entry_level",
        "q19_search_status": "student_training"
    },
    "module_d": {
        "q21_pressure": "accept_without_hesitation",
        "q20_values_top3": [
        "financial_reward",
        "technical_growth",
        "status"
        ],
        "q22_career_type": "specialist",
        "q23_learning_style": [
        "hands_on_projects",
        "mentorship_community"
        ]
    }
    }

    trait_data = {
    "trait_created_at": "2026-03-04T09:10:00Z",
    "trait_raw_scores": {
        "decision": 5,
        "learning": 6,
        "transfer": 2,
        "ambiguity": 5,
        "structure": 0
    },
    "primary_archetype": "AMBIGUITY_NAVIGATOR",
    "trait_raw_responses": {
        "Q1": "B",
        "Q2": "B",
        "Q3": "A",
        "Q4": "A",
        "Q5": "B",
        "Q6": "A",
        "Q7": "A",
        "Q8": "A",
        "Q9": "B",
        "Q10": "C"
    },
    "secondary_archetypes": [
        "RAPID_DECISION_MAKER",
        "LEARNING_ACCELERATOR"
    ],
    "trait_normalized_scores": {
        "decision": 86,
        "learning": 80,
        "transfer": 43,
        "ambiguity": 100,
        "structure": 0
    }
    }

    return survey_data, trait_data


# ==========================================
# 測試情境區 (Test Cases)
# ==========================================

def verify_db_save(user_id: str):
    """驗證是否成功將生成的報告寫入 Supabase 資料庫"""
    from src.core.database.supabase_client import get_supabase_client
    supabase = get_supabase_client()
    
    print(f"\n🧪 驗證點：正在檢查 Supabase 中的 career_analysis_report 表 (user_id={user_id})...")
    try:
        response = supabase.table("career_analysis_report") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("generated_at", desc=True) \
            .limit(1) \
            .execute()
        
        if response.data:
            record = response.data[0]
            print(f"✅ 成功！已從資料庫撈到最新生成的報告紀錄。")
            print(f"   - 紀錄 ID: {record.get('id')}")
            print(f"   - 報告版本: {record.get('report_version')}")
            print(f"   - 存入時間: {record.get('generated_at')}")
            print(f"   - 目標職位: {record.get('target_position')}")
        else:
            print("❌ 失敗：資料庫中找不到剛剛存入的報告。請檢查 DB 儲存邏輯。")
    except Exception as e:
        print(f"❌ 驗證過程中發生錯誤: {e}")


def test_experienced_analysis():
    """1. 帶入有經驗者假資料，並從 DB 撈取其履歷進行測試"""
    print("\n\n====== TEST CASE 1: EXPERIENCED ANALYSIS (Mock Data + DB Resume) ======")
    user_id = "4" # 強迫 Agent 去撈資料庫裡的該 user_id 的履歷
    manager = CareerAgentManager()
    survey_data, trait_data = get_experienced_mock_data()
    trait_data["user_id"] = user_id

    user_input = {
        "user_id": user_id,
        "survey_json": json.dumps(survey_data),
        "trait_json": json.dumps(trait_data)
    }

    print(f"🚀 啟動任務... Agent 將自主撈取 DB 中 User {user_id} 的履歷，並與【有經驗者假資料】進行分析。")
    result = manager.run_task("career_analysis", user_input)
    
    print("\n🎉 分析結果 (Analysis Result):")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    verify_db_save(user_id)


def test_entry_level_analysis():
    """2. 帶入無經驗者假資料，並從 DB 撈取其履歷進行測試"""
    print("\n\n====== TEST CASE 2: ENTRY LEVEL ANALYSIS (Mock Data + DB Resume) ======")
    user_id = "39" # 強迫 Agent 去撈資料庫裡的該 user_id 的履歷
    manager = CareerAgentManager()
    survey_data, trait_data = get_entry_level_mock_data()
    trait_data["user_id"] = user_id

    user_input = {
        "user_id": user_id,
        "survey_json": json.dumps(survey_data),
        "trait_json": json.dumps(trait_data)
    }

    print(f"🚀 啟動任務... Agent 將自主撈取 DB 中 User {user_id} 的履歷，並透過分流機制處理【無經驗/轉職者】分析。")
    result = manager.run_task("career_analysis", user_input)
    
    print("\n🎉 分析結果 (Analysis Result):")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    verify_db_save(user_id)


def test_analysis_with_db_survey():
    """3. 透過 user_id 從 DB 同時撈取履歷與問卷資料 (career_survey 表) 進行測試"""
    print("\n\n====== TEST CASE 3: DB SURVEY & DB RESUME ======")
    user_id = input("請輸入要測試的 user_id (可以直接 Enter 預設為 4): ").strip()
    if not user_id:
        user_id = "5"

    from src.core.database.supabase_client import get_supabase_client
    supabase = get_supabase_client()
    
    print(f"🔍 正在從資料庫 fetch user_id={user_id} 的 career_survey 資料...")
    try:
        response = supabase.table("career_survey").select("questionnaire_response, personality").eq("user_id", user_id).execute()
        
        if not response.data:
            print(f"❌ 找不到 user_id={user_id} 的 career_survey 資料！請確認該 user_id 有填寫問卷。")
            return
            
        record = response.data[0]
        survey_data = record.get("questionnaire_response", {})
        trait_data = record.get("personality", {})
        
        if isinstance(trait_data, dict):
             trait_data["user_id"] = user_id
             
        print("✅ 成功取得問卷與特質資料！")
    except Exception as e:
        print(f"❌ 撈取資料失敗: {e}")
        return

    manager = CareerAgentManager()
    
    user_input = {
        "user_id": user_id,
        "survey_json": json.dumps(survey_data) if isinstance(survey_data, dict) else survey_data,
        "trait_json": json.dumps(trait_data) if isinstance(trait_data, dict) else trait_data
    }

    print(f"🚀 啟動任務... Agent 將自主撈取 DB 中 User {user_id} 的履歷，並使用 DB 問卷資料進行分析。")
    result = manager.run_task("career_analysis", user_input)
    
    print("\n🎉 分析結果 (Analysis Result):")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    verify_db_save(user_id)


if __name__ == "__main__":
    print("請選擇你要執行的測試項目：")
    print("==========================")
    print("1: 測試有經驗者 (假資料 + 透過 user_id 從 DB 撈取履歷 + DB 儲存)")
    print("2: 測試無經驗者/轉職者 (假資料 + 透過 user_id 從 DB 撈取履歷 + DB 儲存)")
    print("3: 測試從 DB 撈取問卷與履歷 (全真實資料 + DB 儲存)")
    
    # test_experienced_analysis()
    # test_entry_level_analysis()
    test_analysis_with_db_survey()
