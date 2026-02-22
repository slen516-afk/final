from flask import Blueprint, request, jsonify, g
from api.auth import login_required
from core.supabase_client import supabase

user_preference_bp = Blueprint('user_preference', __name__)

@user_preference_bp.route('/dream-jobs', methods=['POST'])
@login_required
def create_career_survey():
    """
    B-02 提交目標工作設定 (Mocked)
    DB: CAREER_SURVEY
    """
    try:
        user_id = g.user_id
        data = request.json
        
        # 驗證必填欄位
        required_fields = ['career_preference', 'skill_self_assessment', 'salary_min', 'salary_max']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400

        # === Mock Response ===
        mock_survey_id = 101

        return jsonify({
            'survey_id': mock_survey_id,
            'message': 'Survey created successfully (Mock)'
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
