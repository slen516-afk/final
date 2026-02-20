"""
將 out_put.json 格式轉換成 test_logic.py 可讀取的格式
將舊格式 (Q1-Q23, 字母選項) 轉換成新格式 (module_a/b/c/d, 具體值)
"""
import json
from datetime import datetime
from typing import List, Dict, Any

# 選項字母到值的映射（根據 index.html 的選項順序）
OPTION_MAPPING = {
    "Q2": {"A": "unfamiliar", "B": "basic_html_css", "C": "framework_spa", 
           "D": "optimization_ssr", "E": "system_design"},
    "Q3": {"A": "unfamiliar", "B": "crud_api", "C": "db_auth_testing", 
           "D": "high_concurrency", "E": "distributed_system"},
    "Q4": {"A": "rdbms_sql", "B": "nosql_document", "C": "key_value_cache", 
           "D": "search_engine", "E": "vector_db", "F": "graph_db", "G": "data_warehouse"},
    "Q5": {"A": "paas_only", "B": "docker_basic", "C": "cloud_manual", 
           "D": "k8s_cicd", "E": "iac_monitoring"},
    "Q6": {"A": "api_consumer", "B": "pandas_numpy", "C": "model_training", 
           "D": "rag_langchain", "E": "mlops"},
    "Q7": {"A": "framework_default", "B": "owasp_basic", "C": "auth_rbac", 
           "D": "audit_devsecops"},
    "Q9": {"A": "restart", "B": "log_search", "C": "rollback", "D": "incident_analysis"},
    "Q10": {"A": "newest_tech", "B": "popularity", "C": "team_familiarity", 
            "D": "tradeoff_analysis"},
    "Q11": {"A": "comply", "B": "reject", "C": "alternative_solution", "D": "value_driven"},
    "Q12": {"A": "formality", "B": "style_check", "C": "logic_safety", 
            "D": "architecture_solid"},
    "Q13": {"A": "just_in_time", "B": "hoarding", "C": "consistent_input", 
            "D": "deep_dive_sharing"},
    "Q14": {"A": "waterfall_none", "B": "agile_scrum", "C": "kanban", 
            "D": "process_optimization"},
    "Q15": {"A": "translation_tool", "B": "slow_reading", "C": "fluent_reading", 
            "D": "global_comm"},
    "Q16": {"A": "entry_level", "B": "junior", "C": "mid_level", 
            "D": "senior", "E": "lead_architect"},
    "Q17": {"A": "frontend", "B": "backend", "C": "fullstack", 
            "D": "data_scientist", "E": "ai_engineer", "F": "devops_sre"},
    "Q18": {"A": "startup", "B": "big_tech", "C": "traditional_digital", 
            "D": "software_house", "E": "product_company"},
    "Q19": {"A": "active_urgent", "B": "passive_open", "C": "market_research", 
            "D": "student_training"},
    "Q21": {"A": "accept_immediately", "B": "consider_short_term", 
            "C": "prefer_health", "D": "reject_absolutely"},
    "Q22": {"A": "specialist", "B": "generalist", "C": "manager"},
    "Q23": {"A": "official_docs", "B": "video_courses", "C": "hands_on_projects", 
            "D": "books", "E": "mentorship_community"},
}

# Q20 價值觀映射（數字到值）
Q20_VALUE_MAPPING = {
    1: "financial_reward",
    2: "technical_growth", 
    3: "work_life_balance",
    4: "brand_reputation",
    5: "team_culture",
    6: "social_impact"
}

