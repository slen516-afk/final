# api/recommendation.py
from flask import Blueprint, request, jsonify

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
    mock_resources = [
        {
            "id": "course_55",
            "title": "Flask 實戰：從零開始開發 REST API",
            "platform": "Udemy",
            "type": "Video Course",
            "priority": "High",
            "url": "https://example.com/flask-course"
        },
        {
            "id": "doc_01",
            "title": "Docker 官方文件 - Get Started",
            "platform": "Docker Docs",
            "type": "Documentation",
            "priority": "Medium",
            "url": "https://docs.docker.com/get-started/"
        }
    ]
    
    return jsonify({
        "status": "success",
        "focus_area": "System Architecture",
        "resources": mock_resources
    }), 200