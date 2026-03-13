from typing import Dict, Any, Optional
from src.core.agent_engine.task_types import TaskType
from .schemas import CareerReport
from .agents import (
    create_tech_lead_agent,
    create_psychologist_agent,
    create_career_advisor_agent,
    create_discovery_mentor_agent
)
from .tasks import (
    create_tech_verification_task,
    create_trait_analysis_task,
    create_final_report_task,
    create_discovery_mentor_task,
    create_entry_level_final_task
)
from .tools import (
    FetchResumeFromDBTool,
    CalculateTechVectorsTool,
    CalculateMatchScoreTool
)

def get_analysis_config(task_type: TaskType, inputs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    提供 Manager 呼叫的配置字典。
    透過調用 agents.py 與 tasks.py 的工廠函數來動態組裝零件。
    """
    
    # === 設定 1: 有經驗者職涯分析 ===
    if task_type == TaskType.CAREER_ANALYSIS_EXPERIENCED:
        # 初始化工具，預先將 survey_json 注入給 CalculateTechVectorsTool
        calc_tool = CalculateTechVectorsTool(survey_json_str=inputs.get('survey_json', '{}'))
        tech_tools = [FetchResumeFromDBTool(), calc_tool, CalculateMatchScoreTool()]

        # 初始化 Agent 零件
        tech_lead = create_tech_lead_agent(tools=tech_tools)
        psychologist = create_psychologist_agent()
        advisor = create_career_advisor_agent()

        # 初始化 Task 零件
        tech_task = create_tech_verification_task(tech_lead, tools=tech_tools)
        trait_task = create_trait_analysis_task(psychologist)
        final_task = create_final_report_task(advisor)

        return {
            "output_model": CareerReport,
            "qa_extra_instructions": f"""
               - **report_metadata (必須包含此物件)**: 
                 - `user_id`: 必須填入 "{inputs.get('user_id', 'unknown')}"。
                 - `timestamp`: 必須填入 "{inputs.get('current_timestamp', 'unknown')}"。
                 - `version`: 必須填入 "{inputs.get('report_version', '1.0')}"。
               - **職位與職級**:
                 - `role` 與 `actual_level` 等欄位，**必須完全匹配** Schema 描述中提供的標準清單。
            """,
            "agents": [
                {
                    "role": tech_lead.role, "goal": tech_lead.goal, "backstory": tech_lead.backstory, 
                    "tools": tech_lead.tools, "step_callback": getattr(tech_lead, "step_callback", None)
                },
                {
                    "role": psychologist.role, "goal": psychologist.goal, "backstory": psychologist.backstory, 
                    "tools": [], "step_callback": getattr(psychologist, "step_callback", None)
                },
                {
                    "role": advisor.role, "goal": advisor.goal, "backstory": advisor.backstory, 
                    "tools": [], "step_callback": getattr(advisor, "step_callback", None)
                }
            ],
            "tasks": [
                {
                    "description": tech_task.description, 
                    "expected_output": tech_task.expected_output,
                    "callback": getattr(tech_task, "callback", None),
                    "tools": getattr(tech_task, "tools", [])
                },
                {
                    "description": trait_task.description, 
                    "expected_output": trait_task.expected_output,
                    "callback": getattr(trait_task, "callback", None),
                    "tools": getattr(trait_task, "tools", [])
                },
                {
                    "description": final_task.description, 
                    "expected_output": final_task.expected_output,
                    "callback": getattr(final_task, "callback", None),
                    "tools": getattr(final_task, "tools", [])
                }
            ]
        }

    # === 設定 2: 無經驗/轉職者分析 ===
    elif task_type == TaskType.CAREER_ANALYSIS_ENTRY_LEVEL:
        # 初始化工具
        mentor_tools = [FetchResumeFromDBTool()]

        # 初始化 Agent 零件
        mentor = create_discovery_mentor_agent(tools=mentor_tools)
        psychologist = create_psychologist_agent()
        advisor = create_career_advisor_agent()

        # 初始化 Task 零件
        transition_task = create_discovery_mentor_task(mentor, tools=mentor_tools)

        # [NEW] 注入問卷與使用者 ID 參數與特質參數
        transition_task.description = transition_task.description.format(
            user_id=inputs.get("user_id", "Unknown"),
            survey_json=inputs.get("survey_json", "{}")
        )

        # 建立特質分析任務並注入參數
        trait_task = create_trait_analysis_task(psychologist)
        trait_task.description = trait_task.description.format(
            trait_json=inputs.get("trait_json", "{}")
        )
        
        final_entry_task = create_entry_level_final_task(advisor)

        return {
            "output_model": CareerReport,
            "qa_extra_instructions": f"""
               - **report_metadata (必須包含此物件)**: 
                 - `user_id`: 必須填入 "{inputs.get('user_id', 'unknown')}"。
                 - `timestamp`: 必須填入 "{inputs.get('current_timestamp', 'unknown')}"。
                 - `version`: 必須填入 "{inputs.get('report_version', '1.0')}"。
               - **職位與職級**:
                 - `role` 與 `actual_level` 等欄位，**必須完全匹配** Schema 描述中提供的標準清單。
            """,
            "agents": [
                {
                    "role": mentor.role, "goal": mentor.goal, "backstory": mentor.backstory, 
                    "tools": [], "step_callback": getattr(mentor, "step_callback", None)
                },
                {
                    "role": psychologist.role, "goal": psychologist.goal, "backstory": psychologist.backstory, 
                    "tools": [], "step_callback": getattr(psychologist, "step_callback", None)
                },
                {
                    "role": advisor.role, "goal": advisor.goal, "backstory": advisor.backstory, 
                    "tools": [], "step_callback": getattr(advisor, "step_callback", None)
                }
            ],
            "tasks": [
                {
                    "description": transition_task.description, 
                    "expected_output": transition_task.expected_output,
                    "callback": getattr(transition_task, "callback", None),
                    "tools": getattr(transition_task, "tools", [])
                },
                {
                    "description": trait_task.description, 
                    "expected_output": trait_task.expected_output,
                    "callback": getattr(trait_task, "callback", None),
                    "tools": getattr(trait_task, "tools", [])
                },
                {
                    "description": final_entry_task.description, 
                    "expected_output": final_entry_task.expected_output,
                    "callback": getattr(final_entry_task, "callback", None),
                    "tools": getattr(final_entry_task, "tools", [])
                }
            ]
        }
    
    return None
