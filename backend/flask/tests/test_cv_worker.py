"""
Tests for worker.cv_worker — all LLM calls are mocked.
"""
import json
import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

import fakeredis

# We need a fresh fake redis that we control in each test
_fake = fakeredis.FakeRedis(decode_responses=True)


@pytest.fixture(autouse=True)
def patch_worker_redis(monkeypatch):
    """Patch redis_client inside cv_worker to use our fakeredis instance."""
    import worker.cv_worker as cw
    monkeypatch.setattr(cw, "redis_client", _fake)
    yield
    _fake.flushall()


def _seed_job(job_id, **overrides):
    now = datetime.now(timezone.utc).isoformat()
    mapping = {
        "status": "queued",
        "user_id": "u1",
        "resume_id": "r1",
        "survey_id": "s1",
        "survey_data": json.dumps({"module_a": {}}),
        "result": "",
        "suggestions": "",
        "error": "",
        "retry_count": "0",
        "created_at": now,
        "updated_at": now,
    }
    mapping.update(overrides)
    _fake.hset(f"job:{job_id}", mapping=mapping)


# ──────────────────────────────────────────────────────────────────────────────
# ensure_group
# ──────────────────────────────────────────────────────────────────────────────

class TestEnsureGroup:

    def test_creates_group(self):
        import worker.cv_worker as cw
        # Should not raise
        cw.ensure_group()

    def test_busygroup_is_ignored(self):
        import worker.cv_worker as cw
        # First call creates, second should hit BUSYGROUP and not raise
        cw.ensure_group()
        cw.ensure_group()


# ──────────────────────────────────────────────────────────────────────────────
# process_job
# ──────────────────────────────────────────────────────────────────────────────

class TestProcessJob:

    def test_cv_analysis_returns_mock_result(self):
        import worker.cv_worker as cw
        _seed_job("pj1")
        result = cw.process_job("pj1", "cv_analysis")
        assert "result" in result
        assert "suggestions" in result
        assert result["result"]["career_readiness_score"] == 85.0

    def test_survey_analysis_calls_run_analysis(self, monkeypatch):
        import worker.cv_worker as cw
        _seed_job("pj2")

        mock_report = {"dream_jobs": ["Data Scientist"], "score": 78}
        monkeypatch.setattr(cw, "_run_analysis", lambda data: mock_report)

        result = cw.process_job("pj2", "survey_analysis")
        assert result["result"]["dream_jobs"] == ["Data Scientist"]

    def test_survey_analysis_error(self, monkeypatch):
        import worker.cv_worker as cw
        _seed_job("pj3")

        monkeypatch.setattr(cw, "_run_analysis", lambda data: {"error": "LLM down"})

        with pytest.raises(RuntimeError, match="LLM down"):
            cw.process_job("pj3", "survey_analysis")

    def test_job_not_found(self):
        import worker.cv_worker as cw
        with pytest.raises(ValueError, match="not found"):
            cw.process_job("nonexistent", "cv_analysis")


# ──────────────────────────────────────────────────────────────────────────────
# handle_message
# ──────────────────────────────────────────────────────────────────────────────

class TestHandleMessage:

    def _make_stream_and_group(self):
        """Create the stream + consumer group so xack works."""
        import worker.cv_worker as cw
        from core.redis_client import STREAM_NAME, GROUP_NAME
        # Add a dummy message so the stream exists, then create the group
        msg_id = _fake.xadd(STREAM_NAME, {"init": "1"})
        try:
            _fake.xgroup_create(STREAM_NAME, GROUP_NAME, id="0", mkstream=True)
        except Exception:
            pass
        return msg_id

    def test_success_flow(self, monkeypatch):
        """status: queued → processing → done, xack called."""
        import worker.cv_worker as cw
        self._make_stream_and_group()
        _seed_job("hm1")

        # Add a real message to the stream
        from core.redis_client import STREAM_NAME
        msg_id = _fake.xadd(STREAM_NAME, {
            "job_id": "hm1", "task_type": "cv_analysis", "retry_count": "0"
        })

        cw.handle_message(msg_id, {
            "job_id": "hm1", "task_type": "cv_analysis", "retry_count": "0"
        })

        job = _fake.hgetall("job:hm1")
        assert job["status"] == "done"
        assert json.loads(job["result"])["career_readiness_score"] == 85.0

    def test_failure_retry(self, monkeypatch):
        """On failure with retry_count < MAX_RETRY → re-queue."""
        import worker.cv_worker as cw
        self._make_stream_and_group()
        _seed_job("hm2")

        from core.redis_client import STREAM_NAME
        msg_id = _fake.xadd(STREAM_NAME, {
            "job_id": "hm2", "task_type": "cv_analysis", "retry_count": "0"
        })

        # Make process_job raise
        monkeypatch.setattr(cw, "process_job", MagicMock(side_effect=Exception("boom")))

        cw.handle_message(msg_id, {
            "job_id": "hm2", "task_type": "cv_analysis", "retry_count": "0"
        })

        job = _fake.hgetall("job:hm2")
        assert job["status"] == "queued"
        assert int(job["retry_count"]) == 1

    def test_failure_dlq(self, monkeypatch):
        """On failure with retry_count >= MAX_RETRY → DLQ + status=failed."""
        import worker.cv_worker as cw
        self._make_stream_and_group()
        _seed_job("hm3", retry_count="2")  # next failure = 3 = MAX_RETRY

        from core.redis_client import STREAM_NAME, DLQ_STREAM_NAME
        msg_id = _fake.xadd(STREAM_NAME, {
            "job_id": "hm3", "task_type": "cv_analysis", "retry_count": "2"
        })

        monkeypatch.setattr(cw, "process_job", MagicMock(side_effect=Exception("fatal")))

        cw.handle_message(msg_id, {
            "job_id": "hm3", "task_type": "cv_analysis", "retry_count": "2"
        })

        job = _fake.hgetall("job:hm3")
        assert job["status"] == "failed"
        assert "超過重試上限" in job["error"]

        # Verify DLQ has the message
        dlq_msgs = _fake.xrange(DLQ_STREAM_NAME)
        assert len(dlq_msgs) >= 1
        dlq_fields = dlq_msgs[-1][1]
        assert dlq_fields["job_id"] == "hm3"
