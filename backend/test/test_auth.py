import pytest
import uuid
import io
from core.supabase_client import supabase
# from main import create_app (Moved to fixture)


@pytest.fixture(scope="session")
def app():
    """建立測試用 Flask 實體"""
    # 確保路徑與 main.py 一致
    import sys
    import os
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    
    # 加入 flask 目錄以便引入 api.*
    flask_dir = os.path.join(backend_dir, "flask")
    if flask_dir not in sys.path:
        sys.path.insert(0, flask_dir)

    # 測試模式中，停用 OCR 模型載入
    # os.environ["SKIP_OCR"] = "True"

    from main import create_app
    app = create_app()
    app.config.update({"TESTING": True})
    return app


@pytest.fixture(scope="session")
def client(app):
    """建立 Flask 測試客戶端"""
    return app.test_client()


@pytest.fixture(scope="session")
def test_user():
    """生成唯一的測試帳號資料"""
    import time
    uid = str(uuid.uuid4())[:8]
    ts = int(time.time())
    return {
        "email": f"tester_{ts}_{uid}@test.careerpilot.io",
        "password": "SecurePassword123!",
        "username": f"bot_{uid}",
    }


class TestAuthAPI:

    def test_01_register_user(self, client, test_user):
        """測試註冊 API 並驗證資料庫"""
        payload = {
            "email": test_user["email"],
            "password": test_user["password"],
            "username": test_user["username"],
        }
        headers = {"X-Test-Bypass": "True"}
        response = client.post("/api/auth/register", json=payload, headers=headers)

    
        # 註冊成功應回傳 201 或 200 (取決於是否需要信箱驗證，當前 auth.py 邏輯可能有 201)
        assert response.status_code in [200, 201]
        data = response.get_json()
        assert "message" in data
        
        # 驗證資料是否寫入 USER 表
        db_user = supabase.table("USER").select("*").eq("email", test_user["email"]).execute()
        assert len(db_user.data) > 0
        assert db_user.data[0]["email"] == test_user["email"]
        
        # 驗證是否建立了 user_profile
        db_profile = supabase.table("user_profile").select("*").eq("user_id", db_user.data[0]["user_id"]).execute()
        assert len(db_profile.data) > 0
        assert db_profile.data[0]["full_name"] == test_user["username"]

    def test_02_login_success(self, client, test_user):
        """測試登入 API 並獲取 Token"""
        payload = {"email": test_user["email"], "password": test_user["password"]}
        response = client.post("/api/auth/login", json=payload)

        assert response.status_code == 200
        data = response.get_json()

        # 驗證回傳格式
        assert "auth" in data
        assert "accessToken" in data["auth"]
        assert "user" in data
        assert data["user"]["id"] is not None

        # 儲存 token 供後續測試使用
        pytest.shared_token = data["auth"]["accessToken"]
        pytest.user_id = data["user"]["id"]
        
        # 驗證 last_login 是否更新 (需要確保 auth_uid 匹配)
        db_user = supabase.table("USER").select("last_login").eq("auth_uid", pytest.user_id).execute()
        
        # 如果透過 auth_uid 找不到，則透過 email 找作為備案(已添加至auth.py)
        if not db_user.data:
            db_user = supabase.table("USER").select("last_login").eq("email", test_user["email"]).execute()
            
        assert len(db_user.data) > 0
        assert db_user.data[0]["last_login"] is not None

    def test_03_login_wrong_password(self, client, test_user):
        """測試錯誤密碼"""
        payload = {"email": test_user["email"], "password": "wrong_password"}
        response = client.post("/api/auth/login", json=payload)
        assert response.status_code == 401

    def test_04_get_profile_with_token(self, client):
        """測試 Profile API"""
        if not hasattr(pytest, "shared_token"):
            pytest.skip("No token available")

        headers = {"Authorization": f"Bearer {pytest.shared_token}"}
        response = client.get("/api/auth/profile", headers=headers)

        assert response.status_code == 200
        data = response.get_json()
        assert "email" in data
        assert data["auth_uid"] == pytest.user_id

    def test_05_get_profile_unauthorized(self, client):
        """測試未授權存取"""
        response = client.get("/api/auth/profile")
        assert response.status_code == 401

    def test_06_upload_avatar(self, client):
        """測試照片上傳 API 並驗證資料庫"""
        if not hasattr(pytest, "shared_token"):
            pytest.skip("No token available")

        # 準備測試圖片資料
        img_data = b"fake-image-binary-content"
        data = {
            'file': (io.BytesIO(img_data), 'test_avatar.png'),
        }
        headers = {"Authorization": f"Bearer {pytest.shared_token}"}
        
        response = client.post(
            "/api/auth/upload-avatar",
            data=data,
            headers=headers,
            content_type='multipart/form-data'
        )

        assert response.status_code == 200
        res_data = response.get_json()
        assert "avatar_url" in res_data
        
        # 驗證資料庫中的 avatar_url 是否更新
        # 先獲取 db_user_id (integer)
        db_user = supabase.table("USER").select("user_id").eq("auth_uid", pytest.user_id).single().execute()
        db_user_id = db_user.data["user_id"]
        
        db_profile = supabase.table("user_profile").select("avatar_url").eq("user_id", db_user_id).single().execute()
        assert db_profile.data["avatar_url"] == res_data["avatar_url"]


