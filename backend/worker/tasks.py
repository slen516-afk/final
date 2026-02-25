from .celery_app import celery_app
from core.supabase_client import supabase
import time

@celery_app.task(bind=True)
# 待寫入實際工作邏輯
# for test purpose, not real processing
def analyze_resume_async(self, user_id, resume_content):
    """
    非同步處理：AI 分析履歷並寫入 Supabase
    """
    try:
        self.update_state(state='PROGRESS', meta={'msg': 'AI 正在分析中...'})
        
        # 1. 模擬調用 AI 模型 (例如 GPT-4)
        time.sleep(5) 
        analysis_result = f"分析報告：針對用戶 {user_id} 的履歷建議..."
        
        # 2. 寫入 Supabase
        data = {
            "user_id": user_id,
            "report": analysis_result,
            "status": "completed"
        }
        response = supabase.table("analysis_reports").insert(data).execute()
        
        return {"status": "success", "db_id": response.data[0]['id']}
        
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise e