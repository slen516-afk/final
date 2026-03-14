# test/matching/test_rag_fix_verification.py
"""
RAG 修復驗證測試（v2）
======================
核心原則：全程呼叫真實模組程式碼，不重複實作邏輯。

測試分三個層次：

  Layer 1 — 資料庫查詢驗證（純 DB，無費用）
    ‣ 直接呼叫 service.py 內部使用的 Supabase 查詢，
      確認 Phase 0.5 能從正確的資料表撈到非空的履歷文字。

  Layer 2 — Prompt 注入驗證（用 mock 攔截 OpenAI，無費用）
    ‣ 呼叫真實的 `advisor.generate_job_insights()`，
      用 unittest.mock 攔截 OpenAI API call，
      檢查「實際送出的 messages」是否包含履歷摘要與職缺描述。
    ‣ 這樣才能真正驗證 advisor.py 的程式碼是否正確組裝 Prompt。

  Layer 3 — 完整整合驗證（End-to-End，會呼叫 OpenAI，有費用）
    ‣ 呼叫真實的 `service.find_best_jobs()`，
      人工審查 AI 建議是否具體引用了技術詞彙或履歷內容。

執行方式（在專案根目錄）：
  python -m test.matching.test_rag_fix_verification
"""

import os
import sys
import json
from unittest.mock import patch, MagicMock

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT_DIR)

from dotenv import load_dotenv
load_dotenv()

from src.common.logger import setup_logger
logger = setup_logger()

# ========================================================
# ✏️  測試參數（請依你的資料庫實際狀況修改）
# ========================================================
TEST_USER_ID     = 2      # 要測試的使用者 ID
TEST_RESUME_ID   = 2      # resume 表中的 resume_id（source_type=RESUME）
TEST_OPT_ID      = 7      # resume_optimization 表中的 optimization_id（source_type=OPTIMIZATION）
TEST_CITY        = ["台北市", "新北市"]
TEST_SALARY_MIN  = 40000
# ========================================================


def _separator(title=""):
    print("\n" + "="*60)
    if title:
        print(f"🔬 {title}")
        print("="*60)


