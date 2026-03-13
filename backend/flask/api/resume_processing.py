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
        from worker.tasks import analyze_resume_async
        from core.redis_client import redis_client
        import uuid

        # 1. 儲存檔案
        current_timestamp = int(time.time() * 1000)
        ext = os.path.splitext(file.filename)[1].lower() if file.filename else ".pdf"
        safe_filename = f"{current_timestamp}_{uuid.uuid4().hex[:8]}{ext}"
        filepath = os.path.abspath(os.path.join(UPLOAD_FOLDER, safe_filename))
        
        file.save(filepath)
        
        # 2. 準備任務
        job_id = f"ocr_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat()

        # 在 Redis 紀錄 Job 初始狀態
        redis_client.hset(f"job:{job_id}", mapping={
            "status": "processing",
            "user_id": str(g.db_user_id) if hasattr(g, 'db_user_id') else "guest",
            "result": "",
            "error": "",
            "created_at": now,
            "updated_at": now,
        })

        # 3. 觸發 Celery 任務
        analyze_resume_async.delay(file_path=filepath, job_id=job_id)

        return jsonify({
            "status": "success",
            "message": "Resume upload successful, analysis started",
            "job_id": job_id,
            "task_id": job_id
        }), 202

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
def get_user_resumes(user_id):
    try:
        from src.core.database.supabase_client import get_supabase_client
        supabase = get_supabase_client()

        # 1. 撈取「原版」履歷
        resumes_resp = supabase.table("resume").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        resumes = resumes_resp.data if hasattr(resumes_resp, 'data') else []

        # 2. 撈取「優化版」履歷
        opts_resp = supabase.table("resume_optimization").select("*").eq("user_id", user_id).execute()
        opts = opts_resp.data if hasattr(opts_resp, 'data') else []

        combined_data = []
        # 做一個字典，方便快速尋找原版還活不活著
        alive_originals = {r.get("resume_id"): r for r in resumes}

        # 先把所有存活的「原版」塞進陣列
        for r in resumes:
            combined_data.append(r)

        # 接著處理「優化版」
        for opt in opts:
            parent_id = opt.get("resume_id")
            
            # 情況 A：如果原版還活著，我們複製原版的外殼
            if parent_id in alive_originals:
                parent_resume = alive_originals[parent_id]
                opt_item = parent_resume.copy()
            # 情況 B：【孤兒救援】如果原版已經被砍了，我們自己幫它捏一個外殼！
            else:
                opt_item = {
                    "resume_id": f"{parent_id}_opt_{opt.get('optimization_version', 1)}",
                    "resume_type": "uploaded_pdf",
                    "created_at": opt.get("created_at")
                }

            # 塞入優化版的專屬資料
            opt_item["resume_id"] = f"{parent_id}_opt_{opt.get('optimization_version', 1)}" 
            opt_item["resume_name"] = opt.get('resume_name', '✨ 獨立存在的 AI 優化版')
            # 這裡對齊你資料庫的結構
            opt_item["structured_data"] = {
                "professional_summary": opt.get("professional_summary"),
                "core_skills": opt.get("core_skills"),
                "professional_experience": opt.get("professional_experience")
            }
            opt_item["is_optimized"] = True 
            
            combined_data.append(opt_item)

        # 根據建立時間重新排序，確保最新的在最上面
        combined_data.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        return jsonify({"status": "success", "data": combined_data}), 200

    except Exception as e:
        print(f"🚨 /list API 發生錯誤: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
@resume_proc_bp.route('/save', methods=['POST'])
@resume_proc_bp.route('/optimize/save_to_resume', methods=['POST']) # 🌟 保險起見，增加別名以相容舊版前端
def save_processed_resume():
    try:
        req_data = request.json
        
        # 1. 接收前端傳來的資料
        resume_name = req_data.get('resume_name')
        resume_data = req_data.get('resume_data') or req_data.get('optimized_data')
        
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
            "resume_type": req_data.get('resume_type', "uploaded_pdf"),
            "structured_data": resume_data,
            "normalized_data": {},
            "is_primary": False,
            "is_embedded": False
        }

        # 5. 寫入資料庫
        response = supabase.table('resume').insert(insert_data).execute()
        print(f"✅ [System] 履歷 '{resume_name}' 已成功存入 Supabase!")

        # 6. 順便更新 user_profile 資料
        try:
            location_parts = [
                resume_data.get('addressCity', ''),
                resume_data.get('addressDistrict', ''),
                resume_data.get('addressDetail', '')
            ]
            location = "".join([p for p in location_parts if p])
            
            profile_update_data = {}
            if resume_data.get('name'):
                profile_update_data['full_name'] = resume_data['name']
            if location:
                profile_update_data['location'] = location
            if resume_data.get('education'):
                profile_update_data['education_background'] = resume_data['education']
            
            if profile_update_data:
                profile_update_data['updated_at'] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S+00")
                supabase.table('user_profile').update(profile_update_data).eq("user_id", user_id).execute()
                print(f"✅ [System] User {user_id} 的 user_profile 已同步更新!")
        except Exception as profile_e:
            print(f"⚠️ [System] 同步更新 user_profile 發生錯誤: {profile_e}")

        return jsonify({
            "status": "success", 
            "message": "履歷儲存成功",
            "data": response.data
        }), 200

    except Exception as e:
        print(f"🚨 [Error] 履歷儲存失敗: {e}")
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

