# 後端入口統一變更為 main.py，app.py 僅保留 Flask App 組裝邏輯
# 組裝 Flask App、註冊路由與掛載 OCR 模型

import os
from flask import Flask, jsonify
from flask_cors import CORS

# API Blueprints
from api.auth import auth_bp
from api.user_preference import user_preference_bp
from api.resume import resume_bp
from api.export import export_bp
from api.analysis import analysis_bp
from api.resume_processing import resume_proc_bp
from api.recommendation import rec_bp
from api.ocr import ocr_bp
from api.cover_letter import cover_letter_bp

try:
    from api.async_tasks import api_bp as async_tasks_bp
    _has_async_tasks = True
except ImportError as e:
    print(f"[Warning] 無法引入 async_tasks Blueprint: {e}")
    _has_async_tasks = False

# ====== 3. OCR Service 引入 (防彈版) ==========================
# 🌟 1. 先宣告所有變數，徹底消滅 NameError！
ResumeOCRService = None
load_model = None
extract_text_from_image = None

# 🌟 2. 嘗試引入各種版本的 OCR
try:
    from service.ocr_service.ocr_service import ResumeOCRService
except ImportError:
    pass

try:
    from service.ocr_service.ocr_service import load_model, extract_text_from_image
except ImportError:
    pass


# ====== Flask App Factory ====================================================
def create_app():
    app = Flask(__name__)
    CORS(app)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    upload_folder = os.path.join(current_dir, 'uploads')
    os.makedirs(upload_folder, exist_ok=True)

# ====== 5. OCR 模型初始化 =======================================
    print("------------------------------------------------")
    print("[System] 正在初始化 Flask 伺服器...")

    # 在測試模式或指定跳過時，不載入大型模型
    # if app.config.get("TESTING") or os.getenv("SKIP_OCR") == "True":
    #     print("[System] 測試模式或 SKIP_OCR=True，跳過 OCR 模型載入。")
    #     app.config["OCR_HANDLER"] = None
    #     app.extract_text_from_image = None
    # else:
    try:
    # ✅ 優先使用新版：ResumeOCRService
        if ResumeOCRService is not None:
            ocr_service = ResumeOCRService()
            ocr_service.load_model()
            app.config["OCR_HANDLER"] = ocr_service.extract_text_from_image
            app.extract_text_from_image = ocr_service.extract_text_from_image
            print("[System] ✅ OCR 模型初始化完成 (使用 ResumeOCRService)")
        
    # ✅ 備用方案：使用舊版 load_model
        elif load_model is not None:
            load_model()
            app.config["OCR_HANDLER"] = extract_text_from_image
            app.extract_text_from_image = extract_text_from_image
            print("[System] ✅ OCR 模型初始化完成 (使用 load_model)")
        
    # ❌ 都沒找到
        else:
            app.config["OCR_HANDLER"] = None
            app.extract_text_from_image = None
            print("[Warning] 找不到任何 OCR 服務，已略過載入。")

    except Exception as e:
        print(f"[Error] OCR 模型初始化失敗: {e}")
        app.config["OCR_HANDLER"] = None
        app.extract_text_from_image = None


# ====== 6. 註冊路由 ====================================================
# 1. 認證功能
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

# 2. 履歷核心
    app.register_blueprint(resume_bp, url_prefix='/api/resumes')
    app.register_blueprint(export_bp, url_prefix='/api/resumes')

# 3. 履歷處理
    app.register_blueprint(resume_proc_bp, url_prefix='/api/resume_process')

# 4. 分析報告
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    app.register_blueprint(ocr_bp, url_prefix='/api/ocr')
    app.register_blueprint(cover_letter_bp, url_prefix="/api/cover_letter")

# 5. 使用者偏好與推薦
    app.register_blueprint(user_preference_bp, url_prefix='/api')
    app.register_blueprint(rec_bp, url_prefix='/api')

# 6. 非同步任務 (選用)
    if _has_async_tasks:
        app.register_blueprint(async_tasks_bp, url_prefix='/api/tasks')

# ====== 7. 系統健康檢查 ================================================
    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "healthy",
            "service": "Career Pilot API",
            "ocr_loaded": "ready" if app.config.get("OCR_HANDLER") else "offline",
        }), 200

    return app
