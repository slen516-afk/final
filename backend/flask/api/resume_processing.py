# api/resume_processing.py
import os

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import uuid
import time
import random
# from service.ocr_service.ocr_service import ResumeOCRService



# 取個簡短的 blueprint 名稱
resume_proc_bp = Blueprint('resume_proc', __name__) 

UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@resume_proc_bp.route('/upload', methods=['POST'])
def upload_resume():
    # 1. 檢查有沒有收到檔案
    if 'file' not in request.files:
        return jsonify({"error": "沒有收到檔案", "code": 400}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "沒有選擇檔案", "code": 400}), 400
    
    try:
        # --- 存檔並定義 filepath ---
        filename = secure_filename(file.filename)
        unique_filename = f"{int(time.time())}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        print(f"✅ 檔案已暫存至: {filepath}")
        
        # ==========================================
        # 🌟 效能大升級：從全域環境直接呼叫已經載好的 OCR
        # ==========================================
        ocr_handler = current_app.config.get("OCR_HANDLER")
        if not ocr_handler:
            return jsonify({"error": "OCR 服務尚未準備好或載入失敗", "code": 500}), 500
        
        print("[API] 呼叫已待命的 OCR 管家開始辨識...")
        # 直接把 filepath 丟給它處理
        raw_ocr_result = ocr_handler(filepath)
        
        # --- 防呆機制：如果 OCR 失敗回傳 Error ---
        if "error" in raw_ocr_result:
            return jsonify({"error": raw_ocr_result["error"], "code": 500}), 500

        # 3. 數據映射 (Mapping)
        res_struct = raw_ocr_result.get("structured_data", {})
        norm = raw_ocr_result.get("normalized_data", {})
        contact = norm.get("contact", {})

        # 防呆：處理 projects 陣列裡可能混入字串或字典的問題
        raw_projects = res_struct.get("projects", [])
        safe_projects = []
        for p in raw_projects:
            if isinstance(p, dict):
                title = p.get("title", p.get("name", ""))
                desc = p.get("description", p.get("details", ""))
                safe_projects.append(f"{title} - {desc}".strip(" -"))
            else:
                safe_projects.append(str(p))

        # ==========================================
        # 組合 mapped_data 準備回傳給前端
        # ==========================================
        mapped_data = {
            "name": contact.get("name", ""),
            "email": contact.get("email", ""),
            "phone": "",  
            "addressCity": contact.get("location", ""),
            "addressDistrict": "",
            "addressDetail": "",
            "bio": res_struct.get("summary", ""),
            
            "education": "\n".join([e.get("details", "") for e in res_struct.get("education", [])]),
            
            "experience": "\n\n".join([
                f"{exp.get('title', '')} - {exp.get('company', '')}\n{exp.get('responsibilities', '')}" 
                for exp in res_struct.get("experience", [])
            ]),
            
            "skills": ", ".join(norm.get("skills", [])),
            
            "projects": "\n".join(safe_projects),
            
            "languages": [{"language": "中文", "proficiency": "3"}],
            "certifications": "",
            "other": ""
        }

        return jsonify({
            "message": "Resume analyzed successfully",
            "data": mapped_data
        }), 200

    except Exception as e:
        print(f"❌ 發生致命錯誤: {str(e)}")
        return jsonify({"error": str(e), "code": 500}), 500


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