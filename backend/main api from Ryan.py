from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import time
from dotenv import load_dotenv

# 1. 載入環境變數
load_dotenv()

# 2. 路徑設定 (確保能讀到其他資料夾的 module)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# 3. 嘗試引入服務
# 使用 try-except 是為了防止因為缺少某些依賴套件而導致連伺服器都開不起來
try:
    from course_service import CourseService
    from ocr_service.ocr_service import extract_text_from_image, load_model
    from llm_service.llm_optimize import generate_resume_advice
    from services.analysis_service import analyze_gap
except ImportError as e:
    print(f"⚠️ [Warning] 部分模組載入失敗: {e}")

app = Flask(__name__)

# 🔥🔥🔥 [關鍵修正] CORS 設定 🔥🔥🔥
# 這行讓前端 (localhost:5173) 可以順利連線，不會被擋
CORS(app, supports_credentials=True)

# 設定上傳資料夾
UPLOAD_FOLDER = os.path.join(current_dir, 'resumes')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 🚀 系統初始化 (載入 AI 模型)
print("--- [Main] 系統啟動中 ---")
try:
    # 如果你的電腦跑不動模型，可以把下面這行 load_model() 註解掉
    load_model()
    print("--- [Main] AI 模型載入成功 ---")
except Exception as e:
    print(f"⚠️ [Main] 模型載入失敗 (不影響登入功能): {e}")


# ==========================================================
# 基礎路由
# ==========================================================
@app.route('/', methods=['GET'])
def health_check():
    return "✅ Backend Server is Running!"

# ==========================================================
# 🔑 1. 登入功能 (保留這個，因為這是你最重要的入口)
# ==========================================================
@app.route('/login', methods=['POST', 'OPTIONS'])
@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    # 處理 CORS 預檢請求
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    print("📢 [Debug] === 收到登入請求 ===")
    
    try:
        data = request.get_json()
        email = data.get('email')
        
        # 這裡只做模擬登入，不連資料庫
        return jsonify({
            "message": "Login successful",
            "access_token": "fake-jwt-token-123",
            "email": email or "user@example.com",
            "user_id": 1
        }), 200
        
    except Exception as e:
        print(f"❌ [Debug] 登入錯誤: {e}")
        return jsonify({"error": str(e)}), 500

# ==========================================================
# 📂 2. 上傳履歷功能 (核心功能)
# ==========================================================
@app.route('/api/upload-resume', methods=['POST']) 
def upload_resume():
    print("📢 [Debug] === 收到履歷上傳請求 ===")
    
    if 'file' not in request.files: 
        return jsonify({"error": "No file"}), 400
        
    file = request.files['file']
    if file.filename == '': 
        return jsonify({"error": "No selected file"}), 400

    try:
        filename = file.filename
        saved_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(saved_path)
        print(f"💾 檔案已存: {saved_path}")

        # OCR 辨識
        print("⚡ 開始 OCR...")
        resume_text = extract_text_from_image(saved_path) 
        
        # LLM 分析
        print("🤖 開始 AI 分析...")
        ai_suggestion = generate_resume_advice(resume_text)

        return jsonify({
            "text": resume_text,
            "suggestion": ai_suggestion,
            "saved_at": saved_path
        })

    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        return jsonify({"error": str(e)}), 500

# ==========================================================
# 📊 3. 職缺差距分析功能
# ==========================================================
@app.route('/api/analyze', methods=['POST'])
def analyze_resume_gap():
    print("📢 [Debug] === 收到職缺分析請求 ===")
    try:
        data = request.json
        resume_text = data.get('resume_content', '')
        jd_text = data.get('jd_content', '')
        
        # 呼叫分析服務
        result = analyze_gap(resume_text, jd_text)
        return jsonify({"status": "success", "data": result})
        
    except Exception as e:
        print(f"❌ 分析失敗: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    print("🚀 伺服器啟動中: http://localhost:5000")
    app.run(debug=True, port=5000, host='0.0.0.0')