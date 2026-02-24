import json
import uuid
from datetime import datetime, timezone

from flask import Blueprint, request, jsonify, g
from api.auth import login_required
from core.redis_client import (
    redis_client,
    STREAM_NAME,
)

user_preference_bp = Blueprint('user_preference', __name__)


def _create_survey_job(user_id: str, survey_data: dict) -> str:
    job_id = f"job_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()

    # 存狀態到 Redis Hash
    redis_client.hset(f"job:{job_id}", mapping={
        "status": "queued",
        "user_id": user_id,
        "survey_data": json.dumps(survey_data, ensure_ascii=False),
        "result": "",
        "error": "",
        "retry_count": "0",
        "created_at": now,
        "updated_at": now,
    })

    # XADD 到 cv_jobs stream
    redis_client.xadd(STREAM_NAME, {
        "job_id": job_id,
        "task_type": "survey_analysis",
        "retry_count": "0",
    })

    return job_id


def _get_job(job_id: str) -> dict | None:
    data = redis_client.hgetall(f"job:{job_id}")
    return data if data else None


# B-02 提交職能問卷（丟 Queue）
@user_preference_bp.route('/dream-jobs', methods=['POST'])
@login_required
def create_career_survey():
    try:
        user_id = g.user_id
        data = request.json

        required_modules = ['module_a', 'module_b', 'module_c', 'module_d']
        for module in required_modules:
            if module not in data:
                return jsonify({'error': f'Missing module: {module}'}), 400

        data['user_id'] = user_id

        job_id = _create_survey_job(user_id, data)

        return jsonify({
            'job_id': job_id,
            'status': 'queued',
        }), 202

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# B-02 輪詢問卷分析進度
@user_preference_bp.route('/dream-jobs/<job_id>', methods=['GET'])
@login_required
def poll_survey_job(job_id):
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
    elif job["status"] == "failed":
        resp["error"] = job.get("error", "")

    return jsonify(resp), 200
