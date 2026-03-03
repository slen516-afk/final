from flask import Blueprint, request, jsonify, g
from api.auth import login_required
from worker.tasks import (
    process_career_analysis,
    process_job_matching,
    process_course_recommendation,
    analyze_resume_async,
    test_connection
)
from celery.result import AsyncResult

api_bp = Blueprint('api', __name__)

# 任務map，如需擴充由此添加
TASK_MAP = {
    "career_analysis": process_career_analysis,
    "job_matching": process_job_matching,
    "course_recommendation": process_course_recommendation,
    "resume_ocr": analyze_resume_async,  # 對應你提到的 OCR/分析任務
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
            task = task_func.delay(user_id, payload.get('survey_json'))
            
        elif task_type == "job_matching":
            # 參數: user_id: int, filters: dict, user_6d_profile: dict
            task = task_func.delay(user_id, payload.get('filters'), payload.get('user_6d_profile'))
            
        elif task_type == "course_recommendation":
            # 參數: user_id: str, top_k: int
            task = task_func.delay(user_id, payload.get('top_k', 5))
            
        elif task_type == "resume_ocr":
            # 參數: user_id, resume_content
            task = task_func.delay(user_id, payload.get('resume_content'))
            
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