from typing import Dict, Any
from .agents import get_cover_letter_strategist_agent
from .tasks import get_cover_letter_task
from .tools import RecommendJobSearchTool, FetchOptimizeResumeTool
from .schemas import CoverLetter
from src.core.agent_engine.task_types import TaskType

def get_cover_letter_config(task_type: TaskType, inputs: Dict[str, Any]) -> Dict[Any, Any]:
    """
    求職信生成模組的配置分發器。
    
    Args:
        task_type (TaskType): 任務類型，預期為 COVER_LETTER。
        inputs (Dict[str, Any]): 包含 'optimize_resume' 與 'job_id'。
        
    Returns:
        Dict[str, Any]: 包含 agents, tasks, output_model。
    """
    
    # 1. 初始化工具
    job_search_tool = RecommendJobSearchTool()
    resume_fetch_tool = FetchOptimizeResumeTool()
    
    # 工具列表
    cover_letter_tools = [job_search_tool, resume_fetch_tool]
    
    # 2. 初始化 Agent
    strategist = get_cover_letter_strategist_agent()
    
    # 3. 初始化 Task
    # 注意：tools 需以 list 傳入，供 manager.py 正確分發給 Agent
    cl_task = get_cover_letter_task(strategist, cover_letter_tools)
    
    return {
        "agents": [
            {
                "role": strategist.role, 
                "goal": strategist.goal, 
                "backstory": strategist.backstory, 
                "tools": cover_letter_tools
            }
        ],
        "tasks": [
            {"description": cl_task.description, "expected_output": cl_task.expected_output}
        ],
        "output_model": CoverLetter
    }
