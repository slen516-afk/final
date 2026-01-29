from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import time
from dotenv import load_dotenv
from course_service import CourseService
# ❌ [刪除] 原本在這裡的 import services... 會導致找不到檔案

# 1. 載入環境變數
load_dotenv()

# 2. 路徑修正 (這段執行完，Python 才能看到根目錄的資料夾)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# 引入 OCR 和 LLM 服務
from ocr_service.ocr_service import extract_text_from_image, load_model
from llm_service.llm_optimize import generate_resume_advice, generate_project_suggestions_from_skills

# ✅ [修正] 把它搬到這裡！(在 sys.path.append 之後)
# 這樣無論你的 services 資料夾是在 backend 還是根目錄，Python 都找得到
from services.analysis_service import analyze_gap

app = Flask(__name__)
# 允許所有網域來源連線
CORS(app, resources={r"/*": {"origins": "*"}})

course_service = CourseService()

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
    if 'file' not in request.files:
        return jsonify({"error": "沒有上傳檔案"}), 400
    
    file = request.files['file'] # 這裡的 'file' 對應前端 formData.append('file', ...) 的名字
    
    if file.filename == '':
        return jsonify({"error": "檔案名稱為空"}), 400

    # 1. 這裡先做 OCR (模擬)
    # text_content = your_ocr_function(file) 
    # 暫時用假資料測試，讓你先跑通流程
    print(f"收到檔案: {file.filename}")
    resume_text = "模擬的 OCR 文字內容：熟悉 Python, React, Flask..." 

    # 2. 這裡呼叫 AI (把你原本的 AI 邏輯接回來)
    # suggestions = call_gemini_or_gpt(resume_text)

    # 3. 回傳格式 (保持跟前端對接的格式一致)
    return jsonify({
        "suggestions": [
            {
                "title": "測試專案 A (來自檔案)",
                "difficulty": "入門",
                "description": f"我們收到了你的檔案 {file.filename}，這是測試回傳。",
                "tech_keywords": ["Python", "OCR"]
            },
            # ... 其他建議
        ]
    })

# ----------------------------------------------------------
# F-04: 學習資源推薦 (已串接 YouTube API 與 Sunny 推薦邏輯)
# ----------------------------------------------------------
@app.route('/api/learning/recommendations', methods=['POST'])
def recommend_learning_resources():
    incoming_data = request.get_json() or {}
    print(f"📡 [F-04] 收到學習推薦請求: {incoming_data}")

    # 1. 取得使用者興趣
    user_input = incoming_data.get('user_interest') or incoming_data.get('keywords') or ""

    if not user_input:
        return jsonify({"status": "error", "message": "請提供 user_interest 或 keywords"}), 400

    # 2. 呼叫服務層處理
    recommendations = course_service.get_recommendations(user_input)

    return jsonify({
        "status": "success",
        "query": user_input,
        "data": recommendations
    })

# ----------------------------------------------------------
# C-01 & C-03 (異步處理模擬，目前沒用到但保留)
# ----------------------------------------------------------
@app.route('/api/resumes/upload', methods=['POST'])
def upload_resume_async():
    if 'file' not in request.files: return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    filename = file.filename
    fake_task_id = "task_5566"
    return jsonify({"message": "File uploaded", "resume_id": fake_task_id})

@app.route('/api/resumes/<resume_id>/status', methods=['GET'])
def check_resume_status(resume_id):
    return jsonify({"id": resume_id, "status": "completed", "progress": 100})

# ----------------------------------------------------------
# 🔥🔥🔥 新增的分析 API 🔥🔥🔥
# ----------------------------------------------------------
@app.route('/api/analyze', methods=['POST'])
def analyze_resume_gap():
    print("收到分析請求...") # 加個 log 方便除錯
    data = request.json
    resume_text = data.get('resume_content', '')
    jd_text = data.get('jd_content', '')
    
    # 呼叫 analysis_service 裡的邏輯
    result = analyze_gap(resume_text, jd_text)
    
    return jsonify({
        "status": "success",
        "data": result
    })

if __name__ == '__main__':
    print("--- 目前所有的 API 路徑 ---")
    print(app.url_map)
    print("-------------------------")
    app.run(debug=False, port=5000, host='0.0.0.0')