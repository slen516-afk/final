import os
import json
import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# 引用 TaskType
from .task_types import TaskType
from .result_handlers import HandlerRegistry
from ..database.supabase_client import get_next_version_number, get_supabase_client

# 載入環境變數
load_dotenv()


class CareerAgentManager:
    """
    總代理管理器 (Facade Pattern)
    負責根據 TaskType 組裝對應的 Agent 與 Task，並執行 CrewAI 流程。
    """

    def __init__(self, model_name: str = "gpt-4o", temp: float = 0.7, mock_mode: bool = False):
        self.mock_mode = mock_mode or os.environ.get("MOCK_MODE", "").lower() == "true"

        if self.mock_mode:
            print("[Mock Mode] CareerAgentManager 以 Mock 模式啟動")
            self.llm = self.qa_llm = self.supabase = self.handler_registry = None
            return

        from crewai import LLM
        # 使用 OpenAI 模型
        self.llm = LLM(model=model_name, temperature=temp)
        self.qa_llm = LLM(model=model_name, temperature=0.1)

        # 初始化 Supabase Client
        self.supabase = get_supabase_client()
        self.handler_registry = HandlerRegistry(self.supabase)

    # ------------------------------------------------------------------
    # 主要入口 (對齊使用者履歷與路徑判定)
    # ------------------------------------------------------------------
    def run_task(self, task_type_str: str, user_input: Dict[str, Any]) -> Dict[str, Any]:
        user_id = user_input.get("user_id")
        if not user_id:
            return {"status": "error", "message": "缺少 user_id"}

        print(f"🚀 Manager 收到請求: {task_type_str} | User ID: {user_id}")

        # 🌟 1. 初始化預設值 (確保不會噴 Missing Variable 錯誤，且預設不再是後端)
        user_input.update({
            "survey_json": "{}",
            "trait_json": "{}",
            "calculated_scores": "{}",
            "target_role": "前端工程師", # 預設改為前端，或從 DB 覆蓋
            "match_score": "0",
            "resume_json": "【系統提示：無履歷資料】"
        })
        
        real_resume_data = {}

        try:
            from src.features.analysis.calculator import CareerAnalyzer, JobMatcher
            
            # 🌟 2. 撈「屬於該用戶」的最新履歷 (解決 ID 1 後端範本錯誤)
            resume_id = user_input.get("resume_id")
            res_query = self.supabase.table("resume").select("structured_data").eq("user_id", user_id)
            
            if resume_id and str(resume_id) != "0":
                res_resp = res_query.eq("resume_id", resume_id).execute()
            else:
                res_resp = res_query.order("created_at", desc=True).limit(1).execute()

            if res_resp.data:
                real_resume_data = res_resp.data[0].get("structured_data", {})
                user_input["resume_json"] = json.dumps(res_resp.data[0], ensure_ascii=False)
                print(f"📄 成功獲取 User {user_id} 本人的履歷資料")
            else:
                print(f"⚠️ User {user_id} 查無履歷，將使用空資料分析")

            # 3. 撈問卷與心理特質
            resp = self.supabase.table("career_survey").select("questionnaire_response, personality").eq("user_id", user_id).order("completed_at", desc=True).limit(1).execute()
            
            if resp.data:
                raw_data = resp.data[0]
                survey_data = raw_data.get("questionnaire_response", {})
                personality_data = raw_data.get("personality") or {}
                
                # 重新計算六維分數
                analyzer = CareerAnalyzer(survey_data)
                analyzer.calculate_vectors()
                user_input["calculated_scores"] = json.dumps(analyzer.scores)
                
                # 獲取目標職位
                t_role = survey_data.get("module_c", {}).get("q17_target_role", "前端工程師")
                user_input["target_role"] = t_role
                user_input["match_score"] = JobMatcher.calculate_match_score(analyzer.scores, t_role)
                user_input["survey_json"] = json.dumps(survey_data, ensure_ascii=False)
                user_input["trait_json"] = json.dumps(personality_data, ensure_ascii=False)
                
                print(f"📊 目標職位設定：{t_role} | 技術分數已載入")

        except Exception as e:
            print(f"⚠️ 資料準備階段發生錯誤: {e}")

        # 🌟 4. 自動路徑判定：問卷分數與履歷內容雙重檢查
        if task_type_str == "career_analysis":
            # 檢查是否有工作經歷或專案
            has_exp = len(real_resume_data.get("work_experience", [])) > 0 or \
                      len(real_resume_data.get("experience", [])) > 0 or \
                      len(real_resume_data.get("projects", [])) > 0
            
            task_type_str = "career_analysis_experienced" if has_exp else "career_analysis_entry_level"
            print(f"➡️ 路徑識別：{'【有經驗者】' if has_exp else '【無經驗/轉職者】'}")

        # ---- Mock 模式處理 ----
        if self.mock_mode:
            return self._mock_result(task_type_str, user_input)

        # ---- 正式 CrewAI 執行 ----
        from crewai import Agent, Task, Crew, Process
        try:
            task_type = TaskType(task_type_str)
        except ValueError:
            return {"status": "error", "message": f"不支援的任務類型: {task_type_str}"}

        user_input["current_timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='milliseconds').replace("+00:00", "Z")
        user_input["report_version"] = get_next_version_number(user_id)

        config = self._get_process_config(task_type, user_input)
        if not config:
            return {"status": "error", "message": f"找不到或無法產生 task 設定: {task_type}"}

        # 建立 Agents
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

        qa_agent = Agent(
            role="資深品質控制與格式專家 (QA)",
            goal="確保最終報告內容準確，且 JSON 格式完全符合 CareerReport 定義。",
            backstory="你負責最後的整合，確保使用台灣繁體中文，且絕對不可以捏造履歷中沒出現過的經歷。",
            verbose=True,
            llm=self.qa_llm,
            allow_delegation=False
        )

        # 建立 Tasks
        crew_tasks = []
        for idx, task_cfg in enumerate(config["tasks"]):
            worker_task = Task(
                description=task_cfg["description"],
                expected_output=task_cfg["expected_output"],
                agent=worker_agents[idx]
            )
            crew_tasks.append(worker_task)

        qa_task = Task(
            description=f"審核整合所有結果，確保 user_id 為 {user_id}，並符合 {config['output_model'].__name__} 結構。",
            expected_output="結構化 JSON 報告",
            agent=qa_agent,
            context=crew_tasks,
            output_pydantic=config["output_model"]
        )

        crew = Crew(
            agents=worker_agents + [qa_agent],
            tasks=crew_tasks + [qa_task],
            process=Process.sequential,
            verbose=True
        )

        # 啟動！
        raw_result = crew.kickoff(inputs=user_input)

        # 5. 回傳並注入真實雷達圖分數
        try:
            pydantic_result = raw_result.pydantic.model_dump()

            # 🎯 最終校準：強制覆蓋雷達圖，確保 D1-D6 來自 Calculator
            try:
                real_scores = json.loads(user_input.get("calculated_scores", "{}"))
                if real_scores:
                    pydantic_result["radar_chart"] = {
                        "dimensions": [
                            {"axis": "前端開發", "score": real_scores.get("D1", real_scores.get("前端開發", 0.0))},
                            {"axis": "後端開發", "score": real_scores.get("D2", real_scores.get("後端開發", 0.0))},
                            {"axis": "運維部署", "score": real_scores.get("D3", real_scores.get("運維部署", 0.0))},
                            {"axis": "AI與數據", "score": real_scores.get("D4", real_scores.get("AI與數據", 0.0))},
                            {"axis": "工程品質", "score": real_scores.get("D5", real_scores.get("工程品質", 0.0))},
                            {"axis": "軟實力", "score": real_scores.get("D6", real_scores.get("軟實力", 0.0))}
                        ]
                    }
                    print("🎯 已強制同步計算機的真實分數到雷達圖")
            except Exception as e:
                print(f"⚠️ 雷達圖校準失敗: {e}")

            # 自動回存資料庫
            try:
                handler = self.handler_registry.get_handler(task_type)
                if handler:
                    handler.process(pydantic_result, **user_input)
                    print(f"✅ 分析報告已存入資料庫")
            except Exception as e:
                print(f"⚠️ 自動儲存失敗: {e}")

            return pydantic_result

        except Exception as e:
            return {"status": "partial_success", "raw": str(raw_result), "error": str(e)}

    def _get_process_config(self, task_type: TaskType, inputs: Dict[str, Any]) -> Optional[Dict]:
        from .config import get_config_by_type
        return get_config_by_type(task_type, inputs)
