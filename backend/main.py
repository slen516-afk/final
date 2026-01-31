from flask import Flask, request, jsonify
from flask_cors import CORS  # 確保這行有留著
import os
import sys
import time
from dotenv import load_dotenv

# 1. 載入環境變數
load_dotenv()

# 2. 路徑修正
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# 引入服務
from course_service import CourseService
from ocr_service.ocr_service import extract_text_from_image, load_model
from llm_service.llm_optimize import generate_resume_advice
from services.analysis_service import analyze_gap

app = Flask(__name__)

# 🔥🔥🔥 [終極修正] 使用 Flask-CORS 最純淨的設定 🔥🔥🔥
# 1. supports_credentials=True: 允許攜帶憑證 (Cookie/Auth)
# 2. 不指定 resources: 預設會套用到所有路徑
# 3. 不指定 origins: 預設會自動反射請求來源 (Reflect Origin)
CORS(app, supports_credentials=True)
# 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥

course_service = CourseService()
UPLOAD_FOLDER = os.path.join(current_dir, 'resumes')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 🚀 系統初始化
print("--- [Main] 正在喚醒 RTX 3070... 載入 Qwen2-VL-2B 模型 ---")
try:
    load_model()
    print("--- [Main] 模型載入成功！火力全開中 ---")
except Exception as e:
    print(f"⚠️ [Main] 模型載入失敗: {e}")

@app.route('/', methods=['GET'])
def health_check():
    return "✅ Backend Server is Running!"

# ==========================================================
# 核心功能
# ==========================================================
@app.route('/api/upload-resume', methods=['POST']) 
# ⚠️ 注意：移除了 methods=['OPTIONS']，交給 CORS 套件自動處理
def upload_resume():
    print("📢 [Debug] === 收到前端的 POST 請求 (/api/upload-resume) ===")
    
    if 'file' not in request.files: 
        print("❌ [Debug] 請求中沒有 file 欄位")
        return jsonify({"error": "No file"}), 400
        
    file = request.files['file']
    if file.filename == '': 
        print("❌ [Debug] 檔名為空")
        return jsonify({"error": "No selected file"}), 400

    try:
        filename = file.filename
        saved_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(saved_path)
        print(f"💾 [Debug] 檔案已存: {saved_path}")

        print("⚡ [Debug] 開始 OCR...")
        start_time = time.time()
        resume_text = extract_text_from_image(saved_path) 
        print(f"✅ [Debug] OCR 完成！耗時: {time.time() - start_time:.2f} 秒")

        print("🤖 [Debug] 正在呼叫 LLM...")
        ai_suggestion = generate_resume_advice(resume_text)

        return jsonify({
            "text": resume_text,
            "suggestion": ai_suggestion,
            "saved_at": saved_path
        })

    except Exception as e:
        print(f"❌ [Debug] 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# (其他 API 保持原樣...)
@app.route('/api/analyze', methods=['POST'])
def analyze_resume_gap():
    print("📢 [Debug] === 收到前端的 POST 請求 (/api/analyze) ===")
    try:
        data = request.json
        resume_text = data.get('resume_content', '')
        jd_text = data.get('jd_content', '')
        result = analyze_gap(resume_text, jd_text)
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        print(f"❌ [Debug] 分析失敗: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, port=5000, host='0.0.0.0')