# ──────────────────────────────────────────────────────────────
# Layer 1：確認 Phase 0.5 能撈到非空履歷文字
# ──────────────────────────────────────────────────────────────
def test_layer1_resume_text_retrieval():
    """
    使用「與 service.py Phase 0.5 完全相同的查詢邏輯」
    直接對 Supabase 發起請求，確認可取得非空的履歷文字。
    """
    _separator("Layer 1：Phase 0.5 履歷文字查詢驗證（Supabase 直連）")

    from src.core.database.supabase_client import get_supabase_client
    supabase = get_supabase_client()

    # ── 1a. RESUME 路徑 ──
    print(f"\n[1a] source_type=RESUME → resume 表 (resume_id={TEST_RESUME_ID}, user_id={TEST_USER_ID})")
    try:
        # 先印出實際存在的 ID，幫助確認參數是否正確
        all_rows = (
            supabase.table('resume')
            .select('resume_id')
            .eq('resume_id',TEST_RESUME_ID)
            .execute()
        )
        if all_rows.data:
            existing_ids = [r.get('resume_id') for r in all_rows.data]
            print(f"  📋 resume 表中 user_id={TEST_USER_ID} 的 resume_id 列表：{existing_ids}")
        else:
            print(f"  ⚠️ resume 表中找不到 user_id={TEST_USER_ID} 的任何記錄！")

        # 使用 maybe_single()：0 筆時回傳 data=None 而非拋出 PGRST116
        resume_text_response = (
            supabase.table('resume')
            .select('structured_data')
            .eq('resume_id', TEST_RESUME_ID)
            .maybe_single()
            .execute()
        )

        if resume_text_response.data is None:
            print(f"  ❌ 查無資料！resume_id={TEST_RESUME_ID} / user_id={TEST_USER_ID} 組合不存在。")
            print(f"     → 請依上方 ID 列表修改 TEST_RESUME_ID")
        else:
            structured_data = resume_text_response.data.get('structured_data') or {}
            parts = []
            if isinstance(structured_data, dict):
                for section_key, section_val in structured_data.items():
                    if section_val:
                        parts.append(f"[{section_key}] {str(section_val)[:300]}")
                resume_summary = "\n".join(parts)[:1200]
            elif isinstance(structured_data, str):
                resume_summary = structured_data[:1200]
            else:
                resume_summary = ""

            if resume_summary:
                print(f"  ✅ 成功取得履歷文字（字元數：{len(resume_summary)}）")
                print(f"\n  ── 文字預覽（前 500 字）──")
                print(resume_summary[:500])
                if isinstance(structured_data, dict):
                    print(f"\n  ── structured_data 包含的節：{list(structured_data.keys())}")
            else:
                print("  ❌ resume_summary 為空！structured_data 欄位已找到但內容為空。")
    except Exception as e:
        print(f"  ❌ 查詢失敗：{e}")

    # ── 1b. OPTIMIZATION 路徑 ──
    print(f"\n[1b] source_type=OPTIMIZATION → resume_optimization 表 (optimization_id={TEST_OPT_ID}, user_id={TEST_USER_ID})")
    try:
        # 先印出實際存在的 ID
        all_opt_rows = (
            supabase.table('resume_optimization')
            .select('optimization_id')
            .eq('optimization_id', TEST_OPT_ID)
            .execute()
        )
        if all_opt_rows.data:
            existing_opt_ids = [r.get('optimization_id') for r in all_opt_rows.data]
            print(f"  📋 resume_optimization 表中 user_id={TEST_USER_ID} 的 optimization_id 列表：{existing_opt_ids}")
        else:
            print(f"  ⚠️ resume_optimization 表中找不到 user_id={TEST_USER_ID} 的任何記錄！")

        opt_text_response = (
            supabase.table('resume_optimization')
            .select('professional_summary, professional_experience, core_skills, projects, education, autobiography')
            .eq('optimization_id', TEST_OPT_ID)
            .maybe_single()
            .execute()
        )

        if opt_text_response.data is None:
            print(f"  ❌ 查無資料！optimization_id={TEST_OPT_ID} / user_id={TEST_USER_ID} 組合不存在。")
            print(f"     → 請依上方 ID 列表修改 TEST_OPT_ID")
        else:
            opt_data = opt_text_response.data or {}
            field_labels = {
                'professional_summary':    '個人摘要',
                'core_skills':             '核心技能',
                'professional_experience': '工作經歷',
                'projects':                '專案經歷',
                'education':               '學歷',
                'autobiography':           '自傳',
            }
            opt_parts = []
            for field, label in field_labels.items():
                val = opt_data.get(field)
                icon = "✅" if val else "⚪ (空)"
                print(f"  [{icon}] {label} ({field})")
                if val:
                    opt_parts.append(f"[{label}] {str(val)[:250]}")

            resume_summary_opt = "\n".join(opt_parts)[:1200]
            if resume_summary_opt:
                print(f"\n  ✅ OPTIMIZATION 摘要組裝成功（字元數：{len(resume_summary_opt)}）")
                print(f"\n  ── 文字預覽（前 500 字）──")
                print(resume_summary_opt[:500])
            else:
                print(f"\n  ❌ 所有欄位皆為空。")
    except Exception as e:
        print(f"  ❌ 查詢失敗：{e}")


