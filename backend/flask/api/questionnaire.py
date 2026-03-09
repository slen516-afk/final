from datetime import datetime, timezone

from flask import Blueprint, request, jsonify, g
from api.auth import login_required
from core.supabase_client import supabase
from src.core.agent_engine.manager import CareerAgentManager

questionnaire_bp = Blueprint("questionnaire", __name__)


# E-01 儲存問卷作答結果 + 觸發 AI 分析
@questionnaire_bp.route("/questionnaire-response", methods=["POST"])
@login_required # 確保有登入機制
def save_questionnaire_response():
    """
    前端傳入職能問卷 JSON，新增一筆至 career_survey.questionnaire_response，
    並立刻觸發 CrewAI 進行職涯落差分析。
    """
    try:
        user_id = g.db_user_id # 你的系統原本從這裡拿 user_id
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        # 檢查必填模組
        required_modules = ["module_a", "module_b", "module_c", "module_d"]
        for module in required_modules:
            if module not in data:
                return jsonify({"error": f"Missing required module: {module}"}), 400

        now = datetime.now(timezone.utc).isoformat()

        # 🌟 1. 先存入資料庫
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

        # ==========================================
        # 🌟 2. 存檔成功後，立刻喚醒 AI 進行分析！
        # ==========================================
        print(f"🚀 [API] 問卷儲存成功，準備進行 AI 職涯分析... User: {user_id}")
        
        manager = CareerAgentManager(mock_mode=False)
        user_input = {
            "user_id": user_id,
            "survey_json": json.dumps(data, ensure_ascii=False) # 剛好是分類好的結構，calculator.py 最愛！
        }

        # 呼叫 CrewAI
        ai_result = manager.run_task("career_analysis", user_input)

        if isinstance(ai_result, dict) and ai_result.get("status") == "error":
            print(f"❌ [CrewAI Error] {ai_result.get('message')}")
            # 就算 AI 失敗，問卷還是存好了，回傳 500 讓前端知道
            return jsonify({"error": ai_result.get("message"), "survey_id": survey_id}), 500

        print("✅ [API] 職涯分析報告生成成功！")

        return jsonify({
            "survey_id": survey_id,
            "status": "success",
            "updated_at": now,
            "data": ai_result # 將 AI 報告一起回傳
        }), 201

    except Exception as e:
        print(f"🚨 [API Error] {e}")
        return jsonify({"error": str(e)}), 500
# E-02 儲存人格特質結果
@questionnaire_bp.route("/personality", methods=["POST"])
@login_required
def save_personality():
    """
    前端傳入人格特質 JSON，新增一筆至 career_survey.personality。
    """
    try:
        user_id = g.db_user_id
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        required_fields = [
            "trait_calculation_debug",
            "trait_normalized_scores",
            "primary_archetype",
            "secondary_archetypes",
            "trait_created_at",
        ]
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
