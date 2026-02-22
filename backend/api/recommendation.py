# api/recommendation.py
from flask import Blueprint

# 取個簡短的 blueprint 名稱
rec_bp = Blueprint('recommendation', __name__)

@rec_bp.route('/jobs', methods=['POST'])
def recommend_jobs():
    pass

@rec_bp.route('/projects', methods=['POST'])
def suggest_projects():
    pass

@rec_bp.route('/learning', methods=['POST'])
def recommend_learning():
    pass