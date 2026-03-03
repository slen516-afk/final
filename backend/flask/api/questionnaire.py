from datetime import datetime, timezone

from flask import Blueprint, request, jsonify, g
from api.auth import login_required
from core.supabase_client import supabase

questionnaire_bp = Blueprint("questionnaire", __name__)


# E-01 儲存問卷作答結果
@questionnaire_bp.route("/questionnaire-response", methods=["POST"])
@login_required
def save_questionnaire_response():
    """
    前端傳入完整問卷 JSON，新增一筆至 career_survey.questionnaire_response。
    同一個 user 可以有多筆問卷紀錄。
    """
    try:
        user_id = g.db_user_id
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        required_modules = ["module_a", "module_b", "module_c", "module_d"]
        for module in required_modules:
            if module not in data:
                return jsonify({"error": f"Missing required module: {module}"}), 400

        now = datetime.now(timezone.utc).isoformat()

        result = (
            supabase.table("career_survey")
            .insert({
                "user_id": user_id,
                "questionnaire_response": data,
                "updated_at": now,
                "completed_at": now,
            })
            .execute()
        )

        survey_id = result.data[0]["survey_id"] if result.data else None

        return jsonify({
            "survey_id": survey_id,
            "status": "saved",
            "updated_at": now,
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# E-02 儲存人格特質結果
@questionnaire_bp.route("/personality", methods=["POST"])
@login_required
def save_personality():
    """
    前端傳入人格特質 JSON，新增一筆至 career_survey.personality。
    同一個 user 可以有多筆紀錄。
    """
    try:
        user_id = g.db_user_id
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        required_fields = ["trait_raw_responses", "trait_normalized_scores", "primary_archetype"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        now = datetime.now(timezone.utc).isoformat()

        result = (
            supabase.table("career_survey")
            .insert({
                "user_id": user_id,
                "personality": data,
                "updated_at": now,
                "completed_at": now,
            })
            .execute()
        )

        survey_id = result.data[0]["survey_id"] if result.data else None

        return jsonify({
            "survey_id": survey_id,
            "status": "saved",
            "updated_at": now,
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
