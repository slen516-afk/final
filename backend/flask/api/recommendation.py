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

# TODO: 請確認這裡有引入你們專案的 supabase 連線物件
# from your_database_config import supabase 
@rec_bp.route('/jobs/recommendations', methods=['POST'])
def recommend_jobs():
    data = request.get_json() or {}

    # 🌟 已經把 page 和 page_size 刪掉了！現在全部交給前端分頁！
    
    resume_id = data.get("resumeId")
    target_city = data.get("city", "不限地區")
    min_salary = data.get("minSalary", 0)
    max_salary_raw = data.get("maxSalary", 999999)
    work_mode = data.get("workMode", "不限")

    if not resume_id and not data.get("resumeText"):
        return jsonify({"status": "error", "message": "缺少履歷資訊，無法推薦"}), 400

    try:
        # ==========================================
        # 步驟 1：取得履歷資料
        # ==========================================
        raw_resume_text = data.get("resumeText")
        
        if raw_resume_text:
            print("DEBUG: 收到前端直接傳來的履歷文字！不再撈資料庫。")
            resume_text = raw_resume_text
        else:
            print(f"DEBUG: 透過 ID ({resume_id}) 去資料庫撈履歷...")
            resume_res = supabase.table('resume').select('structured_data').eq('resume_id', resume_id).execute()
            if not resume_res.data:
                return jsonify({"status": "error", "message": f"找不到 ID 為 {resume_id} 的履歷"}), 404
            resume_text = json.dumps(resume_res.data[0].get('structured_data', {}), ensure_ascii=False)

        try:
            max_salary = 999999 if max_salary_raw == "依公司規定" else int(max_salary_raw)
        except:
            max_salary = 999999

        # ==========================================
        # 步驟 2：撈取並清洗職缺 (放大漏斗)
        # ==========================================
        search_city = target_city.replace("市", "").replace("縣", "")
        print(f"DEBUG: 準備撈取 - 地點: {search_city}, 條件: {min_salary} ~ {max_salary}")

        query = supabase.table('job_posting').select('job_id, job_title, job_description, city, salary_min, salary_max')
        if target_city != "不限地區":
            query = query.ilike('city', f'%{search_city}%')
            
        # 🌟 放大撈取量：一次撈 300 筆出來
        raw_jobs = query.limit(300).execute().data
        
        clean_jobs = []
        for job in raw_jobs:
            s_min = job.get('salary_min') or 0
            s_max = job.get('salary_max') or 0

            if s_min > 100000: s_min = int(s_min / 12)
            if s_max > 100000: s_max = int(s_max / 12)

            # 絕對嚴格模式
            if s_min < min_salary or s_min > max_salary:
                continue

            if s_min == s_max or s_max == 0:
                final_salary_str = f"{int(s_min/1000)}k"
            else:
                final_salary_str = f"{int(s_min/1000)}k - {int(s_max/1000)}k"

            clean_job = {
                "id": job.get("job_id"),
                "title": job.get("job_title"),
                "description": job.get("job_description"),
                "location": job.get("city"),
                "salary_range": final_salary_str
            }
            clean_jobs.append(clean_job)

        # 🌟 直接取洗乾淨的前 30 筆，不再做後端分頁！
        candidate_jobs = clean_jobs[:30]

        if not candidate_jobs:
            return jsonify({
                "status": "success", 
                "recommendations": [], 
                "message": "這區間目前沒有符合的職缺了"
            }), 200

        jobs_context = json.dumps(candidate_jobs, ensure_ascii=False)

        # ==========================================
        # 步驟 3：設定 AI 任務
        # ==========================================
        job_advisor = Agent(
            role='資深技術獵頭顧問',
            goal=f'根據求職者的履歷，評估提供的 {len(candidate_jobs)} 個候選職缺，並打上分數。',
            backstory='你是頂尖獵頭，擅長分析求職者技能與職缺的關聯。',
            verbose=True,
            allow_delegation=False
        )

        job_search_task = Task(
            description=f"""
            請分析以下履歷與職缺：
            
            【履歷】：{resume_text}
            【乾淨職缺清單】：{jobs_context}
            
            任務要求：
            1. 從【乾淨職缺清單】中評估職缺。請確保你回傳的陣列中，盡可能包含清單內所有的職缺（最多 {len(candidate_jobs)} 筆）。
            2. `id`, `title`, `location`, `salary_range` 請「完全照抄」清單裡的內容，不要做任何更改！
            3. `company` 統一輸出為 "精選企業"。
            4. `match_score` 請根據技能相符程度給予 1~100 的分數。
            5. `required_skills` 請從職缺描述中萃取出技術關鍵字陣列。
            
            🚨 嚴格警告：絕對不准輸出任何解釋文字！不准說 "Here is the JSON"！
            """,
            expected_output="""
            [{"id": 1, "title": "工程師", "company": "精選企業", "location": "新北", "salary_range": "60k - 80k", "match_score": 85, "required_skills": ["Python"], "description": "..."}]
            
            確保輸出「只有」合法 JSON 陣列，以 [ 開頭，以 ] 結尾。
            """,
            agent=job_advisor
        )

        crew = Crew(agents=[job_advisor], tasks=[job_search_task], verbose=True)
        
        # ==========================================
        # 步驟 4：執行任務並回傳給前端
        # ==========================================
        print(f"🚀 開始執行 AI 媒合任務 (共 {len(candidate_jobs)} 筆候選職缺)...")
        result = crew.kickoff()
        
        raw_output = str(result.raw).strip()
        
        try:
            json_match = re.search(r'\[.*\]', raw_output, re.DOTALL)
            if json_match:
                final_jobs = json.loads(json_match.group(0))
            else:
                final_jobs = json.loads(raw_output)

            final_jobs = sorted(final_jobs, key=lambda x: x.get('match_score', 0), reverse=True)

            print(f"✅ AI 成功吐出 {len(final_jobs)} 筆職缺！準備傳給前端...")
            return jsonify({
                "status": "success",
                "count": len(final_jobs),
                "recommendations": final_jobs
            }), 200

        except Exception as e:
            print(f"❌ JSON 解析失敗！AI 回傳內容：\n{raw_output}")
            return jsonify({
                "status": "success", 
                "recommendations": [], 
                "message": "AI 無法解析該地區的職缺，請嘗試放寬條件"
            }), 200
            
    except Exception as e:
        print(f"❌ 推薦過程發生錯誤: {str(e)}")
        return jsonify({"status": "error", "message": "伺服器內部錯誤"}), 500
    

