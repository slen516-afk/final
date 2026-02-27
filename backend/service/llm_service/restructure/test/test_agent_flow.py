import json
import os
from dotenv import load_dotenv
from src.core.agent_engine.manager import CareerAgentManager

load_dotenv()

def test_experienced_analysis():
    print("\n\n====== TEST CASE: EXPERIENCED ANALYSIS ======")
    manager = CareerAgentManager(model_name="o3-mini")

    INPUT_CAREER_DATA = {
    "module_a": {
        "q1_languages": [{"name": "Python", "score": 5}, {"name": "SQL", "score": 4}, {"name": "Git", "score": 4}],
        "q2_frontend": "unfamiliar",
        "q3_backend": "distributed_system",
        "q4_database": ["rdbms_sql", "key_value_cache"],
        "q5_devops": "k8s_cicd",
        "q6_ai_data": "api_consumer",
        "q7_security": "framework_default",
        "q8_domain": "電子商務"
    },
    "module_b": {
        "q9_troubleshoot": "incident_analysis",
        "q10_tech_choice": "tradeoff_analysis",
        "q11_communication": "alternative_solution",
        "q12_code_review": "architecture_solid",
        "q13_learning": "deep_dive_sharing",
        "q14_process": "process_optimization",
        "q15_english": "global_comm"
    },
    "module_c": {
        "q16_current_level": "senior",
        "q17_target_role": "backend",
        "q18_industry": "product_company",
        "q19_search_status": "passive_open"
    },
    "module_d": {
        "q20_values_top3": ["technical_growth", "social_impact", "financial_reward"],
        "q21_pressure": "consider_short_term",
        "q22_career_type": "specialist",
        "q23_learning_style": ["official_docs", "hands_on_projects"]
    }
    }

    INPUT_TRAIT_DATA = {
    "user_id": "1", # Assuming same user
    "trait_raw_responses": {"Q1": "C", "Q2": "A", "Q3": "B", "Q4": "C", "Q5": "A", "Q6": "B", "Q7": "B", "Q8": "A", "Q9": "A", "Q10": "A"},
    "trait_calculation_debug": {"structure_raw": 10, "ambiguity_raw": 0, "decision_raw": 2, "learning_raw": 4, "transfer_raw": 5},
    "trait_normalized_scores": {
        "structure": 95,
        "ambiguity": 35,
        "decision": 50,
        "learning": 60,
        "transfer": 85
    },
    "primary_archetype": "STRUCTURE_ARCHITECT",
    "secondary_archetypes": ["CROSS_DOMAIN_INTEGRATOR"],
    "trait_created_at": "2026-02-15T10:00:00Z"
    }

    RESUME_DATA = {
    "basics": {
    "name": "陳浩宇",
    "summary": "擁有 5 年經驗的後端工程師，專精於 Python 與高流量電商系統開發..."
    },
    "skills": {
    "languages": ["Python (Expert)", "SQL (Advanced)"],
    "frameworks": ["Django", "Flask", "FastAPI"],
    "infrastructure": ["Docker (Basic)", "AWS EC2/S3"] # 履歷顯示 K8s 經驗確實較少
    },
    "work": [
    {
      "company": "PChome 網路家庭",
      "position": "資深後端工程師",
      "highlights": ["主導雙11購物節高併發流量優化", "Redis 快取", "重構為微服務"]
    }
    ]
    }

    user_input = {
        "survey_json": json.dumps(INPUT_CAREER_DATA),
        "trait_json": json.dumps(INPUT_TRAIT_DATA),
        "resume_json": json.dumps(RESUME_DATA)
    }

    result = manager.run_task("career_analysis_experienced", "user_123", user_input)
    print("\n🎉 Analysis Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

def test_resume_analysis():
    print("\n\n====== TEST CASE: RESUME CRITIQUE ======")
    manager = CareerAgentManager(model_name="o3-mini")

    user_input = {
        "resume_content": "我是一個有五年經驗的工程師，我會寫程式，也喜歡學習新技術。",
        "target_role": "資深後端工程師"
    }

    result = manager.run_task("resume_analysis", "user_123", user_input)
    print("\n🎉 Analysis Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    # 這裡可以選擇要跑哪個測試
    test_experienced_analysis()
    # test_resume_critique()
