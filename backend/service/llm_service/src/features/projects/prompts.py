from typing import Dict, Any
from .agents import get_project_architect_agent, get_industry_qa_agent
from .tasks import get_project_design_task, get_project_refinement_task
from .schemas import SideProject
from .tools import FetchGapAnalysisTool
from src.core.agent_engine.task_types import TaskType

def get_project_config(task_type: TaskType, inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Side Project 推薦模組的配置分發器。
    
    Args:
        task_type (TaskType): 任務類型，預期為 PROJECT_REC。
        inputs (Dict[str, Any]): 使用者輸入，應包含 'user_id'。
        
    Returns:
        Dict[str, Any]: 包含 agents, tasks, output_model 的配置字典。
    """
    
    # 初始化工具
    architect_tools = [FetchGapAnalysisTool()]

    # 1. 建立 Agents
    architect = get_project_architect_agent(tools=architect_tools)
    qa_expert = get_industry_qa_agent()
    
    # 2. 建立 Tasks
    design_task = get_project_design_task(architect, tools=architect_tools)
    # QA 任務會獲取設計任務的結果作為上下文
    refinement_task = get_project_refinement_task(qa_expert, [design_task])
    
    return {
        "agents": [
            {"role": architect.role, "goal": architect.goal, "backstory": architect.backstory, "tools": architect_tools},
            {"role": qa_expert.role, "goal": qa_expert.goal, "backstory": qa_expert.backstory}
        ],
        "tasks": [
            {"description": design_task.description, "expected_output": design_task.expected_output},
            {"description": refinement_task.description, "expected_output": refinement_task.expected_output}
        ],
        "output_model": SideProject
    }

