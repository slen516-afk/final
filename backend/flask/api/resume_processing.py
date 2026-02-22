# api/resume_processing.py
from flask import Blueprint, request, jsonify
import uuid
import time
import random

# 取個簡短的 blueprint 名稱
resume_proc_bp = Blueprint('resume_proc', __name__) 

@resume_proc_bp.route('/upload', methods=['POST'])
def upload_resume():
    if 'file' not in request.files:
        return jsonify({"error": "No file part", "code": 400}), 400
    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file", "code": 400}), 400
    
    fake_resume_id = str(uuid.uuid4())

    return jsonify({
        "message": "Resume uploaded successfully. OCR processing started.",
        "resume_id": fake_resume_id,
        "filename": file.filename,
        "upload_time": time.strftime('%Y-%m-%d %H:%M:%S'),
        "status_check_url": f"/api/resumes/{fake_resume_id}/status"
    }), 201

@resume_proc_bp.route('/<id>/status', methods=['GET'])
def check_ocr_status(id):
    mock_parsed_data = {
        "name": "王小明",
        "email": "wang.test@example.com",
        "skills": ["Python", "Flask", "Docker", "SQL", "React"],
        "experience_years": 2,
        "education": "國立科技大學 資訊工程系"
    }

    return jsonify({
        "resume_id": id,
        "status": "completed",  # 可能是 'processing', 'completed', 'failed'
        "progress": 100,
        "ocr_result": mock_parsed_data,
        "generated_at": time.strftime('%Y-%m-%d %H:%M:%S')
    }), 200