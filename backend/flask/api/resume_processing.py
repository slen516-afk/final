# api/resume_processing.py
import os
import json
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import uuid
import time
import random
from core.supabase_client import supabase
from src.core.agent_engine.manager import CareerAgentManager
from datetime import datetime, timezone

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

@resume_proc_bp.route('/analyze', methods=['POST'])
def analyze_resume_with_ai():
    try:
        req_data = request.json
        user_id = req_data.get('user_id')
        resume_data = req_data.get('resume_data')
        resume_id = req_data.get('resume_id') # 🌟 確保這行有寫！

        if not user_id or not resume_data:
            return jsonify({"status": "error", "message": "缺少 user_id 或 resume_data"}), 400

        print(f"\n🚀 [API] 收到 User {user_id} 的履歷 AI 診斷請求！")

        # 1. 召喚你的大腦總機！
        # 💡 測試階段可以先保持 mock_mode=True，確定連線通了再改成 False 讓真 LLM 跑
        manager = CareerAgentManager() 

        # 2. 準備給 CrewAI 的輸入字典 (對應 manager.py 的 user_input)
        # 把 JSON 轉成格式化字串，讓 LLM 比較好閱讀
        user_input = {
            "user_id": user_id,
            "resume_id": resume_id, # 🌟 確保有傳遞給 Manager
            "resume_text": json.dumps(resume_data, ensure_ascii=False, indent=2) 
        }

        # 3. 執行任務！告訴 Manager 我們要做 "resume_analysis"
        print("🤖 [CrewAI] 開始執行履歷深度診斷任務...")
        result = manager.run_task("resume_analysis", user_input)

        # 4. 錯誤處理 (如果 manager 回傳 status: error)
        if isinstance(result, dict) and result.get("status") == "error":
             print(f"❌ [CrewAI Error] {result.get('message')}")
             return jsonify({"status": "error", "message": result.get("message")}), 500

        # 5. 成功！把符合 Pydantic schema 的完美 JSON 丟回給前端
        print("✅ [CrewAI] 診斷完成，準備回傳給前端 UI！")
        return jsonify({
            "status": "success",
            "data": result  
        }), 200

    except Exception as e:
        print(f"🚨 [Fatal Error] AI 履歷診斷發生致命錯誤: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# 🌟 使用正確的 Blueprint 名稱：resume_proc_bp
@resume_proc_bp.route('/career-analyze', methods=['POST'])
def analyze_career_with_ai():
    try:
        req_data = request.json
        user_id = req_data.get('user_id')
        resume_id = req_data.get('resume_id')

        if not user_id:
            return jsonify({"status": "error", "message": "缺少 user_id"}), 400

        print(f"\n🚀 [API] 收到 User {user_id} 的【職能圖譜】AI 診斷請求！")

        from service.llm_service.src.core.agent_engine.manager import CareerAgentManager
        manager = CareerAgentManager() 

        user_input = {
            "user_id": user_id,
            "resume_id": resume_id
        }

        print("🤖 [CrewAI] 開始執行職能圖譜深度分析...")
        result = manager.run_task("career_analysis", user_input)

        if isinstance(result, dict) and result.get("status") == "error":
             return jsonify({"error": result.get("message")}), 500

        print("✅ [CrewAI] 職能分析完成！")
        return jsonify(result), 200

    except Exception as e:
        print(f"🚨 [Fatal Error] AI 職能分析發生致命錯誤: {str(e)}")
        return jsonify({"error": str(e)}), 500

@resume_proc_bp.route('/optimize/generate', methods=['POST'])
def generate_optimized_resume():
    try:
        req_data = request.json
        user_id = req_data.get('user_id')
        resume_data = req_data.get('resume_data')

        if not user_id or not resume_data:
            return jsonify({"status": "error", "message": "缺少 user_id 或 resume_data"}), 400

        print(f"\n🚀 [API] 收到使用者 {user_id} 的 AI 全文履歷優化請求！")

        # 🌟 直接呼叫 Manager (不用再寫 import 了，因為最上面已經 import 過了)
        manager = CareerAgentManager(mock_mode=False) 

        # 準備給 CrewAI 的輸入資料
        user_input = {
            "user_id": user_id,
            "resume_text": json.dumps(resume_data, ensure_ascii=False, indent=2) 
        }

        print("🤖 [CrewAI] 開始執行履歷全文重寫與優化任務 (resume_opt)...")
        result = manager.run_task("resume_opt", user_input)

        if isinstance(result, dict) and result.get("status") == "error":
             print(f"❌ [CrewAI Error] {result.get('message')}")
             return jsonify({"status": "error", "message": result.get("message")}), 500

        print("✅ [CrewAI] 履歷生成完成，準備渲染至前端樣板！")
        return jsonify({
            "status": "success",
            "data": result  
        }), 200

    except Exception as e:
        print(f"🚨 [Error] AI 履歷生成失敗: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ==========================================
# 🌟 儲存優化後的履歷到資料庫 (完美對齊 Schema)
# ==========================================
@resume_proc_bp.route('/optimize/save', methods=['POST'])
def save_optimized_resume():
    try:
        req_data = request.json
        user_id = req_data.get('user_id')
        resume_id = req_data.get('original_resume_id')
        template_id = req_data.get('template_id')
        optimized_data = req_data.get('optimized_data', {})

        if not user_id:
            return jsonify({"status": "error", "message": "缺少 user_id"}), 400

        print(f"🚀 [API] 準備將 User {user_id} 的優化履歷存入 resume_optimization...")

        from src.core.database.supabase_client import get_supabase_client
        supabase = get_supabase_client()

        # 🔧 輔助函式：確保要存入 jsonb 的欄位絕對是 list 或 dict，防止 Supabase 報錯
        def to_jsonb(val):
            if isinstance(val, list) or isinstance(val, dict):
                return val
            if isinstance(val, str) and val.strip():
                # 如果前端傳來的是換行字串，我們把它包成陣列
                return [val]
            return []

        # 🌟 完美對齊你截圖中的所有欄位
        insert_data = {
            "user_id": user_id,
            "resume_id": resume_id,
            # Text 欄位
            "professional_summary": optimized_data.get("professional_summary", ""),
            "autobiography": optimized_data.get("autobiography", ""),
            "resume_name": f"{optimized_data.get('name', '未命名')} 的優化履歷",
            "optimization_version": "v1.0",
            "llm_model_used": "gpt-4o",
            # JSONB 欄位 (使用輔助函式確保格式正確)
            "professional_experience": to_jsonb(optimized_data.get("professional_experience")),
            "core_skills": to_jsonb(optimized_data.get("core_skills")),
            "projects": to_jsonb(optimized_data.get("projects")),
            "education": to_jsonb(optimized_data.get("education")),
            "template_color": {"template_id": template_id}, # 將樣板紀錄在 jsonb 裡
            # 其他欄位
            "is_embedded": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        # 寫入 Supabase
        response = supabase.table('resume_optimization').insert(insert_data).execute()

        print("✅ [API] 優化履歷已成功儲存！")
        return jsonify({
            "status": "success",
            "message": "優化履歷儲存成功",
            "data": response.data
        }), 200

    except Exception as e:
        print(f"🚨 [Error] 儲存優化履歷失敗: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500