def convert_single_user(old_data: Dict[str, Any]) -> Dict[str, Any]:
    """轉換單一使用者的資料從舊格式到新格式"""
    user_info = old_data.get("user_info", {})
    responses = old_data.get("responses", {})
    
    # 轉換 Q1 語言資料 (language/level -> name/score)
    q1_languages = []
    if "Q1" in responses and isinstance(responses["Q1"], list):
        for lang_item in responses["Q1"]:
            q1_languages.append({
                "name": lang_item.get("language", ""),
                "score": lang_item.get("level", 1)
            })
    
    # 轉換 Q4 資料庫（複選，字母陣列）
    q4_database = []
    if "Q4" in responses:
        q4_choices = responses["Q4"]
        if isinstance(q4_choices, list):
            for option in q4_choices:
                if option in OPTION_MAPPING["Q4"]:
                    q4_database.append(OPTION_MAPPING["Q4"][option])
        elif isinstance(q4_choices, str):
            # 如果是單一字串，也處理
            if q4_choices in OPTION_MAPPING["Q4"]:
                q4_database.append(OPTION_MAPPING["Q4"][q4_choices])
    
    # 轉換 Q20 價值觀（數字陣列）
    q20_values = []
    if "Q20" in responses:
        q20_choices = responses["Q20"]
        if isinstance(q20_choices, list):
            for num in q20_choices:
                if num in Q20_VALUE_MAPPING:
                    q20_values.append(Q20_VALUE_MAPPING[num])
        elif isinstance(q20_choices, (int, str)):
            # 如果是單一數字或字串數字
            num = int(q20_choices) if isinstance(q20_choices, str) else q20_choices
            if num in Q20_VALUE_MAPPING:
                q20_values.append(Q20_VALUE_MAPPING[num])
    
    # 轉換 Q23 學習偏好（複選，字母陣列）
    q23_learning = []
    if "Q23" in responses:
        q23_choices = responses["Q23"]
        if isinstance(q23_choices, list):
            for option in q23_choices:
                if option in OPTION_MAPPING["Q23"]:
                    q23_learning.append(OPTION_MAPPING["Q23"][option])
        elif isinstance(q23_choices, str):
            # 如果是單一字串
            if q23_choices in OPTION_MAPPING["Q23"]:
                q23_learning.append(OPTION_MAPPING["Q23"][q23_choices])
    
    # 建立新格式的資料
    new_data = {
        "user_id": f"user_{user_info.get('id', 'unknown')}",
        "timestamp": datetime.now().isoformat() + "Z",
        "module_a": {
            "q1_languages": q1_languages,
            "q2_frontend": OPTION_MAPPING["Q2"].get(responses.get("Q2", ""), ""),
            "q3_backend": OPTION_MAPPING["Q3"].get(responses.get("Q3", ""), ""),
            "q4_database": q4_database,
            "q5_devops": OPTION_MAPPING["Q5"].get(responses.get("Q5", ""), ""),
            "q6_ai_data": OPTION_MAPPING["Q6"].get(responses.get("Q6", ""), ""),
            "q7_security": OPTION_MAPPING["Q7"].get(responses.get("Q7", ""), ""),
            "q8_domain": responses.get("Q8", "")
        },
        "module_b": {
            "q9_troubleshoot": OPTION_MAPPING["Q9"].get(responses.get("Q9", ""), ""),
            "q10_tech_choice": OPTION_MAPPING["Q10"].get(responses.get("Q10", ""), ""),
            "q11_communication": OPTION_MAPPING["Q11"].get(responses.get("Q11", ""), ""),
            "q12_code_review": OPTION_MAPPING["Q12"].get(responses.get("Q12", ""), ""),
            "q13_learning": OPTION_MAPPING["Q13"].get(responses.get("Q13", ""), ""),
            "q14_process": OPTION_MAPPING["Q14"].get(responses.get("Q14", ""), ""),
            "q15_english": OPTION_MAPPING["Q15"].get(responses.get("Q15", ""), "")
        },
        "module_c": {
            "q16_current_level": OPTION_MAPPING["Q16"].get(responses.get("Q16", ""), ""),
            "q17_target_role": OPTION_MAPPING["Q17"].get(responses.get("Q17", ""), ""),
            "q18_industry": OPTION_MAPPING["Q18"].get(responses.get("Q18", ""), ""),
            "q19_search_status": OPTION_MAPPING["Q19"].get(responses.get("Q19", ""), "")
        },
        "module_d": {
            "q20_values_top3": q20_values,
            "q21_pressure": OPTION_MAPPING["Q21"].get(responses.get("Q21", ""), ""),
            "q22_career_type": OPTION_MAPPING["Q22"].get(responses.get("Q22", ""), ""),
            "q23_learning_style": q23_learning
        }
    }
    
    return new_data

