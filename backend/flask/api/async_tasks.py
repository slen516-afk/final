from flask import Blueprint, request, jsonify, g
from api.auth import login_required
from worker.tasks import (
    process_career_analysis,
    process_job_matching,
    process_course_recommendation,
    analyze_resume_async,
    test_connection,
    process_cover_letter,
    process_resume_analysis,
    process_resume_optimization,
    process_project_recommendation
)
from celery.result import AsyncResult

api_bp = Blueprint('api', __name__)

# 任務map，如需擴充由此添加
TASK_MAP = {
    "career_analysis": process_career_analysis,
    "resume_analysis": process_resume_analysis,
    "resume_opt": process_resume_optimization,
    "project_rec": process_project_recommendation,
    "job_matching": process_job_matching,
    "course_recommendation": process_course_recommendation,
    "resume_ocr": analyze_resume_async,  
    "cover_letter": process_cover_letter,
    "test": test_connection
}

@api_bp.route('/submit', methods=['POST'])
@login_required
def submit_task():
    data = request.json
    task_type = data.get('task_type', 'test')
    payload = data.get('payload', {})
    
    # 使用由token解析出的user_id
    user_id = g.user_id
    if task_type not in TASK_MAP:
        return jsonify({"error": "無效的任務類型"}), 400

    # 根據 tasks.py 的參數定義進行派發
    task_func = TASK_MAP[task_type]
    
    try:
        
        if task_type == "career_analysis":
            # 參數: user_id: str, survey_json: str
            task = task_func.delay(str(user_id), payload.get('survey_json'))
            
        elif task_type in ["resume_analysis", "resume_opt", "project_rec"]:
            # 外部 LLM 分析模型任務參數: user_id: str
            task = task_func.delay(str(user_id))
            
        elif task_type == "job_matching":
            # 參數: user_id: int, filters: dict, document_id: int, source_type: str
            task = task_func.delay(user_id, payload.get('filters'), payload.get('document_id'), payload.get('source_type'))
            
        elif task_type == "course_recommendation":
            # 參數: user_id: str, top_k: int
            task = task_func.delay(user_id, payload.get('top_k', 5))
            
        elif task_type == "resume_ocr":
            # 參數: file_path 
            task = task_func.delay(payload.get('file_path'))
            
        elif task_type == "cover_letter":
            # 參數: user_id: int, job_id: str, optimization_id: str, resume_id: str
            task = task_func.delay(
                user_id,
                payload.get('job_id'),
                payload.get('optimization_id'),
                payload.get('resume_id')
            )
            
        else:
            task = task_func.delay(user_id, payload.get('content'))

        return jsonify({
            "task_id": task.id,
            "task_type": task_type,
            "status": "Task queued"
        }), 202
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/status/<task_id>', methods=['GET'])
@login_required
def get_status(task_id):
    task_result = AsyncResult(task_id)
    response = {
        "task_id": task_id,
        "state": task_result.state,
        "result": task_result.result if task_result.ready() else None
    }
    if task_result.state == 'PROGRESS' and isinstance(task_result.info, dict):
        response["message"] = task_result.info.get('msg', '處理中...')
    
    return jsonify(response)