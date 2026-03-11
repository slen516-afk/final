"""
conftest.py
===========
共用的 pytest fixture 與模組層級 mock。

tasks.py 在 module-level 初始化 QdrantClient 與 ResumeOCRService，
這些依賴在測試環境中不存在。
在任何實際 import 之前先用 sys.modules 把它們全部換成假模組，
確保整個測試套件能在不需要真實服務的情況下運行。

重要：CareerAgentManager.run_task() 必須回傳可 JSON 序列化的字典，
否則 cv_worker.handle_message 在 json.dumps() 時會失敗並觸發 DLQ 邏輯。
"""

import sys
import types
from unittest.mock import MagicMock


def _make_stub(*names):
    """以點分隔路徑建立巢狀假模組，並返回葉模組。"""
    parts = names[0].split(".")
    parent = None
    full = ""
    for part in parts:
        full = f"{full}.{part}" if full else part
        if full not in sys.modules:
            mod = types.ModuleType(full)
            sys.modules[full] = mod
            if parent is not None:
                setattr(parent, part, mod)
        parent = sys.modules[full]
    return parent


# ── 1. qdrant_client ──────────────────────────────────────────────────────────
_qdrant_mod = _make_stub("qdrant_client")
_qdrant_mod.QdrantClient = MagicMock()

# ── 2. crewai ─────────────────────────────────────────────────────────────────
_crewai = _make_stub("crewai")
_crewai.Agent = MagicMock()
_crewai.Task = MagicMock()
_crewai.Crew = MagicMock()
_crewai.Process = MagicMock()
_crewai.LLM = MagicMock()

# ── 3. LLM service 整個 src 樹 ───────────────────────────────────────────────
for _pkg in [
    "src",
    "src.core",
    "src.core.agent_engine",
    "src.core.agent_engine.manager",
    "src.features",
    "src.features.matching",
    "src.features.matching.service",
    "src.features.course",
    "src.features.course.course_matching",
    "src.features.analysis",
    "src.features.cover_letter",
    "src.features.cover_letter.agents",
    "src.features.cover_letter.tasks",
    "src.features.cover_letter.tools",
]:
    _make_stub(_pkg)

# ── CareerAgentManager mock（回傳符合測試期望的字典結構）─────────────────────

_CAREER_REPORT = {
    "report_metadata": {"version": "1.0", "mock": True},
    "radar_chart": {"dimensions": [{} for _ in range(6)]},
    "gap_analysis": {"target_position": {"match_score": 85}},
    "action_plan": {"steps": []},
}

_RESUME_ANALYSIS = {
    "candidate_positioning": "mock",
    "critical_issues": [],
    "ats_risk_level": "low",
}

_RESUME_OPT = {
    "professional_summary": "mock summary",
    "professional_experience": [],
    "core_skills": [],
}


def _make_cam_instance(**kwargs):
    """工廠函式：回傳一個 run_task() 依 task_type_str 給出正確結構的 MagicMock 實例。"""
    inst = MagicMock()

    def _run_task(task_type_str="career_analysis", user_input=None, **kw):
        if task_type_str == "career_analysis":
            return _CAREER_REPORT
        elif task_type_str == "resume_analysis":
            return _RESUME_ANALYSIS
        elif task_type_str == "resume_opt":
            return _RESUME_OPT
        return {"status": "ok"}

    inst.run_task.side_effect = _run_task
    return inst


_MockCareerAgentManager = MagicMock(side_effect=_make_cam_instance)

_manager_mod = sys.modules["src.core.agent_engine.manager"]
_manager_mod.CareerAgentManager = _MockCareerAgentManager

# CareerMatchingService mock
_matching_mod = sys.modules["src.features.matching.service"]
_matching_mod.CareerMatchingService = MagicMock()

# CourseRecommendationService mock
_course_mod = sys.modules["src.features.course.course_matching"]
_course_mod.CourseRecommendationService = MagicMock()

# ── 4. service.llm_service.src.* 別名（tasks.py 使用此路徑）──────────────────
for _pkg in [
    "service",
    "service.llm_service",
    "service.llm_service.src",
    "service.llm_service.src.core",
    "service.llm_service.src.core.agent_engine",
    "service.llm_service.src.core.agent_engine.manager",
    "service.llm_service.src.features",
    "service.llm_service.src.features.matching",
    "service.llm_service.src.features.matching.service",
    "service.llm_service.src.features.course",
    "service.llm_service.src.features.course.course_matching",
    "service.llm_service.src.features.cover_letter",
    "service.llm_service.src.features.cover_letter.agents",
    "service.llm_service.src.features.cover_letter.tasks",
    "service.llm_service.src.features.cover_letter.tools",
]:
    _make_stub(_pkg)

_cam_mod = sys.modules["service.llm_service.src.core.agent_engine.manager"]
_cam_mod.CareerAgentManager = _MockCareerAgentManager

_cms_mod = sys.modules["service.llm_service.src.features.matching.service"]
_cms_mod.CareerMatchingService = MagicMock()

_crs_mod = sys.modules["service.llm_service.src.features.course.course_matching"]
_crs_mod.CourseRecommendationService = MagicMock()

_cl_agents = sys.modules["service.llm_service.src.features.cover_letter.agents"]
_cl_agents.get_cover_letter_strategist_agent = MagicMock()

_cl_tasks = sys.modules["service.llm_service.src.features.cover_letter.tasks"]
_cl_tasks.get_cover_letter_task = MagicMock()

_cl_tools = sys.modules["service.llm_service.src.features.cover_letter.tools"]
_cl_tools.RecommendJobSearchTool = MagicMock()
_cl_tools.FetchOptimizeResumeTool = MagicMock()

# ── 5. OCR service ────────────────────────────────────────────────────────────
for _pkg in [
    "service.ocr_service",
]:
    _make_stub(_pkg)

_ocr_mod = _make_stub("service.ocr_service.ocr_service")
_ocr_mod.ResumeOCRService = MagicMock()

# ── 6. paddleocr / paddlepaddle ───────────────────────────────────────────────
for _pkg in ["paddleocr", "paddle", "paddlepaddle"]:
    _make_stub(_pkg)

# ── 7. langchain 相關 ─────────────────────────────────────────────────────────
for _pkg in [
    "langchain",
    "langchain_community",
    "langchain_openai",
    "langchain.chat_models",
]:
    _make_stub(_pkg)

# ── 8. faiss ──────────────────────────────────────────────────────────────────
_make_stub("faiss")

# ── 9. supabase (REMOVED: let tests use actual DB or local patch) ────
# removed mock

