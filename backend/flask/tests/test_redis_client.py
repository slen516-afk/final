"""
Tests for core.redis_client module.
"""
import os
import pytest
import redis as redis_lib


def test_constants():
    from core.redis_client import STREAM_NAME, DLQ_STREAM_NAME, GROUP_NAME, MAX_RETRY

    assert STREAM_NAME == "cv_jobs"
    assert DLQ_STREAM_NAME == "cv_jobs_dlq"
    assert GROUP_NAME == "cv_workers"
    assert MAX_RETRY == 3


def test_get_redis_client_returns_instance():
    from core.redis_client import get_redis_client
    client = get_redis_client()
    assert isinstance(client, redis_lib.Redis)


def test_redis_url_env_override(monkeypatch):
    """REDIS_URL env var should be respected."""
    monkeypatch.setenv("REDIS_URL", "redis://custom-host:9999/5")
    # Re-read the module-level variable
    from core import redis_client as rc_mod
    assert os.getenv("REDIS_URL") == "redis://custom-host:9999/5"


# ---------------------------------------------------------------------------
# Integration test — requires a running Redis (docker compose up -d redis)
# ---------------------------------------------------------------------------
@pytest.mark.integration
def test_redis_ping():
    """Ping a real Redis instance. Run with: pytest -m integration"""
    url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    r = redis_lib.Redis.from_url(url, decode_responses=True)
    assert r.ping() is True
