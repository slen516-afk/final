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
    # 針對 CrewAI 的 src 目錄進行特別處理
    # 這裡加入多種可能的路徑嘗試，確保容器內外都能對齊
    if os.path.exists(llm_service_dir) and llm_service_dir not in sys.path:
        # 加入 llm_service 目錄，這樣 'from src...' 才能運作
        sys.path.append(llm_service_dir)

# 確保 backend_dir 在最前面，以便正確引入核心模組 (如 core.supabase_client)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

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


@celery_app.task(name='analyze_resume_async')
def analyze_resume_async(file_path, job_id=None):
    """
    執行履歷 OCR 分析任務
    """
    from core.redis_client import redis_client
    from datetime import datetime, timezone
    
    try:
        # self.update_state(state='PROGRESS', meta={'msg': 'AI 正在分析履歷中...'})

        # 1. 實例化 Service 並傳入 supabase 實例
        ocr_service = ResumeOCRService(supabase_client=supabase)

        # 2. 執行處理邏輯
        raw_ocr_result = ocr_service.extract_text_from_image(file_path=file_path)

        # ==========================================
        # 🌟 3. 數據映射 (Mapping) - 同步自原本 resume_processing.py 的邏輯
        # ==========================================
        if isinstance(raw_ocr_result, str):
            try:
                raw_ocr_result = json.loads(raw_ocr_result)
            except:
                raw_ocr_result = {}
        
        # 提取子結構
        res_struct = raw_ocr_result.get("structured_data", raw_ocr_result)
        norm = raw_ocr_result.get("normalized_data", raw_ocr_result)
        contact = norm.get("contact", res_struct.get("contact", raw_ocr_result))

        # 教育背景
        raw_edu = res_struct.get("education", [])
        if isinstance(raw_edu, list):
            safe_edu = "\n".join([str(e.get("details", e.get("school", ""))) if isinstance(e, dict) else str(e) for e in raw_edu])
        else:
            safe_edu = str(raw_edu)

        # 工作經歷
        raw_exp = res_struct.get("experience", res_struct.get("work_experience", []))
        if isinstance(raw_exp, list):
            exp_list = []
            for exp in raw_exp:
                if isinstance(exp, dict):
                    title = exp.get('title', exp.get('role', ''))
                    comp = exp.get('company', '')
                    desc = exp.get('responsibilities', exp.get('description', ''))
                    exp_list.append(f"{title} - {comp}\n{desc}".strip(" -\n"))
                else:
                    exp_list.append(str(exp))
            safe_exp = "\n\n".join(exp_list)
        else:
            safe_exp = str(raw_exp)

        # 專案/作品集
        raw_projects = res_struct.get("projects", res_struct.get("portfolio", []))
        if isinstance(raw_projects, list):
            proj_list = []
            for p in raw_projects:
                if isinstance(p, dict):
                    title = p.get("title", p.get("name", ""))
                    desc = p.get("description", p.get("details", ""))
                    proj_list.append(f"{title}\n{desc}".strip(" -\n"))
                else:
                    proj_list.append(str(p))
            safe_projects = "\n\n".join(proj_list)
        else:
            safe_projects = str(raw_projects)

        # 技能
        raw_skills = norm.get("skills", res_struct.get("skills", []))
        safe_skills = ", ".join([str(s) for s in raw_skills]) if isinstance(raw_skills, list) else str(raw_skills)

        # 自傳 / 關於我
        safe_bio = res_struct.get("summary", res_struct.get("autobiography", res_struct.get("bio", res_struct.get("關於我", ""))))
        if isinstance(safe_bio, list): 
            safe_bio = "\n".join([str(b) for b in safe_bio])
        else:
            safe_bio = str(safe_bio)

        # 最終對齊前端欄位
        mapped_data = {
            "name": contact.get("name", contact.get("full_name", "")),
            "email": contact.get("email", ""),
            "phone": contact.get("phone", ""),
            "address": contact.get("location", contact.get("address", "")),
            "education": safe_edu,
            "experience": safe_exp,
            "skills": safe_skills,
            "portfolio": safe_projects,
            "autobiography": safe_bio,
            "languages": "中文(精通)", 
            "certifications": "",
            "other": res_struct.get("other", "")
        }

        # 🌟 如果有傳入 job_id，則回寫結果到 Redis
        if job_id:
            now = datetime.now(timezone.utc).isoformat()
            redis_client.hset(f"job:{job_id}", mapping={
                "status": "done",
                "result": json.dumps(mapped_data),
                "updated_at": now
            })

        return {"status": "success", "data": mapped_data}

    except Exception as e:
        print(f"Resume OCR Task Failed: {e}")
        # self.update_state(state='FAILURE', meta={'error': str(e)})
        
        if job_id:
            now = datetime.now(timezone.utc).isoformat()
            redis_client.hset(f"job:{job_id}", mapping={
                "status": "failed",
                "error": str(e),
                "updated_at": now
            })
            
        return {"status": "error", "message": str(e)}


# for test purpose, not real processing
@celery_app.task(name='test_connection')
def test_connection(user_id=None, content=None):
    return f"Worker is up and running! Received user_id: {user_id}, content: {content}"
