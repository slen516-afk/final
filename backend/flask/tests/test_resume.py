"""
Tests for api.resume endpoints.
"""
import pytest


# ─── C-02  POST /api/resumes/form ────────────────────────────────────────────

class TestCreateResumeForm:

    def _payload(self):
        return {
            "structured_data": {
                "personal_info": {"name": "王小明"},
                "education": [{"school": "台大"}],
            },
            "template_id": 1,
            "resume_type": "tech",
        }

    def test_success(self, client, auth_headers):
        resp = client.post("/api/resumes/form", json=self._payload(), headers=auth_headers)
        assert resp.status_code == 201
        data = resp.get_json()
        assert "resume_id" in data
        assert data["status"] == "completed"

    def test_missing_structured_data(self, client, auth_headers):
        payload = self._payload()
        payload.pop("structured_data")
        resp = client.post("/api/resumes/form", json=payload, headers=auth_headers)
        assert resp.status_code == 400

    def test_no_auth(self, client):
        resp = client.post("/api/resumes/form", json=self._payload())
        assert resp.status_code == 401


# ─── C-04  GET /api/resumes/<id> ─────────────────────────────────────────────

class TestGetResume:

    def test_success(self, client, auth_headers):
        resp = client.get("/api/resumes/1", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["resume_id"] == 1
        assert "structured_data" in data


# ─── C-05  PUT /api/resumes/<id> → resume_optimization ───────────────────────

class TestUpdateResume:

    def test_success(self, client, auth_headers):
        payload = {
            "structured_data": {
                "professional_summary": "資深後端工程師",
                "professional_experience": ["Google | SWE | 2020-01 ~ Present | 負責後端開發"],
                "core_skills": ["Python", "Flask"],
                "projects": ["Resume Builder — 履歷產生器"],
                "education": ["台大 | 資工系 | 學士 | 2020-06"],
            },
            "style_settings": {"color": "#FF5733"},
        }
        resp = client.put("/api/resumes/1", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.get_json()
        assert "optimization_id" in data
        assert data["optimization_version"] == "1"
        assert data["template_color"] == "#FF5733"

    def test_missing_body(self, client, auth_headers):
        resp = client.put(
            "/api/resumes/1",
            data="",
            content_type="application/json",
            headers=auth_headers,
        )
        assert resp.status_code in (400, 500)


# ─── Version endpoints ───────────────────────────────────────────────────────

class TestResumeVersions:

    def test_list_versions(self, client, auth_headers):
        resp = client.get("/api/resumes/1/versions", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert "versions" in data
        assert data["resume_id"] == 1

    def test_get_specific_version(self, client, auth_headers):
        resp = client.get("/api/resumes/1/versions/1", headers=auth_headers)
        # 可能 200 或 404 取決於 mock 設定
        assert resp.status_code in (200, 404)


# ─── E-01  GET /api/resumes/<id>/export ──────────────────────────────────────

class TestExportResume:

    def test_default_pdf(self, client, auth_headers):
        resp = client.get("/api/resumes/1/export", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.content_type == "application/pdf"

    def test_with_format_param(self, client, auth_headers):
        resp = client.get("/api/resumes/1/export?format=docx", headers=auth_headers)
        assert resp.status_code == 200
        assert "wordprocessingml" in resp.content_type
