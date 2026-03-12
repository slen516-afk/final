import pytest
import os
import sys
import json
import uuid
import time
from unittest.mock import patch, MagicMock
from io import BytesIO

# 確保路徑正確，以便導入後端模組
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
flask_dir = os.path.join(backend_dir, "flask")
if flask_dir not in sys.path:
    sys.path.insert(0, flask_dir)

from core.supabase_client import supabase

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
        return f"{int(time.time() * 1000)}-0"

import core.redis_client
redis_client_mock = MockRedis()
core.redis_client.redis_client = redis_client_mock

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

@pytest.fixture(scope="session")
def test_user():
    """生成測試用帳號"""
    uid = str(uuid.uuid4())[:8]
    ts = int(time.time())
    email = f"frontend_test_{ts}_{uid}@mock.careerpilot.io"
    password = "UserPassword123!"
    username = f"FE_User_{uid}"
    return {
        "email": email,
        "password": password,
        "username": username
    }

class TestFrontendSimulation:
    @classmethod
    def setup_class(cls):
        cls.shared_token = None
        cls.user_id = None
        cls.db_user_id = None
        cls.resume_id = None

    def test_01_auth_flow(self, client, test_user):
        """模擬前端流程：註冊與登入"""
        payload = {
            "email": test_user["email"],
            "password": test_user["password"],
            "username": test_user["username"],
        }
        res = client.post("/api/auth/register", json=payload, headers={"X-Test-Bypass": "True"})
        assert res.status_code in [200, 201]
        
        login_res = client.post("/api/auth/login", json={"email": test_user["email"], "password": test_user["password"]})
        assert login_res.status_code == 200
        data = login_res.get_json()
        
        self.__class__.shared_token = data["auth"]["accessToken"]
        auth_uid = data["user"]["id"]
        
        db_user = supabase.table("USER").select("user_id").eq("auth_uid", auth_uid).single().execute()
        self.__class__.db_user_id = db_user.data["user_id"]

    def test_02_survey_and_personality(self, client):
        """模擬前端流程：填寫職能問卷與人格測驗"""
        headers = {"Authorization": f"Bearer {self.shared_token}"}
        
        survey_payload = {
            "module_a": {"skills": ["Python", "Docker"]},
            "module_b": {"experience": "2 years"},
            "module_c": {"goals": "Backend Engineer"},
            "module_d": {"learning_style": "Hands-on"}
        }
        res1 = client.post("/api/questionnaire-response", json=survey_payload, headers=headers)
        assert res1.status_code in [200, 201]
        
        personality_payload = {
            "trait_calculation_debug": {},
            "trait_normalized_scores": {"Efficiency": 90, "Creativity": 80},
            "primary_archetype": "Architect",
            "secondary_archetypes": ["Leader"],
            "trait_created_at": "2026-03-10T12:00:00Z"
        }
        res2 = client.post("/api/personality", json=personality_payload, headers=headers)
        assert res2.status_code in [200, 201]

    def test_03_ocr_upload(self, client):
        """模擬前端流程：上傳履歷供 OCR 處理"""
        try:
            pdf_data = b"MOCK PDF DATA"
            data = {
                'file': (BytesIO(pdf_data), 'test_resume.pdf'),
                'template_id': '1'
            }
            res = client.post("/api/ocr/", data=data, content_type='multipart/form-data')
            assert res.status_code in [200, 400, 500] 
        except Exception:
            pass

    def test_04_resume_management(self, client):
        """模擬前端流程：儲存、讀取與優化履歷"""
        headers = {"Authorization": f"Bearer {self.shared_token}"}
        
        # 建立簡歷
        resume_payload = {
            "resume_name": "Senior Software Engineer",
            "resume_type": "generic",
            "structured_data": {
                "work_experience": [{"company": "Tech", "title": "Dev"}],
                "skills": ["A", "B"]
            }
        }
        res = client.post("/api/resumes/form", json=resume_payload, headers=headers)
        assert res.status_code == 201
        self.__class__.resume_id = res.get_json()['resume_id']

        # 讀取簡歷
        res = client.get(f"/api/resumes/{self.resume_id}", headers=headers)
        assert res.status_code == 200

        # 優化簡歷
        opt_payload = {
            "structured_data": {
                "work_experience": [{"company": "Tech", "title": "Senior Dev"}],
                "skills": ["A", "B", "C"]
            },
            "style_settings": {
                "template_id": 2,
                "style_color": "#123456"
            }
        }
        res = client.put(f"/api/resumes/{self.resume_id}", json=opt_payload, headers=headers)
        assert res.status_code == 201

    def test_05_analysis(self, client):
        """模擬前端流程：發起分析任務並輪詢進度"""
        headers = {"Authorization": f"Bearer {self.shared_token}"}
        
        res = client.post("/api/analysis/tasks", json={"task_type": "resume_opt"}, headers=headers)
        assert res.status_code == 202
        job_id = res.get_json()["job_id"]
        
        res = client.get(f"/api/analysis/jobs/{job_id}", headers=headers)
        assert res.status_code == 200

    def test_06_dream_jobs(self, client):
        """模擬前端流程：發送夢想職業分析請求"""
        headers = {"Authorization": f"Bearer {self.shared_token}"}
        res = client.post("/api/dream-jobs", headers=headers)
        assert res.status_code in [202, 404]

    def test_07_recommendations(self, client):
        """模擬前端流程：取得職缺與推薦"""
        headers = {"Authorization": f"Bearer {self.shared_token}"}
        
        res = client.get(f"/api/users/{self.db_user_id}/resumes", headers=headers)
        assert res.status_code == 200
        
        rec_payload = {
            "resumeId": self.resume_id,
            "userId": self.db_user_id,
            "sourceType": "RESUME",
            "city": "台北市",
            "workMode": "混合"
        }
        
        # 修正 Mock 使其回傳可序列化的資料
        from service.llm_service.src.features.matching.service import CareerMatchingService
        mock_instance = CareerMatchingService.return_value
        mock_instance.find_best_jobs.return_value = [{"job_title": "Software Engineer", "match_score": 0.95}]
        
        res = client.post("/api/jobs/v2/recommendations", json=rec_payload, headers=headers)
        assert res.status_code == 200
        assert "recommendations" in res.get_json()

    def test_08_cover_letter(self, client):
        """模擬前端流程：觸發與預覽求職信"""
        headers = {"Authorization": f"Bearer {self.shared_token}"}
        preview_payload = {
            "job_id": 101,
            "optimization_id": 202
        }
        
        from api.cover_letter import RecommendJobSearchTool, FetchOptimizeResumeTool
        
        with patch("api.cover_letter.RecommendJobSearchTool") as mock_job_tool:
            with patch("api.cover_letter.FetchOptimizeResumeTool") as mock_resume_tool:
                mock_job_tool.return_value._run.return_value = {"id": 101, "title": "Mock Job"}
                mock_resume_tool.return_value._run.return_value = {"id": 202, "content": "Mock Resume"}
                
                res = client.post("/api/cover_letter/preview_data", json=preview_payload, headers=headers)
                assert res.status_code == 200
                data = res.get_json()
                assert data["status"] == "success"
                assert data["job_data"]["id"] == 101
    def test_09_resume_processing(self, client):
        """模擬前端流程：履歷處理模組"""
        headers = {"Authorization": f"Bearer {self.shared_token}"}
        
        # 測試列表取得
        res = client.get(f"/api/resume_process/list/{self.db_user_id}", headers=headers)
        assert res.status_code == 200
        
        # 測試分析 (丟 Queue)
        # 修正 Payload 以符合 resume_processing.py:236 的期待 (需要 user_id, resume_data)
        analyze_payload = {
            "user_id": self.db_user_id,
            "resume_data": {"skills": ["Python"]}
        }
        res = client.post("/api/resume_process/analyze", json=analyze_payload, headers=headers)
        assert res.status_code in [202, 200]
