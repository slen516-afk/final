# api/recommendation.py
from flask import Blueprint, request, jsonify
from service.llm_service.src.features.course.tools import CourseRecommendationTool
from crewai import Agent, Task, Crew
import json
import re
from supabase import create_client
import os
from qdrant_client import QdrantClient
from service.llm_service.src.features.matching.service import CareerMatchingService

SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("project_url")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("service_role_key")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("請在 .env 設定 project_url + service_role_key 或 SUPABASE_URL + SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 取個簡短的 blueprint 名稱
rec_bp = Blueprint('recommendation', __name__)


# =====================================================================
# 🌟 V1 舊版引擎 (保留備用)
# =====================================================================
@rec_bp.route('/jobs/recommendations', methods=['POST'])
def recommend_jobs():
    data = request.get_json() or {}
    
    resume_id = data.get("resumeId")
    if not resume_id and not data.get("resumeText"):
        return jsonify({"status": "error", "message": "缺少履歷資訊，無法推薦"}), 400

    try:
        raw_resume_text = data.get("resumeText")
        if raw_resume_text:
            resume_text = raw_resume_text
        else:
            resume_res = supabase.table('resume').select('structured_data').eq('resume_id', resume_id).execute()
            if not resume_res.data:
                return jsonify({"status": "error", "message": f"找不到 ID 為 {resume_id} 的履歷"}), 404
            resume_text = json.dumps(resume_res.data[0].get('structured_data', {}), ensure_ascii=False)

        # 這裡原本有 V1 的 AI 任務邏輯，先維持原樣不干涉
        return jsonify({
            "status": "success", 
            "recommendations": [], 
            "message": "請改用 V2 引擎"
        }), 200
            
    except Exception as e:
        print(f"❌ 推薦過程發生錯誤: {str(e)}")
        return jsonify({"status": "error", "message": "伺服器內部錯誤"}), 500
    

# =====================================================================
# 🌟 單筆職缺查詢 API
# =====================================================================
@rec_bp.route('/jobs/<job_id>', methods=['GET'])
def get_job_detail(job_id):
    print(f"DEBUG: 準備查詢單筆職缺，ID: {job_id}")
    try:
        res = supabase.table('job_posting').select('*').eq('job_id', job_id).execute()
        if not res.data:
            return jsonify({"status": "error", "message": "找不到該職缺"}), 404
            
        return jsonify({
            "status": "success",
            "data": res.data[0]
        }), 200
    except Exception as e:
        print(f"❌ 查詢單筆職缺發生錯誤: {str(e)}")
        return jsonify({"status": "error", "message": "伺服器內部錯誤"}), 500


# =====================================================================
# 🌟 專案建議 API
# =====================================================================
@rec_bp.route('/projects/suggestions', methods=['POST'])
def suggest_projects():
    mock_projects = [
        {
            "id": "proj_001",
            "title": "電商 API 系統實作",
            "difficulty": "Intermediate",
            "tech_stack": ["Flask", "SQLAlchemy", "JWT"],
            "reason": "這個專案可以幫助你加強對 RESTful API 和資料庫設計的理解。",
            "estimated_hours": 20
        },
        {
            "id": "proj_002",
            "title": "個人履歷分析儀表板",
            "difficulty": "Advanced",
            "tech_stack": ["Python", "Pandas", "Streamlit"],
            "reason": "結合資料分析與前端展示，適合展示你的全方位能力。",
            "estimated_hours": 30
        }
    ]
    return jsonify({
        "status": "success",
        "category": "Backend Development",
        "projects": mock_projects
    }), 200


# =====================================================================
# 🌟 課程推薦 API
# =====================================================================
@rec_bp.route('/learning/recommendations', methods=['POST'])
def recommend_learning():
    data = request.get_json() or {}
    user_id = data.get("user_id", 1)
    
    print(f"🚀 開始呼叫 CrewAI，幫使用者 {user_id} 尋找課程...")
    course_tool = CourseRecommendationTool()
    learning_advisor = Agent(
        role='資深技術培訓顧問',
        goal='根據使用者的技能缺口與程度，推薦最適合的線上課程',
        backstory='你是一位精通各類線上課程平台的專家。',
        tools=[course_tool],
        verbose=True,
        allow_delegation=False
    )
    recommend_task = Task(
        description=f"請使用工具，查詢 user_id 為 '{user_id}' 的推薦課程。",
        expected_output="必須嚴格輸出合法的 JSON 陣列 (Array)。",
        agent=learning_advisor
    )
    crew = Crew(agents=[learning_advisor], tasks=[recommend_task], verbose=True)
    raw_result = crew.kickoff()

    try:
        clean_result = raw_result.raw.replace("```json", "").replace("```", "").strip()
        parsed_resources = json.loads(clean_result)
        return jsonify({
            "status": "success",
            "resources": parsed_resources
        }), 200
    except json.JSONDecodeError as e:
        print(f"❌ AI 格式錯亂: {e}")
        return jsonify({"status": "error", "message": "AI 未回傳正確格式"}), 500


# =====================================================================
# 🚀🚀🚀 V2 超跑 AI 引擎 (全新混合檢索架構) 🚀🚀🚀
# =====================================================================
@rec_bp.route('/jobs/v2/recommendations', methods=['POST'])
def smart_recommend_jobs_v2():
    data = request.get_json() or {}
    
    # 1. 抓取前端傳來的包裹
    document_id = data.get("resumeId")
    if not document_id:
        return jsonify({"status": "error", "message": "缺少履歷 ID"}), 400
        
    user_id = data.get("userId", 1) 
    source_type = data.get("sourceType", "RESUME").upper() 

    # ==========================================
    # 2. 整理問卷篩選條件 (Filters) 給 Qdrant
    # ==========================================
    filters = {}
    
    # --- A. 城市過濾 (聰明版) ---
    target_city = data.get("city", "不限地區")
    if target_city and target_city != "不限地區":
        # 為了防止 Qdrant 太笨，我們同時給它 "苗栗" 和 "苗栗縣"
        base_city = target_city.replace("市", "").replace("縣", "")
        filters["city"] = [base_city, f"{base_city}市", f"{base_city}縣"]

    # --- B. 薪資過濾 ---
    min_salary = data.get("minSalary")
    max_salary = data.get("maxSalary")
    if min_salary:
        filters["salary_min"] = int(min_salary)
    if max_salary:
        filters["salary_max"] = int(max_salary)

    # --- C. 工作型態過濾 ---
    work_mode = data.get("workMode", "不限")
    if work_mode and work_mode != "不限":
        filters["work_mode"] = [work_mode]

    print(f"🚀 [V2 引擎啟動] User: {user_id}, Doc: {document_id}, Filters: {filters}")

    try:
        # 3. 準備環境變數與連線
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")

        if not openai_api_key:
            raise ValueError("伺服器缺少 OPENAI_API_KEY 環境變數")
        
        # 🌟 實例化 Qdrant Client，並帶入金鑰
        qdrant_client = QdrantClient(
            url=qdrant_url, 
            api_key=qdrant_api_key 
        )

        # 4. 實例化你超強的 Matching Service
        matching_service = CareerMatchingService(
            qdrant_client=qdrant_client,
            supabase_client=supabase,  
            openai_api_key=openai_api_key
        )

        # 5. 執行 RAG 與混合檢索！
        final_jobs = matching_service.find_best_jobs(
            user_id=user_id,
            document_id=int(document_id),
            source_type=source_type,
            filters=filters
        )

        # 6. 回傳跟 V1 一模一樣格式的 JSON，這樣前端就不用改寫接收邏輯！
        return jsonify({
            "status": "success",
            "count": len(final_jobs),
            "recommendations": final_jobs
        }), 200

    except Exception as e:
        print(f"❌ V2 推薦過程發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc() # 印出詳細錯誤軌跡方便 Debug
        return jsonify({"status": "error", "message": f"內部引擎錯誤: {str(e)}"}), 500