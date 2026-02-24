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

def _create_job(user_id: str, resume_id: str, survey_id: str) -> str:
    """
    建立 job hash 在 Redis 並 XADD 到 stream。
    回傳 job_id。
    """
    job_id = f"job_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()

    # 存狀態到 Redis Hash
    redis_client.hset(f"job:{job_id}", mapping={
        "status": "queued",
        "user_id": user_id,
        "resume_id": resume_id,
        "survey_id": survey_id,
        "result": "",
        "suggestions": "",
        "error": "",
        "retry_count": "0",
        "created_at": now,
        "updated_at": now,
    })

    # XADD 到 cv_jobs stream
    redis_client.xadd(STREAM_NAME, {
        "job_id": job_id,
        "task_type": "cv_analysis",
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
        user_id = g.user_id
        data = request.json

        if "resume_id" not in data or "survey_id" not in data:
            return jsonify({"error": "Missing resume_id or survey_id"}), 400

        job_id = _create_job(user_id, data["resume_id"], data["survey_id"])

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


# D-02 查詢任務狀態
@analysis_bp.route("/tasks/<task_id>/status", methods=["GET"])
@login_required
def get_analysis_status(task_id):
    job = _get_job(task_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    return jsonify({
        "task_id": task_id,
        "status": job["status"],
    }), 200


# D-03 取得履歷優化結果
@analysis_bp.route("/tasks/<task_id>/results", methods=["GET"])
@login_required
def get_optimization_results(task_id):
    job = _get_job(task_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    if job["status"] != "done":
        return jsonify({"task_id": task_id, "status": job["status"], "message": "尚未完成"}), 202

    result = json.loads(job["result"]) if job.get("result") else {}
    return jsonify(result), 200


# D-04 取得履歷優化建議
@analysis_bp.route("/tasks/<task_id>/suggestions", methods=["GET"])
@login_required
def get_optimization_suggestions(task_id):
    job = _get_job(task_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    if job["status"] != "done":
        return jsonify({"task_id": task_id, "status": job["status"], "message": "尚未完成"}), 202

    suggestions = json.loads(job["suggestions"]) if job.get("suggestions") else {}
    return jsonify(suggestions), 200
