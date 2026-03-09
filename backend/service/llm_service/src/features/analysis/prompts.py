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
from .tools import FetchResumeFromDBTool, CalculateTechVectorsTool, CalculateMatchScoreTool

def get_analysis_config(task_type: Any, inputs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    type_key = str(task_type).upper()
    print(f"🔍 [Debug] Prompts 收到匹配鍵: {type_key}")

    # 🌟 確保這裡只有變數，沒有任何「後端」範例文字！
    resume_json = inputs.get("resume_json", "【無履歷資料】")
    
    authority_prompt = f"""
    【📄 使用者真實履歷原文（最高權威基準）】
    {resume_json}

    【核心指令】
    請分析上述履歷。如果履歷中充滿 Vue, Nuxt, CSS，你必須認定他是「前端」人才。
    絕對不要參考任何外部範例或假設使用者是後端工程師。
    """

    # === 模式 A: 有經驗者 ===
    if "EXPERIENCED" in type_key:
        calc_tool = CalculateTechVectorsTool(survey_json_str=inputs.get('survey_json', '{}'))
        tech_tools = [FetchResumeFromDBTool(), calc_tool, CalculateMatchScoreTool()]
        
        a1, a2, a3 = create_tech_lead_agent(tools=tech_tools), create_psychologist_agent(), create_career_advisor_agent()
        t1, t2, t3 = create_tech_verification_task(a1, tools=tech_tools), create_trait_analysis_task(a2), create_final_report_task(a3)

        t1.description = str(t1.description) + authority_prompt
        return {
            "output_model": CareerReport,
            "qa_extra_instructions": f"user_id: {inputs.get('user_id')}",
            "agents": [
                {"role": a1.role, "goal": a1.goal, "backstory": a1.backstory, "tools": a1.tools},
                {"role": a2.role, "goal": a2.goal, "backstory": a2.backstory, "tools": []},
                {"role": a3.role, "goal": a3.goal, "backstory": a3.backstory, "tools": []}
            ],
            "tasks": [
                {"description": t1.description, "expected_output": t1.expected_output},
                {"description": t2.description, "expected_output": t2.expected_output},
                {"description": t3.description, "expected_output": t3.expected_output}
            ]
        }

    # === 模式 B: 轉職者 (就算誤判進來也要能動) ===
    elif "ENTRY_LEVEL" in type_key:
        mentor_tools = [FetchResumeFromDBTool()]
        a_m, a_a = create_discovery_mentor_agent(tools=mentor_tools), create_career_advisor_agent()
        t_t = create_discovery_mentor_task(a_m, tools=mentor_tools)
        
        # 🌟 安全替換法：直接拿建立好的描述來改
        new_desc = str(t_t.description).replace("{user_id}", str(inputs.get("user_id", "Unknown")))
        new_desc = new_desc.replace("{survey_json}", str(inputs.get("survey_json", "{}")))
        new_desc = new_desc.replace("{trait_json}", str(inputs.get("trait_json", "{}")))
        
        t_t.description = new_desc + authority_prompt
        t_f = create_entry_level_final_task(a_a)

        return {
            "output_model": CareerReport,
            "qa_extra_instructions": f"user_id: {inputs.get('user_id')}",
            "agents": [
                {"role": a_m.role, "goal": a_m.goal, "backstory": a_m.backstory, "tools": a_m.tools},
                {"role": a_a.role, "goal": a_a.goal, "backstory": a_a.backstory, "tools": []}
            ],
            "tasks": [
                {"description": t_t.description, "expected_output": t_t.expected_output},
                {"description": t_f.description, "expected_output": t_f.expected_output}
            ]
        }
    return None