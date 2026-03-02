"""
Shared pytest fixtures — fakeredis + Flask test client + auth bypass.
"""
import json
import sys
import os
from types import SimpleNamespace
from datetime import datetime, timezone
from unittest.mock import MagicMock, PropertyMock

import pytest
import fakeredis

# ---------------------------------------------------------------------------
# 1.  Patch redis_client BEFORE any app code imports it
# ---------------------------------------------------------------------------
_fake_redis = fakeredis.FakeRedis(decode_responses=True)

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
    _fake_redis.flushall()


# ---------------------------------------------------------------------------
# 2.  Table-aware Supabase mock
# ---------------------------------------------------------------------------
FAKE_DB_USER_ID = 42  # integer user_id in USER table

# Default mock rows keyed by table name
_MOCK_ROWS = {
    "USER": [{"user_id": FAKE_DB_USER_ID, "email": "test@example.com"}],
    "resume": [{
        "resume_id": 1,
        "user_id": FAKE_DB_USER_ID,
        "template_id": 1,
        "resume_type": "generic",
        "structured_data": {"personal_info": {"name": "王小明"}},
        "normalized_data": {},
        "is_primary": True,
    }],
    "resume_optimization": [{
        "optimization_id": 1,
        "resume_id": 1,
        "user_id": FAKE_DB_USER_ID,
        "optimization_version": "1.0",
        "professional_summary": "資深後端工程師",
        "professional_experience": [
            "Google | SWE | 3 年 | 負責後端系統設計與開發，提升系統效能 30%。"
        ],
        "core_skills": ["Python", "Flask"],
        "projects": [
            "Resume Builder — 使用 Python + Flask 開發履歷生成系統，支援 PDF/DOCX 匯出。"
        ],
        "education": [
            "國立台灣大學 | 資訊工程學系 | 學士 | 2020 年畢業"
        ],
        "autobiography": None,
        "template_color": "#FF5733",
        "created_at": "2026-01-01T00:00:00+00",
    }],
}


def _make_query_chain(rows):
    """Create a MagicMock that behaves like supabase query builder.

    .single() causes .execute().data to return a dict (first row)
    instead of a list.
    """
    chain = MagicMock()
    # Track whether .single() was called
    chain._single_mode = False

    def _mark_single():
        chain._single_mode = True
        return chain

    # All builder methods return chain itself
    for method in ("select", "eq", "neq", "gt", "lt", "gte", "lte",
                   "order", "limit", "range", "in_"):
        getattr(chain, method).return_value = chain

    chain.single.side_effect = _mark_single

    def _execute():
        result = MagicMock()
        if chain._single_mode:
            result.data = rows[0] if rows else None
        else:
            result.data = rows
        return result

    chain.execute.side_effect = _execute

    # insert / update / upsert / delete also return a chain
    for write_method in ("insert", "update", "upsert", "delete"):
        sub = MagicMock()
        sub._single_mode = False

        def _make_sub_single(s=sub):
            s._single_mode = True
            return s

        for m2 in ("eq", "neq", "select", "order", "limit", "range"):
            getattr(sub, m2).return_value = sub
        sub.single.side_effect = _make_sub_single

        def _sub_execute(s=sub):
            result = MagicMock()
            if s._single_mode:
                result.data = rows[0] if rows else None
            else:
                result.data = rows
            return result

        sub.execute.side_effect = _sub_execute
        getattr(chain, write_method).return_value = sub

    return chain


def _build_mock_supabase():
    mock = MagicMock()

    def _table_dispatch(table_name):
        rows = _MOCK_ROWS.get(table_name, [{}])
        return _make_query_chain(rows)

    mock.table.side_effect = _table_dispatch
    return mock


@pytest.fixture(autouse=True)
def _patch_supabase(monkeypatch):
    """Provide a table-aware MagicMock supabase."""
    mock_supabase = _build_mock_supabase()

    for mod_path in [
        "core.supabase_client",
        "api.auth",
        "api.resume",
        "api.export",
    ]:
        try:
            mod = __import__(mod_path, fromlist=["supabase"])
            monkeypatch.setattr(mod, "supabase", mock_supabase)
        except Exception:
            pass

    yield


# ---------------------------------------------------------------------------
# 3.  Flask test app with TESTING=True
# ---------------------------------------------------------------------------
@pytest.fixture()
def app(monkeypatch):
    """Create a minimal Flask app for testing."""
    monkeypatch.setenv("SUPABASE_URL", "https://fake.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "fake-service-role-key")

    from flask import Flask
    from api.auth import auth_bp, login_required  # noqa: F811
    from api.analysis import analysis_bp
    from api.resume import resume_bp
    from api.export import export_bp
    from api.user_preference import user_preference_bp

    test_app = Flask(__name__)
    test_app.config["TESTING"] = True

    test_app.register_blueprint(auth_bp, url_prefix="/api/auth")
    test_app.register_blueprint(user_preference_bp, url_prefix="/api")
    test_app.register_blueprint(resume_bp, url_prefix="/api/resumes")
    test_app.register_blueprint(export_bp, url_prefix="/api/resumes")
    test_app.register_blueprint(analysis_bp, url_prefix="/api/analysis")

    return test_app


@pytest.fixture()
def client(app):
    return app.test_client()


# ---------------------------------------------------------------------------
# 4.  Auth helpers
# ---------------------------------------------------------------------------
FAKE_USER_ID = "user-test-001"  # Supabase auth UUID (string)


@pytest.fixture()
def auth_headers(monkeypatch):
    """Return headers with a fake Bearer token AND patch supabase.auth.get_user
    so login_required passes and g.db_user_id is set correctly."""
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
              task_type="resume_analysis", survey_data="", retry_count="0"):
        now = datetime.now(timezone.utc).isoformat()
        mapping = {
            "status": status,
            "user_id": user_id,
            "resume_id": resume_id,
            "survey_id": survey_id,
            "task_type": task_type,
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
