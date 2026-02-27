"""
Tests for api.user_preference endpoints (queue-based).
"""
import json
import pytest


def _valid_payload():
    return {
        "module_a": {"q1_languages": [{"name": "Python", "score": 2}]},
        "module_b": {"q9_troubleshoot": "log_search"},
        "module_c": {"q16_current_level": "entry_level"},
        "module_d": {"q20_values_top3": ["financial_reward"]},
    }


# ─── B-02  POST /api/dream-jobs ──────────────────────────────────────────────

class TestCreateCareerSurvey:

    def test_success(self, client, auth_headers):
        resp = client.post("/api/dream-jobs", json=_valid_payload(), headers=auth_headers)
        assert resp.status_code == 202
        data = resp.get_json()
        assert "job_id" in data
        assert data["status"] == "queued"

    def test_missing_module_a(self, client, auth_headers):
        payload = _valid_payload()
        payload.pop("module_a")
        resp = client.post("/api/dream-jobs", json=payload, headers=auth_headers)
        assert resp.status_code == 400
        assert "module_a" in resp.get_json()["error"]

    def test_missing_module_d(self, client, auth_headers):
        payload = _valid_payload()
        payload.pop("module_d")
        resp = client.post("/api/dream-jobs", json=payload, headers=auth_headers)
        assert resp.status_code == 400
        assert "module_d" in resp.get_json()["error"]

    def test_no_auth(self, client):
        resp = client.post("/api/dream-jobs", json=_valid_payload())
        assert resp.status_code == 401


# ─── B-02  GET /api/dream-jobs/<job_id> ──────────────────────────────────────

class TestPollSurveyJob:

    def test_queued(self, client, auth_headers, seed_job):
        jid = seed_job("job_up1")
        resp = client.get(f"/api/dream-jobs/{jid}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "queued"

    def test_done(self, client, auth_headers, seed_job):
        result = json.dumps({"dream_jobs": ["Backend Engineer"]})
        jid = seed_job("job_up2", status="done", result=result)
        resp = client.get(f"/api/dream-jobs/{jid}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["result"]["dream_jobs"] == ["Backend Engineer"]

    def test_failed(self, client, auth_headers, seed_job):
        jid = seed_job("job_up3", status="failed", error="LLM timeout")
        resp = client.get(f"/api/dream-jobs/{jid}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["error"] == "LLM timeout"

    def test_not_found(self, client, auth_headers):
        resp = client.get("/api/dream-jobs/nonexistent", headers=auth_headers)
        assert resp.status_code == 404
