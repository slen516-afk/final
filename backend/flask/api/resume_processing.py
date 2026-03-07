# api/resume_processing.py
import os
import json
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import uuid
import time
import random
from core.supabase_client import supabase

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
        # ==========================================
        # 🌟 1. 終極防呆存檔法：強制加上 .pdf
        # ==========================================
        current_timestamp = int(time.time() * 1000)
        safe_filename = f"{current_timestamp}_{uuid.uuid4().hex[:8]}.pdf"
        filepath = os.path.join(UPLOAD_FOLDER, safe_filename)
        
        file.save(filepath)
        print(f"✅ 檔案已暫存至: {filepath}")
        
        # ==========================================
        # 🌟 2. 呼叫 OCR 進行辨識
        # ==========================================
        ocr_handler = current_app.config.get("OCR_HANDLER")
        if not ocr_handler:
            return jsonify({"error": "OCR 服務尚未準備好或載入失敗", "code": 500}), 500
        
        print("[API] 呼叫已待命的 OCR 管家開始辨識...")
        raw_ocr_result = ocr_handler(filepath)
        
        # --- 防呆機制：如果 OCR 失敗回傳 Error ---
        if isinstance(raw_ocr_result, dict) and "error" in raw_ocr_result:
            return jsonify({"error": raw_ocr_result["error"], "code": 500}), 500

        # ==========================================
        # 🌟 3. 無敵鐵金剛數據映射 (Mapping) + 型別防呆
        # ==========================================
        # 確保 raw_ocr_result 是字典，避免 .get() 報錯
        if isinstance(raw_ocr_result, str):
            try:
                raw_ocr_result = json.loads(raw_ocr_result)
            except:
                raw_ocr_result = {}
        if not isinstance(raw_ocr_result, dict):
            raw_ocr_result = {}

        print("\n🔍 [Debug] AI 辨識出的原始結構:", raw_ocr_result, "\n")

        # 容錯提取子結構
        res_struct = raw_ocr_result.get("structured_data", {})
        if not isinstance(res_struct, dict): res_struct = raw_ocr_result
        
        norm = raw_ocr_result.get("normalized_data", {})
        if not isinstance(norm, dict): norm = raw_ocr_result
        
        contact = norm.get("contact", {})
        if not isinstance(contact, dict): contact = raw_ocr_result

        # 🛡️ 安全處理教育背景 (解決垂直文字「跑版」問題)
        raw_edu = res_struct.get("education", [])
        if isinstance(raw_edu, list):
            safe_edu = "\n".join([str(e.get("details", e.get("school", ""))) if isinstance(e, dict) else str(e) for e in raw_edu])
        else:
            safe_edu = str(raw_edu) # 如果是單純字串，直接轉型，絕對不跑迴圈！

        # 🛡️ 安全處理工作經歷 (Experience)
        raw_exp = res_struct.get("experience", res_struct.get("work_experience", []))
        if isinstance(raw_exp, list):
            exp_list = []
            for exp in raw_exp:
                if isinstance(exp, dict):
                    title = exp.get('title', exp.get('role', ''))
                    comp = exp.get('company', '')
                    desc = exp.get('responsibilities', exp.get('description', ''))
                    exp_list.append(f"{title} - {comp}\n{desc}".strip(" -\n"))
                else:
                    exp_list.append(str(exp))
            safe_exp = "\n\n".join(exp_list)
        else:
            safe_exp = str(raw_exp)

        # 🛡️ 安全處理專案/作品集 (Portfolio)
        raw_projects = res_struct.get("projects", res_struct.get("portfolio", []))
        if isinstance(raw_projects, list):
            proj_list = []
            for p in raw_projects:
                if isinstance(p, dict):
                    title = p.get("title", p.get("name", ""))
                    desc = p.get("description", p.get("details", ""))
                    proj_list.append(f"{title}\n{desc}".strip(" -\n"))
                else:
                    proj_list.append(str(p))
            safe_projects = "\n\n".join(proj_list)
        else:
            safe_projects = str(raw_projects)

        # 🛡️ 安全處理技能
        raw_skills = norm.get("skills", res_struct.get("skills", []))
        safe_skills = ", ".join([str(s) for s in raw_skills]) if isinstance(raw_skills, list) else str(raw_skills)

        # 🛡️ 安全處理自傳 / 關於我
        safe_bio = res_struct.get("summary", res_struct.get("autobiography", res_struct.get("bio", res_struct.get("關於我", ""))))
        if isinstance(safe_bio, list): 
            safe_bio = "\n".join([str(b) for b in safe_bio])
        else:
            safe_bio = str(safe_bio)

        # ==========================================
        # 🌟 4. 嚴格對齊前端需要的欄位名稱 (非常重要！)
        # ==========================================
        mapped_data = {
            "name": contact.get("name", contact.get("full_name", "")),
            "email": contact.get("email", ""),
            "phone": contact.get("phone", ""),
            "address": contact.get("location", contact.get("address", "")), # 前端叫 address
            
            "education": safe_edu,
            "experience": safe_exp,
            "skills": safe_skills,
            "portfolio": safe_projects, # 專案經驗會被填入這裡
            "autobiography": safe_bio,  # 關於我會被填入這裡
            
            "languages": "中文(精通)", 
            "certifications": "",
            "other": res_struct.get("other", "")
        }

        return jsonify({
            "message": "Resume analyzed successfully",
            "data": raw_ocr_result,
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