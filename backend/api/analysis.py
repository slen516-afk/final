from flask import Blueprint, request, jsonify, g
from api.auth import login_required
import uuid

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/tasks', methods=['POST'])
@login_required
def start_analysis_task():
    """
    D-01 啟動履歷分析任務 - Mocked
    DB: CAREER_ANALYSIS_REPORT (trigger)
    """
    try:
        user_id = g.user_id
        data = request.json
        if 'resume_id' not in data or 'survey_id' not in data:
            return jsonify({'error': 'Missing resume_id or survey_id'}), 400
            
        # === Mock Task Trigger ===
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        return jsonify({
            'task_id': task_id,
            'status': 'pending'
        }), 202

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/tasks/<task_id>/status', methods=['GET'])
@login_required
def get_analysis_status(task_id):
    """
    D-02 查詢履歷分析狀態 - Mocked
    """
    user_id = g.user_id
    return jsonify({
        'task_id': task_id,
        'status': 'processing' # Always processing for mock
    }), 200

@analysis_bp.route('/tasks/<task_id>/results', methods=['GET'])
@login_required
def get_analysis_results(task_id):
    """
    D-03 取得履歷分析結果 - Mocked
    DB: CAREER_ANALYSIS_REPORT, SKILL_GAP
    """
    user_id = g.user_id
    # === Mock Results ===
    mock_results = {
        "career_readiness_score": 85.0,
        "skill_gap_analysis": [
            { "skill": "Kubernetes", "priority": "High" },
            { "skill": "React", "priority": "Medium" }
        ],
        "market_insights": "後端工程師職缺近期需求增加，特別是熟悉雲端架構的人才。"
    }
    
    return jsonify(mock_results), 200
