from flask import Blueprint, request, jsonify, g
from api.auth import login_required
from core.supabase_client import supabase

# 定義藍圖名稱
ocr_bp = Blueprint('ocr', __name__)

# 路徑: /api/resumes/<id>/status
# 因為 app.py 的 prefix 是 /api/resumes，這裡只要寫 /<id>/status
@ocr_bp.route('/<string:resume_id>/status', methods=['GET'])
def check_ocr_status(resume_id):
    # TODO: 連接資料庫查詢狀態
    return jsonify({
        "resume_id": resume_id,
        "status": "processing", # 範例回傳
        "message": "OCR is running"
    })