# ──────────────────────────────────────────────────────────────
# Layer 2：用 mock 攔截真實 advisor.py 的 OpenAI 呼叫
# ──────────────────────────────────────────────────────────────
def test_layer2_advisor_prompt_via_mock():
    """
    呼叫真實的 `CareerLLMAdvisor.generate_job_insights()`，
    用 unittest.mock.patch 替換 openai.OpenAI 的 API 呼叫，
    攔截實際送出的 messages，驗證 Prompt 中是否真的包含
    履歷摘要、職缺描述、職缺要求三個 RAG 區塊。
    """
    _separator("Layer 2：Prompt 注入驗證（攔截真實 advisor.py 的 OpenAI 呼叫）")

    from src.features.matching.advisor import CareerLLMAdvisor

    # ── 準備測試輸入（模擬 service.py 傳入的資料）──
    fake_resume_summary = (
        "[工作經歷] 在 ABC 公司擔任後端工程師，使用 FastAPI + PostgreSQL 開發 RESTful API，"
        "並導入 Docker 容器化部署，負責微服務架構設計。\n"
        "[核心技能] Python, FastAPI, Docker, PostgreSQL, Redis, Git"
    )
    fake_job_description = (
        "尋找熟悉 Kubernetes 與 Google Cloud Platform 的後端工程師，"
        "需有微服務架構設計經驗，熟悉 gRPC 通訊協定。"
    )
    fake_job_requirements = "3年以上後端開發 | 熟悉 Kubernetes | GCP 或 AWS 雲端部署"
    fake_user_6d = {"D1": 1.5, "D2": 4.2, "D3": 2.8, "D4": 2.0, "D5": 3.5, "D6": 3.8}
    fake_job_6d  = {
        "d1_frontend": 1, "d2_backend": 5, "d3_devops": 4,
        "d4_ai_data": 2, "d5_quality": 3, "d6_soft_skills": 3
    }

    # ── 建立 mock：讓 OpenAI client 回傳假的 JSON 結果 ──
    mock_response = MagicMock()
    mock_response.choices[0].message.content = json.dumps({
        "recommendation_reason": "mock reason",
        "strengths":             "mock strengths",
        "weaknesses":            "mock weaknesses",
        "interview_tips":        "mock tips",
    }, ensure_ascii=False)

    # ── 用 patch 替換 openai.OpenAI，攔截實際的 messages 參數 ──
    captured_messages = []

    def fake_create(**kwargs):
        captured_messages.extend(kwargs.get("messages", []))
        return mock_response

    with patch("src.features.matching.advisor.OpenAI") as MockOpenAI:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = fake_create
        MockOpenAI.return_value = mock_client

        advisor = CareerLLMAdvisor(api_key="test-key")

        # ▶ 呼叫真實的 advisor.py 程式碼
        result = advisor.generate_job_insights(
            job_title="後端工程師 (Python/GCP)",
            user_6d=fake_user_6d,
            job_6d=fake_job_6d,
            match_score="78.5%",
            job_description=fake_job_description,
            job_requirements=fake_job_requirements,
            resume_summary=fake_resume_summary,
        )

    # ── 驗證結果 ──
    if not captured_messages:
        print("  ❌ 未攔截到任何 messages！advisor.py 可能未呼叫 OpenAI API。")
        return

    # 取出 user_prompt（第二條 message）
    user_msg  = next((m["content"] for m in captured_messages if m["role"] == "user"), "")
    sys_msg   = next((m["content"] for m in captured_messages if m["role"] == "system"), "")

    print("\n[實際送出的 system_prompt]")
    print("-" * 60)
    print(sys_msg)

    print("\n[實際送出的 user_prompt]")
    print("-" * 60)
    print(user_msg)
    print("-" * 60)

    # ── 自動驗證各 RAG 區塊是否存在於真實 Prompt 中 ──
    checks = {
        "【候選人履歷摘要】區塊已注入 user_prompt":   "候選人履歷摘要"   in user_msg,
        "【職缺描述摘要】區塊已注入 user_prompt":     "職缺描述摘要"     in user_msg,
        "【職缺要求條件】區塊已注入 user_prompt":     "職缺要求條件"     in user_msg,
        "履歷內容文字 (FastAPI) 出現在 Prompt 中":    "FastAPI"           in user_msg,
        "職缺內容文字 (Kubernetes) 出現在 Prompt 中": "Kubernetes"        in user_msg,
        "system_prompt 要求具體個人化語言":           "具體" in sys_msg or "個人化" in sys_msg,
    }

    print("\n[自動驗證結果]")
    all_pass = True
    for desc, passed in checks.items():
        icon = "✅" if passed else "❌"
        print(f"  {icon} {desc}")
        if not passed:
            all_pass = False

    if all_pass:
        print("\n✅ Layer 2 通過：advisor.py 確實將三個 RAG 區塊注入到真實 Prompt 中！")
    else:
        print("\n❌ Layer 2 失敗：部分區塊未注入，請檢查 advisor.py 第 48~67 行的 Prompt 組裝邏輯。")


