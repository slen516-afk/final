import os
from flask import Flask, jsonify
from flask_cors import CORS
import traceback  # 確保最上面有引入這個

# API Blueprints
from api.auth import auth_bp
from api.user_preference import user_preference_bp
from api.resume import resume_bp
from api.analysis import analysis_bp
from api.resume_processing import resume_proc_bp
from api.recommendation import rec_bp
from api.ocr import ocr_bp
from api.questionnaire import questionnaire_bp
from api.cover_letter import cover_letter_bp
from api.gap_analysis import gap_analysis_bp

try:
    from api.async_tasks import api_bp as async_tasks_bp
    _has_async_tasks = True
except ImportError as e:
    print(f"[Warning] 無法引入 async_tasks Blueprint: {e}")
    _has_async_tasks = False


# ====== 2. Worker 狀態檢查器 ======
def check_worker_health():
    """
    檢查是否有任何活躍的 Celery Worker。
    此函數需要由 Flask Context 或已有正確 sys.path 的環境呼叫。
    """
    try:
        import sys
        import os
        
        # 嘗試動態補足路徑以防引入失敗 (Worker 任務依賴 llm_service/src)
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        llm_src = os.path.join(backend_dir, "service", "llm_service", "src")
        if os.path.exists(llm_src) and llm_src not in sys.path:
            sys.path.insert(0, llm_src)

        from worker.celery_app import celery_app
        # 嘗試獲取所有活躍節點的狀態 (改用 ping 較輕量且快，timeout 也調高一點)
        insp = celery_app.control.inspect(timeout=2.0)
        pings = insp.ping()
        
        if pings:
            nodes = list(pings.keys())
            print(f"✅ [Worker] 偵測到 {len(pings)} 個活躍節點: {nodes}")
            return True, nodes
        else:
            print("🚨 [Worker] 警告：目前沒有任何活躍的 Celery Worker 在線！非同步任務將無法執行。")
            return False, []
    except Exception as e:
        print(f"❌ [Worker] 無法與 Broker 通訊或檢查失敗: {e}")
        return False, []

# ====== 3. OCR Service 引入 (防彈版) ==========================
# 🌟 1. 先宣告所有變數，徹底消滅 NameError！
ResumeOCRService = None
load_model = None
extract_text_from_image = None

# 🌟 2. 嘗試引入各種版本的 OCR
try:
    from service.ocr_service.ocr_service import ResumeOCRService
    print("[System] 成功找到 ResumeOCRService 模組庫！")
except Exception as e:
    print(f"🚨 [Fatal Error] OCR 服務檔案 (ocr_service.py) 引入失敗：{e}")
    print("👇👇👇 詳細錯誤追蹤 👇👇👇")
    traceback.print_exc()  # 這行會把真正的兇手連根拔起！
    print("👆👆👆 詳細錯誤追蹤 👆👆👆")




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
    
    # 檢查 Worker 狀態
    worker_ok, _ = check_worker_health()
    app.config["WORKER_ONLINE"] = worker_ok

    try:
        # ✅ 優先使用新版：ResumeOCRService
        if ResumeOCRService is not None:
            ocr_service = ResumeOCRService()
            
            # ⚠️ 注意：新版 OpenAI+PaddleOCR 已經在 init 完成初始化，不需要 load_model() 了，所以拔掉！
            
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
            # 👇 這裡直接印字串，不要再放 {e} 了
            print("🚨 [Fatal Error] 找不到任何 OCR 模組！請檢查最上方的錯誤追蹤。")
            print("[Warning] 找不到任何 OCR 服務，已略過載入。")

    except Exception as e:
        # 這裡才是真正的執行時期錯誤
        print(f"🚨 [Fatal Error] OCR 服務實例化失敗: {e}")
        traceback.print_exc()
        app.config["OCR_HANDLER"] = None
        app.extract_text_from_image = None


# ====== 6. 註冊路由 ====================================================
# 1. 認證功能
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

# 2. 履歷核心
    app.register_blueprint(resume_bp, url_prefix='/api/resumes')

# 3. 履歷處理
    app.register_blueprint(resume_proc_bp, url_prefix='/api/resume_process')

# 4. 分析報告
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    app.register_blueprint(gap_analysis_bp, url_prefix='/api')
    app.register_blueprint(ocr_bp, url_prefix='/api/ocr')
    app.register_blueprint(cover_letter_bp, url_prefix="/api/cover_letter")

# 5. 使用者偏好與推薦
    app.register_blueprint(user_preference_bp, url_prefix='/api')
    app.register_blueprint(rec_bp, url_prefix='/api')

# 6. 問卷作答
    app.register_blueprint(questionnaire_bp, url_prefix='/api')

# 7. 非同步任務 (選用)
    if _has_async_tasks:
        app.register_blueprint(async_tasks_bp, url_prefix='/api/tasks')

# ====== 7. 系統健康檢查 ================================================
    @app.route("/health", methods=["GET"])
    def health_check():
        worker_ok, nodes = check_worker_health()
        return jsonify({
            "status": "healthy",
            "service": "Career Pilot API",
            "ocr_loaded": "ready" if app.config.get("OCR_HANDLER") else "offline",
            "worker": {
                "status": "online" if worker_ok else "offline",
                "nodes": nodes
            }
        }), 200

    return app