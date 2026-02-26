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


def run_analysis(user_data: dict) -> dict:
  
    # --- 1. 計算能力向量 ---
    analyzer = CareerAnalyzer(user_data)
    analyzer.calculate_vectors()
    vectors = analyzer.scores

    # --- 2. 計算目標職位匹配度 ---
    target_role = user_data['module_c']['q17_target_role']
    real_match_score = JobMatcher.calculate_match_score(vectors, target_role)

    # --- 3. 取得履歷文字 ---
    retriever = ResumeRetriever()
    resume_text = retriever.get_resume_text_by_user(user_data.get("user_id", ""))

    # --- 4. 生成 AI 分析報告 ---
    processed_data = {
        "calculated_vectors": vectors,
        "user_raw_input": user_data
    }

    generator = CareerReportGenerator(model_name="o3-mini")
    report = generator.generate_report(
        processed_data,
        match_score=real_match_score,
        resume_content=resume_text
    )

    # 錯誤檢查
    if "error" in report:
        return report

    # 覆蓋雷達圖數據 (雙重保險)
    if "radar_chart" in report:
        report['radar_chart']['dimensions'] = [
            {"axis": "前端開發", "score": vectors.get("D1", 0)},
            {"axis": "後端開發", "score": vectors.get("D2", 0)},
            {"axis": "運維部署", "score": vectors.get("D3", 0)},
            {"axis": "AI與數據", "score": vectors.get("D4", 0)},
            {"axis": "工程品質", "score": vectors.get("D5", 0)},
            {"axis": "軟實力",   "score": vectors.get("D6", 0)},
        ]

    return report


def main():
    print("--- 1. 開始計算能力向量 (Calculated Vectors) ---")
    report = run_analysis(TEST_DATA)

    if "error" in report:
        print("\n[!] 報告生成失敗，原因如下：")
        print(report["error"])
        return

    print("\n--- 最終報告 (可回傳前端) ---")
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()