import os
import json
from .celery_app import celery_app
from core.supabase_client import supabase
import time
from qdrant_client import QdrantClient
# To import llm service
# from service.llm_service.src.core import CareerAgentManager  > manager.py # crewai_engine related process
# from service.llm_service.src.features.matching import CareerMatchingService >service.py # matching related process
# from service.llm_service.src.features.course import CourseRecommendationService >course_matching.py # course recommendation related process


# 初始化常駐客戶端
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# --- Service Tasks ---
@celery_app.task(name='process_career_analysis')
def process_career_analysis(user_id: str, survey_json: str):
    """
    執行 CrewAI 職涯分析任務 (Manager.py 邏輯)
    """
    try:
        manager = CareerAgentManager(model_name="o3-mini")
        user_input = {"survey_json": survey_json}
        
        # 執行 CrewAI 流程
        result = manager.run_task(
            task_type_str="career_analysis", 
            user_id=user_id, 
            user_input=user_input
        )
        
        return result
    except Exception as e:
        print(f" Career Analysis Task Failed: {e}")
        return {"status": "error", "message": str(e)}


@celery_app.task(name='process_job_matching')
def process_job_matching(user_id: int, filters: dict, user_6d_profile: dict):
    """
    執行職缺匹配任務 (Service.py 邏輯)
    """
    try:
        matching_service = CareerMatchingService(
            qdrant_client=qdrant_client,
            supabase_client=supabase,
            openai_api_key=OPENAI_API_KEY
        )
        
        # 執行三階段匹配流程
        best_jobs = matching_service.find_best_jobs(
            user_id=user_id,
            filters=filters,
            user_6d_profile=user_6d_profile
        )
        
        return {"status": "success", "jobs": best_jobs}
    except Exception as e:
        print(f" Job Matching Task Failed: {e}")
        return {"status": "error", "message": str(e)}


@celery_app.task(name='process_course_recommendation')
def process_course_recommendation(user_id: str, top_k: int = 5):
    """
    執行課程推薦任務 (Course_matching.py 邏輯)
    """
    try:
        # 傳入 supabase 實例
        course_service = CourseRecommendationService(supabase_client=supabase)
        
        # 獲取推薦結果
        recommendations = course_service.get_recommendations(user_id=user_id, top_k=top_k)
        
        return recommendations
    except Exception as e:
        print(f"Course Recommendation Task Failed: {e}")
        return {"status": "error", "message": str(e)}


# for test purpose, not real processing
@celery_app.task(name='test_connection')
def test_connection(user_id=None, content=None):
    return f"Worker is up and running! Received user_id: {user_id}, content: {content}"

@celery_app.task(name='analyze_resume_async', bind=True)
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