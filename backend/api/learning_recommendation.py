from flask import Blueprint, request, jsonify, g
from api.auth import login_required
from core.supabase_client import supabase

# 定義藍圖名稱
learning_recommendation_bp = Blueprint('learning_recommendation', __name__)

# 路由設定
# app.py 已經設定前綴是 '/api/learning'
# 這裡設 '/recommendations'，拼起來就是 '/api/learning/recommendations'
@learning_recommendation_bp.route('/recommendations', methods=['POST'])
def recommend_learning():
    # 這裡寫你的邏輯...
    return jsonify({
        "message": "F-04 Learning Recommendations",
        "data": ["Course A", "Course B"]
    })