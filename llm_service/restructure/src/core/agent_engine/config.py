from typing import Dict, Any, Optional
from .task_types import TaskType

# ===============
# 配置分發器 (Configuration Dispatcher)
# ===============
def get_config_by_type(task_type: TaskType, inputs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    
    # 根據 TaskType 路由到對應的 Feature 模組配置
    
    # 1. 職涯分析相關 (Experienced & Entry Level)
    if task_type in [TaskType.CAREER_ANALYSIS_EXPERIENCED, TaskType.CAREER_ANALYSIS_ENTRY_LEVEL]:
        from src.features.analysis.prompts import get_analysis_config
        return get_analysis_config(task_type, inputs)
    
    # 2. 履歷相關 (Critique & Generation)
    elif task_type in [TaskType.RESUME_ANALYSIS, TaskType.RESUME_OPT]:
        from src.features.resume.prompts import get_resume_config
        return get_resume_config(task_type, inputs)

    # 3. Side Project 推薦 (Recommendation)
    elif task_type == TaskType.PROJECT_REC:
        from src.features.projects.prompts import get_project_config
        return get_project_config(task_type, inputs)

    # 4. 求職信生成 (Cover Letter)
    elif task_type == TaskType.COVER_LETTER:
        from src.features.cover_letter.prompts import get_cover_letter_config
        return get_cover_letter_config(task_type, inputs)

    return None
