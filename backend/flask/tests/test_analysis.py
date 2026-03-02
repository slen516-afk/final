"""
Tests for api.analysis endpoints.
"""
import json
import pytest


# ─── D-01  POST /api/analysis/tasks ──────────────────────────────────────────

class TestStartAnalysisTask:

    def test_success(self, client, auth_headers):
        payload = {"task_type": "resume_analysis"}
        resp = client.post("/api/analysis/tasks", json=payload, headers=auth_headers)

        assert resp.status_code == 202
        data = resp.get_json()
        assert "job_id" in data
        assert data["status"] == "queued"

    def test_success_with_optional_ids(self, client, auth_headers):
        payload = {"task_type": "resume_opt", "resume_id": "r1", "survey_id": "s1"}
        resp = client.post("/api/analysis/tasks", json=payload, headers=auth_headers)
        assert resp.status_code == 202

    def test_unsupported_task_type(self, client, auth_headers):
        resp = client.post("/api/analysis/tasks", json={"task_type": "invalid"}, headers=auth_headers)
        assert resp.status_code == 400
        assert "Unsupported" in resp.get_json()["error"]

    def test_no_auth(self, client):
        resp = client.post("/api/analysis/tasks", json={"task_type": "resume_analysis"})
        assert resp.status_code == 401


# ─── D-02  GET /api/analysis/jobs/<job_id> ───────────────────────────────────

class TestPollJob:

    def test_queued(self, client, auth_headers, seed_job):
        jid = seed_job("job_q1")
        resp = client.get(f"/api/analysis/jobs/{jid}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "queued"
        assert "result" not in data

    def test_done(self, client, auth_headers, seed_job):
        result = json.dumps({"score": 85})
        suggestions = json.dumps({"tip": "add Docker"})
        jid = seed_job("job_d1", status="done", result=result, suggestions=suggestions)

        resp = client.get(f"/api/analysis/jobs/{jid}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "done"
        assert data["result"]["score"] == 85
        assert data["suggestions"]["tip"] == "add Docker"

    def test_failed(self, client, auth_headers, seed_job):
        jid = seed_job("job_f1", status="failed", error="timeout")
        resp = client.get(f"/api/analysis/jobs/{jid}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["error"] == "timeout"

    def test_not_found(self, client, auth_headers):
        resp = client.get("/api/analysis/jobs/nonexistent", headers=auth_headers)
        assert resp.status_code == 404


# ─── D-02  GET /api/analysis/tasks/<id>/status ───────────────────────────────

class TestGetAnalysisStatus:

    def test_success(self, client, auth_headers, seed_job):
        jid = seed_job("job_s1", status="processing")
        resp = client.get(f"/api/analysis/tasks/{jid}/status", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "processing"

    def test_not_found(self, client, auth_headers):
        resp = client.get("/api/analysis/tasks/no_such/status", headers=auth_headers)
        assert resp.status_code == 404


# ─── D-03  GET /api/analysis/tasks/<id>/suggestions ──────────────────────────

class TestGetOptimizationSuggestions:

    def test_done(self, client, auth_headers, seed_job):
        suggestions = json.dumps({"skill_gap": ["K8s"]})
        jid = seed_job("job_sg1", status="done", suggestions=suggestions, task_type="resume_analysis")
        resp = client.get(f"/api/analysis/tasks/{jid}/suggestions", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["skill_gap"] == ["K8s"]

    def test_pending(self, client, auth_headers, seed_job):
        jid = seed_job("job_sg2", status="queued", task_type="resume_analysis")
        resp = client.get(f"/api/analysis/tasks/{jid}/suggestions", headers=auth_headers)
        assert resp.status_code == 202

    def test_wrong_task_type(self, client, auth_headers, seed_job):
        jid = seed_job("job_sg3", status="done", task_type="resume_opt")
        resp = client.get(f"/api/analysis/tasks/{jid}/suggestions", headers=auth_headers)
        assert resp.status_code == 400


# ─── D-04  GET /api/analysis/tasks/<id>/results ──────────────────────────────

class TestGetOptimizationResults:

    def test_done(self, client, auth_headers, seed_job):
        result = json.dumps({"career_readiness_score": 90})
        jid = seed_job("job_r1", status="done", result=result, task_type="resume_opt")
        resp = client.get(f"/api/analysis/tasks/{jid}/results", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["career_readiness_score"] == 90

    def test_pending(self, client, auth_headers, seed_job):
        jid = seed_job("job_r2", status="processing", task_type="resume_opt")
        resp = client.get(f"/api/analysis/tasks/{jid}/results", headers=auth_headers)
        assert resp.status_code == 202
        assert "尚未完成" in resp.get_json()["message"]

    def test_wrong_task_type(self, client, auth_headers, seed_job):
        jid = seed_job("job_r3", status="done", task_type="resume_analysis")
        resp = client.get(f"/api/analysis/tasks/{jid}/results", headers=auth_headers)
        assert resp.status_code == 400