def convert_file(input_file: str, output_file: str = None, user_index: int = None):
    """
    轉換檔案格式
    
    Args:
        input_file: 輸入檔案路徑 (out_put.json)
        output_file: 輸出檔案路徑（選填，不指定則自動命名）
        user_index: 要轉換的使用者索引（選填，None 則轉換所有使用者，索引從 0 開始）
    """
    print(f"正在讀取檔案: {input_file}")
    
    # 讀取原始資料
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            old_data_list = json.load(f)
    except FileNotFoundError:
        print(f"❌ 錯誤：找不到檔案 {input_file}")
        return
    except json.JSONDecodeError as e:
        print(f"❌ 錯誤：JSON 格式錯誤 - {e}")
        return
    
    if not isinstance(old_data_list, list):
        print("❌ 錯誤：輸入檔案格式不正確，應該是陣列格式")
        return
    
    print(f"✓ 讀取成功，共 {len(old_data_list)} 個使用者")
    
    # 決定要轉換哪些使用者
    if user_index is not None:
        if 0 <= user_index < len(old_data_list):
            users_to_convert = [old_data_list[user_index]]
            output_suffix = f"_user{user_index + 1}"
            print(f"只轉換第 {user_index + 1} 個使用者")
        else:
            print(f"❌ 錯誤：使用者索引 {user_index} 超出範圍 (0-{len(old_data_list)-1})")
            return
    else:
        users_to_convert = old_data_list
        output_suffix = "_converted"
        print(f"轉換所有 {len(users_to_convert)} 個使用者")
    
    # 轉換資料
    print("\n開始轉換...")
    converted_list = []
    errors = []
    
    for idx, user_data in enumerate(users_to_convert, 1):
        try:
            converted = convert_single_user(user_data)
            converted_list.append(converted)
            user_id = user_data.get("user_info", {}).get("id", idx)
            print(f"  [{idx}/{len(users_to_convert)}] ✓ 使用者 {user_id} 轉換成功")
        except Exception as e:
            user_id = user_data.get("user_info", {}).get("id", idx)
            print(f"  [{idx}/{len(users_to_convert)}] ❌ 使用者 {user_id} 轉換失敗: {e}")
            errors.append({"user_id": user_id, "error": str(e)})
    
    # 決定輸出格式和檔案名稱
    if user_index is not None:
        # 單一使用者：輸出為單一物件
        result = converted_list[0] if converted_list else {}
        output_data = result
    else:
        # 多個使用者：輸出為陣列
        output_data = converted_list
    
    # 決定輸出檔案名稱
    if output_file is None:
        base_name = input_file.replace('.json', '')
        output_file = f"{base_name}{output_suffix}.json"
    
    # 儲存轉換後的資料
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ 轉換完成！")
        print(f"  輸入：{input_file}")
        print(f"  輸出：{output_file}")
        print(f"  成功轉換：{len(converted_list)} 個使用者")
        if errors:
            print(f"  失敗：{len(errors)} 個使用者")
            for err in errors:
                print(f"    - 使用者 {err['user_id']}: {err['error']}")
    except Exception as e:
        print(f"❌ 儲存檔案時發生錯誤: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("=" * 60)
        print("格式轉換工具 - 將 out_put.json 轉換成 test_logic.py 可讀取的格式")
        print("=" * 60)
        print("\n使用方法：")
        print("  python convert_format.py <輸入檔案> [選項]")
        print("\n選項：")
        print("  -o <輸出檔案>    指定輸出檔案名稱")
        print("  -u <索引>        只轉換指定索引的使用者（從 0 開始）")
        print("\n範例：")
        print("  # 轉換所有使用者")
        print("  python convert_format.py out_put.json")
        print("\n  # 轉換所有使用者並指定輸出檔名")
        print("  python convert_format.py out_put.json -o converted.json")
        print("\n  # 只轉換第 1 個使用者（索引 0）")
        print("  python convert_format.py out_put.json -u 0 -o user1.json")
        print("\n  # 只轉換第 2 個使用者（索引 1）")
        print("  python convert_format.py out_put.json -u 1 -o user2.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = None
    user_index = None
    
    # 解析參數
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "-o" and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "-u" and i + 1 < len(sys.argv):
            try:
                user_index = int(sys.argv[i + 1])
            except ValueError:
                print(f"❌ 錯誤：無效的使用者索引 '{sys.argv[i + 1]}'，必須是數字")
                sys.exit(1)
            i += 2
        else:
            print(f"⚠ 警告：未知參數 '{sys.argv[i]}'，將忽略")
            i += 1
    
    convert_file(input_file, output_file, user_index)
