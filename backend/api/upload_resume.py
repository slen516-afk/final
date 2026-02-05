from flask import Blueprint, request, jsonify, g
from api.auth import login_required
from core.supabase_client import supabase

upload_resume_bp = Blueprint('upload_resume', __name__)

# 路徑: /api/resumes/upload/ (最後可能會有斜線，看前端怎麼送)
@upload_resume_bp.route('/upload', methods=['POST'])
def upload_resume():
    # 上傳邏輯...
    return jsonify({"message": "Uploaded"})