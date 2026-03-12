import os
import uuid
from flask import Blueprint, request, jsonify, g
from functools import wraps
from datetime import datetime
from core.supabase_client import supabase, get_supabase_client

auth_bp = Blueprint("auth", __name__)


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
        # 使用獨立的 client 進行註冊，避免影響全域 Service Role Client 的狀態
        auth_client = get_supabase_client()
        is_test = request.headers.get("X-Test-Bypass") == "True"
        
        if is_test:
            res = auth_client.auth.admin.create_user({
                "email": email,
                "password": password,
                "user_metadata": {"username": username},
                "email_confirm": True
            })
            user = res.user
            session = None
        else:
            res = auth_client.auth.sign_up(
                {
                    "email": email,
                    "password": password,
                    "options": {
                        "data": {"username": username}
                    },
                }
            )
            user = res.user
            session = res.session

        # 同步寫入 USER 表（auth_uuid 橋接）
        if user:
            try:
                # 取得插入後的資料
                user_res = supabase.table("USER").insert({
                    "email": email,
                    "password_hash": "supabase_managed",
                    "auth_uid": user.id,
                    "auth_provider": "Email",
                    "is_active": True
                }).execute()
                
                # 同步建立 user_profile 記錄
                if user_res.data:
                    db_user_id = user_res.data[0]["user_id"]
                    supabase.table("user_profile").insert({
                        "user_id": db_user_id,
                        "full_name": username
                    }).execute()
            except Exception as db_e:
                # 這裡可以使用 logger 或是靜默失敗（如果用戶已存在）
                pass

        # 驗證用戶信箱 (如果是 admin 建立則 session 為 None 但 email_confirm 已 True)
        if user and not session and not is_test:
            return (
                jsonify(
                    {
                        "message": "註冊成功！請檢查您的信箱以驗證帳號。",
                        "needsConfirmation": True,
                    }
                ),
                201,
            )

        return jsonify({"message": "註冊成功"}), 201

    except Exception as e:
        return jsonify({"message": str(e)}), 400


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    print(f"[Debug] Login attempt for data: {data}")
    email = data.get("email", "").strip()
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Missing credentials"}), 400

    try:
        auth_client = get_supabase_client()
        res = auth_client.auth.sign_in_with_password({"email": email, "password": password})
        user = res.user
        session = res.session

        if not user:
            print("[Debug] Login failed: User is None")
            return jsonify({"message": "Invalid credentials"}), 401

        # 🌟 核心修改：從 USER 資料表撈取包含「整數 user_id」的完整資料
        # 我們利用 auth_uid (UUID) 來對應
        # 🌟 核心修改：從 USER 資料表撈取包含「整數 user_id」的完整資料
        # 我們利用 auth_uid (UUID) 來對應
        try:
            # 1. 撈取使用者資料 (來自你的修改，確保後續 API 回傳有整數 user_id)
            user_record = supabase.table("USER").select("*").eq("auth_uid", user.id).single().execute()
            db_user_data = user_record.data
            
            # 2. 準備精確的 timestamp (來自 be_tz 的修改)
            current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S+00')
            
            # 3. 優先使用 auth_uid 更新最後登入時間 (來自 be_tz 的修改)
            update_res = supabase.table("USER").update(
                {"last_login": current_time}
            ).eq("auth_uid", str(user.id)).execute()
            
            # 4. 備案：如果 auth_uid 無法更新，嘗試以 email 更新 (來自 be_tz 的修改)
            if not update_res.data:
                print(f"[Auth] last_login update by auth_uid failed, trying email fallback for {email}")
                supabase.table("USER").update(
                    {"last_login": current_time}
                ).eq("email", email).execute()

        except Exception as e:
            print(f"[Debug] Failed to fetch user record or update last_login for {email}: {e}")
            # 確保萬一出錯，db_user_data 有預設值，不會導致下方 return 時發生 Key Error
            db_user_data = {}

        # 🌟 修改回傳格式：把 db_user_data 裡面的整數 user_id 塞進去
        return (
            jsonify(
                {
                    "user": {
                        "id": user.id,              # UUID (字串)
                        "user_id": db_user_data.get("user_id"), # 🌟 真實的整數 ID
                        "email": user.email,
                        "role": user.role or "user"
                    },
                    "auth": {
                        "accessToken": session.access_token,
                        "refreshToken": session.refresh_token,
                        "expiresIn": session.expires_in,
                    },
                    "security": {"mfaRequired": False, "passwordExpired": False},
                }
            ),
            200,
        )

    except Exception as e:
        error_msg = str(e).lower()
        print(f"[Debug] Login Exception: {type(e).__name__} - {e}")
        if "invalid login credentials" in error_msg or "not found" in error_msg:
            return jsonify({"message": "帳號或密碼錯誤"}), 401
        print(f"[Auth] Login Error: {e}")
        return jsonify({"message": str(e)}), 500