# ──────────────────────────────────────────────────────────────
# Layer 3：完整整合測試（End-to-End，會呼叫 OpenAI）
# ──────────────────────────────────────────────────────────────
def test_layer3_end_to_end():
    """
    呼叫真實的 `service.find_best_jobs()`，
    確認：
    1. service.py 確實在 Phase 0.5 成功撈取到履歷文字（看 log）
    2. 每一筆職缺的 AI 建議欄位非空且非預設錯誤值
    3. 人工判斷 AI 建議是否引用了具體技術詞彙
    """
    _separator("Layer 3：完整整合驗證（End-to-End，會消耗 OpenAI 費用）")

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ 找不到 OPENAI_API_KEY，跳過 Layer 3。")
        return

    from src.core.database.supabase_client import get_supabase_client
    from src.core.database.qdrant_client import get_qdrant_client
    from src.features.matching.service import CareerMatchingService

    try:
        qdrant_client   = get_qdrant_client()
        supabase_client = get_supabase_client()

        service = CareerMatchingService(
            qdrant_client=qdrant_client,
            supabase_client=supabase_client,
            openai_api_key=openai_api_key,
        )

        filters = {"city": TEST_CITY, "salary_min": TEST_SALARY_MIN}

        print(f"\n[執行] source_type=RESUME (user_id={TEST_USER_ID}, resume_id={TEST_RESUME_ID})")
        print("⏳ 執行中（Qdrant + Supabase + OpenAI）...")
        print("📌 請同時觀察上方 log 輸出，確認以下兩行有出現：")
        print('   ✅ 成功取得履歷文字摘要 (字元數: XXX)')
        print('   ── 若看到 ⚠️ 查無履歷文字 → Phase 0.5 查詢仍有問題')

        results = service.find_best_jobs(
            user_id=TEST_USER_ID,
            document_id=TEST_OPT_ID,
            source_type="OPTIMIZATION",
            filters=filters,
        )

        if not results:
            print("\n⚠️ 未找到任何職缺，請確認篩選條件與資料庫內容。")
            return

        print(f"\n✅ 取得 {len(results)} 筆推薦職缺")

        # ── 人工審查輸出 ──
        print("\n" + "="*60)
        print("📋 人工審查區（每筆職缺的 AI 建議）")
        print("   判斷標準：建議中應有具體技術詞彙，而非「加強 D2 能力」等泛化語句")
        print("="*60)

        for i, job in enumerate(results, 1):
            print(f"\n【第 {i} 名】{job.get('id')} @ {job.get('title')} @ {job.get('company')}")
            print(f"  匹配度  ：{job.get('match_score')}")
            print(f"  推薦理由：{job.get('recommendation_reason')}")
            print(f"  優勢    ：{job.get('strengths')}")
            print(f"  劣勢    ：{job.get('weaknesses')}")
            print(f"  面試建議：{job.get('interview_tips')}")

        # ── 自動化基礎驗證（欄位完整性）──
        print("\n" + "-"*60)
        print("🤖 自動驗證：欄位完整性")
        print("-"*60)
        DEFAULT_ERROR = {"系統分析中...", "無", ""}
        fail_count = 0
        for i, job in enumerate(results, 1):
            title = job.get('job_title', f'Job #{i}')
            for field in ["recommendation_reason", "strengths", "weaknesses", "interview_tips"]:
                val = (job.get(field) or "").strip()
                if val in DEFAULT_ERROR:
                    print(f"  ❌ [{title}] {field} 為空或預設錯誤值！")
                    fail_count += 1

        if fail_count == 0:
            print(f"  ✅ 所有 {len(results)} 筆職缺的 AI 欄位皆有實質內容。")
        else:
            print(f"  ⚠️ 共 {fail_count} 個欄位異常，請捲動查看人工審查區的詳情。")

        print("\n💡 同步確認 logs/crewai_outputs/task_audit_trail.log 可查看 LLM 原始輸出。")

    except Exception as e:
        logger.error(f"Layer 3 測試失敗：{e}", exc_info=True)


# ──────────────────────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════╗")
    print("║     RAG 修復驗證測試 v2（呼叫真實模組，非重複實作）      ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"\n測試參數：")
    print(f"  USER_ID          = {TEST_USER_ID}")
    print(f"  RESUME_ID        = {TEST_RESUME_ID}  (source_type=RESUME)")
    print(f"  OPTIMIZATION_ID  = {TEST_OPT_ID}  (source_type=OPTIMIZATION)")

    # Layer 1：純資料庫查詢，無費用
    # test_layer1_resume_text_retrieval()

    # Layer 2：mock OpenAI，呼叫真實 advisor.py，無費用
    # test_layer2_advisor_prompt_via_mock()

    # Layer 3：完整端對端，會消耗 OpenAI 費用
    # 若只想測試 Layer 1+2，可將下一行注解掉：
    test_layer3_end_to_end()

    print("\n\n✅ 所有測試層次執行完畢。")
