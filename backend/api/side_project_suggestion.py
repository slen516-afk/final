from flask import Blueprint, request, jsonify, g
from api.auth import login_required
from core.supabase_client import supabase


side_project_suggestion_bp = Blueprint('side_project_suggestion', __name__)


@side_project_suggestion_bp.route('/suggestions', methods=['POST'])
def suggest_projects():
    return jsonify({
        "message": "F-03 Project Suggestions",
        "data": ["Project X", "Project Y"]
    })