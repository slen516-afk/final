import json
from app.generator import CareerReportGenerator
from app.calculator import CareerAnalyzer
from app.calculator import JobMatcher
from app.retriever import ResumeRetriever

# 1. 問卷資料 (維持之前的測試資料)
TEST_DATA = {
  "user_id": "test_user_bio_001",
  "timestamp": "2026-02-06T13:36:07.158Z",
  "module_a": {
    "q1_languages": [
      {
        "name": "Python",
        "score": 2
      },
      {
        "name": "SQL",
        "score": 2
      },
      {
        "name": "JS",
        "score": 2
      }
    ],
    "q2_frontend": "basic_html_css",
    "q3_backend": "crud_api",
    "q4_database": [
      "rdbms_sql",
      "vector_db"
    ],
    "q5_devops": "docker_basic",
    "q6_ai_data": "pandas_numpy",
    "q7_security": "framework_default",
    "q8_domain": "生命科學"
  },
  "module_b": {
    "q9_troubleshoot": "log_search",
    "q10_tech_choice": "team_familiarity",
    "q11_communication": "alternative_solution",
    "q12_code_review": "style_check",
    "q13_learning": "hoarding",
    "q14_process": "process_optimization",
    "q15_english": "slow_reading"
  },
  "module_c": {
    "q16_current_level": "entry_level",
    "q17_target_role": "data_scientist",
    "q18_industry": "traditional_digital",
    "q19_search_status": "active_urgent"
  },
  "module_d": {
    "q20_values_top3": [
      "financial_reward",
      "technical_growth",
      "work_life_balance"
    ],
    "q21_pressure": "consider_short_term",
    "q22_career_type": "generalist",
    "q23_learning_style": [
      "hands_on_projects"
    ]
  }
}

def main():
    print("--- 1. 開始計算能力向量 (Calculated Vectors) ---")
    analyzer = CareerAnalyzer(TEST_DATA)
    analyzer.calculate_vectors()
    vectors = analyzer.scores
    print(f"向量計算結果: {vectors}")

    print("\n--- 2. 計算目標職位匹配度 (Match Score) ---")
    # 從使用者資料中獲取目標職位代碼 (例如 'data_scientist')
    target_role = TEST_DATA['module_c']['q17_target_role']
    
    # 呼叫 JobMatcher 計算百分比
    real_match_score = JobMatcher.calculate_match_score(vectors, target_role)

    # 2. [修改] 直接從 SQL 模擬層撈資料
    retriever = ResumeRetriever()
    # 這裡的邏輯是：直接指定 user_id 拿文字，不經過向量轉換
    resume_text = retriever.get_resume_text_by_user(TEST_DATA["user_id"])

    print(f"目標職位 [{target_role}] 匹配度: {real_match_score}")

    print("\n--- 3. 生成 AI 分析報告 ---")
    # 準備資料包
    processed_data = {
        "calculated_vectors": vectors,
        "user_raw_input": TEST_DATA
    }
    
    generator = CareerReportGenerator(model_name="o3-mini")
    
    # [關鍵]: 將算好的 real_match_score 傳給 generator
    report = generator.generate_report(processed_data, match_score=real_match_score,
    resume_content=resume_text)

    # [修改開始] --- 加入錯誤檢查邏輯 ---
    if "error" in report:
        print("\n[!] 報告生成失敗，原因如下：")
        print(report["error"])
        # 如果是 JSON 解析錯誤，通常是因為模型輸出了 Markdown (```json ... ```)
        return  # 直接結束，避免後續報錯
    
    # 覆蓋雷達圖數據 (雙重保險)
    if "radar_chart" in report:
        report['radar_chart']['dimensions'] = [
            {"axis": "前端開發", "score": vectors.get("D1", 0)},
            {"axis": "後端開發", "score": vectors.get("D2", 0)},
            {"axis": "運維部署", "score": vectors.get("D3", 0)},
            {"axis": "AI與數據", "score": vectors.get("D4", 0)},
            {"axis": "工程品質", "score": vectors.get("D5", 0)},
            {"axis": "軟實力", "score": vectors.get("D6", 0)},
        ]

    print("\n--- 最終報告 (可回傳前端) ---")
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()