# 權限驗證
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"message": "請先登入"}), 401

        token = auth_header.replace("Bearer ", "")

        # 🚀 支援開發模式下的 Mock Token
        is_mock_mode = os.environ.get("MOCK_MODE", "False").lower() == "true"
        if is_mock_mode and token == "mock-token":
            g.user_id = "mock-uuid-11"
            g.db_user_id = 11
            return f(*args, **kwargs)

        try:
            # 使用 Supabase SDK 驗證用戶資訊
            user_info = supabase.auth.get_user(token)
            auth_user = user_info.user

            # g.user_id = Supabase auth UUID (保留向下相容)
            g.user_id = auth_user.id

            # g.db_user_id = USER 表的 integer user_id (用 auth_uuid 橋接)
            db_user = (
                supabase.table("USER")
                .select("user_id")
                .eq("auth_uid", auth_user.id)
                .execute()
            )
            
            if db_user.data:
                g.db_user_id = db_user.data[0]["user_id"]
            else:
                # 備案：如果 auth_uid 找不到（可能是第三方登入尚未同步），嘗試用 email 找
                email = getattr(auth_user, 'email', None)
                if email:
                    db_user_email = supabase.table("USER").select("user_id").eq("email", email).execute()
                    g.db_user_id = db_user_email.data[0]["user_id"] if db_user_email.data else None
                else:
                    g.db_user_id = None

        except Exception as e:
            # token 驗證失敗或其他錯誤
            print(f"[Auth] Token verification failed: {type(e).__name__}: {e}")
            return jsonify({"message": "Token 無效 / 逾期", "error": str(e)}), 401

        return f(*args, **kwargs)

    return decorated


@auth_bp.route("/profile", methods=["GET"])
@login_required
def get_profile():
    try:
        # 1. 取得 USER 表基本資料
        user_res = supabase.table("USER").select("*").eq("auth_uid", g.user_id).execute()
        
        if not user_res.data:
            print(f"[Auth] USER record missing for auth_uid: {g.user_id}")
            return jsonify({"message": "User record not found in database"}), 404
            
        user_data = user_res.data[0]
        
        # 2. 取得 user_profile 表擴充資料
        profile_res = (
            supabase.table("user_profile")
            .select("full_name, avatar_url, location, years_of_experience, current_position, education_background, github_repo")
            .eq("user_id", user_data["user_id"])
            .execute()
        )
        
        profile_data = profile_res.data[0] if profile_res.data else {}
        
        # 3. 合併資料並轉換成前端預期的 CamelCase
        result = {
            "id": user_data["user_id"],
            "auth_uid": user_data["auth_uid"],
            "email": user_data["email"],
            "fullName": profile_data.get("full_name") or "",
            "avatarUrl": profile_data.get("avatar_url") or "",
            "title": profile_data.get("current_position") or "", 
            "location": profile_data.get("location") or "",
            "experience": profile_data.get("years_of_experience") or "",
            "education": profile_data.get("education_background") or "",
            "github": profile_data.get("github_repo") or ""
        }
        
        return jsonify(result), 200
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[Auth] Get Profile Error:\n{error_details}")
        return jsonify({"message": str(e), "details": "Check server logs"}), 500



