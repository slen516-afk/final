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


def _create_job(user_id: str, task_type: str = "resume_analysis", **extra) -> str:
    """
    建立 job hash 在 Redis 並 XADD 到 stream。
    回傳 job_id。
    extra: 可傳入 resume_id, survey_id 等，視 task_type 而定。
    """
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
    # 動態加入額外欄位（resume_id, survey_id 等）
    for k, v in extra.items():
        if v is not None:
            mapping[k] = str(v)

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
        user_id = g.user_id
        data = request.json

        task_type = data.get("task_type", "resume_analysis")
        if task_type not in VALID_TASK_TYPES:
            return jsonify({"error": f"Unsupported task_type: {task_type}. 支援: {', '.join(VALID_TASK_TYPES)}"}), 400

        # resume_id / survey_id 為 optional metadata
        extra = {}
        if data.get("resume_id"):
            extra["resume_id"] = data["resume_id"]
        if data.get("survey_id"):
            extra["survey_id"] = data["survey_id"]

        job_id = _create_job(user_id, task_type, **extra)

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


# D-03 取得履歷優化建議
@analysis_bp.route("/tasks/<task_id>/suggestions", methods=["GET"])
@login_required
def get_optimization_suggestions(task_id):
    job = _get_job(task_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    if job.get("task_type") != "resume_analysis":
        return jsonify({"error": "此任務非 resume_analysis，請改用 /results 端點"}), 400

    if job["status"] != "done":
        return jsonify({"task_id": task_id, "status": job["status"], "message": "尚未完成"}), 202

    raw = job.get("suggestions", "")
    if not raw:
        return jsonify({"error": "此任務尚未產生建議資料"}), 404

    return jsonify(json.loads(raw)), 200

# D-04 取得履歷優化結果
@analysis_bp.route("/tasks/<task_id>/results", methods=["GET"])
@login_required
def get_optimization_results(task_id):
    job = _get_job(task_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    if job.get("task_type") != "resume_opt":
        return jsonify({"error": "此任務非 resume_opt，請改用 /suggestions 端點"}), 400

    if job["status"] != "done":
        return jsonify({"task_id": task_id, "status": job["status"], "message": "尚未完成"}), 202

    raw = job.get("result", "")
    if not raw:
        return jsonify({"error": "此任務尚未產生優化結果"}), 404

    return jsonify(json.loads(raw)), 200
