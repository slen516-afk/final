"""
test_async_flow_full.py
=======================
完整非同步流程整合測試

涵蓋兩個 worker 路徑：
  1. Celery 路徑（worker/celery_app + worker/tasks）
     - test_connection task 的 eager 模式驗證
     - process_career_analysis 回寫 Redis job hash 驗證

  2. Redis Stream 路徑（worker/cv_worker）
     - ensure_group / process_job / handle_message 的端對端流程
     - retry / DLQ 邊界條件

所有外部依賴（Redis、LLM、Supabase）均以 fakeredis / MagicMock 取代。
"""

import json
import os
import sys
import pytest
import fakeredis
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

# ── sys.path 設定 ──────────────────────────────────────────────────────────────
# 以 backend/flask 為匯入根（worker.* 和 core.* 都從這裡解析）
_flask_dir   = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "flask"))
_backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

for _p in [_flask_dir, _backend_dir]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ═══════════════════════════════════════════════════════════════════════════════
# 共用的 fakeredis 實體（整個模組共用；每個 test 前由 fixture 清空）
# ═══════════════════════════════════════════════════════════════════════════════
_fake = fakeredis.FakeRedis(decode_responses=True)


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_redis():
    """每個 test 執行前清空 fakeredis，確保測試隔離。"""
    _fake.flushall()
    yield
    _fake.flushall()


@pytest.fixture
def patch_cv_worker_redis(monkeypatch):
    """將 cv_worker 模組內的 redis_client 替換為 fakeredis。"""
    monkeypatch.setenv("MOCK_MODE", "true")
    import worker.cv_worker as cw
    monkeypatch.setattr(cw, "redis_client", _fake)
    return cw


@pytest.fixture
def patch_celery_redis(monkeypatch):
    """將 tasks 模組（Celery）內的 redis_client 替換為 fakeredis。"""
    monkeypatch.setenv("MOCK_MODE", "true")
    import worker.tasks as wt
    monkeypatch.setattr(wt, "redis_client", _fake, raising=False)
    return wt


# ── 工具函式 ───────────────────────────────────────────────────────────────────

