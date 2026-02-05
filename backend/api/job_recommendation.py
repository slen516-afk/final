from flask import Blueprint, request, jsonify, g
from api.auth import login_required
from core.supabase_client import supabase

job_rec_bp = Blueprint('job_rec', __name__)

# 路徑: /api/jobs/recommendations
# 因為 app.py 的 prefix 是 /api/jobs，這裡只要寫 /recommendations
@job_rec_bp.route('/recommendations', methods=['POST'])
def recommend_jobs():
    data = request.get_json()
    # TODO: 呼叫 LLM 或是搜尋邏輯
    return jsonify({
        "message": "Job recommendations generated",
        "jobs": ["Frontend Dev", "Backend Dev"]
    })