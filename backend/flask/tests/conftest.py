"""
Shared pytest fixtures — fakeredis + Flask test client + auth bypass.
"""
import json
import sys
import os
from types import SimpleNamespace
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
import fakeredis

# ---------------------------------------------------------------------------
# 1.  Patch redis_client BEFORE any app code imports it
# ---------------------------------------------------------------------------
_fake_redis = fakeredis.FakeRedis(decode_responses=True)

# We need to patch core.redis_client at the module level before importing app
# Insert paths so core / api / worker packages are importable
_flask_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # backend/flask
_backend_dir = os.path.dirname(_flask_dir)                                # backend

for _p in [_flask_dir, _backend_dir]:
    if _p not in sys.path:
        sys.path.insert(0, _p)


@pytest.fixture(autouse=True)
def _patch_redis(monkeypatch):
    """Replace redis_client with fakeredis in every module that imported it."""
    import core.redis_client as rc_mod
    monkeypatch.setattr(rc_mod, "redis_client", _fake_redis)

    # Also patch the local references inside each API / worker module
    try:
        import api.analysis as analysis_mod
        monkeypatch.setattr(analysis_mod, "redis_client", _fake_redis)
    except Exception:
        pass

    try:
        import api.user_preference as up_mod
        monkeypatch.setattr(up_mod, "redis_client", _fake_redis)
    except Exception:
        pass

    try:
        import worker.cv_worker as cw_mod
        monkeypatch.setattr(cw_mod, "redis_client", _fake_redis)
    except Exception:
        pass

    yield

    # Flush after each test to keep isolation
    _fake_redis.flushall()


# ---------------------------------------------------------------------------
# 2.  Mock Supabase so `from core.supabase_client import supabase` doesn't
#     need real env vars
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def _patch_supabase(monkeypatch):
    """Provide a MagicMock supabase so auth / resume modules can import."""
    mock_supabase = MagicMock()
    try:
        import core.supabase_client as sc_mod
        monkeypatch.setattr(sc_mod, "supabase", mock_supabase)
    except Exception:
        pass
    try:
        import api.auth as auth_mod
        monkeypatch.setattr(auth_mod, "supabase", mock_supabase)
    except Exception:
        pass
    try:
        import api.resume as resume_mod
        monkeypatch.setattr(resume_mod, "supabase", mock_supabase)
    except Exception:
        pass
    yield


# ---------------------------------------------------------------------------
# 3.  Flask test app with TESTING=True
# ---------------------------------------------------------------------------
@pytest.fixture()
def app(monkeypatch):
    """Create a minimal Flask app for testing (no OCR, no model loading)."""
    # Prevent supabase_client from raising during import
    monkeypatch.setenv("SUPABASE_URL", "https://fake.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "fake-service-role-key")

    from flask import Flask
    from api.auth import auth_bp, login_required  # noqa: F811
    from api.analysis import analysis_bp
    from api.resume import resume_bp
    from api.user_preference import user_preference_bp

    test_app = Flask(__name__)
    test_app.config["TESTING"] = True

    test_app.register_blueprint(auth_bp, url_prefix="/api/auth")
    test_app.register_blueprint(user_preference_bp, url_prefix="/api")
    test_app.register_blueprint(resume_bp, url_prefix="/api/resumes")
    test_app.register_blueprint(analysis_bp, url_prefix="/api/analysis")

    return test_app


@pytest.fixture()
def client(app):
    return app.test_client()


# ---------------------------------------------------------------------------
# 4.  Auth helpers
# ---------------------------------------------------------------------------
FAKE_USER_ID = "user-test-001"


@pytest.fixture()
def auth_headers(monkeypatch):
    """Return headers with a fake Bearer token AND patch supabase.auth.get_user
    so login_required passes."""
    import api.auth as auth_mod

    fake_user = SimpleNamespace(id=FAKE_USER_ID)
    fake_response = SimpleNamespace(user=fake_user)
    monkeypatch.setattr(auth_mod.supabase.auth, "get_user", lambda _: fake_response)

    return {"Authorization": "Bearer fake-token"}


# ---------------------------------------------------------------------------
# 5.  Job seed helper
# ---------------------------------------------------------------------------
@pytest.fixture()
def seed_job():
    """Factory to pre-populate a job hash in fake Redis."""
    def _seed(job_id, *, status="queued", result="", suggestions="", error="",
              user_id=FAKE_USER_ID, resume_id="r1", survey_id="s1",
              survey_data="", retry_count="0"):
        now = datetime.now(timezone.utc).isoformat()
        mapping = {
            "status": status,
            "user_id": user_id,
            "resume_id": resume_id,
            "survey_id": survey_id,
            "survey_data": survey_data,
            "result": result,
            "suggestions": suggestions,
            "error": error,
            "retry_count": retry_count,
            "created_at": now,
            "updated_at": now,
        }
        _fake_redis.hset(f"job:{job_id}", mapping=mapping)
        return job_id
    return _seed
