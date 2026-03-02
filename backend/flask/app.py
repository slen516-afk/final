# 後端入口統一變更為main.py，app.py僅保留Flask入口
# 組裝 Flask App、註冊路由與掛載 OCR 模型

import sys
import os
import json
from crewai import Agent, Task, Crew
import uuid
from flask import Flask, app, jsonify
from flask_cors import CORS
from service.llm_service.src.features.course.tools import CourseRecommendationTool


# ====== 1. 解決路徑問題 (修正版) =================

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
service_dir = os.path.join(backend_dir, "service")
sys.path.append(service_dir)

def create_app():
    app = Flask(__name__)
    CORS(app, origins=["http://localhost:3000"])  # 啟用 CORS

    # --- Celery 配置 ---
    app.config.update(
        CELERY_BROKER_URL='redis://redis:6379/0',
        CELERY_RESULT_BACKEND='redis://redis:6379/0'
    )

    # --- OCR模型預載入 ---
    try:
        from service.ocr_service.ocr_service import ResumeOCRService

        print("[System] 正在初始化 OCR 模型...")
        try:
        # ✅ 先建立管家，再請管家做事
            ocr_service = ResumeOCRService() 
            ocr_service.load_model()
        except Exception as e:
            print(f"[Error] OCR 模型初始化失敗: {e}")
        
    except ImportError as e:
        print(f"[Critical] 無法引入 ocr_service！請檢查路徑。錯誤: {e}")
        # 這裡不 exit，避免為了 OCR 讓整個 App 掛掉
        app.config["OCR_HANDLER"] = None
    

    # --- 註冊路由 ---
    from api.auth import auth_bp
    from api.user_preference import user_preference_bp
    from api.resume import resume_bp
    from api.ocr import ocr_bp
    from api.analysis import analysis_bp
    from api.resume_processing import resume_proc_bp
    from api.recommendation import rec_bp
    from api.async_tasks import api_bp as async_tasks_bp

    # 1. 認證功能模組
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    # 2. 履歷核心模組
    app.register_blueprint(resume_bp, url_prefix="/api/resumes")

    # 3. 履歷處理模組
    app.register_blueprint(resume_proc_bp, url_prefix="/api/resume_process")

    # 4. 分析報告模組
    app.register_blueprint(ocr_bp, url_prefix="/api/ocr")
    app.register_blueprint(analysis_bp, url_prefix="/api/analysis")

    # 5. 使用者偏好與推薦模組
    app.register_blueprint(user_preference_bp, url_prefix="/api/preferences")
    app.register_blueprint(rec_bp, url_prefix="/api")

    # 6. 非同步任務模組
    app.register_blueprint(async_tasks_bp, url_prefix="/api/tasks")

    # --- 系統健康檢查 ---
    @app.route("/health", methods=["GET"])
    def health_check():
        return (
            jsonify(
                {
                    "status": "healthy",
                    "service": "Career Pilot API",
                    "ocr_loaded": (
                        "ready" if app.config.get("OCR_HANDLER") else "offline"
                    ),
                }
            ),
            200,
        )

    return app



