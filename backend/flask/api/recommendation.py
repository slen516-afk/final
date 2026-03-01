# api/recommendation.py
from flask import Blueprint, request, jsonify
from service.llm_service.src.features.course.tools import CourseRecommendationTool
from crewai import Agent, Task, Crew
import json
import re
from supabase import create_client
import os

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

    page = request.args.get('page', 1, type=int)
    page_size = 10  # 每一頁只挑 10 個最精華的給 AI 看，省錢又精準！
    
    resume_id = data.get("resumeId")
    target_city = data.get("city", "不限地區")
    min_salary = data.get("minSalary", 0)
    max_salary = data.get("maxSalary", "依公司規定")
    work_mode = data.get("workMode", "不限")

    if not resume_id:
        return jsonify({"status": "error", "message": "缺少履歷資訊，無法推薦"}), 400

    try:
        # ==========================================
        # 步驟 1：履歷來源雙軌制 (支援直接傳文字或傳 ID)
        # ==========================================
        # 🌟 如果前端有直接傳 "resumeText"，就優先用它，不鳥資料庫！
        raw_resume_text = data.get("resumeText")
        
        if raw_resume_text:
            print("DEBUG: 收到前端直接傳來的履歷文字！不再撈資料庫。")
            resume_text = raw_resume_text
        else:
            # 如果沒有傳文字，才用老方法去資料庫找 ID
            if not resume_id:
                return jsonify({"status": "error", "message": "缺少履歷資訊"}), 400
            
            print(f"DEBUG: 透過 ID ({resume_id}) 去資料庫撈履歷...")
            resume_res = supabase.table('resume').select('structured_data').eq('resume_id', resume_id).execute()
            if not resume_res.data:
                return jsonify({"status": "error", "message": f"找不到 ID 為 {resume_id} 的履歷"}), 404
            resume_text = json.dumps(resume_res.data[0].get('structured_data', {}), ensure_ascii=False)

        # 解析問卷薪水上限 (沒填就給無限大)
        max_salary_raw = data.get("maxSalary", 999999)
        try:
            max_salary = 999999 if max_salary_raw == "依公司規定" else int(max_salary_raw)
        except:
            max_salary = 999999

        # ==========================================
        # 步驟 2：撈取多一點庫存 + Python 頁碼切片
        # ==========================================

        # 🌟 就是這裡！把這三行補回來，Python 才知道要搜哪裡！
        target_city = data.get("city", "不限地區")
        search_city = target_city.replace("市", "").replace("縣", "")
        print(f"DEBUG: 準備撈取 - 地點: {search_city}, 條件: {min_salary} ~ {max_salary}")

        query = supabase.table('job_posting').select('job_id, job_title, job_description, city, salary_min, salary_max')
        if target_city != "不限地區":
            query = query.ilike('city', f'%{search_city}%')
            
        # 🌟 1. 放大撈取量：一次撈 300 筆出來給 Python 慢慢洗，不要只撈 50 筆
        raw_jobs = query.limit(300).execute().data
        
        # ... (中間 Python 洗薪水、過濾大數字的 for 迴圈完全不變) ...
        clean_jobs = []
        for job in raw_jobs:
            s_min = job.get('salary_min') or 0
            s_max = job.get('salary_max') or 0

            # 年薪轉月薪 (超過 10 萬直接認定為年薪)
            if s_min > 100000: s_min = int(s_min / 12)
            if s_max > 100000: s_max = int(s_max / 12)

            actual_s_max = s_max if s_max > 0 else 999999

            # 🌟 絕對嚴格模式：只要起薪不符合區間，直接踢掉！
            if s_min < min_salary or s_min > max_salary:
                continue

            # 預先格式化為 k (例如 40000 變 40k)
            if s_min == s_max or s_max == 0:
                final_salary_str = f"{int(s_min/1000)}k"
            else:
                final_salary_str = f"{int(s_min/1000)}k - {int(s_max/1000)}k"

            # 🌟 就是這裡！重新定義乾淨的 clean_job 字典，隱藏真實的大數字！
            clean_job = {
                "id": job.get("job_id"),
                "title": job.get("job_title"),
                "description": job.get("job_description"),
                "location": job.get("city"),
                "salary_range": final_salary_str
            }
            clean_jobs.append(clean_job)

        # 🌟 2. 核心魔法：根據前端的頁碼，算出這次要切哪幾筆給 AI！
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        candidate_jobs = clean_jobs[start_idx:end_idx]

        # 如果切片切不到東西 (例如使用者翻到第 100 頁，或是這區真的沒工作了)
        if not candidate_jobs:
            return jsonify({
                "status": "success", 
                "recommendations": [], 
                "message": "這頁沒有符合的職缺了"
            }), 200

        # 將「這頁專屬」的 10 筆資料轉成字串，餵給 AI
        jobs_context = json.dumps(candidate_jobs, ensure_ascii=False)

        # ==========================================
        # 步驟 3：設定 AI 任務 (大幅簡化，因為資料已經乾淨了)
        # ==========================================
        job_advisor = Agent(
            role='資深技術獵頭顧問',
            goal='根據求職者的真實履歷技能，從提供的候選職缺中挑選出最匹配的 5 個，並打上分數。',
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
            1. 從【乾淨職缺清單】中挑選最符合履歷的職缺。
            2. `id`, `title`, `location`, `salary_range` 請「完全照抄」清單裡的內容，不要做任何更改！
            3. `company` 統一輸出為 "精選企業"。
            4. `match_score` 請根據技能相符程度給予 1~100 的分數。
            5. `required_skills` 請從職缺描述中萃取出技術關鍵字陣列。
            
            🚨 嚴格警告：你的輸出將被機器直接讀取！
            絕對不准輸出任何解釋文字！不准說 "Here is the JSON" 或 "The JSON array above"！
            """,
            expected_output="""
            [{"id": 1, "title": "工程師", "company": "精選企業", "location": "新北", "salary_range": "60k - 80k", "match_score": 85, "required_skills": ["Python"], "description": "..."}]
            
            請確保你的最後輸出「只有」一個合法的 JSON 陣列，必須以 [ 開頭，以 ] 結尾。即使找不到合適的工作，也請只輸出 []，禁止任何多餘文字！
            """,
            agent=job_advisor
        )

        crew = Crew(agents=[job_advisor], tasks=[job_search_task], verbose=True)
        # ==========================================
        # 步驟 4：執行任務並回傳給前端 (加入 JSON 崩潰防護)
        # ==========================================
        print("🚀 開始執行 AI 媒合任務...")
        result = crew.kickoff()
        
        # 1. 擷取 JSON 內容
        raw_output = str(result.raw).strip()
        
        # 🌟 加入 try...except 來捕捉 AI 的亂說話
        try:
            json_match = re.search(r'\[.*\]', raw_output, re.DOTALL)
            if json_match:
                final_jobs = json.loads(json_match.group(0))
            else:
                final_jobs = json.loads(raw_output)

            # 確保有根據匹配分數高低來排序
            final_jobs = sorted(final_jobs, key=lambda x: x.get('match_score', 0), reverse=True)

            # 🌟 兇手就是少了這一段！成功解析後，必須把資料回傳給前端！
            return jsonify({
                "status": "success",
                "count": len(final_jobs),
                "recommendations": final_jobs
            }), 200

        except Exception as e:
            # 萬一 AI 吐出來的不是 JSON，我們把它印出來看兇手長怎樣
            print(f"❌ JSON 解析失敗！AI 沒照規矩輸出。AI 回傳內容：\n{raw_output}")
            
            # 回傳空陣列，讓前端顯示「哎呀，目前沒有符合條件的職缺」的漂亮畫面
            return jsonify({
                "status": "success", 
                "recommendations": [], 
                "message": "AI 無法解析該地區的職缺，請嘗試放寬條件"
            }), 200
    except Exception as e:
        print(f"❌ 推薦過程發生錯誤: {str(e)}")
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