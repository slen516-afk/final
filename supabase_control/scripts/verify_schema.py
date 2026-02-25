"""
驗證 Supabase 資料表與說明文件對齊

比對項目：
1. 欄位對齊：各表是否具備說明文件（career_pilot說明文件v4_with_chinese.md）中定義的欄位
2. 關聯關係（可選）：若有 DATABASE_URL，會檢查 FK 是否與說明文件一致

使用方式：
  # 僅用 Supabase API 檢查欄位（不需直接連 DB）
  python scripts/verify_schema.py

  # 含 FK 檢查（需在 .env 設定 DATABASE_URL）
  python scripts/verify_schema.py --fk

  # 強制只用 API 檢查欄位（不連 DB）
  python scripts/verify_schema.py --api-only

說明：
- 表名以「說明文件英文表名」轉成小寫、底線對應（如 USER_PROFILE → user_profile）
- 若實際表名不同（例如 DB 用 users 而文件用 user），可在 .env 同目錄下改腳本內 TABLE_ALIAS
- DATABASE_URL：Supabase 專案 → Settings → Database → Connection string（Session mode 即可）
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# 專案根目錄 = supabase_control
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 依說明文件 v4 定義：表名(小寫) -> 欄位列表
# 若 DB 表名與說明文件不同，可設對照：{ "文件表名": "實際表名" }
TABLE_ALIAS = {}  # 例: {"user": "users"}

EXPECTED_SCHEMA = {
    "user": [
        "user_id", "email", "password_hash", "auth_provider",
        "created_at", "last_login", "is_active",
    ],
    "user_profile": [
        "profile_id", "user_id", "github_repo", "full_name", "location",
        "years_of_experience", "current_position", "education_background",
        "privacy_settings", "updated_at",
    ],
    "career_survey": [
        "survey_id", "user_id", "career_preference", "skill_self_assessment",
        "salary_min", "salary_max", "location_preference", "remote_preference",
        "career_motivation", "questionnaire_response", "completed_at", "updated_at",
    ],
    "resume": [
        "resume_id", "user_id", "template_id", "resume_type", "structured_data",
        "normalized_data", "vector_id", "is_embedded", "is_primary",
        "created_at", "updated_at",
    ],
    "resume_version": [
        "version_id", "resume_id", "version_number", "file_path", "content",
        "optimization_target", "created_at",
    ],
    "resume_template": [
        "template_id", "template_name", "template_type", "template_structure", "created_at",
    ],
    "resume_analysis": [
        "analysis_id", "resume_id", "user_id", "candidate_positioning",
        "target_role_gap_summary", "overall_strengths", "overall_weaknesses",
        "ats_risk_level", "screening_outcome_prediction", "recommended_next_actions",
        "target_job_id", "llm_model_used", "analysis_version", "generated_at", "critical_issues",
    ],
    "resume_optimization": [
        "optimization_id", "resume_id", "version_id", "user_id", "target_job_id",
        "professional_summary", "professional_experience", "core_skills", "projects",
        "education", "autobiography", "llm_model_used", "optimization_version", "created_at",
    ],
    "upload_event": [
        "event_id", "user_id", "file_name", "file_path", "upload_type",
        "status", "uploaded_at", "metadata",
    ],
    "ocr_result": [
        "ocr_id", "event_id", "resume_id", "raw_text", "extracted_data",
        "confidence_score", "is_manual_review_needed", "ocr_status", "processed_at",
    ],
    "company_info": [
        "company_id", "company_name", "industry", "company_size", "location",
        "website", "description", "created_at",
    ],
    "job_posting": [
        "job_id", "company_id", "job_category", "role_type", "role_name",
        "d1_frontend", "d2_backend", "d3_devops", "d4_ai_data", "d5_quality", "d6_soft_skills",
        "job_title", "job_description", "requirements", "vector_id", "is_embedded",
        "salary_min", "salary_max", "full_address", "city", "district", "remote_option",
        "job_details", "source_platform", "source_url", "posted_date", "scraped_at", "is_active",
    ],
    "skill_master": [
        "skill_id", "skill_name", "skill_category", "synonyms", "created_at",
    ],
    "job_skill_requirement": [
        "requirement_id", "job_id", "skill_id", "importance", "proficiency_level",
    ],
    "user_skill": [
        "user_skill_id", "user_id", "skill_id", "proficiency_level",
        "years_of_experience", "verified", "created_at",
    ],
    "course": [
        "course_id", "course_name", "url", "primary_skill_name", "primary_skill_id",
        "rating", "review_count", "level", "course_type", "course_information",
        "duration_suggested", "skills", "source_platform", "created_at",
    ],
    "job_matching": [
        "matching_id", "resume_id", "job_id", "overall_match_score", "matching_algorithm",
        "matched_at", "user_viewed", "matching_status",
    ],
    "match_score": [
        "score_id", "matching_id", "skill_match_score", "experience_match_score",
        "salary_match_score", "location_match_score", "score_breakdown", "created_at",
    ],
    "cover_letter": [
        "cover_letter_id", "user_id", "job_id", "resume_id", "agent_session_id",
        "subject", "content", "llm_model_used", "is_sent", "sent_at", "created_at",
    ],
    "application_record": [
        "application_id", "user_id", "job_id", "version_id", "application_status",
        "applied_at", "status_updated_at", "days_since_application", "user_feedback",
    ],
    "career_analysis_report": [
        "report_id", "survey_id", "resume_id", "target_position", "skill_gap_analysis",
        "career_path_suggestions", "market_insights", "career_readiness_score",
        "generated_at", "user_id", "report_version", "preliminary_summary",
        "radar_chart", "gap_analysis", "action_plan",
    ],
    "skill_gap": [
        "gap_id", "report_id", "skill_id", "current_level", "target_level",
        "priority_rank", "time_investment_hours", "skill_roi_score",
    ],
    "side_project_recommendation": [
        "recommendation_id", "gap_id", "project_name", "tech_stack", "difficulty",
        "capability_gaps_addressed", "project_phases", "overall_resume_impact", "created_at",
    ],
    "agent_session": [
        "session_id", "user_id", "resume_id", "trigger_type", "user_input_summary",
        "tool_job_match_called", "tool_resume_analysis_called", "tool_resume_optimize_called",
        "tool_skill_gap_called", "tool_side_project_called", "tool_course_recommend_called",
        "tool_cover_letter_called", "analysis_id", "optimization_id", "career_report_id",
        "recommended_job_ids", "recommended_course_ids", "total_tokens_used", "latency_ms",
        "llm_model_used", "status", "error_message", "created_at", "completed_at",
    ],
}

# 說明文件中預期的 FK：(子表, 子表欄位, 父表, 父表欄位)
EXPECTED_FKS = [
    ("user_profile", "user_id", "user", "user_id"),
    ("career_survey", "user_id", "user", "user_id"),
    ("resume", "user_id", "user", "user_id"),
    ("resume", "template_id", "resume_template", "template_id"),
    ("resume_version", "resume_id", "resume", "resume_id"),
    ("resume_analysis", "resume_id", "resume", "resume_id"),
    ("resume_analysis", "user_id", "user", "user_id"),
    ("resume_analysis", "target_job_id", "job_posting", "job_id"),
    ("resume_optimization", "resume_id", "resume", "resume_id"),
    ("resume_optimization", "version_id", "resume_version", "version_id"),
    ("resume_optimization", "user_id", "user", "user_id"),
    ("resume_optimization", "target_job_id", "job_posting", "job_id"),
    ("upload_event", "user_id", "user", "user_id"),
    ("ocr_result", "event_id", "upload_event", "event_id"),
    ("ocr_result", "resume_id", "resume", "resume_id"),
    ("job_posting", "company_id", "company_info", "company_id"),
    ("job_skill_requirement", "job_id", "job_posting", "job_id"),
    ("job_skill_requirement", "skill_id", "skill_master", "skill_id"),
    ("user_skill", "user_id", "user", "user_id"),
    ("user_skill", "skill_id", "skill_master", "skill_id"),
    ("course", "primary_skill_id", "skill_master", "skill_id"),
    ("job_matching", "resume_id", "resume", "resume_id"),
    ("job_matching", "job_id", "job_posting", "job_id"),
    ("match_score", "matching_id", "job_matching", "matching_id"),
    ("cover_letter", "user_id", "user", "user_id"),
    ("cover_letter", "job_id", "job_posting", "job_id"),
    ("cover_letter", "resume_id", "resume", "resume_id"),
    ("cover_letter", "agent_session_id", "agent_session", "session_id"),
    ("application_record", "user_id", "user", "user_id"),
    ("application_record", "job_id", "job_posting", "job_id"),
    ("application_record", "version_id", "resume_version", "version_id"),
    ("career_analysis_report", "survey_id", "career_survey", "survey_id"),
    ("career_analysis_report", "resume_id", "resume", "resume_id"),
    ("career_analysis_report", "user_id", "user", "user_id"),
    ("skill_gap", "report_id", "career_analysis_report", "report_id"),
    ("skill_gap", "skill_id", "skill_master", "skill_id"),
    ("side_project_recommendation", "gap_id", "skill_gap", "gap_id"),
    ("agent_session", "user_id", "user", "user_id"),
    ("agent_session", "resume_id", "resume", "resume_id"),
    ("agent_session", "analysis_id", "resume_analysis", "analysis_id"),
    ("agent_session", "optimization_id", "resume_optimization", "optimization_id"),
    ("agent_session", "career_report_id", "career_analysis_report", "report_id"),
]


def load_dotenv():
    from dotenv import load_dotenv as _load
    for p in [PROJECT_ROOT / ".env", PROJECT_ROOT / "Erd" / ".env"]:
        if p.exists():
            _load(p)
            break


def get_supabase_client():
    load_dotenv()
    from supabase import create_client
    url = os.getenv("SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise SystemExit("請在 .env 設定 SUPABASE_URL 與 SUPABASE_SERVICE_ROLE_KEY（或 SUPABASE_KEY）")
    return create_client(url, key)


def _actual_table(table: str) -> str:
    return TABLE_ALIAS.get(table, table)


def check_columns_via_api(supabase, expected_schema: dict) -> tuple[dict, dict]:
    """用 Supabase REST API 檢查每個表的欄位：表存在則回傳 {表: 缺少的欄位}，表不存在則記在 missing_tables。"""
    missing_tables = {}
    missing_columns = {}

    for table, expected_cols in expected_schema.items():
        actual_table = _actual_table(table)
        try:
            # 先確認表存在：limit 0 不取資料
            supabase.table(actual_table).select("*").limit(0).execute()
        except Exception as e:
            err = str(e).lower()
            if "does not exist" in err or "relation" in err or "404" in err or "could not find" in err:
                missing_tables[table] = str(e)
                continue
            # 可能是權限或網路錯誤，仍嘗試逐欄檢查
        missing = []
        for col in expected_cols:
            try:
                supabase.table(actual_table).select(col).limit(0).execute()
            except Exception as e:
                err = str(e).lower()
                if "column" in err and "does not exist" in err:
                    missing.append(col)
                elif "does not exist" in err or "relation" in err:
                    missing_tables[table] = str(e)
                    break
        if table not in missing_tables and missing:
            missing_columns[table] = missing
    return missing_tables, missing_columns


def run_schema_check_db(db_url: str) -> tuple[dict, dict, dict]:
    """用 PostgreSQL information_schema 取得實際表與欄位，回傳 (實際表與欄位, 缺少表, 缺少欄位)。"""
    try:
        import psycopg2
    except ImportError:
        raise SystemExit("FK 檢查需要 psycopg2，請執行: pip install psycopg2-binary")

    actual = {}
    missing_tables = {}
    missing_columns = {}

    with psycopg2.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name, column_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position
            """)
            for table, column in cur.fetchall():
                t = table.lower()
                actual.setdefault(t, []).append(column.lower())
    for table, expected_cols in EXPECTED_SCHEMA.items():
        actual_table = _actual_table(table)
        cols_in_db = actual.get(actual_table) or actual.get(table)
        if not cols_in_db:
            missing_tables[table] = "表在資料庫中不存在"
            continue
        actual_set = set(c.lower() for c in cols_in_db)
        missing = [c for c in expected_cols if c.lower() not in actual_set]
        if missing:
            missing_columns[table] = missing
    return actual, missing_tables, missing_columns


