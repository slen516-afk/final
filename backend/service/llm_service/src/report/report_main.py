# main.py
import json
import os
from dotenv import load_dotenv
from crewai import Crew, Process

# 引入拆分後的模組
from .agents import CareerAgentFactory
from .tasks import CareerTaskFactory
from src.features.analysis.schemas import CareerReport

load_dotenv()

class CareerOrchestrator:
    def __init__(self):
        self.agents = CareerAgentFactory()
        self.tasks = CareerTaskFactory()

    def determine_user_type(self, survey_data: dict) -> str:
        """
        簡單路由邏輯：檢查職級或技能
        """
        current_level = survey_data.get("module_c", {}).get("q16_current_level", "")
        # 如果自評是 entry_level，歸類為無經驗
        if current_level == "entry_level":
            return "entry_level"
        return "experienced"

    def run(self, survey_str, trait_str, resume_str, target_role=None, learning_style=""):
        # 1. 解析資料與路由
        survey_data = json.loads(survey_str)
        user_type = self.determine_user_type(survey_data)
        
        inputs = {
            "survey_json": survey_str,
            "trait_json": trait_str,
            "resume_json": resume_str,
            "target_role": target_role,
            "learning_style": learning_style
        }

        print(f"🔍 系統偵測使用者類型: [{user_type.upper()}] - 啟動對應 Crew 流程...")

        if user_type == "experienced":
            return self._run_experienced_flow(inputs)
        else:
            return self._run_entry_level_flow(inputs)

    
    # --- 定義流程 ---

    # --- 流程 A: 有經驗者 ---
    def _run_experienced_flow(self, inputs):
        # 1. 召喚 Agents：技術評估專家、心理學家、職涯顧問
        tech_agent = self.agents.create_tech_assessor()
        psych_agent = self.agents.create_psychologist()
        advisor_agent = self.agents.create_career_advisor()

        # 2. 派發 Tasks
        # t1: 技術分析 (算分、驗證履歷)
        t1 = self.tasks.tech_analysis(tech_agent, inputs)
        # t2: 心理分析 (壓力測試)
        t2 = self.tasks.psych_analysis(psych_agent, inputs)
        # t3: 寫報告 (把 t1, t2 的結果整合，並寫入 Metadata)
        # 注意：這裡把 inputs 傳進去了，為了抓 user_id 和 timestamp
        t3 = self.tasks.final_report_experienced(advisor_agent, [t1, t2], inputs=inputs)

        # 3. 組建 Crew
        crew = Crew(
            agents=[tech_agent, psych_agent, advisor_agent],
            tasks=[t1, t2, t3], # 順序：依序執行 (t1 -> t2 -> t3
            process=Process.sequential,
            verbose=True
        )
        return crew.kickoff()

    # --- 流程 B: 無經驗者 ---
    def _run_entry_level_flow(self, inputs):
        # 1. 召喚 Agents (現在我們需要三位專家)
        mentor_agent = self.agents.create_discovery_mentor()
        psych_agent = self.agents.create_psychologist()      # 加入心理學家
        advisor_agent = self.agents.create_career_advisor()  # 加入顧問
        
        # 2. 派發 Tasks
        # Task 1: 導師做技能轉譯
        t1 = self.tasks.discovery_analysis(mentor_agent, inputs)

        # Task 2: 心理學家做潛力分析
        t2 = self.tasks.psych_analysis(psych_agent, inputs)

        # Task 3: 顧問寫最終報告 (參考 t1 和 t2 的產出)
        t3 = self.tasks.final_report_entry_level(advisor_agent, [t1, t2], inputs=inputs)

        # 3. 組建 Crew
        crew = Crew(
            agents=[mentor_agent, psych_agent, advisor_agent],
            tasks=[t1, t2, t3],
            process=Process.sequential, # 依序執行
            verbose=True
        )
        return crew.kickoff()

# ==========================================
# 測試資料與執行區
# ==========================================
if __name__ == "__main__":
    
    orchestrator = CareerOrchestrator()

    # --- 測試案例 1: 有經驗的資深工程師 ---
    print("\n\n====== TEST CASE 1: EXPERIENCED ======")
    INPUT_CAREER_DATA = {
    "user_id": "1",
    "timestamp": "2026-02-13T12:00:00.000Z",
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

    # 2. 執行 Orchestrator
    result = orchestrator.run(
        survey_str=json.dumps(INPUT_CAREER_DATA), # 使用上方定義完整的 INPUT_CAREER_DATA
        trait_str=json.dumps(INPUT_TRAIT_DATA),   # 使用上方定義完整的 INPUT_TRAIT_DATA
        resume_str=json.dumps(RESUME_DATA),       # 使用上方定義完整的 RESUME_DATA
        target_role="backend",                    # 指定目標職位
        learning_style="Hands-on Projects"        # 指定學習風格
    )

    # 3. 輸出結果
    print("\n🎉 [有經驗者] 最終報告 (Pydantic JSON):")
    if hasattr(result, 'pydantic') and result.pydantic:
        print(result.pydantic.model_dump_json(indent=2))
    else:
        print(result)

    # --- 測試案例 2: 無經驗的行政轉職者 ---
    # print("\n\n====== TEST CASE 2: ENTRY LEVEL ======")
    
    # # Mock Data (Entry Level)
    # mock_entry_survey = {
    # "module_c": {
    #     "q16_current_level": "entry_level",
    #     "q17_target_role": None, # <--- 關鍵修改
    #     "q18_industry": "traditional_digital",
    #     "q19_search_status": "passive_open"
    # },
    # "module_d": {
    #     "q20_values_top3": ["financial_reward", "work_life_balance", "technical_growth"],
    #     "q21_pressure": "reject_health_first",
    #     "q22_career_type": "specialist",
    #     "q23_learning_style": ["structured_courses", "books"]
    # }
    # }
    
    # mock_entry_resume = {
    # "basic_info": {
    #     "name": "Alex Chen",
    #     "current_title": "行政專員 (Administrative Specialist)",
    #     "years_of_experience": 3,
    #     "education": {"degree": "學士", "major": "企業管理學系", "school_type": "非本科系"}
    # },
    # "resume_summary": "擁有3年行政與流程管理經驗。擅長透過 Excel (VLOOKUP, 樞紐分析) 處理複雜報表與數據整理。雖然沒有程式開發經驗，但對邏輯流程優化有高度興趣，曾利用 Notion 與 Trello 建立部門協作SOP，提升團隊效率 20%。",
    # "skills_tags": ["進階 Excel", "流程管理 (SOP)", "專案協作 (Notion/Trello)", "財務報表基礎", "邏輯分析"],
    # "domain_knowledge": "行政作業流程、會計基礎、文件管理"
    # }
    
    # mock_traits = {
    # "user_id": "test_user_zero_001",
    # "trait_normalized_scores": {
    #     "structure": 100, "ambiguity": 28, "decision": 42, "learning": 60, "transfer": 85
    # },
    # "primary_archetype": "STRUCTURE_ARCHITECT",
    # }

    # result = orchestrator.run(
    #     survey_str=json.dumps(mock_entry_survey),
    #     trait_str=json.dumps(mock_traits),
    #     resume_str=json.dumps(mock_entry_resume),
    #     target_role=None,
    #     learning_style="Video Courses"
    # )

    # print("\n🎉 最終報告 (Pydantic JSON):")
    # print(result.pydantic.model_dump_json(indent=2))