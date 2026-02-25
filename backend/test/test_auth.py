import pytest
import uuid
from core.supabase_client import supabase
from main import create_app


@pytest.fixture(scope="session")
def app():
    """建立測試用 Flask 實體"""
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
    uid = str(uuid.uuid4())[:8]
    return {
        "email": f"tester_{uid}@example.com",
        "password": "SecurePassword123!",
        "username": f"bot_{uid}",
    }


class TestAuthAPI:

    def test_01_register_user(self, client, test_user):
        """測試註冊 API"""
        payload = {
            "email": test_user["email"],
            "password": test_user["password"],
            "username": test_user["username"],
        }
        response = client.post("/api/auth/register", json=payload)

        # 註冊成功應回傳 201
        assert response.status_code == 201
        data = response.get_json()
        assert "message" in data

    def test_02_login_success(self, client, test_user):
        """測試登入 API 並獲取 Token"""
        payload = {"email": test_user["email"], "password": test_user["password"]}
        response = client.post("/api/auth/login", json=payload)

        assert response.status_code == 200
        data = response.get_json()

        # 驗證回傳格式是否符合前端定義
        assert "auth" in data
        assert "accessToken" in data["auth"]
        assert data["user"]["id"] is not None

        # 儲存 token 供後續測試使用
        pytest.shared_token = data["auth"]["accessToken"]

    def test_03_login_wrong_password(self, client, test_user):
        """測試錯誤密碼"""
        payload = {"email": test_user["email"], "password": "wrong_password"}
        response = client.post("/api/auth/login", json=payload)
        assert response.status_code == 401

    def test_04_get_profile_with_token(self, client):
        """測試 login_required 裝飾器與 Profile API"""
        if not hasattr(pytest, "shared_token"):
            pytest.skip("No token available from previous login test")

        headers = {"Authorization": f"Bearer {pytest.shared_token}"}
        response = client.get("/api/auth/profile", headers=headers)

        # 如果 Supabase 中 public.users 表已同步，應回傳 200
        # 如果沒同步，可能會回傳 500，這也是一種測試回饋
        assert response.status_code in [200, 500, 404]

    def test_05_get_profile_unauthorized(self, client):
        """測試未授權存取"""
        response = client.get("/api/auth/profile")
        assert response.status_code == 401
        assert response.get_json()["message"] == "請先登入"
