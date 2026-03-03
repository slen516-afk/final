"""
Tests for worker.cv_worker — all LLM calls are mocked.
"""
import json
import os
import sys
import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

# Add backend/flask to sys.path so it can find worker and core modules
backend_flask_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "flask"))
if backend_flask_dir not in sys.path:
    sys.path.insert(0, backend_flask_dir)

import fakeredis

# We need a fresh fake redis that we control in each test
_fake = fakeredis.FakeRedis(decode_responses=True)


@pytest.fixture(autouse=True)
def patch_worker_redis(monkeypatch):
    """Patch redis_client inside cv_worker to use our fakeredis instance."""
    # 啟用 mock 模式讓 CareerAgentManager 不初始化外部依賴
    monkeypatch.setenv("MOCK_MODE", "true")
    import worker.cv_worker as cw
    monkeypatch.setattr(cw, "redis_client", _fake)
    yield
    _fake.flushall()


def _seed_job(job_id, **overrides):
    now = datetime.now(timezone.utc).isoformat()
    # 使用與 calculator.py 一致的真實 enum key
    survey_data = {
        "module_a": {
            "q1_languages": [{"name": "Python", "score": 2}, {"name": "JavaScript", "score": 1}],
            "q2_frontend": "basic_html_css",
            "q3_backend": "db_auth_testing",
            "q4_database": ["rdbms_sql", "nosql_document", "key_value_cache"],
            "q5_devops": "docker_basic",
            "q6_ai_data": "pandas_numpy",
            "q7_security": "owasp_basic",
        },
        "module_b": {
            "q9_troubleshoot": "log_search",
            "q10_tech_choice": "tradeoff_analysis",
            "q11_communication": "alternative_solution",
            "q12_code_review": "logic_safety",
            "q13_learning": "consistent_input",
            "q14_process": "kanban",
            "q15_english": "fluent_reading",
        },
        "module_c": {
            "q17_target_role": "後端工程師 / 全端工程師",
        },
        "module_d": {
            "q23_values_top3": ["技術成長", "薪資報酬"],
        },
    }
    mapping = {
        "status": "queued",
        "user_id": "u1",
        "resume_id": "r1",
        "survey_id": "s1",
        "survey_data": json.dumps({
            "module_a": survey_data["module_a"],
            "module_b": survey_data["module_b"],
            "module_c": survey_data["module_c"],
            "module_d": survey_data["module_d"],
            "trait_data": {},
        }, ensure_ascii=False),
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

    def test_survey_analysis_returns_mock_result(self):
        """survey_analysis 走 CareerAgentManager(mock_mode) → 回傳 CareerReport mock。"""
        import worker.cv_worker as cw
        _seed_job("pj1")
        result = cw.process_job("pj1", "survey_analysis")
        assert "result" in result
        # 驗證 CareerReport 真實結構的頂層 key
        report = result["result"]
        assert "report_metadata" in report
        assert "radar_chart" in report
        assert "gap_analysis" in report
        assert "action_plan" in report
        # radar_chart 有 6 個維度
        assert len(report["radar_chart"]["dimensions"]) == 6
        # gap_analysis 有 target_position 包含 match_score
        assert "match_score" in report["gap_analysis"]["target_position"]

    def test_resume_analysis_returns_mock_suggestions(self):
        """resume_analysis → suggestions 欄位應包含 mock ResumeAnalysis。"""
        import worker.cv_worker as cw
        _seed_job("pj2")
        result = cw.process_job("pj2", "resume_analysis")
        suggestions = result["suggestions"]
        assert "candidate_positioning" in suggestions
        assert "critical_issues" in suggestions
        assert "ats_risk_level" in suggestions

    def test_resume_opt_returns_mock_result(self):
        """resume_opt → result 欄位應包含 mock ResumeOptimization。"""
        import worker.cv_worker as cw
        _seed_job("pj3")
        result = cw.process_job("pj3", "resume_opt")
        opt = result["result"]
        assert "professional_summary" in opt
        assert "professional_experience" in opt
        assert "core_skills" in opt

    def test_job_not_found(self):
        import worker.cv_worker as cw
        with pytest.raises(ValueError, match="not found"):
            cw.process_job("nonexistent", "survey_analysis")


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
            "job_id": "hm1", "task_type": "survey_analysis", "retry_count": "0"
        })

        cw.handle_message(msg_id, {
            "job_id": "hm1", "task_type": "survey_analysis", "retry_count": "0"
        })

        job = _fake.hgetall("job:hm1")
        assert job["status"] == "done"
        assert "report_metadata" in json.loads(job["result"])

    def test_failure_retry(self, monkeypatch):
        """On failure with retry_count < MAX_RETRY → re-queue."""
        import worker.cv_worker as cw
        self._make_stream_and_group()
        _seed_job("hm2")

        from core.redis_client import STREAM_NAME
        msg_id = _fake.xadd(STREAM_NAME, {
            "job_id": "hm2", "task_type": "survey_analysis", "retry_count": "0"
        })

        # Make process_job raise
        monkeypatch.setattr(cw, "process_job", MagicMock(side_effect=Exception("boom")))

        cw.handle_message(msg_id, {
            "job_id": "hm2", "task_type": "survey_analysis", "retry_count": "0"
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
            "job_id": "hm3", "task_type": "survey_analysis", "retry_count": "2"
        })

        monkeypatch.setattr(cw, "process_job", MagicMock(side_effect=Exception("fatal")))

        cw.handle_message(msg_id, {
            "job_id": "hm3", "task_type": "survey_analysis", "retry_count": "2"
        })

        job = _fake.hgetall("job:hm3")
        assert job["status"] == "failed"
        assert "超過重試上限" in job["error"]

        # Verify DLQ has the message
        dlq_msgs = _fake.xrange(DLQ_STREAM_NAME)
        assert len(dlq_msgs) >= 1
        dlq_fields = dlq_msgs[-1][1]
        assert dlq_fields["job_id"] == "hm3"
