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
# 注意：請確保你的 ocr_service.py 已經更新為支援 PDF 的版本
from ocr_service.ocr_service import extract_text_from_image, load_model
from llm_service.llm_optimize import generate_resume_advice 

app = Flask(__name__)
# 允許所有網域來源連線，解決前端連線被擋的問題
CORS(app, resources={r"/*": {"origins": "*"}})

# =================設定區=================
# 設定履歷存放的資料夾名稱
UPLOAD_FOLDER = os.path.join(current_dir, 'resumes')
# 確保資料夾存在
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

# 👇👇👇【新增這裡】這就是解決 "404" 錯誤的關鍵 👇👇👇
@app.route('/', methods=['GET'])
def health_check():
    """
    健康檢查路由。
    當瀏覽器或前端程式訪問 http://127.0.0.1:5000/ 時，
    會回傳這個訊息，證明後端活著。
    """
    return "✅ Backend Server is Running! (後端伺服器運作中)"
# 👆👆👆【新增結束】👆👆👆


@app.route('/api/upload-resume', methods=['POST'])
def upload_resume():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({"error": "No selected file"}), 400

    saved_path = None
    try:
        # 1. 存檔 (存到 backend/resumes 資料夾)
        filename = file.filename
        saved_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(saved_path)
        print(f"💾 履歷已儲存至: {saved_path}")

        # 2. 執行 OCR
        start_time = time.time()
        print("⚡ 正在進行 AI 辨識 (OCR)...")
        
        # 這裡會呼叫 ocr_service.py (支援 PDF/圖片)
        resume_text = extract_text_from_image(saved_path) 
        
        ocr_time = time.time() - start_time
        print(f"✅ OCR 完成！耗時: {ocr_time:.2f} 秒")

        # 3. 執行 LLM 分析
        print("🤖 正在生成建議 (LLM)...")
        ai_suggestion = generate_resume_advice(resume_text)

        return jsonify({
            "text": resume_text,
            "suggestion": ai_suggestion,
            "saved_at": saved_path
        })

    except Exception as e:
        print(f"❌ 錯誤: {e}")
        # 如果是開發階段，把詳細錯誤回傳給前端方便除錯
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # host='0.0.0.0' 代表允許區域網路內的其他電腦也能連線 (例如手機)
    app.run(debug=False, port=5000, host='0.0.0.0')