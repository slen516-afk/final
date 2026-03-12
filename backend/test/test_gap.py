import pytest
import os
import json
import uuid
import time
from datetime import datetime, timezone

# Mock Redis BEFORE other imports that might use it
class MockRedis:
    def __init__(self):
        self.data = {}
    def hset(self, name, key=None, value=None, mapping=None):
        if name not in self.data: self.data[name] = {}
        if mapping: self.data[name].update(mapping)
        else: self.data[name][key] = value
    def hgetall(self, name):
        return self.data.get(name, {})
    def xadd(self, name, fields, id='*', maxlen=None, approximate=True):
        pass

import sys
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
flask_dir = os.path.join(backend_dir, "flask")
if flask_dir not in sys.path:
    sys.path.insert(0, flask_dir)

import core.redis_client
redis_client = MockRedis()
core.redis_client.redis_client = redis_client

from core.supabase_client import supabase

# 根據 backend/service/llm_service/src/features/analysis/schemas.py 的 CareerReport 建立 Mock 資料
MOCK_GAP_ANALYSIS_RESULT = {
    "report_metadata": {
        "user_id": "mock_user_123",
        "timestamp": "2026-03-10T12:00:00Z",
        "version": "1.0"
    },
    "preliminary_summary": {
        "core_insight": "【產業洞察】：後端開發市場對雲端運算與微服務架構的需求持續增加。 【個人總結】：具備扎實的 Python 基礎，但在系統架構設計上略顯不足。"
    },
    "radar_chart": {
        "dimensions": [
            {"axis": "前端開發", "score": 2.0},
            {"axis": "後端開發", "score": 4.0},
            {"axis": "運維部署", "score": 3.0},
            {"axis": "AI與數據", "score": 3.5},
            {"axis": "工程品質", "score": 4.0},
            {"axis": "軟實力", "score": 4.5}
        ]
    },
    "gap_analysis": {
        "current_status": {
            "self_assessment": "初階工程師 (Junior)",
            "actual_level": "中階工程師 (Mid Level)",
            "cognitive_bias": "自評較保守，雖經驗尚淺，但技術儲備已達中階水準。建議補強 K8s 與 CI/CD 流程。"
        },
        "target_position": {
            "role": "後端工程師",
            "match_score": "80%",
            "gap_description": "【優勢 (Strengths)】：熟悉的 Python 後端技術棧。\n【劣勢 (Weaknesses)】：缺乏微服務實戰經驗。\n【機會 (Opportunities)】：雲計算推升後端需求。\n【威脅 (Threats)】：技術迭代快。\n【核心落差 (Gap)】：需加強 K8s 與高併發開發經驗。"
        }
    },
    "action_plan": {
        "short_term": "學習 Docker 與 K8s，完成微服務架構教學專案。",
        "mid_term": "參與開源專案，豐富系統架構經驗。",
        "long_term": "專注於高併發系統設計與領域驅動設計 (DDD)。"
    }
}

# 測試用設定
USE_REAL_ANALYSIS = os.environ.get("USE_REAL_ANALYSIS", "False").lower() in ("true", "1", "yes")

@pytest.fixture(scope="session")
def app(monkeypatch_session):
    """建立測試用 Flask 實體"""
    from main import create_app
    app = create_app()
    app.config.update({"TESTING": True})
    return app

@pytest.fixture(scope="session")
def monkeypatch_session():
    from _pytest.monkeypatch import MonkeyPatch
    m = MonkeyPatch()
    yield m
    m.undo()

@pytest.fixture(scope="session")
def client(app):
    return app.test_client()

@pytest.fixture(scope="class")
def test_user():
    """建立測試帳號，並確保有問卷與人格測驗結果以通過 API 驗證"""
    uid = str(uuid.uuid4())[:8]
    ts = int(time.time())
    email = f"gap_tester_{ts}_{uid}@test.careerpilot.io"
    password = "SecurePassword123!"
    username = f"gap_bot_{uid}"

    # 1. 建立測試使用者 (Supabase Auth 需自行註冊或直接新增資料)
    from core.supabase_client import supabase
    
    # 這裡借用 auth api 來註冊
    return {
        "email": email,
        "password": password,
        "username": username
    }

