from flask import Blueprint, request, jsonify, g
from api.auth import login_required
from core.supabase_client import supabase
from datetime import datetime

resume_bp = Blueprint('resume', __name__)

@resume_bp.route('/form', methods=['POST'])
@login_required
def create_resume_form():
    """
    C-02 建立履歷 (表單填寫) - Mocked
    DB: RESUME
    """
    try:
        user_id = g.user_id
        data = request.json
        # NOTE: survey_id is used for linkage, though NOT in RESUME table directly.
        if 'survey_id' not in data or 'structured_data' not in data:
            return jsonify({'error': 'Missing survey_id or structured_data'}), 400
        
        template_id = data.get('template_id', 1) 
        resume_type = data.get('resume_type', 'generic')

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
        "user_id": user_id,
        "template_id": 1,
        "resume_type": "general",
        "structured_data": {
            "personal_info": { "name": "王小明", "email": "wang@example.com" },
            "education": [
                 { "school": "台灣大學", "degree": "學士" }
            ],
            "work_experience": [],
            "skills": ["Python", "Docker"]
        },
        "normalized_data": {}, # ERD column
        "vector_id": None,     # ERD column
        "is_embedded": False,  # ERD column
        "is_primary": True,    # ERD column
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-02T00:00:00Z"
    }

    return jsonify(mock_data), 200

@resume_bp.route('/<int:id>', methods=['PUT'])
@login_required
def update_resume(id):
    """
    C-05 用戶更新/確認履歷內容 - Mocked
    DB: RESUME
    Updates: structured_data, template_id, style_settings (color)
    """
    try:
        user_id = g.user_id
        data = request.json
        if 'structured_data' not in data:
             return jsonify({'error': 'Missing structured_data'}), 400
             
        # Extract template choices
        template_id = data.get('template_id')
        style_settings = data.get('style_settings') # e.g. {"color": "#1A73E8"}

        # === Mock DB Update ===
        # In real DB: Update RESUME set template_id=?, structured_data=?, updated_at=? ...
        # Color might be stored in normalized_data or a separate config column.
        
        return jsonify({
            'resume_id': id,
            'updated_at': datetime.utcnow().isoformat() + 'Z',
            'saved_settings': {
                'template_id': template_id,
                'style_settings': style_settings
            }
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