@rec_bp.route('/jobs/<job_id>', methods=['GET'])
def get_job_detail(job_id):
    print(f"DEBUG: 準備查詢單筆職缺，ID: {job_id}")
    try:
        # 去 Supabase 撈這筆職缺的完整資料
        res = supabase.table('job_posting').select('*').eq('job_id', job_id).execute()
        
        if not res.data:
            return jsonify({"status": "error", "message": "找不到該職缺"}), 404
            
        return jsonify({
            "status": "success",
            "data": res.data[0]  # 回傳這筆職缺的所有欄位 (包含工作要求、福利等)
        }), 200
        
    except Exception as e:
        print(f"❌ 查詢單筆職缺發生錯誤: {str(e)}")
        return jsonify({"status": "error", "message": "伺服器內部錯誤"}), 500

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

@rec_bp.route('/learning/recommendations', methods=['POST'])
def recommend_learning():
    data = request.get_json() or {}
    user_id = data.get("user_id", 1) # 假設前端有傳 user_id，沒傳就給個預設值
    
    print(f"🚀 開始呼叫 CrewAI，幫使用者 {user_id} 尋找課程...")

    # 1. 裝備組員寫好的工具
    course_tool = CourseRecommendationTool()

    # 2. 創造 AI 大腦 (Agent)
    learning_advisor = Agent(
        role='資深技術培訓顧問',
        goal='根據使用者的技能缺口與程度，推薦最適合的線上課程',
        backstory='你是一位精通各類線上課程平台的專家，擅長幫工程師規劃學習路徑，補足技能落差。',
        tools=[course_tool], # 把工具交給他
        verbose=True,
        allow_delegation=False
    )

    # 3. 給予任務，並強制吐出「前端看得懂的 JSON 格式」
    recommend_task = Task(
        description=f"""
        請使用你的工具，查詢 user_id 為 '{user_id}' 的推薦課程。
        你需要將工具回傳的課程清單，整理成前端畫面需要的 JSON 格式。
        """,
        expected_output="""
        必須嚴格輸出合法的 JSON 陣列 (Array)，不要包含 markdown 標記 (如 ```json)。
        欄位必須完全符合以下格式：
        [
            {
                "title": "課程名稱 (從工具結果中提取)",
                "platform": "根據課程名稱猜測平台(如 Udemy/YouTube/Coursera)，若不知道則填 '線上課程'",
                "type": "Video Course",
                "priority": "High (如果優先權分數大於 0.5 填 High，否則填 Medium)",
                "url": "課程連結 (從工具結果中提取)"
            }
        ]
        """,
        agent=learning_advisor
    )

    # 4. 組建團隊並開工！
    crew = Crew(
        agents=[learning_advisor],
        tasks=[recommend_task],
        verbose=True
    )

    raw_result = crew.kickoff()

    # 5. 清理 AI 的字串並轉成 JSON 回傳給 React
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

@rec_bp.route('/jobs/v2/recommendations', methods=['POST'])
def smart_recommend_jobs_v2():
    data = request.get_json() or {}
    
    # 1. 抓取前端傳來的包裹
    document_id = data.get("resumeId")
    if not document_id:
        return jsonify({"status": "error", "message": "缺少履歷 ID"}), 400
        
    # TODO: 由於你目前的 service.py 需要 user_id，如果前端沒傳，我們先假設是 1 號使用者
    user_id = data.get("userId", 1) 
    source_type = data.get("sourceType", "RESUME").upper() # 預設是履歷

    # 2. 整理篩選條件 (Filters) 給 Qdrant 
    target_city = data.get("city", "不限地區")
    search_city = target_city.replace("市", "").replace("縣", "") if target_city != "不限地區" else None
    
    filters = {}
    if search_city:
        filters["city"] = search_city
        
    print(f"🚀 [V2 引擎啟動] User: {user_id}, Doc: {document_id}, Filters: {filters}")

    try:
        # 3. 準備環境變數與連線
        # (確保你的 .env 裡面有 QDRANT_URL 跟 OPENAI_API_KEY)
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        qdrant_client = QdrantClient(url=qdrant_url)
        openai_key = os.getenv("OPENAI_API_KEY")

        if not openai_key:
            raise ValueError("伺服器缺少 OPENAI_API_KEY 環境變數")

        # 4. 實例化你超強的 Matching Service
        matching_service = CareerMatchingService(
            qdrant_client=qdrant_client,
            supabase_client=supabase,  # 這裡使用你檔案最上方已經連好的 supabase
            openai_api_key=openai_key
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