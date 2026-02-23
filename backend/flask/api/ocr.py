import sys
import os
import uuid
import json
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, current_app

# 解決跨資料夾 Import core 的問題
current_dir = os.path.dirname(os.path.abspath(__file__))
flask_dir = os.path.dirname(current_dir)
backend_dir = os.path.dirname(flask_dir)

if backend_dir not in sys.path:
    sys.path.append(backend_dir)

UPLOAD_FOLDER = os.path.join(flask_dir, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

from core.supabase_client import supabase

ocr_bp = Blueprint('ocr', __name__) 

@ocr_bp.route('/', methods=['POST'])
def run_ocr_api():
    extract_func = getattr(current_app, 'extract_text_from_image', None)
    if not extract_func:
        return jsonify({"error": "OCR Service not available"}), 500

    # 這裡的 template_id 完美對應到了你的 resume_template 表！
    template_id = request.form.get("template_id", 1)

    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    files = request.files.getlist('file')
    if not files or files[0].filename == '':
        return jsonify({"error": "No file selected"}), 400

    # 查詢 11-20 號的空位
    try:
        response = supabase.table("resume").select("user_id").gte("user_id", 11).lte("user_id", 20).execute()
        used_ids = [row['user_id'] for row in response.data]
        available_ids = [uid for uid in range(11, 21) if uid not in used_ids]
    except Exception as e:
        print(f"[API] ❌ 查詢空位失敗: {e}")
        available_ids = []

    processed_results = []

    for index, file in enumerate(files):
        if index >= len(available_ids):
            msg = "11-20 號會員已全部配發完畢，無法再新增。"
            print(f"[API] ⚠️ {msg}")
            processed_results.append({"filename": file.filename, "status": "skipped", "message": msg})
            continue

        dynamic_user_id = available_ids[index]
        filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        try:
            now_str = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S+00')

            print(f"\n[API] 📦 正在處理批次檔案: {file.filename} (遞補給 User ID: {dynamic_user_id})")


            # 寫入第 0 張表： upload_event (先取得事件 ID)
            insert_event_payload = {
                "user_id": int(dynamic_user_id),
                "file_name": file.filename,
                "file_path": file_path,
                "upload_type": "batch_resume",
                "status": "processing",  # 先標記為處理中
                "uploaded_at": now_str,
                "metadata": {}
            }
            event_response = supabase.table("upload_event").insert(insert_event_payload).execute()
            inserted_event_id = event_response.data[0]['event_id']
            print(f"[API] 成功建立 upload_event！Event ID: {inserted_event_id}")

            # 呼叫 Qwen 取得 JSON 字典
            extracted_data = extract_func(file_path)

            if isinstance(extracted_data, dict) and "error" in extracted_data:
                 print(f"[API] ❌ {file.filename} 解析失敗: {extracted_data['error']}")
                 # OCR 失敗，把 event 狀態更新為 failed
                 supabase.table("upload_event").update({"status": "failed"}).eq("event_id", inserted_event_id).execute()
                 processed_results.append({"filename": file.filename, "status": "error", "message": extracted_data["error"]})
                 continue

            # OCR 成功，把 event 狀態更新為 completed
            supabase.table("upload_event").update({"status": "completed"}).eq("event_id", inserted_event_id).execute()


            # 寫入第一張表： resume
            insert_resume_payload = {
                "user_id": int(dynamic_user_id),     
                "template_id": int(template_id),     
                "resume_type": "uploaded",
                "structured_data": extracted_data.get("structured_data", {}),
                "normalized_data": extracted_data.get("normalized_data", {}),
                "vector_id": str(uuid.uuid4()),  
                "is_embedded": False,            
                "is_primary": True,
                "created_at": now_str,           
                "updated_at": now_str
            }
            resume_response = supabase.table("resume").insert(insert_resume_payload).execute()
            inserted_resume_id = resume_response.data[0]['resume_id']
            print(f"[API] 💾 成功寫入 resume 表！Resume ID: {inserted_resume_id}")


            # 寫入第二張表： ocr_result
            insert_ocr_payload = {
                "resume_id": inserted_resume_id, 
                "event_id": inserted_event_id,          # 🔥 完美對應剛剛產生的 Event ID！
                "raw_text": json.dumps(extracted_data, ensure_ascii=False),
                "extracted_data": extracted_data,
                "confidence_score": 0.95,               
                "is_manual_review_needed": False,       
                "ocr_status": "completed",              
                "processed_at": now_str                 
            }
            ocr_response = supabase.table("ocr_result").insert(insert_ocr_payload).execute()
            print(f"[API] 💾 成功寫入 ocr_result 表！")

          
            # 寫入第三張表： user_profile
            try:
                # 1. 改去 normalized_data 裡面的 contact 找名字
                contact_info = extracted_data.get("normalized_data", {}).get("contact", {})
                
                experiences = extracted_data.get("structured_data", {}).get("experience", [])
                educations = extracted_data.get("structured_data", {}).get("education", [])
                work_history = extracted_data.get("normalized_data", {}).get("work_history", [])

                total_years = 0
                for job in work_history:
                    try:
                        total_years += float(job.get("duration_years", 0))
                    except (ValueError, TypeError):
                        pass

                current_pos = experiences[0].get("title", "") if experiences else ""
                edu_bg = educations[0].get("details", "") if educations else ""

                # 2. 組裝 Payload，使用正確的 contact_info
                insert_profile_payload = {
                    "user_id": int(dynamic_user_id),
                    "github_repo": contact_info.get("github", ""),      
                    "full_name": contact_info.get("name", ""),          
                    "location": contact_info.get("location", ""),       
                    "years_of_experience": int(total_years),
                    "current_position": current_pos,
                    "education_background": edu_bg,
                    "privacy_settings": {"privacy": extracted_data.get("structured_data", {}).get("privacy", "public")},
                    "updated_at": now_str
                }
                profile_response = supabase.table("user_profile").insert(insert_profile_payload).execute()
                print(f"[API] 成功同步寫入 user_profile 表！")
            except Exception as profile_e:
                print(f"[API] user_profile 寫入失敗: {profile_e}")

            processed_results.append({
                "filename": file.filename,
                "status": "success",
                "resume_id": inserted_resume_id,
                "data": extracted_data
            })

        except Exception as e:
            print(f"[API] ❌ {file.filename} 處理發生錯誤: {e}")
            processed_results.append({"filename": file.filename, "status": "error", "message": str(e)})
        
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    return jsonify({
        "status": "batch_completed",
        "total_processed": len(files),
        "results": processed_results
    })