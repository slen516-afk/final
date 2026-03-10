from typing import Dict, Any
from .agents import get_career_strategist_agent, get_learning_designer_agent
from .tasks import get_diagnostic_analysis_task, get_roadmap_design_task
from .schemas import CareerRoadmap
from src.core.agent_engine.task_types import TaskType
# 把預算好的分數跟 role 傳進 user_input 裡，所以無需 Tool。
# from src.features.projects.tools import FetchGapAnalysisTool # 專案模組已有這個 tool，可重用

def get_course_config(task_type: TaskType, inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    課程推薦模組的配置分發器。
    
    Args:
        task_type (TaskType): 任務類型，預期為 COURSE_REC。
        inputs (Dict[str, Any]): 使用者輸入，應包含 'user_id' 與 'courses' (由演算法挑出的清單)。
        
    Returns:
        Dict[str, Any]: 包含 agents, tasks, output_model 的配置字典。
    """
    
    # 1. 建立 Agents
    analyst = get_career_strategist_agent(tools=[])
    planner = get_learning_designer_agent()
    
    # 2. 建立 Tasks
    # 這個 format 會把 input dictionary 裡面的變數替換進 description 裡，
    # 但 CrewAI 在 task.description 裡面如果有 {user_id} 或 {courses}，kickoff 時會自動 mapping inputs 裡的值。
    # 為了確保明確，我們可以在這邊設定或是讓 crewai 自己吃 inputs。
    # Task 建立時 description 會包含這些 placeholder。
    
    diagnostic_task = get_diagnostic_analysis_task(analyst)
    # Planner 任務會獲取診斷任務的結果作為上下文
    roadmap_task = get_roadmap_design_task(planner, [diagnostic_task])
    
    return {
        "agents": [
            {"role": analyst.role, "goal": analyst.goal, "backstory": analyst.backstory, "tools": []},
            {"role": planner.role, "goal": planner.goal, "backstory": planner.backstory, "tools": []}
        ],
        "tasks": [
            {
                "description": diagnostic_task.description, 
                "expected_output": diagnostic_task.expected_output,
                "callback": getattr(diagnostic_task, "callback", None)
            },
            {
                "description": roadmap_task.description, 
                "expected_output": roadmap_task.expected_output,
                "callback": getattr(roadmap_task, "callback", None)
            }
        ],
        "output_model": CareerRoadmap
    }
