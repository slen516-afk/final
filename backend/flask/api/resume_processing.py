# api/resume_processing.py
import os
import json
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import uuid
import time
import random
from core.supabase_client import supabase
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
        parsed_data = current_app.extract_text_from_image(filepath)
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
            "data": parsed_data,
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

@resume_proc_bp.route('/list/<int:user_id>', methods=['GET'])
def list_resumes(user_id):
    try:
        # 🌟 核心：去資料庫撈取特定 user_id 的履歷
        res = supabase.table('resume').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        return jsonify({"status": "success", "data": res.data}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@resume_proc_bp.route('/save', methods=['POST'])
def save_processed_resume():
    try:
        req_data = request.json
        
        # 1. 接收前端傳來的資料
        resume_name = req_data.get('resume_name')
        resume_data = req_data.get('resume_data')
        
        # 2. 🛡️ 【超級保命防護罩】：強制把 user_id 轉成數字！
        # 就算前端硬傳 '5F82A' 這種字串來，我們也會把它攔截並強制變成 1
        raw_user_id = req_data.get('user_id', 1)
        try:
            user_id = int(raw_user_id)
        except (ValueError, TypeError):
            user_id = 1 # 轉換失敗就預設給 1

        # 3. 檢查必填欄位
        if not resume_name or not resume_data:
            return jsonify({"status": "error", "message": "缺少履歷名稱或履歷資料"}), 400

        # 4. 準備要寫入 Supabase 的資料
        insert_data = {
            "user_id": user_id,
            "resume_name": resume_name,
            "resume_type": "uploaded_pdf",
            "structured_data": resume_data,
            "normalized_data": {},
            "is_primary": False,
            "is_embedded": False
        }

        # 5. 寫入資料庫
        response = supabase.table('resume').insert(insert_data).execute()
        print(f"✅ [System] 履歷 '{resume_name}' 已成功存入 Supabase!")

        # ⚠️ 這裡一定要有 return！
        return jsonify({
            "status": "success", 
            "message": "履歷儲存成功",
            "data": response.data
        }), 200

    except Exception as e:
        print(f"🚨 [Error] 履歷儲存失敗: {e}")
        # ⚠️ 這裡也一定要有 return！(你剛才可能就是漏了這個單字)
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500