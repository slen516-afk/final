from flask import Blueprint, request, jsonify, g
from functools import wraps
from datetime import datetime
import supabase

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# 用戶註冊
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    username = data.get("username")

    if not email or not password or not username:
        return jsonify({"message": "Missing required fields"}), 400

    try:
        # 呼叫 Supabase Auth 註冊
        result = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {"username": username}
                # 驗證後跳轉頁面<url>
                # "email_redirect_to": "<url>"
            }
        })

        # 驗證用戶信箱
        # Supabase -> Sign In / Providers -> Supabase Auth -> Confirm email(Open)
        if result.user and not result.session:
            return jsonify({
                "message": "註冊成功！請檢查您的信箱以驗證帳號。",
                "needsConfirmation": True
            }), 201
            
        return jsonify({"message": "註冊成功"}), 201

    except Exception as e:
        return jsonify({"message": str(e)}), 400



# 用戶登入
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Missing credentials"}), 400

    try:
        # 呼叫 Supabase Auth 登入
        result = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        user = result.user
        session = result.session

        if not user:
            return jsonify({"message": "Invalid credentials"}), 401

        # 更新最後登入時間
        supabase.table("users").update({
            "last_login": datetime.utcnow().isoformat()
        }).eq("id", user.id).execute()

        # 回傳指定格式
        return jsonify({
            "user": {
                "id": user.id,
                "role": user.role or "user"
            },
            "auth": {
                "accessToken": session.access_token,
                "refreshToken": session.refresh_token,
                "expiresIn": session.expires_in
            },
            "security": {
                "mfaRequired": False,
                "passwordExpired": False
            }
        }), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500

# 權限驗證
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"message": "請先登入"}), 401
        
        token = auth_header.replace("Bearer ", "")       
        
        try:
            # 使用 Supabase SDK 驗證用戶資訊
            # 以get_user驗證JWT並回傳用戶資訊
            user_info = supabase.auth.get_user(token)

            # 將 user_id 存入 Flask 的全域變數 g，供後續業務流程使用
            g.user_id = user_info.user.id

        except Exception as e:
            return jsonify({"message": "Token 無效 / 逾期"}), 401
            
        return f(*args, **kwargs)
    return decorated

# 用戶首頁 - 登入後可使用
@auth_bp.route("/profile", methods=["GET"])
@login_required
def get_profile():
    try:
        user_data = supabase.table("users").select("*").eq("id", g.user_id).single().execute()
        return jsonify(user_data.data), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500