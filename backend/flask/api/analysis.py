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


def _create_job(user_id: str, task_type: str = "resume_analysis") -> str:
    # 建立job hash 在 Redis 並 XADD 到 stream
    job_id = f"job_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()

    mapping = {
        "status": "queued",
        "user_id": user_id,
        "task_type": task_type,
        "result": "",
        "suggestions": "",
        "error": "",
        "retry_count": "0",
        "created_at": now,
        "updated_at": now,
    }

    redis_client.hset(f"job:{job_id}", mapping=mapping)

    # XADD 到 cv_jobs stream
    redis_client.xadd(STREAM_NAME, {
        "job_id": job_id,
        "task_type": task_type,
        "retry_count": "0",
    })

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

        job_id = _create_job(db_user_id, task_type)

        return jsonify({
            "job_id": job_id,
            "status": "queued",
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
        resp["result"] = json.loads(job["result"]) if job.get("result") else None
        resp["suggestions"] = json.loads(job["suggestions"]) if job.get("suggestions") else None
    elif job["status"] == "failed":
        resp["error"] = job.get("error", "")

    return jsonify(resp), 200


    

    



