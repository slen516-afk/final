import os
import sys
import json
from .celery_app import celery_app
import time

# ── 路徑初始化 ────────────────────────────────────────────────────
# current_dir  = backend/flask/worker/
# flask_dir    = backend/flask/
# backend_dir  = backend/
current_dir = os.path.dirname(os.path.abspath(__file__))
flask_dir   = os.path.abspath(os.path.join(current_dir, ".."))
backend_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))

for p in [flask_dir, backend_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

# 🌟 把 llm_service 與 src 加入系統路徑
llm_service_dir = os.path.join(backend_dir, "service", "llm_service")
if os.path.exists(llm_service_dir):
    if llm_service_dir not in sys.path:
        sys.path.insert(0, llm_service_dir)
    
    # 針對 CrewAI 的 src 目錄進行特別處理
    # 這裡加入多種可能的路徑嘗試，確保容器內外都能對齊
    llm_src_dir = os.path.join(llm_service_dir, "src")
    if os.path.exists(llm_src_dir) and llm_src_dir not in sys.path:
        sys.path.insert(0, llm_src_dir)

# 嘗試處理從 src 開頭的絕對引入問題
try:
    import src.core.agent_engine.manager
except ImportError:
    # 如果失敗，嘗試將 llm_service/src 加入路徑的最前端
    llm_src_dir = os.path.join(backend_dir, "service", "llm_service", "src")
    if llm_src_dir not in sys.path:
        sys.path.insert(0, llm_src_dir)

from qdrant_client import QdrantClient
from core.supabase_client import supabase

from src.core.agent_engine.manager import CareerAgentManager  # crewai_engine related process
from src.features.matching.service import CareerMatchingService  # matching related process
from src.features.course.course_matching import CourseRecommendationService  # course recommendation related process

from service.ocr_service.ocr_service import ResumeOCRService

# 初始化常駐客戶端
QDRANT_HOST    = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT    = int(os.getenv("QDRANT_PORT", 6333))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)


# --- Service Tasks ---

@celery_app.task(name='process_career_analysis')
def process_career_analysis(user_id: str, survey_json: str, job_id: str = None):
    """
    執行 CrewAI 職涯分析任務 (Manager.py 邏輯)
    """
    from core.redis_client import redis_client
    from datetime import datetime, timezone

    try:
        manager = CareerAgentManager(model_name="gpt-4o")
        user_input = {"user_id": user_id, "survey_json": survey_json}

        # 執行 CrewAI 流程
        result = manager.run_task(
            task_type_str="career_analysis",
            user_input=user_input
        )

        # 🌟 如果有傳入 job_id，則回寫結果到 Redis
        if job_id:
            now = datetime.now(timezone.utc).isoformat()
            redis_client.hset(f"job:{job_id}", mapping={
                "status": "done",
                "result": json.dumps(result),
                "updated_at": now
            })

        return result
    except Exception as e:
        print(f" Career Analysis Task Failed: {e}")
        if job_id:
            now = datetime.now(timezone.utc).isoformat()
            redis_client.hset(f"job:{job_id}", mapping={
                "status": "failed",
                "error": str(e),
                "updated_at": now
            })
        return {"status": "error", "message": str(e)}


@celery_app.task(name='process_resume_analysis')
def process_resume_analysis(user_id: str, job_id: str = None):
    """
    執行履歷分析任務 (Manager.py 邏輯)
    """
    from core.redis_client import redis_client
    from datetime import datetime, timezone

    try:
        manager = CareerAgentManager(model_name="gpt-4o")
        user_input = {"user_id": user_id}

        result = manager.run_task(
            task_type_str="resume_analysis",
            user_input=user_input
        )

        if job_id:
            now = datetime.now(timezone.utc).isoformat()
            redis_client.hset(f"job:{job_id}", mapping={
                "status": "done",
                "result": json.dumps(result),
                "updated_at": now
            })

        return result
    except Exception as e:
        print(f" Resume Analysis Task Failed: {e}")
        if job_id:
            now = datetime.now(timezone.utc).isoformat()
            redis_client.hset(f"job:{job_id}", mapping={
                "status": "failed",
                "error": str(e),
                "updated_at": now
            })
        return {"status": "error", "message": str(e)}


@celery_app.task(name='process_resume_optimization')
def process_resume_optimization(user_id: str, job_id: str = None):
    """
    執行履歷優化任務 (Manager.py 邏輯)
    """
    from core.redis_client import redis_client
    from datetime import datetime, timezone

    try:
        manager = CareerAgentManager(model_name="gpt-4o")
        user_input = {"user_id": user_id}

        result = manager.run_task(
            task_type_str="resume_opt",
            user_input=user_input
        )

        if job_id:
            now = datetime.now(timezone.utc).isoformat()
            redis_client.hset(f"job:{job_id}", mapping={
                "status": "done",
                "result": json.dumps(result),
                "updated_at": now
            })

        return result
    except Exception as e:
        print(f" Resume Optimization Task Failed: {e}")
        if job_id:
            now = datetime.now(timezone.utc).isoformat()
            redis_client.hset(f"job:{job_id}", mapping={
                "status": "failed",
                "error": str(e),
                "updated_at": now
            })
        return {"status": "error", "message": str(e)}


@celery_app.task(name='process_project_recommendation')
def process_project_recommendation(user_id: str, job_id: str = None):
    """
    執行專案推薦任務 (Manager.py 邏輯)
    """
    from core.redis_client import redis_client
    from datetime import datetime, timezone

    try:
        manager = CareerAgentManager(model_name="gpt-4o")
        # 專案推薦通常需要缺口分析結果，Manager 的工具會自己去抓
        user_input = {"user_id": user_id}

        result = manager.run_task(
            task_type_str="project_rec",
            user_input=user_input
        )

        if job_id:
            now = datetime.now(timezone.utc).isoformat()
            redis_client.hset(f"job:{job_id}", mapping={
                "status": "done",
                "result": json.dumps(result),
                "updated_at": now
            })

        return result
    except Exception as e:
        print(f" Project Recommendation Task Failed: {e}")
        if job_id:
            now = datetime.now(timezone.utc).isoformat()
            redis_client.hset(f"job:{job_id}", mapping={
                "status": "failed",
                "error": str(e),
                "updated_at": now
            })
        return {"status": "error", "message": str(e)}


@celery_app.task(name='process_cover_letter')
def process_cover_letter(user_id: int, job_id: str, optimization_id: str, resume_id: str, tracking_id: str = None):
    """
    執行 CrewAI 求職信生成任務 (Manager.py 邏輯)
    """
    from core.redis_client import redis_client
    from datetime import datetime, timezone

    try:
        manager = CareerAgentManager(model_name="gpt-4o")

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

        if tracking_id:
            now = datetime.now(timezone.utc).isoformat()
            redis_client.hset(f"job:{tracking_id}", mapping={
                "status": "done",
                "result": json.dumps(result),
                "updated_at": now
            })

        return result
    except Exception as e:
        print(f"Cover Letter Task Failed: {e}")
        if tracking_id:
            now = datetime.now(timezone.utc).isoformat()
            redis_client.hset(f"job:{tracking_id}", mapping={
                "status": "failed",
                "error": str(e),
                "updated_at": now
            })
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


# for test purpose, not real processing
@celery_app.task(name='test_connection')
def test_connection(user_id=None, content=None):
    return f"Worker is up and running! Received user_id: {user_id}, content: {content}"
