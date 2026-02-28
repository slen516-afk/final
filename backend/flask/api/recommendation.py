# api/recommendation.py
from flask import Blueprint, request, jsonify
from service.llm_service.src.features.course.tools import CourseRecommendationTool
from crewai import Agent, Task, Crew
import json

# 取個簡短的 blueprint 名稱
rec_bp = Blueprint('recommendation', __name__)

@rec_bp.route('/jobs/recommendations', methods=['POST'])
def recommend_jobs():
    data = request.get_json() or {}
    mock_jobs = [
        {
            "id": "job_101",
            "title": "Python Backend Engineer",
            "company": "TechStart Inc.",
            "location": "Taipei, Taiwan",
            "salary_range": "60k - 80k TWD",
            "match_score": 95,
            "required_skills": ["Python", "Flask", "PostgreSQL"],
            "description": "負責後端 API 開發與維護..."
        },
        {
            "id": "job_102",
            "title": "Full Stack Developer",
            "company": "Global Data Co.",
            "location": "Remote",
            "salary_range": "80k - 100k TWD",
            "match_score": 88,
            "required_skills": ["React", "Node.js", "Python"],
            "description": "全端開發，需熟悉前後端整合..."
        },
        {
            "id": "job_101",
            "title": "Python Backend Engineer",
            "company": "TechStart Inc.",
            "location": "Taipei, Taiwan",
            "salary_range": "60k - 80k TWD",
            "match_score": 95,
            "required_skills": ["Python", "Flask", "PostgreSQL"],
            "description": "負責後端 API 開發與維護..."
        }
    ]

    return jsonify({
        "status": "success",
        "count": len(mock_jobs),
        "recommendations": mock_jobs
    }), 200

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