"""
Tests for api.resume endpoints.
"""
import pytest


# ─── C-02  POST /api/resumes/form ────────────────────────────────────────────

class TestCreateResumeForm:

    def _payload(self):
        return {
            "survey_id": "s1",
            "structured_data": {
                "personal_info": {"name": "王小明"},
                "education": [{"school": "台大"}],
            },
            "template_id": 2,
            "resume_type": "tech",
        }

    def test_success(self, client, auth_headers):
        resp = client.post("/api/resumes/form", json=self._payload(), headers=auth_headers)
        assert resp.status_code == 201
        data = resp.get_json()
        assert "resume_id" in data
        assert data["status"] == "completed"

    def test_missing_survey_id(self, client, auth_headers):
        payload = self._payload()
        payload.pop("survey_id")
        resp = client.post("/api/resumes/form", json=payload, headers=auth_headers)
        assert resp.status_code == 400
        assert "survey_id" in resp.get_json()["error"]

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


# ─── C-05  PUT /api/resumes/<id> ─────────────────────────────────────────────

class TestUpdateResume:

    def test_success(self, client, auth_headers):
        payload = {
            "structured_data": {"personal_info": {"name": "李大華"}},
            "template_id": 3,
            "style_settings": {"color": "#FF5733"},
        }
        resp = client.put("/api/resumes/1", json=payload, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["resume_id"] == 1
        assert data["saved_settings"]["template_id"] == 3

    def test_missing_structured_data(self, client, auth_headers):
        resp = client.put("/api/resumes/1", json={"template_id": 1}, headers=auth_headers)
        assert resp.status_code == 400


# ─── E-01  GET /api/resumes/<id>/export ──────────────────────────────────────

class TestExportResume:

    def test_default_pdf(self, client, auth_headers):
        resp = client.get("/api/resumes/1/export", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.content_type == "application/pdf"

    def test_with_format_param(self, client, auth_headers):
        resp = client.get("/api/resumes/1/export?format=docx", headers=auth_headers)
        assert resp.status_code == 200
        assert b"docx" in resp.data
