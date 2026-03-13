import json
import uuid
from datetime import datetime, timezone
import re
from flask import Blueprint, request, jsonify, g
from api.auth import login_required
from core.redis_client import redis_client, STREAM_NAME
from core.supabase_client import supabase

gap_analysis_bp = Blueprint('gap_analysis', __name__)

def _create_gap_analysis_job(user_id: str, survey_data: dict) -> str:
    job_id = f"job_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()

    # 存狀態到 Redis Hash
    redis_client.hset(f"job:{job_id}", mapping={
        "status": "processing",
        "user_id": user_id,
        "result": "",
        "error": "",
        "retry_count": "0",
        "created_at": now,
        "updated_at": now,
    })

    # 呼叫 Celery (使用 apply_async 並指定 task_id)
    from worker.tasks import process_career_analysis
    process_career_analysis.apply_async(args=[user_id, json.dumps(survey_data), job_id], task_id=job_id)

    return job_id

def _get_job(job_id: str) -> dict | None:
    data = redis_client.hgetall(f"job:{job_id}")
    return data if data else None

# 提交落差分析任務（丟 Queue）
@gap_analysis_bp.route('/gap-analysis', methods=['POST'])
@login_required
def start_gap_analysis():
    try:
        db_user_id = g.db_user_id

        if db_user_id is None:
            return jsonify({'error': 'User not found in DB'}), 403

        # 從 career_survey 確認是否有最新問卷及人格測驗結果
        # 分開查詢最新有值的資料，以免分開儲存導致 limit 1 抓到不齊全的資料 row
        # 分開查詢最新有值的資料，以免分開儲存導致 limit 1 抓到不齊全的資料 row
        q_res = (
            supabase.table("career_survey")
            .select("questionnaire_response")
            .eq("user_id", db_user_id)
            .not_.is_("questionnaire_response", "null")
            .order("completed_at", desc=True)
            .limit(1)
            .execute()
        )
        
        p_res = (
            supabase.table("career_survey")
            .select("personality")
            .eq("user_id", db_user_id)
            .not_.is_("personality", "null")
            .order("completed_at", desc=True)
            .limit(1)
            .execute()
        )

        if not q_res.data:
             return jsonify({'error': '尚未完成職涯拓荒問卷。請先完成問卷後再進行分析。'}), 400
        if not p_res.data:
             return jsonify({'error': '尚未完成人格特性測驗。請先完成測驗後再進行分析。'}), 400

        questionnaire_response = q_res.data[0].get("questionnaire_response")
        personality = p_res.data[0].get("personality")

        survey_data = {
            "questionnaire_response": questionnaire_response,
            "personality": personality
        }

        # 確認資料齊全後，推進 job
        job_id = _create_gap_analysis_job(str(db_user_id), survey_data)

        return jsonify({
            "job_id": job_id,
            "status": "processing",
        }), 202

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[Gap Analysis] 500 Error: {error_details}")
        return jsonify({'error': str(e), 'details': '請檢查伺服器日誌', 'traceback': error_details}), 500

# 輪詢落差分析任務進度
@gap_analysis_bp.route('/gap-analysis/<job_id>', methods=['GET'])
@login_required
def poll_gap_analysis_job(job_id):
    try:
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
            result = json.loads(job["result"]) if job.get("result") else None
            if result:
                # 1. 處理核心洞察與個人總結的拆分
                pre_summary = result.get("preliminary_summary", {})
                core_insight = pre_summary.get("core_insight", "")
                
                # 嘗試使用標籤拆分
                industry_match = re.search(r'【產業洞察】[：:]?\s*(.*?)(?=【|$)', core_insight, re.S)
                personal_match = re.search(r'【個人總結】[：:]?\s*(.*)', core_insight, re.S)
                
                if industry_match:
                    pre_summary["industry_insight"] = industry_match.group(1).strip()
                    if personal_match:
                        pre_summary["personal_summary"] = personal_match.group(1).strip()
                    else:
                        pre_summary["personal_summary"] = ""
                else:
                    # 備援方案：如果沒有標籤，嘗試在 "您" 或 "你" 處拆分
                    split_match = re.search(r'(.*?[。！？](?=\s*[您你]))(.*)', core_insight, re.S)
                    if split_match:
                        pre_summary["industry_insight"] = split_match.group(1).strip()
                        pre_summary["personal_summary"] = split_match.group(2).strip()
                    else:
                        pre_summary["industry_insight"] = core_insight
                        pre_summary["personal_summary"] = ""
                
                result["preliminary_summary"] = pre_summary

                # 2. 處理匹配度百分比符號移除與 Action Plan 欄位搬移
                gap_analysis = result.get("gap_analysis", {})
                
                # 將 action_plan 放入 gap_analysis 中，以符合前端 Skills.tsx 預期 (gap_analysis?.action_plan)
                if "action_plan" in result:
                    gap_analysis["action_plan"] = result["action_plan"]

                target_pos = gap_analysis.get("target_position", {})
                match_score = target_pos.get("match_score", "0")
                
                if isinstance(match_score, str):
                    clean_score = re.sub(r'[^\d]', '', match_score)
                    try:
                        target_pos["match_score"] = int(clean_score)
                    except ValueError:
                        target_pos["match_score"] = 0
                
                gap_analysis["target_position"] = target_pos
                result["gap_analysis"] = gap_analysis
                
                resp["result"] = result
            else:
                resp["result"] = None
        elif job["status"] == "failed" or job["status"] == "dlq":
            resp["error"] = job.get("error", "")

        return jsonify(resp), 200
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[Gap Analysis Poll] 500 Error: {error_details}")
        return jsonify({'error': str(e), 'traceback': error_details}), 500
