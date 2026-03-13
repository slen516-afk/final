import json
import uuid
from datetime import datetime, timezone

from flask import Blueprint, request, jsonify, g
from api.auth import login_required
from core.redis_client import (
    redis_client,
    STREAM_NAME,
)
from core.supabase_client import supabase


user_preference_bp = Blueprint('user_preference', __name__)


def _submit_survey_to_celery(user_id: str, survey_data: dict) -> str:
    """
    將問卷資料提交給 Celery 進行非同步分析。
    """
    import uuid
    from datetime import datetime, timezone
    from worker.tasks import process_career_analysis
    
    job_id = f"job_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()

    # 1. 在 Redis 紀錄 Job 初始狀態 (為了讓 poll_survey_job 能抓到)
    redis_client.hset(f"job:{job_id}", mapping={
        "status": "processing",
        "user_id": user_id,
        "result": "",
        "error": "",
        "created_at": now,
        "updated_at": now,
    })

    # 2. 觸發 Celery 任務
    process_career_analysis.delay(user_id, json.dumps(survey_data), job_id)

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
        db_user_id = g.db_user_id

        if db_user_id is None:
            return jsonify({'error': 'User not found in DB'}), 403

        # 從 career_survey 找出該使用者最新的 questionnaire_response
        result = (
            supabase.table("career_survey")
            .select("questionnaire_response")
            .eq("user_id", db_user_id)
            .order("completed_at", desc=True)
            .execute()
        )

        data = None
        for row in result.data:
            if row.get("questionnaire_response"):
                data = row["questionnaire_response"]
                break

        if not data:
            return jsonify({'error': 'No career survey response found for this user.'}), 404

        required_modules = ['module_a', 'module_b', 'module_c', 'module_d']
        for module in required_modules:
            if module not in data:
                return jsonify({'error': f'Missing module in DB: {module}'}), 400

        # 將 DB 取得的 data 放進 job
        job_id = _submit_survey_to_celery(db_user_id, data)

        return jsonify({
            'job_id': job_id,
            'status': 'processing',
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
