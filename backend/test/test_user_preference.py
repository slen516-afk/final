from types import SimpleNamespace

from api import auth as auth_module
from app import app


def _auth_headers():
    return {"Authorization": "Bearer fake-token"}


def _valid_payload():
    return {
        "module_a": {"skills": ["Python"]},
        "module_b": {"soft_skills": ["Communication"]},
        "module_c": {"status": {"experience_years": 1}},
        "module_d": {"values": ["Growth"]},
    }


def test_create_career_survey_success(monkeypatch):
    fake_user = SimpleNamespace(id="user-test-001")
    fake_response = SimpleNamespace(user=fake_user)
    monkeypatch.setattr(auth_module.supabase.auth, "get_user", lambda _: fake_response)

    app.config["TESTING"] = True
    client = app.test_client()

    response = client.post("/api/dream-jobs", json=_valid_payload(), headers=_auth_headers())

    assert response.status_code == 201
    data = response.get_json()
    assert data["survey_id"] == 101


def test_create_career_survey_missing_module(monkeypatch):
    fake_user = SimpleNamespace(id="user-test-001")
    fake_response = SimpleNamespace(user=fake_user)
    monkeypatch.setattr(auth_module.supabase.auth, "get_user", lambda _: fake_response)

    app.config["TESTING"] = True
    client = app.test_client()
    payload = _valid_payload()
    payload.pop("module_d")

    response = client.post("/api/dream-jobs", json=payload, headers=_auth_headers())

    assert response.status_code == 400
    assert "module_d" in response.get_json()["error"]


def test_create_career_survey_requires_auth():
    app.config["TESTING"] = True
    client = app.test_client()

    response = client.post("/api/dream-jobs", json=_valid_payload())

    assert response.status_code == 401
