import json
import uuid
from datetime import datetime, timezone

from flask import Blueprint, request, jsonify, g
from api.auth import login_required
from core.redis_client import (
    redis_client,
    STREAM_NAME,
    MAX_RETRY,
)

analysis_bp = Blueprint("analysis", __name__)

VALID_TASK_TYPES = {"resume_analysis", "resume_opt"}


def _create_celery_job(user_id: str, task_type: str = "resume_analysis") -> str:
    """
    將分析任務提交給 Celery 進行非同步處理。
    """
    from worker.tasks import process_resume_analysis, process_resume_optimization
    
    job_id = f"job_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()

    # 1. 在 Redis 紀錄 Job 初始狀態
    redis_client.hset(f"job:{job_id}", mapping={
        "status": "processing",
        "user_id": user_id,
        "task_type": task_type,
        "result": "",
        "suggestions": "",
        "error": "",
        "created_at": now,
        "updated_at": now,
    })

    # 2. 依據類型觸發對應的 Celery 任務
    if task_type == "resume_opt":
        process_resume_optimization.delay(user_id, job_id)
    else:
        process_resume_analysis.delay(user_id, job_id)

    return job_id


def _get_job(job_id: str) -> dict | None:
    data = redis_client.hgetall(f"job:{job_id}")
    return data if data else None



# D-01 建立分析任務
@analysis_bp.route("/tasks", methods=["POST"])
@login_required
def start_analysis_task():
    try:
        db_user_id = g.db_user_id
        if db_user_id is None:
            return jsonify({'error': 'User not found in DB'}), 403

        data = request.json

        task_type = data.get("task_type", "resume_analysis")
        if task_type not in VALID_TASK_TYPES:
            return jsonify({"error": f"Unsupported task_type: {task_type}. 支援: {', '.join(VALID_TASK_TYPES)}"}), 400

        job_id = _create_celery_job(db_user_id, task_type)

        return jsonify({
            "job_id": job_id,
            "status": "processing",
        }), 202

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# D-02  前端輪詢進度
@analysis_bp.route("/jobs/<job_id>", methods=["GET"])
@login_required
def poll_job(job_id):
    job = _get_job(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    resp = {
        "job_id": job_id,
        "status": job["status"],
        "created_at": job.get("created_at", ""),
        "updated_at": job.get("updated_at", ""),
    }

    if job["status"] == "done":
        raw_result = job.get("result")
        if raw_result:
            try:
                parsed = json.loads(raw_result)
                resp["result"] = parsed
                # 如果 suggestions 沒獨立存，嘗試從 result 裡面抓
                resp["suggestions"] = json.loads(job.get("suggestions")) if job.get("suggestions") else parsed.get("suggestions", None)
            except:
                resp["result"] = raw_result
        else:
            resp["result"] = None
    elif job["status"] == "failed" or job["status"] == "dlq":
        resp["error"] = job.get("error", "")

    return jsonify(resp), 200
