import os
import sys
import json
from .celery_app import celery_app
from core.supabase_client import supabase
import time
from qdrant_client import QdrantClient
# 引入llm service 路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from service.llm_service.src.core.agent_engine.manager import CareerAgentManager  # crewai_engine related process
from service.llm_service.src.features.matching.service import CareerMatchingService # matching related process
from service.llm_service.src.features.course.course_matching import CourseRecommendationService  # course recommendation related process

from service.ocr_service.ocr_service import ResumeOCRService
service = ResumeOCRService(device="cpu")

# 初始化常駐客戶端
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY","")

qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# --- Service Tasks ---
@celery_app.task(name='process_career_analysis')
def process_career_analysis(user_id: str, survey_json: str):
    """
    執行 CrewAI 職涯分析任務 (Manager.py 邏輯)
    """
    try:
        manager = CareerAgentManager(model_name="o3-mini")
        user_input = {"user_id": user_id,"survey_json": survey_json}
        
        # 執行 CrewAI 流程
        result = manager.run_task(
            task_type_str="career_analysis", 
            user_input=user_input
        )
        
        return result
    except Exception as e:
        print(f" Career Analysis Task Failed: {e}")
        return {"status": "error", "message": str(e)}


@celery_app.task(name='process_job_matching')
def process_job_matching(user_id: int, filters: dict, document_id: int, source_type: str):
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
            document_id=document_id,
            source_type=source_type,
            filters=filters
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

@celery_app.task(name='analyze_resume_async', bind=True)
def analyze_resume_async(self, file_path):
    """
    執行履歷 OCR 分析任務
    """
    try:
        self.update_state(state='PROGRESS', meta={'msg': 'AI 正在分析履歷中...'})
        
        # 1. 實例化 Service 並傳入 supabase 實例
        ocr_service = ResumeOCRService(supabase_client=supabase)
        
        # 2. 執行處理邏輯
        result = ocr_service.extract_text_from_image(file_path=file_path)
        
        return {"status": "success", "data": result}
        
    except Exception as e:
        print(f"Resume OCR Task Failed: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        return {"status": "error", "message": str(e)}

@celery_app.task(name='process_cover_letter')
def process_cover_letter(user_id: int, job_id: str, optimization_id: str, resume_id: str):
    """
    執行 CrewAI 求職信生成任務 (Manager.py 邏輯)
    """
    try:
        manager = CareerAgentManager(model_name="o3-mini")
        
        # 根據文件，如果選擇優化履歷則 resume_id 為空字串，如果選擇原始履歷則 optimization_id 為空字串
        user_input = {
            "user_id": user_id,
            "job_id": job_id,
            "optimization_id": optimization_id,
            "resume_id": resume_id
        }
        
        # 執行 CrewAI 流程
        result = manager.run_task(
            task_type_str="cover_letter", 
            user_input=user_input
        )
        
        return result
    except Exception as e:
        print(f"Cover Letter Task Failed: {e}")
        return {"status": "error", "message": str(e)}

# for test purpose, not real processing
@celery_app.task(name='test_connection')
def test_connection(user_id=None, content=None):
    return f"Worker is up and running! Received user_id: {user_id}, content: {content}"

