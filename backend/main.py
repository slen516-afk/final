from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# 假設你的 ocr_service 和 llm_service 都在根目錄，需要加入路徑以便 import
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# --- 【修正 1】 這裡引入的是正確的新函式名稱 ---
from ocr_service.ocr_service import extract_text_from_image
from llm_service.llm_optimize import generate_resume_advice
# -------------------------------------

app = Flask(__name__)
CORS(app) # 允許跨域請求

@app.route('/api/upload-resume', methods=['POST'])
def upload_resume():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # 1. 暫存檔案
        temp_path = f"./temp_{file.filename}"
        file.save(temp_path)

        # --- 【修正 2】 呼叫 OCR：使用上面 Import 的正確名稱 ---
        # 原本寫 image_to_text_function (這是錯的，找不到定義)
        print("正在執行 OCR...")
        resume_text = extract_text_from_image(temp_path) 

        # --- 【修正 3】 呼叫 LLM：使用上面 Import 的正確名稱 ---
        # 原本寫 optimize_resume_function (這也是錯的)
        print("正在執行 LLM 分析...")
        ai_suggestion = generate_resume_advice(resume_text)

        # 4. 清理暫存檔
        if os.path.exists(temp_path):
            os.remove(temp_path)

        # --- 【修正 4】 回傳 Key：改成跟前端 ResumeUploader 對應的名字 ---
        # 前端在找 result.text 和 result.suggestion，所以這裡要改
        return jsonify({
            "text": resume_text,           # 原本是 original_text (前端會找不到)
            "suggestion": ai_suggestion    # 原本是 optimized_result (前端會找不到)
        })

    except Exception as e:
        print(f"發生錯誤: {e}") # 印出錯誤方便 Debug
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)