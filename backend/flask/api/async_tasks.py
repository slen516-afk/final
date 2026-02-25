from flask import Blueprint, request, jsonify
from worker.tasks import analyze_resume_async

api_bp = Blueprint('api', __name__)

@api_bp.route('/submit', methods=['POST'])
def submit_task():
    content = request.json.get('content')
    user_id = request.json.get('user_id', 'guest')
    # 使用 .delay() 將任務發送到 Redis，這會立即回傳
    task = analyze_resume_async.delay(user_id, content)
    return jsonify({"task_id": task.id}), 202

@api_bp.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    task_result = analyze_resume_async.AsyncResult(task_id)
    response = {
        "state": task_result.state,
        "result": task_result.result if task_result.ready() else None
    }
    return jsonify(response)