@resume_proc_bp.route('/analyze', methods=['POST'])
def analyze_resume_with_ai():
    try:
        from worker.tasks import process_resume_analysis
        from core.redis_client import redis_client

        req_data = request.json
        user_id = req_data.get('user_id')

        if not user_id:
            return jsonify({"status": "error", "message": "缺少 user_id"}), 400

        tracking_id = f"job_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat()

        # 1. 在 Redis 紀錄 Job 初始狀態
        redis_client.hset(f"job:{tracking_id}", mapping={
            "status": "processing",
            "user_id": user_id,
            "result": "",
            "error": "",
            "created_at": now,
            "updated_at": now,
        })

        # 2. 觸發 Celery 任務
        process_resume_analysis.delay(user_id=user_id, job_id=tracking_id)

        return jsonify({
            "status": "success",
            "job_id": tracking_id,
            "task_id": tracking_id
        }), 202

    except Exception as e:
        print(f"🚨 [Fatal Error] AI 履歷診斷發生致命錯誤: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@resume_proc_bp.route('/optimize/generate', methods=['POST'])
def generate_optimized_resume():
    try:
        from worker.tasks import process_resume_optimization
        from core.redis_client import redis_client

        req_data = request.json
        user_id = req_data.get('user_id')
        
        if not user_id:
            return jsonify({"status": "error", "message": "缺少 user_id"}), 400

        tracking_id = f"job_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat()

        # 1. 在 Redis 紀錄 Job 初始狀態
        redis_client.hset(f"job:{tracking_id}", mapping={
            "status": "processing",
            "user_id": user_id,
            "result": "",
            "error": "",
            "created_at": now,
            "updated_at": now,
        })

        # 2. 觸發 Celery 任務
        process_resume_optimization.delay(user_id=user_id, job_id=tracking_id)

        return jsonify({
            "status": "success",
            "job_id": tracking_id,
            "task_id": tracking_id
        }), 202

    except Exception as e:
        print(f"🚨 [Fatal Error] AI 履歷優化發生致命錯誤: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
# ==========================================
# 🌟 儲存/更新優化後的履歷到資料庫 (無 ID 報錯修復版)
# ==========================================
@resume_proc_bp.route('/optimize/save', methods=['POST'])
def save_optimized_resume():
    try:
        req_data = request.json
        user_id = req_data.get('user_id')
        resume_id = req_data.get('original_resume_id')
        template_id = req_data.get('template_id')
        optimized_data = req_data.get('optimized_data', {})

        if not user_id or not resume_id:
            return jsonify({"status": "error", "message": "缺少 user_id 或 original_resume_id"}), 400

        print(f"🚀 [API] 準備更新 User {user_id} 的優化履歷...")

        from src.core.database.supabase_client import get_supabase_client
        supabase = get_supabase_client()

        # 🔧 輔助函式：確保要存入 jsonb 的欄位絕對是 list 或 dict
        def to_jsonb(val):
            if isinstance(val, list) or isinstance(val, dict):
                return val
            if isinstance(val, str) and val.strip():
                return [val]
            return []

        # 🌟 優先取得「原版履歷名稱」
        orig_name = "未命名履歷"
        try:
            orig_resp = supabase.table("resume").select("resume_name").eq("resume_id", resume_id).execute()
            if hasattr(orig_resp, 'data') and len(orig_resp.data) > 0:
                orig_name = orig_resp.data[0].get("resume_name", "未命名履歷")
        except Exception as e:
            print(f"⚠️ [API] 讀取原版履歷名稱時發生錯誤: {e}")

        # 🌟 準備要「更新」的資料
        update_data = {
            "professional_summary": optimized_data.get("professional_summary", ""),
            "autobiography": optimized_data.get("autobiography", ""),
            "resume_name": f"{orig_name}_優化",
            "professional_experience": to_jsonb(optimized_data.get("professional_experience")),
            "core_skills": to_jsonb(optimized_data.get("core_skills")),
            "projects": to_jsonb(optimized_data.get("projects")),
            "education": to_jsonb(optimized_data.get("education")),
            "template_color": {"template_id": template_id},
            "is_published": True
        }

        # ==========================================
        # 🌟 修正：不用找 'id' 欄位了，直接用 user_id 和 resume_id 雙重鎖定更新！
        # ==========================================
        
        # 1. 先檢查背景 Worker 是不是已經幫我們自動存檔了
        check_resp = supabase.table("resume_optimization") \
            .select("resume_id") \
            .eq("user_id", user_id) \
            .eq("resume_id", resume_id) \
            .execute()

        if hasattr(check_resp, 'data') and len(check_resp.data) > 0:
            # 找到 Worker 存的資料了！執行覆蓋更新 (Update)
            response = supabase.table('resume_optimization') \
                .update(update_data) \
                .eq("user_id", user_id) \
                .eq("resume_id", resume_id) \
                .execute()
            print("✅ [API] 優化履歷已成功【更新】！")
        else:
            # 萬一 Worker 偷懶沒存，我們就自己 Insert
            print("⚠️ [API] 找不到既有的優化紀錄，改為執行新增 (Insert)...")
            update_data["user_id"] = user_id
            update_data["resume_id"] = resume_id
            update_data["optimization_version"] = "1"
            update_data["llm_model_used"] = "gpt-4o"
            update_data["is_embedded"] = False
            response = supabase.table('resume_optimization').insert(update_data).execute()

        return jsonify({
            "status": "success",
            "message": "優化履歷儲存/更新成功",
            "data": response.data
        }), 200

    except Exception as e:
        print(f"🚨 [Error] 儲存/更新優化履歷失敗: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

        return jsonify({
            "status": "success",
            "message": "優化履歷儲存/更新成功",
            "data": response.data
        }), 200

    except Exception as e:
        print(f"🚨 [Error] 儲存/更新優化履歷失敗: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
# 🌟 注意路由改成了 <string:resume_id> 才能接收 "129_opt_1" 這種字串

@resume_proc_bp.route('/delete/<string:resume_id>', methods=['DELETE'])
def delete_resume(resume_id):
    try:
        from src.core.database.supabase_client import get_supabase_client
        supabase = get_supabase_client()

        print(f"\n===================================")
        print(f"🗑️ [DELETE API] 收到刪除請求，前端傳來的 ID 是: '{resume_id}'")

        if "_opt_" in str(resume_id):
            real_id_str = str(resume_id).split("_")[0]
            
            # 🎯 情況 A：這是被 Set Null 遺留下來的「孤兒優化版」
            if real_id_str == "None":
                print(f"🎯 判定為【獨立優化版】。正在清除沒有原版綁定的優化紀錄...")
                # 透過找尋 resume_id 為 null 的資料來刪除它
                result = supabase.table("resume_optimization").delete().is_("resume_id", "null").execute()
                print(f"✅ 獨立優化版刪除成功！")
                
            # 🎯 情況 B：這是正常的優化版 (原版還活著)
            else:
                real_id = int(real_id_str)
                print(f"🎯 判定為【優化版】。正在清除 resume_optimization (原版 ID: {real_id})...")
                result = supabase.table("resume_optimization").delete().eq("resume_id", real_id).execute()
                print(f"✅ 優化版刪除成功！(原版履歷安全存活)")
                
        else:
            # 🎯 情況 C：刪除原版
            real_id = int(resume_id)
            print(f"🎯 判定為【原版】。正在清除 resume 表格中的資料 (ID: {real_id})...")
            result = supabase.table("resume").delete().eq("resume_id", real_id).execute()
            print(f"✅ 原版刪除成功！")

        print(f"===================================\n")
        return jsonify({"status": "success", "message": "履歷刪除成功"}), 200

    except Exception as e:
        print(f"🚨 刪除履歷失敗: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500