@auth_bp.route("/profile", methods=["PUT"])
@login_required
def update_profile():
    try:
        data = request.json
        if not data:
            return jsonify({"message": "No data provided"}), 400
            
        update_data = {}
        
        # 欄位映射：前端 camelCase 對應資料庫 snake_case
        if "fullName" in data:
            update_data["full_name"] = data["fullName"]
        if "avatarUrl" in data:
            update_data["avatar_url"] = data["avatarUrl"]
        if "title" in data:
            update_data["current_position"] = data["title"]
        if "location" in data:
            update_data["location"] = data["location"]
        if "experience" in data:
            update_data["years_of_experience"] = data["experience"]
        if "education" in data:
            update_data["education_background"] = data["education"]
        if "github" in data:
            update_data["github_repo"] = data["github"]
            
        if not update_data:
            return jsonify({"message": "No valid fields to update"}), 400
            
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        if not g.db_user_id:
            return jsonify({"message": "找不到資料庫使用者 ID"}), 404
            
        # 執行更新
        update_res = supabase.table("user_profile").update(update_data).eq("user_id", g.db_user_id).execute()
        
        # 取得更新後的完整資料
        user_res = supabase.table("USER").select("*").eq("auth_uid", g.user_id).execute()
        if not user_res.data:
            return jsonify({"message": "User record not found in database"}), 404
        user_data = user_res.data[0]
        
        profile_res = (
            supabase.table("user_profile")
            .select("full_name, avatar_url, location, years_of_experience, current_position, education_background, github_repo")
            .eq("user_id", user_data["user_id"])
            .execute()
        )
        
        profile_data = profile_res.data[0] if profile_res.data else {}
        
        result = {
            "id": user_data["user_id"],
            "auth_uid": user_data["auth_uid"],
            "email": user_data["email"],
            "fullName": profile_data.get("full_name") or "",
            "avatarUrl": profile_data.get("avatar_url") or "",
            "title": profile_data.get("current_position") or "", 
            "location": profile_data.get("location") or "",
            "experience": profile_data.get("years_of_experience") or "",
            "education": profile_data.get("education_background") or "",
            "github": profile_data.get("github_repo") or ""
        }
        
        return jsonify(result), 200

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[Auth] Update Profile Error:\n{error_details}")
        return jsonify({"message": str(e), "details": "Check server logs"}), 500



# 用戶上傳照片
@auth_bp.route("/upload-avatar", methods=["POST"])
@login_required
def upload_avatar():
    if "file" not in request.files:
        return jsonify({"message": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"message": "No file selected"}), 400

    try:
        # 1. 產生唯一的檔名
        ext = os.path.splitext(file.filename)[1]
        if not ext:
            ext = ".png" # 預設副檔名
        filename = f"{g.user_id}_{uuid.uuid4().hex}{ext}"
        
        # 2. 讀取檔案內容
        file_bytes = file.read()
        
        # 3. 上傳到 Supabase Storage (存到 bucket 'avatars')
        res = supabase.storage.from_("avatars").upload(
            path=filename,
            file=file_bytes,
            file_options={"content-type": file.content_type}
        )
        
        # 4. 取得公開的 avatar_url
        avatar_url = supabase.storage.from_("avatars").get_public_url(filename)
        
        # 5. 回寫到 user_profile 表裡 (使用 integer user_id)
        if not g.db_user_id:
            return jsonify({"message": "找不到資料庫使用者 ID"}), 404
            
        supabase.table("user_profile").update({
            "avatar_url": avatar_url,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("user_id", g.db_user_id).execute()
        
        return jsonify({
            "message": "照片上傳成功",
            "avatar_url": avatar_url
        }), 200

    except Exception as e:
        print(f"照片上傳發生錯誤: {e}")
        return jsonify({"message": str(e)}), 500
