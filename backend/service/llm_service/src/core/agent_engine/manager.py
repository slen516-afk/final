import os
import json
import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# 引用 TaskType
from .task_types import TaskType

# 載入環境變數
load_dotenv()


class CareerAgentManager:
    """
    總代理管理器 (Facade Pattern)
    負責根據 TaskType 組裝對應的 Agent 與 Task，並執行 CrewAI 流程。
    支援 Mock 模式：mock_mode=True 或環境變數 MOCK_MODE=true 時，
    跳過 LLM / Supabase 初始化，直接回傳符合 Pydantic schema 的假資料。
    """

    def __init__(self, model_name: str = "gpt-4o", temp: float = 0.7, mock_mode: bool = False):
        self.mock_mode = mock_mode or os.environ.get("MOCK_MODE", "").lower() == "true"

        if self.mock_mode:
            print("[Mock Mode] CareerAgentManager 以 Mock 模式啟動，跳過 LLM / Supabase 初始化")
            self.llm = None
            self.qa_llm = None
            self.supabase = None
            self.handler_registry = None
            return

        from crewai import LLM
        from .result_handlers import HandlerRegistry
        from src.core.database.supabase_client import get_supabase_client

        # 初始化共用的 LLM 設定 (使用 OpenAI o3-mini 模型)
        self.llm = LLM(model=model_name, temperature=temp)
        self.qa_llm = LLM(model=model_name, temperature=0.1)

        # 初始化 Supabase Client 與結果處理註冊器
        self.supabase = get_supabase_client()
        self.handler_registry = HandlerRegistry(self.supabase)

    # ------------------------------------------------------------------
    # Mock 資料產生器
    # ------------------------------------------------------------------
    def _mock_result(self, task_type_str: str, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """依據 task_type 回傳符合 Pydantic schema 的 mock dict。"""
        user_id = user_input.get("user_id", "mock_user")
        now = datetime.datetime.now(datetime.timezone.utc).isoformat(
            timespec="milliseconds"
        ).replace("+00:00", "Z")

        if task_type_str in (
            "career_analysis",
            "career_analysis_experienced",
            "career_analysis_entry_level",
        ):
            # CareerReport schema
            return {
                "report_metadata": {
                    "user_id": user_id,
                    "timestamp": now,
                    "version": "1.0",
                },
                "preliminary_summary": {
                    "core_insight": "【Mock】候選人在後端開發與分散式系統設計方面展現出堅實的技術優勢。"
                },
                "radar_chart": {
                    "dimensions": [
                        {"axis": "前端開發", "score": 2.0},
                        {"axis": "後端開發", "score": 4.0},
                        {"axis": "運維部署", "score": 3.0},
                        {"axis": "AI與數據", "score": 1.5},
                        {"axis": "工程品質", "score": 3.5},
                        {"axis": "軟實力", "score": 4.0},
                    ]
                },
                "gap_analysis": {
                    "current_status": {
                        "self_assessment": "【Mock】中階工程師 (Mid Level)",
                        "actual_level": "【Mock】中階工程師 (Mid Level)",
                        "cognitive_bias": "【Mock】自評與實際水平大致吻合，但在運維部署方面有輕微高估。",
                    },
                    "target_position": {
                        "role": "【Mock】後端工程師",
                        "match_score": "78%",
                        "gap_description": "【Mock】後端技術紮實但缺乏 K8s 與 CI/CD 實操經驗，需加強雲端維運能力。",
                    },
                },
                "action_plan": {
                    "short_term": "【Mock】短期 1-3 個月：學習 K8s 基礎與 CI/CD 流程。",
                    "mid_term": "【Mock】中期 3-6 個月：參與微服務架構實戰專案。",
                    "long_term": "【Mock】長期 6 個月以上：深入架構設計與跨域整合。",
                },
            }

        elif task_type_str == "resume_analysis":
            # ResumeAnalysis schema
            return {
                "candidate_positioning": "【Mock】目前履歷呈現為具備 3 年經驗的後端工程師。",
                "target_role_gap_summary": "【Mock】與資深後端工程師職位仍有架構設計經驗的落差。",
                "overall_strengths": [
                    "【Mock】Python / FastAPI 實戰經驗豐富",
                    "【Mock】具備微服務設計概念",
                ],
                "overall_weaknesses": [
                    "【Mock】缺乏量化成果描述",
                    "【Mock】專案經歷未突顯技術深度",
                ],
                "critical_issues": [
                    {
                        "section": "【Mock】專案經歷",
                        "original_text": "【Mock】負責後端 API 開發",
                        "issue_type": ["【Mock】描述模糊", "【Mock】缺乏量化證據"],
                        "severity": ["【Mock】明顯扣分"],
                        "diagnosis_dimension": "【Mock】技術深度展現",
                        "issue_reason": "【Mock】HR 無法從描述中判斷實際技術水準與貢獻度。",
                        "improvement_direction": [
                            "【Mock】補充 API 吞吐量、回應時間等量化指標",
                            "【Mock】描述具體使用的技術棧與架構決策",
                        ],
                    }
                ],
                "ats_risk_level": "【Mock】中",
                "screening_outcome_prediction": "【Mock】HR 快速掃描後可能因缺乏量化成果而歸入待定區。",
                "recommended_next_actions": [
                    "【Mock】為每段經歷補充 2-3 個量化指標",
                    "【Mock】調整專業摘要以匹配目標職位關鍵字",
                ],
            }

        elif task_type_str == "resume_opt":
            # ResumeOptimization schema
            return {
                "professional_summary": "【Mock】具備 3 年 Python 後端開發經驗，專精 FastAPI 與微服務架構設計。",
                "professional_experience": [
                    "【Mock】ABC 科技 | 後端工程師 | 2023-2026 | 負責 API 設計與效能優化，QPS 提升 40%。"
                ],
                "core_skills": [
                    "【Mock】Python",
                    "【Mock】FastAPI",
                    "【Mock】PostgreSQL",
                    "【Mock】Docker",
                    "【Mock】Redis",
                    "【Mock】微服務架構",
                ],
                "projects": [
                    "【Mock】職涯導航平台：使用 CrewAI + GPT-4o 建構多 Agent 履歷分析系統，處理效率提升 60%。"
                ],
                "education": ["【Mock】國立台灣大學 | 資訊工程學系 | 學士 | 2023"],
                "autobiography": "【Mock】我是一位熱愛技術的後端工程師，從大學時期便開始接觸程式開發……（Mock 自傳內容）",
            }

        # 其他未知 task_type → 通用 stub
        return {
            "status": "mock",
            "task_type": task_type_str,
            "message": f"【Mock】{task_type_str} 尚無專屬 mock 資料，回傳通用 stub。",
        }

    # ------------------------------------------------------------------
    # 主要入口
    # ------------------------------------------------------------------
    def run_task(self, task_type_str: str, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        執行特定任務的主要入口。
        """
        # 1. 從字典中提取 user_id
        user_id = user_input.get("user_id")
        if not user_id:
            return {"status": "error", "message": "user_input 中缺少 user_id"}

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

        # ---- Mock 模式：直接回傳假資料，不走 CrewAI ----
        if self.mock_mode:
            print(f" [Mock Mode] 回傳 {task_type_str} 的 mock 資料")
            return self._mock_result(task_type_str, user_input)

        # ---- 正式模式：CrewAI pipeline ----
        from crewai import Agent, Task, Crew, Process
        from src.core.database.supabase_client import get_next_version_number

        try:
            task_type = TaskType(task_type_str)
        except ValueError:
            return {"status": "error", "message": f"不支援的 task_type: {task_type_str}"}

        # 0. 注入 分析報告所需 Metadata 資訊 (動態獲取版本號)
        # user_input["user_id"] = user_id
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

        # 4. 組建 Crew 並執行
        crew = Crew(
            agents=final_agents,
            tasks=final_tasks,
            process=Process.sequential, # 確保依序執行：Worker 1 -> Worker 2 -> ... -> QA
            verbose=True
        )

        result = crew.kickoff(inputs=user_input)

        # 5. 回傳 Pydantic 模型轉出的 Dict
        try:
            pydantic_result = result.pydantic.model_dump()

            # --- 自動回存資料庫 (整合點) ---
            try:
                # 取得該任務對應的 Handler
                handler = self.handler_registry.get_handler(task_type)
                if handler:
                    # 執行儲存 (user_id 已包含在 **user_input 中)
                    handler.process(pydantic_result, **user_input)
                    print(f"✅ {task_type_str} 資料已成功自動存入資料庫")
            except Exception as e:
                # ⚠️ 儲存失敗不影響主流程，僅紀錄日誌
                print(f"⚠️ [Storage Integration] 自動儲存失敗，僅回傳生成資料: {e}")

            return pydantic_result

        except AttributeError:
             # Fallback: 如果沒有成功轉成 Pydantic (極少發生)，回傳 raw text
            return {"status": "partial_success", "raw_content": result.raw}

    def _get_process_config(self, task_type: TaskType, inputs: Dict[str, Any]) -> Optional[Dict]:
        """
        配置工廠 (Configuration Factory)
        user_input 進入內部邏輯，重新命名為 input (兩個變數為相同記憶體位置)
        """
        from .config import get_config_by_type
        return get_config_by_type(task_type, inputs)
