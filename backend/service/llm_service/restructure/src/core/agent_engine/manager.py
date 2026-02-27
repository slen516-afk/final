import os
import json
import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

# 引用 TaskType
from .task_types import TaskType
from src.core.database.supabase_client import get_next_version_number

# 載入環境變數
load_dotenv()

class CareerAgentManager:
    """
    總代理管理器 (Facade Pattern)
    負責根據 TaskType 組裝對應的 Agent 與 Task，並執行 CrewAI 流程。
    """
    
    def __init__(self, model_name: str = "o3-mini"):
        # 初始化共用的 LLM 設定 (使用 OpenAI o3-mini 模型)
        self.llm = LLM(model=model_name)
        self.qa_llm = LLM(model=model_name) 

    def run_task(self, task_type_str: str, user_id: str, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        執行特定任務的主要入口。
        """
        print(f"🚀 Manager 收到請求: {task_type_str} | User ID: {user_id}")

        # 1. 處理自動分流邏輯 (Auto-Dispatch)
        if task_type_str == "career_analysis":
            try:
                survey_data = json.loads(user_input.get("survey_json", "{}"))
                # 檢查 module_a 技術填寫紀錄 (q1_languages 是否有值且非空)
                has_experience = (
                    survey_data.get("module_a", {}).get("q1_languages") is not None and 
                    len(survey_data.get("module_a", {}).get("q1_languages")) > 0
                )
                
                if has_experience:
                    task_type_str = "career_analysis_experienced"
                    print("➡️ 自動識別為：有經驗者分析路徑")
                else:
                    task_type_str = "career_analysis_entry_level"
                    print("➡️ 自動識別為：無經驗/轉職者分析路徑")
            except Exception as e:
                print(f"⚠️ 自動分流識別失敗，預設採用無經驗者路徑: {e}")
                task_type_str = "career_analysis_entry_level"

        try:
            task_type = TaskType(task_type_str)
        except ValueError:
            return {"status": "error", "message": f"不支援的 task_type: {task_type_str}"}

        # 0. 注入 分析報告所需 Metadata 資訊 (動態獲取版本號)
        user_input["user_id"] = user_id
        user_input["current_timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='milliseconds').replace("+00:00", "Z")
        user_input["report_version"] = get_next_version_number(user_id)
        
        # 1. 取得任務配置 (Configuration) - 引入 config 找與對應 task_type 的藍圖
        config = self._get_process_config(task_type, user_input)
        
        if not config:
            return {"status": "error", "message": f"找不到或無法產生 task 設定: {task_type}"}

        # 2. 建立 Agents
        # A. Worker Agents (執行者) - 可能有多個
        worker_agents = []
        for agent_cfg in config["agents"]:
            worker = Agent(
                role=agent_cfg["role"],
                goal=agent_cfg["goal"],
                backstory=agent_cfg["backstory"],
                tools=agent_cfg.get("tools", []),
                verbose=True,
                llm=self.llm,
                allow_delegation=False
            )
            worker_agents.append(worker)

        # B. QA Agent (品質監控者) - 固定存在，負責最終把關
        qa_agent = Agent(
            role="資深品質與格式監控官 (QA Lead)",
            goal="審核內容的準確性、專業度，並確保輸出完全符合指定的 Pydantic JSON 結構。",
            backstory="""
            你是一位極其挑剔的技術編輯與資料結構專家。
            你的職責不是創造新內容，而是：
            1. **驗證**：檢查 Worker 的產出是否符合邏輯、是否出現幻覺。
            2. **修潤**：確保語氣專業、溫暖且具建設性（符合繁體中文習慣）。
            3. **格式化**：將最終結果強制轉換為嚴格的 JSON 格式。
            """,
            verbose=True,
            llm=self.qa_llm, # 使用低溫度的 LLM
            allow_delegation=False
        )

        # 3. 建立 Tasks
        crew_tasks = []
        
        # A. Worker Tasks
        # 這裡支援多個 Worker 任務 (例如：先做技術分析 -> 再做心理分析)
        previous_tasks = []
        for idx, task_cfg in enumerate(config["tasks"]): # enumerate() 函數會返回一個索引和對應的值
            worker_task = Task(
                description=task_cfg["description"],
                expected_output=task_cfg["expected_output"],
                agent=worker_agents[idx], # 對應的 Agent
                context=previous_tasks if idx > 0 else None # 串接上下文
            )
            crew_tasks.append(worker_task)
            previous_tasks.append(worker_task)

        # B. QA Task (最後一哩路)
        # QA 任務會接收所有 Worker 任務的產出作為 Context
        qa_extra_instructions = config.get("qa_extra_instructions", "")
        
        qa_task = Task(
            description=f"""
            審核並整合上述所有任務的產出結果。
            
            **你的核心檢查清單 (Checklist)**:
            1. **完整性檢查**: 確認所有必要的分析維度（技術、心理、建議）都已包含。
            2. **格式驗證**: 確保輸出嚴格符合 `{config['output_model'].__name__}` 的定義。
            3. **語氣校正**: 確保使用流暢的台灣繁體中文。
            
            {qa_extra_instructions}
            
            **關鍵指示**: 如果 Worker 的產出有遺漏或矛盾，請根據上下文進行合理的修正或標註，但不要自行捏造數據。
            """,
            expected_output="最終審核通過的結構化 JSON 報告。",
            agent=qa_agent,
            context=crew_tasks, # 獲取所有 Worker 的產出
            output_pydantic=config["output_model"] # <--- 最終輸出由 QA 負責結構化
        )
        
        # 將 QA 任務加入列表末尾
        final_tasks = crew_tasks + [qa_task]
        final_agents = worker_agents + [qa_agent]

        # 4. 組建 Crew 並執行 (改走 Mock 模式)
        # crew = Crew(
        #     agents=final_agents,
        #     tasks=final_tasks,
        #     process=Process.sequential,
        #     verbose=True
        # )

        # result = crew.kickoff(inputs=user_input)
        
        # # 5. 回傳 Pydantic 模型轉出的 Dict
        # try:
        #     return result.pydantic.model_dump()
        # except AttributeError:
        #     return {"status": "partial_success", "raw_content": result.raw}

        # ---------------- MOCK 模式 ----------------
        print(f"⚠️ 啟動 MOCK 模式：不調用實體模型以節省 Token ({task_type_str})")
        import time
        time.sleep(2)  # 模擬運算

        if "career_analysis" in task_type_str:
            return {
                "report_metadata": {
                    "version": user_input.get("report_version", "1.0"),
                    "timestamp": user_input.get("current_timestamp", datetime.datetime.now(datetime.timezone.utc).isoformat()),
                    "user_id": user_id
                },
                "preliminary_summary": {
                    "core_insight": "[MOCK] 具備後端架構強項，但缺乏運維經驗。"
                },
                "radar_chart": {
                    "dimensions": [
                        {"axis": "前端開發", "score": 3.0},
                        {"axis": "後端開發", "score": 4.5},
                        {"axis": "運維部署", "score": 2.0},
                        {"axis": "AI與數據", "score": 3.0},
                        {"axis": "工程品質", "score": 4.0},
                        {"axis": "軟實力", "score": 3.5}
                    ]
                },
                "gap_analysis": {
                    "current_status": {
                        "self_assessment": "D. 資深工程師 (Senior)",
                        "actual_level": "Mid-to-Senior",
                        "cognitive_bias": "[MOCK] 認知準確。"
                    },
                    "target_position": {
                        "role": "E. 技術主管(Lead)",
                        "match_score": "65%",
                        "gap_description": "[MOCK] 尚缺運維與軟實力提升。"
                    }
                },
                "action_plan": {
                    "priority_items": [
                        {"category": "技術提升", "action": "[MOCK] 加強 Kubernetes", "recommendation_type": "實作專案"}
                    ],
                    "learning_resource_preference": "[MOCK] 實作專案做中學。"
                }
            }
        elif "resume_analysis" in task_type_str:
            return {
                "candidate_positioning": "[MOCK] 資深後端開發工程師，具備雲端與微服務架構潛力",
                "target_role_gap_summary": "[MOCK] 與目標職缺技術相符，但缺乏具體量化成果展現。",
                "overall_strengths": [
                    "[MOCK] 具備紮實的 Python 與 Flask 開發經驗",
                    "[MOCK] 曾參與過系統重構與效能優化專案"
                ],
                "overall_weaknesses": [
                    "[MOCK] 履歷多採條列式描述職責，缺乏具體成效數據",
                    "[MOCK] 在系統部署與 CI/CD 部分的描述較為薄弱"
                ],
                "critical_issues": [
                    {
                        "section": "工作經歷",
                        "original_text": "負責優化後端 API 效能，重構舊有系統",
                        "issue_type": ["描述模糊", "缺乏量化證據"],
                        "severity": ["可優化"],
                        "diagnosis_dimension": "技術深度",
                        "issue_reason": "企業無法透過純文字衡量優化效益",
                        "improvement_direction": [
                            "具體列出優化前的瓶頸，以及優化後提升多少 % 效能"
                        ]
                    }
                ],
                "ats_risk_level": "[MOCK] 中",
                "screening_outcome_prediction": "[MOCK] 可通過初步自動篩選，但人資審核可能會將優先級排後。",
                "recommended_next_actions": [
                    "[MOCK] 將工作經歷改以 STAR 原則重新撰寫"
                ]
            }
        elif "resume_opt" in task_type_str:
            return {
                "name": "[MOCK] 王小明",
                "phone": "0912345678",
                "email": "xiaoming@example.com",
                "linkedln": "https://linkedin.com/in/xiaoming",
                "github": "https://github.com/xiaoming",
                "professional_summary": "[MOCK] 具備 5 年以上後端開發經驗，專精於 Python 與高效能雲端架構設計。擅長重構遺留系統並導入 CI/CD 流程。",
                "professional_experience": [
                    "[MOCK] X科技股份有限公司 | 資深後端工程師 | 2021-Present\n- 透過導入 Redis Cache，提升 API 讀取效能達 40%。\n- 規劃微服務架構，成功將單一節點系統拆分為 5 個核心服務。"
                ],
                "core_skills": [
                    "Python", "Flask", "Docker", "Kubernetes", "Redis", "PostgreSQL"
                ],
                "projects": [
                    "[MOCK] 電商高併發結帳系統\n- 使用 RabbitMQ 處理秒殺活動訂單，成功消化每秒 10,000 筆請求。"
                ],
                "education": [
                    "[MOCK] 國立台灣大學 | 資訊工程學系 | 學士 | 2015-2019"
                ],
                "autobiography": "[MOCK] 由於對技術的熱愛，我經常參與開源社群，期望能透過自身後端領域的專長，為產品創造真正的價值。"
            }
        else:
            return {
                "status": "mock_success",
                "message": f"[MOCK] 這是 {task_type_str} 的 Mock 產出。"
            }

    def _get_process_config(self, task_type: TaskType, inputs: Dict[str, Any]) -> Optional[Dict]:
        """
        配置工廠 (Configuration Factory)
        user_input 進入內部邏輯，重新命名為 input (兩個變數為相同記憶體位置)
        """
        from .config import get_config_by_type
        return get_config_by_type(task_type, inputs)