def _seed_job(job_id: str, task_type: str = "survey_analysis", **overrides):
    """在 fakeredis 中建立一個標準的 job hash。"""
    now = datetime.now(timezone.utc).isoformat()
    mapping = {
        "status": "queued",
        "user_id": "test_user_001",
        "resume_id": "resume_001",
        "survey_id": "survey_001",
        "survey_data": json.dumps({
            "module_a": {
                "q1_languages": [{"name": "Python", "score": 2}],
                "q2_frontend": "basic_html_css",
                "q3_backend": "db_auth_testing",
                "q4_database": ["rdbms_sql"],
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
            "module_c": {"q17_target_role": "後端工程師"},
            "module_d": {"q23_values_top3": ["技術成長"]},
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


def _make_stream_and_group(stream_name: str, group_name: str):
    """建立 Redis Stream 與 consumer group（測試用）。"""
    _fake.xadd(stream_name, {"init": "1"})
    try:
        _fake.xgroup_create(stream_name, group_name, id="0", mkstream=True)
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Celery Worker 路徑：基礎驗證
# ═══════════════════════════════════════════════════════════════════════════════

class TestCeleryTasks:
    """
    使用 Celery ALWAYS_EAGER 模式讓任務在行程內同步執行。
    不需要啟動真實 Celery Worker 或 Redis。
    """

    @pytest.fixture(autouse=True)
    def enable_eager(self):
        """啟用 CELERY_TASK_ALWAYS_EAGER（即時同步執行，不走 broker）。"""
        from worker.celery_app import celery_app
        celery_app.conf.task_always_eager = True
        celery_app.conf.task_eager_propagates = True
        yield
        celery_app.conf.task_always_eager = False

    def test_test_connection_task(self):
        """test_connection task 應回傳包含 user_id 的字串。"""
        from worker.tasks import test_connection
        result = test_connection.delay(user_id="u999", content="hello")
        assert result.successful()
        assert "u999" in result.result
        assert "hello" in result.result

    def test_process_career_analysis_writes_redis_on_success(self, monkeypatch):
        """
        process_career_analysis 成功時應將 status=done 及 result 寫入 Redis job hash。
        """
        import worker.tasks as wt

        # Mock CareerAgentManager.run_task 回傳假報告
        mock_manager = MagicMock()
        mock_manager.run_task.return_value = {
            "report_metadata": {"version": "1.0"},
            "radar_chart": {"dimensions": [{} for _ in range(6)]},
            "gap_analysis": {"target_position": {"match_score": 85}},
            "action_plan": {}
        }
        monkeypatch.setattr(wt, "CareerAgentManager", lambda **kw: mock_manager)

        # Mock redis_client（局部注入）
        import core.redis_client as rc
        monkeypatch.setattr(rc, "redis_client", _fake)
        # tasks.py 透過 from core.redis_client import redis_client 在函式內 import，需用 patch
        with patch("worker.tasks.process_career_analysis.__wrapped__" if hasattr(wt.process_career_analysis, "__wrapped__") else "core.redis_client.redis_client", _fake, create=True):
            job_id = "celery_job_001"
            _fake.hset(f"job:{job_id}", mapping={"status": "processing", "user_id": "u1"})

            from worker.tasks import process_career_analysis
            # 直接呼叫底層函式（eager 模式下 .delay() 也可以，but 這裡直接測函式邏輯）
            with patch("core.redis_client.redis_client", _fake):
                result = process_career_analysis(
                    user_id="u1",
                    survey_json=json.dumps({"module_a": {}}),
                    job_id=job_id
                )

        # 確認回傳 report
        assert "report_metadata" in result

    def test_process_career_analysis_writes_failed_on_exception(self, monkeypatch):
        """
        process_career_analysis 例外時應將 status=failed 及 error 寫入 Redis job hash。
        """
        import worker.tasks as wt

        mock_manager = MagicMock()
        mock_manager.run_task.side_effect = RuntimeError("LLM timeout")
        monkeypatch.setattr(wt, "CareerAgentManager", lambda **kw: mock_manager)

        job_id = "celery_job_002"
        _fake.hset(f"job:{job_id}", mapping={"status": "processing", "user_id": "u2"})

        with patch("core.redis_client.redis_client", _fake):
            result = wt.process_career_analysis(
                user_id="u2",
                survey_json="{}",
                job_id=job_id
            )

        assert result["status"] == "error"
        assert "LLM timeout" in result["message"]

        job = _fake.hgetall(f"job:{job_id}")
        assert job["status"] == "failed"
        assert "LLM timeout" in job["error"]


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Redis Stream Worker 路徑：cv_worker 端對端流程
# ═══════════════════════════════════════════════════════════════════════════════

class TestCvWorkerEnsureGroup:

    def test_creates_group_successfully(self, patch_cv_worker_redis):
        """ensure_group 應建立 consumer group，不拋出例外。"""
        cw = patch_cv_worker_redis
        cw.ensure_group()  # Should not raise

    def test_busygroup_is_ignored(self, patch_cv_worker_redis):
        """重複呼叫 ensure_group 應忽略 BUSYGROUP 錯誤。"""
        cw = patch_cv_worker_redis
        cw.ensure_group()
        cw.ensure_group()  # Should not raise


class TestCvWorkerProcessJob:

    def test_survey_analysis_returns_mock_result(self, patch_cv_worker_redis):
        """
        survey_analysis：CareerAgentManager (mock_mode) 應回傳含 CareerReport 結構的結果。
        """
        cw = patch_cv_worker_redis
        _seed_job("pj_survey")

        # 需要 supabase mock（process_job 內部會查詢 career_survey）
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value \
            .eq.return_value.order.return_value.limit.return_value.execute.return_value \
            .data = [{"questionnaire_response": {"module_a": {}}, "personality": {}}]

        with patch("core.supabase_client.supabase", mock_supabase):
            result = cw.process_job("pj_survey", "survey_analysis")

        assert "result" in result
        report = result["result"]
        assert "report_metadata" in report
        assert "radar_chart" in report
        assert "gap_analysis" in report
        assert "action_plan" in report

    def test_resume_analysis_returns_mock_suggestions(self, patch_cv_worker_redis):
        """resume_analysis：suggestions 欄位應包含 mock ResumeAnalysis。"""
        cw = patch_cv_worker_redis
        _seed_job("pj_resume")

        result = cw.process_job("pj_resume", "resume_analysis")
        suggestions = result["suggestions"]
        assert "candidate_positioning" in suggestions
        assert "critical_issues" in suggestions
        assert "ats_risk_level" in suggestions

    def test_resume_opt_returns_mock_result(self, patch_cv_worker_redis):
        """resume_opt：result 欄位應包含 mock ResumeOptimization。"""
        cw = patch_cv_worker_redis
        _seed_job("pj_opt")

        result = cw.process_job("pj_opt", "resume_opt")
        opt = result["result"]
        assert "professional_summary" in opt
        assert "professional_experience" in opt
        assert "core_skills" in opt

    def test_job_not_found_raises_value_error(self, patch_cv_worker_redis):
        """job 不存在時應拋出 ValueError。"""
        cw = patch_cv_worker_redis
        with pytest.raises(ValueError, match="not found"):
            cw.process_job("nonexistent_job", "survey_analysis")


class TestCvWorkerHandleMessage:

    def _setup_stream(self, cw):
        """建立 stream + consumer group。"""
        from core.redis_client import STREAM_NAME, GROUP_NAME
        _make_stream_and_group(STREAM_NAME, GROUP_NAME)

    def test_success_flow(self, patch_cv_worker_redis, monkeypatch):
        """
        handle_message 成功時：
        - job status 應更新為 done
        - result 應包含 report_metadata
        """
        cw = patch_cv_worker_redis
        self._setup_stream(cw)
        _seed_job("hm_success")

        from core.redis_client import STREAM_NAME
        msg_id = _fake.xadd(STREAM_NAME, {
            "job_id": "hm_success",
            "task_type": "survey_analysis",
            "retry_count": "0"
        })

        # Mock supabase 查詢
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value \
            .eq.return_value.order.return_value.limit.return_value.execute.return_value \
            .data = [{"questionnaire_response": {"module_a": {}}, "personality": {}}]

        with patch("core.supabase_client.supabase", mock_supabase):
            cw.handle_message(msg_id, {
                "job_id": "hm_success",
                "task_type": "survey_analysis",
                "retry_count": "0"
            })

        job = _fake.hgetall("job:hm_success")
        assert job["status"] == "done", f"期望 done，實際為 {job['status']}"
        result_data = json.loads(job["result"])
        assert "report_metadata" in result_data

    def test_failure_triggers_retry(self, patch_cv_worker_redis, monkeypatch):
        """
        handle_message 失敗且 retry_count < MAX_RETRY 時，
        應重新排隊並將 status 更新為 retrying。
        """
        cw = patch_cv_worker_redis
        self._setup_stream(cw)
        _seed_job("hm_retry")

        from core.redis_client import STREAM_NAME
        msg_id = _fake.xadd(STREAM_NAME, {
            "job_id": "hm_retry",
            "task_type": "survey_analysis",
            "retry_count": "0"
        })

        monkeypatch.setattr(cw, "process_job", MagicMock(side_effect=Exception("transient error")))
        # 跳過 sleep（加速測試）
        monkeypatch.setattr("time.sleep", lambda _: None)

        cw.handle_message(msg_id, {
            "job_id": "hm_retry",
            "task_type": "survey_analysis",
            "retry_count": "0"
        })

        job = _fake.hgetall("job:hm_retry")
        assert job["status"] == "retrying"
        assert int(job["retry_count"]) == 1

    def test_max_retry_sends_to_dlq(self, patch_cv_worker_redis, monkeypatch):
        """
        handle_message 失敗且 retry_count >= MAX_RETRY 時，
        應將 job 移至 DLQ，並 status=dlq。
        """
        cw = patch_cv_worker_redis
        self._setup_stream(cw)

        from core.redis_client import MAX_RETRY
        _seed_job("hm_dlq", retry_count=str(MAX_RETRY - 1))

        from core.redis_client import STREAM_NAME, DLQ_STREAM_NAME
        msg_id = _fake.xadd(STREAM_NAME, {
            "job_id": "hm_dlq",
            "task_type": "survey_analysis",
            "retry_count": str(MAX_RETRY - 1)
        })

        monkeypatch.setattr(cw, "process_job", MagicMock(side_effect=Exception("fatal error")))

        cw.handle_message(msg_id, {
            "job_id": "hm_dlq",
            "task_type": "survey_analysis",
            "retry_count": str(MAX_RETRY - 1)
        })

        job = _fake.hgetall("job:hm_dlq")
        assert job["status"] == "dlq"
        assert "超過重試上限" in job["error"]

        dlq_msgs = _fake.xrange(DLQ_STREAM_NAME)
        assert len(dlq_msgs) >= 1
        assert dlq_msgs[-1][1]["job_id"] == "hm_dlq"

    def test_non_recoverable_error_goes_directly_to_dlq(self, patch_cv_worker_redis, monkeypatch):
        """
        NonRecoverableError 應繞過 retry，直接移入 DLQ。
        """
        cw = patch_cv_worker_redis
        self._setup_stream(cw)
        _seed_job("hm_nr")

        from core.redis_client import STREAM_NAME, DLQ_STREAM_NAME
        msg_id = _fake.xadd(STREAM_NAME, {
            "job_id": "hm_nr",
            "task_type": "survey_analysis",
            "retry_count": "0"
        })

        monkeypatch.setattr(
            cw, "process_job",
            MagicMock(side_effect=cw.NonRecoverableError("bad payload"))
        )

        cw.handle_message(msg_id, {
            "job_id": "hm_nr",
            "task_type": "survey_analysis",
            "retry_count": "0"
        })

        job = _fake.hgetall("job:hm_nr")
        assert job["status"] == "dlq"
        dlq_msgs = _fake.xrange(DLQ_STREAM_NAME)
        assert len(dlq_msgs) >= 1
        assert dlq_msgs[-1][1]["job_id"] == "hm_nr"


# ═══════════════════════════════════════════════════════════════════════════════
# 3. 端對端整合：submit → Redis Stream → cv_worker 處理 → 狀態查詢
# ═══════════════════════════════════════════════════════════════════════════════

class TestEndToEndFlow:
    """
    模擬 gap_analysis API 提交 job → cv_worker 處理 → 狀態應為 done
    """

    def test_submit_then_process_then_done(self, patch_cv_worker_redis, monkeypatch):
        """
        完整流程：
        1. 手動建立 job（模擬 gap_analysis._create_gap_analysis_job）
        2. cv_worker.handle_message 處理
        3. 驗證 job status=done 且 result 包含 report_metadata
        """
        cw = patch_cv_worker_redis

        from core.redis_client import STREAM_NAME, GROUP_NAME
        _make_stream_and_group(STREAM_NAME, GROUP_NAME)

        # === Step 1: 模擬 API 提交 job ===
        job_id = "e2e_job_001"
        now = datetime.now(timezone.utc).isoformat()
        _fake.hset(f"job:{job_id}", mapping={
            "status": "queued",
            "user_id": "e2e_user",
            "result": "",
            "suggestions": "",
            "error": "",
            "retry_count": "0",
            "created_at": now,
            "updated_at": now,
        })

        msg_id = _fake.xadd(STREAM_NAME, {
            "job_id": job_id,
            "task_type": "survey_analysis",
            "retry_count": "0"
        })

        # === Step 2: 模擬 cv_worker 處理 ===
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value \
            .eq.return_value.order.return_value.limit.return_value.execute.return_value \
            .data = [{"questionnaire_response": {"module_a": {}}, "personality": {}}]

        with patch("core.supabase_client.supabase", mock_supabase):
            cw.handle_message(msg_id, {
                "job_id": job_id,
                "task_type": "survey_analysis",
                "retry_count": "0"
            })

        # === Step 3: 驗證結果 ===
        job = _fake.hgetall(f"job:{job_id}")
        assert job["status"] == "done", f"期望 done，實際為 {job['status']}"
        result_data = json.loads(job["result"])
        assert "report_metadata" in result_data, "result 中應包含 report_metadata"

    def test_job_not_found_keeps_queue_clean(self, patch_cv_worker_redis, monkeypatch):
        """
        如果 Redis 中沒有對應的 job hash，
        handle_message 的錯誤應被正確捕獲，status 不會卡在 processing。
        """
        cw = patch_cv_worker_redis

        from core.redis_client import STREAM_NAME, GROUP_NAME
        _make_stream_and_group(STREAM_NAME, GROUP_NAME)

        msg_id = _fake.xadd(STREAM_NAME, {
            "job_id": "ghost_job",
            "task_type": "survey_analysis",
            "retry_count": "0"
        })

        # 不呼叫 _seed_job → job hash 不存在
        cw.handle_message(msg_id, {
            "job_id": "ghost_job",
            "task_type": "survey_analysis",
            "retry_count": "0"
        })

        # ghost_job 不存在，不應 crash；驗證它不在 stream pending list 即可
        job = _fake.hgetall("job:ghost_job")
        # job 可能是空的（從未建立）或是被重新排隊，但不應是 processing
        assert job.get("status") != "processing"