import sys
import os
import uuid



# ====== 1. 解決路徑問題 (修正版) =================
# 取得目前 app.py 的資料夾路徑 (backend/flask)
current_dir = os.path.dirname(os.path.abspath(__file__))
# 取得 backend 資料夾路徑
backend_dir = os.path.dirname(current_dir)

if backend_dir not in sys.path:
    sys.path.append(backend_dir)

# 取得 service 資料夾路徑
service_dir = os.path.join(backend_dir, 'service')
# 🔥 關鍵修正：因為你的 .py 檔躲在 service 裡面的一個子資料夾，我們要指到那裡
ocr_inner_dir = os.path.join(service_dir, 'ocr_service')

# 把這兩個路徑都加入搜尋清單 (保險起見)
sys.path.append(service_dir)
sys.path.append(ocr_inner_dir)  # <--- 加入這行，Python 就能直接找到裡面的 ocr_service.py 了！



from flask import Flask, request, jsonify
from flask_cors import CORS
# from core.supabase_client import supabase
from datetime import datetime
from api.auth import auth_bp
from api.user_preference import user_preference_bp
from api.resume import resume_bp
from api.analysis import analysis_bp
from api.resume_processing import resume_proc_bp 
from api.recommendation import rec_bp
from api.ocr import ocr_bp       

try:
    from ocr_service import load_model, extract_text_from_image
    print(f"[System] 成功引入 OCR Service")
except ImportError as e:
    print(f"[Critical] 無法引入 ocr_service！請檢查路徑。錯誤: {e}")
    # 這裡不 exit，避免為了 OCR 讓整個 App 掛掉
    load_model = None
    extract_text_from_image = None




app = Flask(__name__)
CORS(app)
app.extract_text_from_image = extract_text_from_image  # 把 OCR 的核心函式掛到 app 上，讓 Blueprint 可以呼叫
UPLOAD_FOLDER = os.path.join(current_dir, 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

print("------------------------------------------------")
print("[System] 正在初始化 Flask 伺服器...")
if load_model:
    try:
        print("[System] 正在預載入 Qwen 模型...")
        load_model()  # <-讓模型在伺服器一啟動就載入進顯示卡/記憶體
        print("[System]  模型載入完成！")
    except Exception as e:
        print(f"[System] 模型載入失敗: {e}")
print("------------------------------------------------")


app.register_blueprint(auth_bp, url_prefix='/api/auth')
# 履歷分析
app.register_blueprint(user_preference_bp, url_prefix='/api')
app.register_blueprint(resume_bp, url_prefix='/api/resumes')
app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
# 履歷處理
app.register_blueprint(resume_proc_bp, url_prefix='/api/resumes')
# 推薦系統
app.register_blueprint(rec_bp, url_prefix='/api')
app.register_blueprint(ocr_bp, url_prefix='/api/ocr')


if __name__ == '__main__':
    print("\n====== 目前註冊的所有 API 路徑 ======")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule}") 
    app.run(debug=False)
    