def run_fk_check(db_url: str) -> tuple[list, list]:
    """比對 DB 的 FK 與 EXPECTED_FKS，回傳 (缺少的 FK, 多出來的 FK)。"""
    try:
        import psycopg2
    except ImportError:
        raise SystemExit("FK 檢查需要 psycopg2，請執行: pip install psycopg2-binary")

    with psycopg2.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    kcu.table_name AS child_table,
                    kcu.column_name AS child_column,
                    ccu.table_name AS parent_table,
                    ccu.column_name AS parent_column
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage ccu
                    ON tc.constraint_name = ccu.constraint_name
                    AND tc.table_schema = ccu.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                  AND tc.table_schema = 'public'
            """)
            rows = cur.fetchall()
    actual_fks = set(
        (child_t.lower(), child_c.lower(), parent_t.lower(), parent_c.lower())
        for child_t, child_c, parent_t, parent_c in rows
    )
    expected_set = set(
        (c.lower(), col.lower(), p.lower(), pcol.lower())
        for c, col, p, pcol in EXPECTED_FKS
    )
    missing_fks = [t for t in EXPECTED_FKS if (t[0].lower(), t[1].lower(), t[2].lower(), t[3].lower()) not in actual_fks]
    extra_fks = [
        (child_t, child_c, parent_t, parent_c)
        for child_t, child_c, parent_t, parent_c in rows
        if (child_t.lower(), child_c.lower(), parent_t.lower(), parent_c.lower()) not in expected_set
    ]
    return missing_fks, extra_fks


def main():
    import argparse
    parser = argparse.ArgumentParser(description="驗證 Supabase 與說明文件欄位/關聯對齊")
    parser.add_argument("--fk", action="store_true", help="同時檢查 FK（需設定 DATABASE_URL）")
    parser.add_argument("--api-only", action="store_true", help="僅用 API 檢查欄位，不使用 DATABASE_URL")
    args = parser.parse_args()

    load_dotenv()
    db_url = os.getenv("DATABASE_URL")

    print("=" * 60)
    print("Supabase 與說明文件對齊驗證")
    print("  說明文件: career_pilot說明文件v4_with_chinese.md")
    print("=" * 60)

    # ----- 欄位檢查 -----
    if db_url and not args.api_only:
        print("\n[1] 欄位檢查（使用 DATABASE_URL + information_schema）")
        try:
            actual, missing_tables, missing_columns = run_schema_check_db(db_url)
        except Exception as e:
            print(f"  連線失敗: {e}")
            print("  改為使用 Supabase API 檢查欄位…")
            supabase = get_supabase_client()
            missing_tables, missing_columns = check_columns_via_api(supabase, EXPECTED_SCHEMA)
        else:
            print(f"  已讀取 public schema 共 {len(actual)} 個表")
    else:
        print("\n[1] 欄位檢查（使用 Supabase API）")
        if not db_url:
            print("  提示: 未設定 DATABASE_URL，無法用 information_schema；僅以 API 逐欄查詢")
        supabase = get_supabase_client()
        missing_tables, missing_columns = check_columns_via_api(supabase, EXPECTED_SCHEMA)

    if missing_tables:
        print("\n  缺少的資料表（說明文件有、DB 沒有）:")
        for t, msg in sorted(missing_tables.items()):
            print(f"    - {t}: {msg}")
    else:
        print("\n  所有說明文件中的表在 DB 皆存在")

    if missing_columns:
        print("\n  缺少的欄位（說明文件有、該表沒有）:")
        for t, cols in sorted(missing_columns.items()):
            print(f"    - {t}: {', '.join(cols)}")
    elif not missing_tables:
        print("  所有表欄位與說明文件一致")

    if not missing_tables and not missing_columns:
        print("  ✅ 欄位對齊通過")

    # ----- FK 檢查 -----
    if args.fk:
        print("\n[2] 關聯關係（FK）檢查")
        if not db_url:
            print("  請在 .env 設定 DATABASE_URL（Supabase 專案 → Settings → Database → Connection string）")
        else:
            try:
                missing_fks, extra_fks = run_fk_check(db_url)
                if missing_fks:
                    print("\n  說明文件有、DB 沒有的 FK:")
                    for (c, col, p, pcol) in missing_fks:
                        print(f"    - {c}.{col} → {p}.{pcol}")
                else:
                    print("  說明文件中預期的 FK 皆存在")
                if extra_fks:
                    print("\n  DB 有、說明文件未列出的 FK（僅供參考）:")
                    for (c, col, p, pcol) in extra_fks[:20]:
                        print(f"    - {c}.{col} → {p}.{pcol}")
                    if len(extra_fks) > 20:
                        print(f"    ... 共 {len(extra_fks)} 筆")
                if not missing_fks:
                    print("  ✅ FK 對齊通過")
            except Exception as e:
                print(f"  FK 檢查失敗: {e}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
