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
                    "tools": analyst.tools # <--- 補齊工具
                }
            ],
            "tasks": [
                {
                    "description": analysis_task.description,
                    "expected_output": analysis_task.expected_output,
                    "callback": getattr(analysis_task, "callback", None),
                    "callback": getattr(analysis_task, "callback", None)
                }
            ]
        }

    # === 2. 履歷優化 (RESUME_OPT) ===
    elif task_type == TaskType.RESUME_OPT:
        # 建立零件
        optimizer = create_optimization_strategy_consultant()
        opt_task = create_optimization_task(optimizer)

        anti_hallucination_rules = """
        
        【⚠️ 最高防造假鋼律 (CRITICAL ANTI-HALLUCINATION RULES) ⚠️】
        1. 絕對忠於原稿：你只能針對使用者「原本就有」的經歷與專案進行排版與語句優化。
        2. 嚴禁無中生有：如果使用者的 experience 為空，你的輸出就必須是空的陣列 []，絕對禁止發明 "ABC科技"、"XYZ資訊" 或任何虛構的公司與年資。
        3. 學歷神聖不可侵犯：學校名稱、科系、畢業年份請嚴格照抄原履歷，絕對不可以隨意竄改為台灣大學或其他學校。
        4. 只能針對「現有文字」進行潤飾，不可添加原本不存在的專案或技能。若違反上述規定捏造資料，將導致系統嚴重崩潰！
        """
        
        # 將緊箍咒綁定到 task 的 description 上
        opt_task.description = str(opt_task.description) + anti_hallucination_rules

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
                    "expected_output": opt_task.expected_output,
                    "callback": getattr(opt_task, "callback", None)
                }
            ]
        }
    
    return None
