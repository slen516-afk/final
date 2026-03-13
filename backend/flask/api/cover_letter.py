from flask import Blueprint, request, jsonify
from crewai import Crew, LLM
import json

# 引入 agents, tasks, tools
from service.llm_service.src.features.cover_letter.agents import get_cover_letter_strategist_agent
from service.llm_service.src.features.cover_letter.tasks import get_cover_letter_task
from service.llm_service.src.features.cover_letter.tools import RecommendJobSearchTool, FetchOptimizeResumeTool, FetchDesignatedResumeTool

cover_letter_bp = Blueprint('cover_letter', __name__)

@cover_letter_bp.route('/generate', methods=['POST'])
def generate_cover_letter():
    """
    第一支 API: 生成 Cover Letter。
    前端傳入 : job_id, optimization_id 以及 LLM 模型參數 (如 model, temperature)
    回傳 task_id 給前端，對齊 Celery 非同步流程。
    """
    try:
        from worker.tasks import process_cover_letter
        import uuid
        from datetime import datetime, timezone
        from core.redis_client import redis_client

        data = request.get_json() or {}
        job_id = data.get("job_id")
        optimization_id = data.get("optimization_id")
        resume_id = data.get("resume_id") # 新增支援原始履歷 ID
        user_id = g.db_user_id

        if not user_id:
             return jsonify({"status": "error", "message": "User not logged in"}), 401
        
        # 🛡️ 防呆：如果 optimization_id 看起來像 resume_id (純數字)，且沒有傳 resume_id，就互換一下
        if str(optimization_id).isdigit() and not resume_id:
            resume_id = optimization_id
        
        if not job_id or (not optimization_id and not resume_id):
            return jsonify({"status": "error", "message": "缺少 job_id 或 resume_id/optimization_id"}), 400

        tracking_id = f"job_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat()

        # 1. 在 Redis 紀錄 Job 初始狀態
        redis_client.hset(f"job:{tracking_id}", mapping={
            "status": "processing",
            "user_id": user_id,
            "result": "",
            "error": "",
            "created_at": now,
            "updated_at": now,
        })

        # 2. 觸發 Celery 任務 (使用 apply_async 並指定 task_id)
        process_cover_letter.apply_async(
            kwargs={
                "user_id": user_id, 
                "job_id": str(job_id), 
                "optimization_id": str(optimization_id or ""), 
                "resume_id": str(resume_id or ""),
                "tracking_id": tracking_id
            },
            task_id=tracking_id
        )

        return jsonify({
            "status": "success",
            "job_id": tracking_id,
            "task_id": tracking_id # 為了與通用 poll 對齊
        }), 202

    except Exception as e:
        print(f"生成 Cover Letter 發生錯誤: {str(e)}")
        return jsonify({"status": "error", "message": "伺服器內部錯誤", "details": str(e)}), 500


@cover_letter_bp.route('/preview_data', methods=['POST'])
def preview_cover_letter_data():
    """
    第二支 API: 提供抓取預覽資料 (Preview)。
    回傳工具抓取的推薦職缺與優化履歷結果給前端，不進入 LLM 生成，便於驗證與檢視。
    """
    try:
        data = request.get_json() or {}
        job_id = data.get("job_id")
        optimization_id = data.get("optimization_id")
        resume_id = data.get("resume_id")

        if str(optimization_id).isdigit() and not resume_id:
            resume_id = optimization_id

        if not job_id or (not optimization_id and not resume_id):
            return jsonify({"status": "error", "message": "缺少 job_id 或 resume_id/optimization_id"}), 400

        # 直接呼叫 Tool 的 run 來抓取資料
        job_info = RecommendJobSearchTool()._run(job_id=str(job_id))
        resume_info = FetchOptimizeResumeTool()._run(optimization_id=str(optimization_id))
        designated_info = FetchDesignatedResumeTool()._run(resume_id=str(resume_id or ""))

        return jsonify({
            "status": "success",
            "job_data": job_info,
            "optimized_resume_data": resume_info,
            "original_resume_data": designated_info
        }), 200

    except Exception as e:
        print(f"預覽發生錯誤: {str(e)}")
        return jsonify({"status": "error", "message": "伺服器內部錯誤", "details": str(e)}), 500
