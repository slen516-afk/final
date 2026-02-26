from typing import Dict, Any, Optional
from src.core.agent_engine.task_types import TaskType
from .schemas import ResumeAnalysis, ResumeOptimization
from .agents import create_analysis_consultant, create_optimization_strategy_consultant
from .tasks import create_analysis_task, create_optimization_task

def get_resume_config(task_type: TaskType, inputs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    獲取履歷模組的配置。
    透過組裝來自 agents.py 與 tasks.py 的零件，實現單一事實來源。
    """
    
    # === 1. 履歷分析 (RESUME_ANALYSIS) ===
    if task_type == TaskType.RESUME_ANALYSIS:
        # 建立零件
        analyst = create_analysis_consultant()
        analysis_task = create_analysis_task(analyst)

        return {
            "output_model": ResumeAnalysis,
            "agents": [
                {
                    "role": analyst.role,
                    "goal": analyst.goal,
                    "backstory": analyst.backstory,
                    "tools": []
                }
            ],
            "tasks": [
                {
                    "description": analysis_task.description,
                    "expected_output": analysis_task.expected_output
                }
            ]
        }

    # === 2. 履歷優化 (RESUME_OPTIMIZATION) ===
    elif task_type == TaskType.RESUME_OPT:
        # 建立零件
        optimizer = create_optimization_strategy_consultant()
        opt_task = create_optimization_task(optimizer)

        return {
            "output_model": ResumeOptimization,
            "agents": [
                {
                    "role": optimizer.role,
                    "goal": optimizer.goal,
                    "backstory": optimizer.backstory,
                    "tools": []
                }
            ],
            "tasks": [
                {
                    "description": opt_task.description,
                    "expected_output": opt_task.expected_output
                }
            ]
        }
    
    return None
