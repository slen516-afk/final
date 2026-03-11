import os
import json
from datetime import datetime
from src.common.logger import setup_logger

sys_logger = setup_logger()

def task_audit_callback(task_output):
    """
    CrewAI 專屬：當某個 Task 執行完畢時，自動觸發並傳入 TaskOutput 物件
    用以儲存 Agent 的最終原始輸出，方便除錯與 Prompt 調整。
    """
    audit_folder = "logs/crewai_outputs"
    
    # 1. 自動建立資料夾
    if not os.path.exists(audit_folder):
        os.makedirs(audit_folder)
        
    audit_file = os.path.join(audit_folder, "task_audit_trail.log")
    
    try:
        # 2. 安全萃取 Agent 名稱 (防呆設計)
        agent_name = "Unknown Agent"
        if hasattr(task_output, "agent") and task_output.agent:
            if hasattr(task_output.agent, "role"):
                agent_name = task_output.agent.role
            else:
                agent_name = str(task_output.agent)

        # 3. 從 TaskOutput 萃取有價值的高維度資訊
        audit_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "agent_name": agent_name,
            "task_description": getattr(task_output, "description", "No description"),
            "final_output": getattr(task_output, "raw", str(task_output))
        }
        
        # 4. 以格式化 JSON 附加模式寫入
        with open(audit_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(audit_data, ensure_ascii=False, indent=4) + "\n" + "="*50 + "\n")
            
        sys_logger.info(f"✅ 已成功稽核 Agent [{agent_name}] 的任務輸出。")
        
    except Exception as e:
        sys_logger.error(f"CrewAI 任務存檔失敗: {e}", exc_info=True)