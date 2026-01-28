from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import time
from dotenv import load_dotenv

# 1. 載入環境變數
load_dotenv()

# 2. 路徑修正 (確保找得到 ocr_service)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# 引入 OCR 和 LLM 服務
from ocr_service.ocr_service import extract_text_from_image, load_model
# 👇👇👇【修改這裡】記得引入新的函式 generate_project_suggestions_from_skills
from llm_service.llm_optimize import generate_resume_advice, generate_project_suggestions_from_skills

app = Flask(__name__)
# 允許所有網域來源連線
CORS(app, resources={r"/*": {"origins": "*"}})

# =================設定區=================
UPLOAD_FOLDER = os.path.join(current_dir, 'resumes')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
# =======================================

# 🚀 系統初始化
print("--- [Main] 正在喚醒 RTX 3070... 載入 Qwen2-VL-2B 模型 ---")
try:
    load_model()
    print("--- [Main] 模型載入成功！火力全開中 ---")
except Exception as e:
    print(f"⚠️ [Main] 模型載入失敗 (請檢查是否已安裝 torchvision): {e}")

@app.route('/', methods=['GET'])
def health_check():
    return "✅ Backend Server is Running! (後端伺服器運作中)"


# ==========================================================
# 核心功能：上傳履歷 -> OCR -> LLM 大禮包分析
# ==========================================================
@app.route('/api/upload-resume', methods=['POST'])
def upload_resume():
    print("--- [Debug] 收到上傳請求 ---")
    
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({"error": "No selected file"}), 400

    saved_path = None
    try:
        # 1. 存檔
        filename = file.filename
        saved_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(saved_path)
        print(f"💾 履歷已儲存至: {saved_path}")

        # 2. 執行 OCR
        start_time = time.time()
        print("⚡ 正在進行 AI 辨識 (OCR)...")
        resume_text = extract_text_from_image(saved_path) 
        ocr_time = time.time() - start_time
        print(f"✅ OCR 完成！耗時: {ocr_time:.2f} 秒")

        # 3. 執行 LLM 分析 (回傳大禮包 JSON)
        print("🤖 正在生成全方位建議 (LLM)...")
        ai_suggestion = generate_resume_advice(resume_text)

        return jsonify({
            "text": resume_text,
            "suggestion": ai_suggestion, # 這裡已經是 Dict 物件了
            "saved_at": saved_path
        })

    except Exception as e:
        print(f"❌ 錯誤: {e}")
        return jsonify({"error": str(e)}), 500


# ==========================================================
# 獨立功能區：手動輸入查詢 (Postman 測試用)
# ==========================================================

# ----------------------------------------------------------
# F-03: 專案建議 (手動輸入 JSON 查詢)
# ----------------------------------------------------------
@app.route('/api/projects/suggestions', methods=['POST'])
def suggest_projects():
    try:
        # 1. 嘗試讀取 JSON (Postman 請選 Raw -> JSON)
        data = request.get_json()
        
        # 防呆：如果使用者還是用 Form-data 上傳檔案，這裡會是 None
        if not data:
            return jsonify({
                "error": "格式錯誤：請使用 application/json 格式，並提供 skills 欄位",
                "hint": "在 Postman 中請選擇 Body -> Raw -> JSON"
            }), 415 # 415 Unsupported Media Type

        skills = data.get('skills', [])
        interests = data.get('interests', "")
        
        print(f"📡 [F-03] 收到專案建議請求 - 技能: {skills}, 興趣: {interests}")

        # 2. 👇👇👇【修改重點】真正呼叫 AI 進行分析 👇👇👇
        # 不再回傳假資料，而是把參數丟給 Gemini
        result = generate_project_suggestions_from_skills(skills, interests)
        
        return jsonify(result)

    except Exception as e:
        print(f"❌ [F-03] 錯誤: {e}")
        return jsonify({"error": str(e)}), 500

# ----------------------------------------------------------
# F-04: 學習資源推薦 (目前仍是模擬資料，可依樣畫葫蘆改成 AI)
# ----------------------------------------------------------
@app.route('/api/learning/recommendations', methods=['POST'])
def recommend_learning_resources():
    incoming_data = request.get_json() or {}
    print(f"📡 [F-04] 收到學習推薦請求: {incoming_data}")

    interest = incoming_data.get('user_interest', '').lower()
    
    recommendations = [
        {"title": "全端工程師路線圖", "url": "https://roadmap.sh/full-stack", "type": "article"},
        {"title": "Google 機器學習速成", "url": "https://developers.google.com/machine-learning/crash-course", "type": "course"}
    ]

    if 'python' in interest:
        recommendations.insert(0, {"title": "Python 官方文件", "url": "https://docs.python.org/3/", "type": "doc"})

    return jsonify({
        "status": "success",
        "data": recommendations
    })

# ----------------------------------------------------------
# C-01 & C-03 (異步處理模擬，目前沒用到但保留)
# ----------------------------------------------------------
@app.route('/api/resumes/upload', methods=['POST'])
def upload_resume_async():
    # ... (保留你原本的模擬程式碼)
    if 'file' not in request.files: return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    filename = file.filename
    fake_task_id = "task_5566"
    return jsonify({"message": "File uploaded", "resume_id": fake_task_id})

@app.route('/api/resumes/<resume_id>/status', methods=['GET'])
def check_resume_status(resume_id):
    # ... (保留你原本的模擬程式碼)
    return jsonify({"id": resume_id, "status": "completed", "progress": 100})


if __name__ == '__main__':
    print("--- 目前所有的 API 路徑 ---")
    print(app.url_map)
    print("-------------------------")
    app.run(debug=False, port=5000, host='0.0.0.0')