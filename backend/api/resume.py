from flask import Blueprint, request, jsonify, g
from api.auth import login_required
from core.supabase_client import supabase
from datetime import datetime

resume_bp = Blueprint('resume', __name__)

@resume_bp.route('/form', methods=['POST'])
@login_required
def create_resume_form():
    """
    C-02 [路徑 B] 建立履歷 (表單填寫) - Mocked
    DB: RESUME
    """
    try:
        user_id = g.user_id
        data = request.json
        if 'survey_id' not in data or 'structured_data' not in data:
            return jsonify({'error': 'Missing survey_id or structured_data'}), 400

        # === Mock DB Operation ===
        mock_resume_id = 203
        
        return jsonify({
            'resume_id': mock_resume_id,
            'status': 'completed',
            'last_updated': datetime.utcnow().isoformat() + 'Z'
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@resume_bp.route('/<int:id>', methods=['GET'])
@login_required
def get_resume(id):
    """
    C-04 取得履歷詳情 - Mocked
    DB: RESUME
    """
    user_id = g.user_id
    # === Mock DB Query ===
    
    mock_data = {
        "resume_id": id,
        "structured_data": {
            "personal_info": { "name": "王小明", "email": "wang@example.com" },
            "education": [
                 { "school": "台灣大學", "degree": "學士" }
            ],
            "work_experience": [],
            "skills": ["Python", "Docker"]
        }
    }

    return jsonify(mock_data), 200

@resume_bp.route('/<int:id>', methods=['PUT'])
@login_required
def update_resume(id):
    """
    C-05 用戶更新/確認履歷內容 - Mocked
    DB: RESUME
    """
    try:
        user_id = g.user_id
        data = request.json
        if 'structured_data' not in data:
             return jsonify({'error': 'Missing structured_data'}), 400
             
        # === Mock DB Update ===
        
        return jsonify({
            'resume_id': id,
            'updated_at': datetime.utcnow().isoformat() + 'Z'
        }), 200

    except Exception as e:
         return jsonify({'error': str(e)}), 500
    
@resume_bp.route('/<int:id>/export', methods=['GET'])
@login_required
def export_resume(id):
    """
    E-01 匯出履歷文件 - Mocked
    """
    user_id = g.user_id
    fmt = request.args.get('format', 'pdf')
    # === Mock Export ===
    
    return f"Binary PDF Stream for Resume {id} ({fmt})", 200, {'Content-Type': 'application/pdf'}
