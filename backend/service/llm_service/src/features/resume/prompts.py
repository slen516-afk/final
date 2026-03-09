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
    
    # 🌟 提取我們在 manager.py 算好的神兵利器 (預設值防呆)
    calculated_scores = inputs.get("calculated_scores", "無資料")
    match_score = inputs.get("match_score", "無資料")
    target_role = inputs.get("target_role", "未指定")
    
    # 🌟 準備要強勢塞給 AI 的系統量化數據模板
    system_metrics_prompt = f"""
    
    【⚠️ 系統量化評估數據（非常重要，請務必以此為基準進行分析與優化）】
    1. 使用者的目標職位：{target_role}
    2. 客觀計算出的六維雷達圖分數 (滿分5.0)：{calculated_scores}
    3. 系統判定他與目標職位的契合度：{match_score}

    【額外目標對齊指令】
    請務必將上述的「目標職位」與「六維雷達圖分數」納入考量：
    - 如果是「履歷診斷」，請明確指出目前的履歷經歷，是否足以支撐他應徵「{target_role}」，並指出缺乏的關鍵字。
    - 如果是「履歷優化」，請刻意針對「{target_role}」所需的核心技能，重新包裝他的經歷，並淡化不相關的雜訊。
    """

    # === 1. 履歷分析 (RESUME_ANALYSIS) ===
    if task_type == TaskType.RESUME_ANALYSIS:
        # 建立零件
        analyst = create_analysis_consultant()
        analysis_task = create_analysis_task(analyst)

        # 🌟 【關鍵修改】：將量化數據直接外掛到分析任務的描述中！
        analysis_task.description += system_metrics_prompt

        return {
            "output_model": ResumeAnalysis,
            "agents": [
                {
                    "role": analyst.role,
                    "goal": analyst.goal,
                    "backstory": analyst.backstory,
                    "tools": analyst.tools # <--- 補齊工具
                }
            ],
            "tasks": [
                {
                    "description": analysis_task.description,
                    "expected_output": analysis_task.expected_output
                }
            ]
        }

    # === 2. 履歷優化 (RESUME_OPT) ===
    elif task_type == TaskType.RESUME_OPT:
        # 建立零件
        optimizer = create_optimization_strategy_consultant()
        opt_task = create_optimization_task(optimizer)

        # 🌟 【關鍵修改】：將量化數據直接外掛到優化任務的描述中！
        opt_task.description += system_metrics_prompt

        return {
            "output_model": ResumeOptimization,
            "agents": [
                {
                    "role": optimizer.role,
                    "goal": optimizer.goal,
                    "backstory": optimizer.backstory,
                    "tools": optimizer.tools # <--- 補齊工具
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