class TestGapAnalysisAPI:

    @classmethod
    def setup_class(cls):
        """設置測試環境：使用者註冊、登入及送出問卷數據"""
        pass # Will be done in setup logic or first test

    def test_01_setup_user_and_survey(self, client, test_user):
        """建立帳戶並登入，寫入測試問卷資料"""
        # 註冊
        payload = {
            "email": test_user["email"],
            "password": test_user["password"],
            "username": test_user["username"],
        }
        client.post("/api/auth/register", json=payload, headers={"X-Test-Bypass": "True"})
        
        # 登入
        login_res = client.post("/api/auth/login", json={"email": test_user["email"], "password": test_user["password"]})
        assert login_res.status_code == 200
        data = login_res.get_json()
        
        pytest.gap_shared_token = data["auth"]["accessToken"]
        pytest.gap_user_id = data["user"]["id"]
        
        # 尋找 db_user_id
        db_user = supabase.table("USER").select("user_id").eq("auth_uid", pytest.gap_user_id).single().execute()
        pytest.gap_db_user_id = db_user.data["user_id"]

        # 加入模擬問卷與人格數據 (用以通過 /gap-analysis 檢查)
        now = datetime.now(timezone.utc).isoformat()
        supabase.table("career_survey").insert({
            "user_id": pytest.gap_db_user_id,
            "questionnaire_response": {"fake_q": "answer"},
            "personality": {"type": "INTJ"},
            "completed_at": now
        }).execute()

    def test_02_start_gap_analysis(self, client):
        """測試提交落差分析任務"""
        headers = {"Authorization": f"Bearer {pytest.gap_shared_token}"}
        response = client.post("/api/gap-analysis", headers=headers)
        
        if response.status_code != 202:
            print(f"Error Response: {response.get_json()}")
        assert response.status_code == 202
        data = response.get_json()
        assert "job_id" in data
        assert data["status"] == "queued"
        
        pytest.current_job_id = data["job_id"]

    def test_03_poll_gap_analysis(self, client):
        """測試輪詢結果 (切換 Mock / 實際)"""
        headers = {"Authorization": f"Bearer {pytest.gap_shared_token}"}
        job_id = pytest.current_job_id

        if not USE_REAL_ANALYSIS:
            # 這是 Mock 模式，不啟動 worker，我們直接介入 Redis 來改變狀態
            now = datetime.now(timezone.utc).isoformat()
            
            # 從 Mock 資料中取得報告所需的 Metadata 並更新
            mock_data = MOCK_GAP_ANALYSIS_RESULT.copy()
            mock_data["report_metadata"]["user_id"] = str(pytest.gap_db_user_id)
            mock_data["report_metadata"]["timestamp"] = now

            redis_client.hset(f"job:{job_id}", mapping={
                "status": "done",
                "result": json.dumps(mock_data, ensure_ascii=False),
                "updated_at": now
            })

            # 測再次輪詢
            response = client.get(f"/api/gap-analysis/{job_id}", headers=headers)
            assert response.status_code == 200
            data = response.get_json()
            
            assert data["status"] == "done"
            assert "result" in data
            
            # 驗證返回的結果結構正確
            res_data = data["result"]
            assert "report_metadata" in res_data
            assert "radar_chart" in res_data
            assert "gap_analysis" in res_data
            assert "action_plan" in res_data
            print("\n[Mock] 成功讀取 Mock Gap Analysis 結果！")

        else:
            # 這是真實模式，需要有 Worker 將 Redis 中的 Queue 取出執行
            # 等待 worker 處理，最多等 60 秒
            print("\n[Real] 等待真實的 Worker 處理任務，請確保開啟了 Celery / Worker...")
            max_retries = 30
            for i in range(max_retries):
                response = client.get(f"/api/gap-analysis/{job_id}", headers=headers)
                assert response.status_code == 200
                data = response.get_json()
                
                status = data["status"]
                print(f"Polling {job_id} - {status} ({i+1}/{max_retries})")
                
                if status == "done":
                    assert "result" in data
                    res_data = data["result"]
                    # 確保包含所需欄位
                    assert "report_metadata" in res_data
                    assert "radar_chart" in res_data
                    assert "gap_analysis" in res_data
                    print("\n[Real] Worker 分析成功！")
                    break
                elif status in ["failed", "dlq"]:
                    pytest.fail(f"Worker failed to process the analysis. Error: {data.get('error')}")
                    
                time.sleep(2)
            else:
                pytest.fail("Timeout: Worker failed to process within 60 seconds")
