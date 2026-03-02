"""
階段九：提取技能需求 (job_skill_requirement)。
依 cleaner步驟_v2.md 階段九，從職缺提取技能並寫入 job_skill_requirement。
技能來源：結構化欄位 skills/tools、JD/requirements 關鍵字整詞匹配。
前置條件：skill_master、job_posting、company_info 已寫入；工作目錄為 supabase_control，具備 data/jobs_rows.csv 或 data/jobs_cleaned.csv。
"""

import os
import re
import json
import sys
from pathlib import Path

import pandas as pd

# 專案根目錄 = supabase_control
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
from supabase import create_client

# 載入 .env
for _path in [PROJECT_ROOT / ".env", PROJECT_ROOT / "Erd" / ".env"]:
    if _path.exists():
        load_dotenv(_path)
        break
else:
    load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("請設定 SUPABASE_URL 與 SUPABASE_KEY（.env）")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
DATA_DIR = str(PROJECT_ROOT / "data")
RAW_CSV = os.path.join(DATA_DIR, "jobs_rows.csv")
if not os.path.isfile(RAW_CSV):
    RAW_CSV = os.path.join(DATA_DIR, "jobs_cleaned.csv")


def build_skill_mapping(supabase_client):
    """步驟 1：從 skill_master 建立技能映射與 JD 關鍵字 regex"""
    response = supabase_client.table("skill_master").select("skill_id, skill_name, synonyms").limit(5000).execute()
    skill_master_df = pd.DataFrame(response.data or [])
    if len(skill_master_df) == 0:
        raise RuntimeError("skill_master 為空，請先填入技能或執行 skill_write_evaluation")

    synonym_to_skill_id = {}
    for _, row in skill_master_df.iterrows():
        skill_id = row["skill_id"]
        skill_name = row["skill_name"]
        synonyms_raw = row.get("synonyms")
        if synonyms_raw is not None:
            synonyms = json.loads(synonyms_raw) if isinstance(synonyms_raw, str) else (list(synonyms_raw) if synonyms_raw else [])
        else:
            synonyms = []
        synonym_to_skill_id[str(skill_name).strip().lower()] = skill_id
        for syn in synonyms:
            if syn is not None and str(syn).strip():
                synonym_to_skill_id[str(syn).strip().lower()] = skill_id

    skill_id_to_jd_patterns = {}
    for _, row in skill_master_df.iterrows():
        skill_id = row["skill_id"]
        skill_name = str(row["skill_name"]).strip()
        synonyms_raw = row.get("synonyms")
        synonyms = []
        if synonyms_raw is not None:
            synonyms = json.loads(synonyms_raw) if isinstance(synonyms_raw, str) else (list(synonyms_raw) if synonyms_raw else [])
        phrases = [skill_name] + [str(s).strip() for s in synonyms if s and len(str(s).strip()) >= 2]
        phrases = list(dict.fromkeys(p for p in phrases if len(p) >= 2))
        if not phrases:
            continue
        patterns = []
        for p in sorted(phrases, key=len, reverse=True):
            try:
                pat = re.compile(r"(?<![a-zA-Z0-9_])" + re.escape(p) + r"(?![a-zA-Z0-9_])", re.IGNORECASE)
                patterns.append((pat, p))
            except Exception:
                continue
        if patterns:
            skill_id_to_jd_patterns[skill_id] = patterns

    return skill_master_df, synonym_to_skill_id, skill_id_to_jd_patterns


def parse_skills(skills_str, tools_str):
    """合併 skills 與 tools，拆成技能列表"""
    all_skills = []
    for raw in (skills_str, tools_str):
        if pd.isna(raw) or not str(raw).strip():
            continue
        s = str(raw).strip()
        for sep in ["、", ","]:
            s = s.replace(sep, "|")
        parts = [x.strip() for x in s.split("|") if x.strip()]
        all_skills.extend(parts)
    return list(dict.fromkeys(all_skills))


def build_jd_text(row):
    parts = []
    for col in ("job_description", "requirements", "other_requirements"):
        if col in row.index and pd.notna(row.get(col)) and str(row.get(col)).strip():
            parts.append(str(row[col]).strip())
    return " ".join(parts) if parts else ""


def infer_importance_and_proficiency(text, skill_id, skill_id_to_jd_patterns, before=100, after=80):
    """從 JD 文字中該技能出現處的前後文推論 importance 與 proficiency_level"""
    importance = "required"
    proficiency_level = None
    if not text or not skill_id_to_jd_patterns or skill_id not in skill_id_to_jd_patterns:
        return importance, proficiency_level
    context = ""
    for pat, _ in skill_id_to_jd_patterns[skill_id]:
        m = pat.search(text)
        if m:
            start = max(0, m.start() - before)
            end = min(len(text), m.end() + after)
            context = text[start:end]
            break
    if not context:
        return importance, proficiency_level
    if re.search(r"加分|佳|優先考慮|preferred|nice\s*to\s*have", context, re.I):
        importance = "nice-to-have"
    elif re.search(r"必備|必要條件|須具備|required", context, re.I):
        importance = "required"
    if re.search(r"精通", context):
        proficiency_level = 8
    elif re.search(r"熟悉|熟練", context):
        proficiency_level = 6
    elif re.search(r"具備|了解", context):
        proficiency_level = 4
    elif re.search(r"初學", context):
        proficiency_level = 2
    else:
        ym = re.search(r"(\d+)\s*年", context)
        if ym:
            y = int(ym.group(1))
            proficiency_level = 7 if y >= 5 else (5 if y >= 3 else (4 if y >= 2 else 3))
    return importance, proficiency_level


def main(do_insert=True, do_export_unmatched=True):
    print(f"使用資料檔：{RAW_CSV}")
    print(f"Supabase 連線：{SUPABASE_URL[:50]}...")

    skill_master_df, synonym_to_skill_id, skill_id_to_jd_patterns = build_skill_mapping(supabase)
    print(f"✅ 讀取了 {len(skill_master_df)} 個技能")
    print(f"✅ 建立了 {len(synonym_to_skill_id)} 個技能映射（含同義詞）")
    print(f"✅ JD 關鍵字匹配：{len(skill_id_to_jd_patterns)} 個技能有整詞 regex")

    raw_df = pd.read_csv(RAW_CSV, encoding="utf-8", low_memory=False)
    print(f"✅ 讀取了 {len(raw_df)} 筆職缺")

    has_company = "company_name" in raw_df.columns
    has_job = "job_title" in raw_df.columns or "job_name" in raw_df.columns
    has_structured = "skills" in raw_df.columns or "tools" in raw_df.columns
    has_jd_text = "job_description" in raw_df.columns or "requirements" in raw_df.columns or "other_requirements" in raw_df.columns
    if not (has_company and has_job and (has_structured or has_jd_text)):
        raise ValueError("缺少必要欄位：需 company_name、job_title/job_name、以及 (skills/tools) 或 (job_description/requirements)")

    raw_df["parsed_skills"] = raw_df.apply(lambda row: parse_skills(row.get("skills"), row.get("tools")), axis=1)
    raw_df["jd_requirements_text"] = raw_df.apply(build_jd_text, axis=1)

    job_response = supabase.table("job_posting").select("job_id, company_id, job_title").limit(20000).execute()
    company_response = supabase.table("company_info").select("company_id, company_name").limit(10000).execute()
    job_posting_df = pd.DataFrame(job_response.data or [])
    company_df = pd.DataFrame(company_response.data or [])
    job_with_company = job_posting_df.merge(company_df, on="company_id")
    job_mapping = {}
    for _, row in job_with_company.iterrows():
        key = (str(row["company_name"]).strip(), str(row["job_title"]).strip())
        job_mapping[key] = row["job_id"]
    print(f"✅ 建立了 {len(job_mapping)} 個職缺映射 (company_name, job_title) -> job_id")

    job_col = "job_title" if "job_title" in raw_df.columns else "job_name"
    job_skill_records = []
    unmatched_skills = set()
    unmatched_jobs = 0
    jd_added_count = 0

    for _, row in raw_df.iterrows():
        company_name = str(row["company_name"]).strip() if pd.notna(row.get("company_name")) else ""
        job_title = str(row[job_col]).strip() if pd.notna(row.get(job_col)) else ""
        key = (company_name, job_title)
        job_id = job_mapping.get(key)
        if not job_id:
            unmatched_jobs += 1
            continue

        skill_ids_from_structured = set()
        for skill_name in row["parsed_skills"]:
            if not skill_name or len(str(skill_name).strip()) < 2:
                continue
            sk = str(skill_name).strip().lower()
            skill_id = synonym_to_skill_id.get(sk)
            if skill_id is not None:
                skill_ids_from_structured.add(skill_id)
            else:
                unmatched_skills.add(skill_name)

        text = row.get("jd_requirements_text") or ""
        skill_ids_from_jd = set()
        if text and skill_id_to_jd_patterns:
            for sid, pattern_list in skill_id_to_jd_patterns.items():
                if sid in skill_ids_from_structured:
                    continue
                for pat, _ in pattern_list:
                    if pat.search(text):
                        skill_ids_from_jd.add(sid)
                        break

        all_skill_ids = skill_ids_from_structured | skill_ids_from_jd
        jd_added_count += len(skill_ids_from_jd)
        for skill_id in all_skill_ids:
            imp, prof = infer_importance_and_proficiency(text, skill_id, skill_id_to_jd_patterns)
            job_skill_records.append({"job_id": job_id, "skill_id": skill_id, "importance": imp, "proficiency_level": prof})

    print(f"✅ 成功匹配 {len(job_skill_records)} 筆技能需求")
    print(f"📊 僅由 JD 關鍵字補上的關聯數：{jd_added_count}")
    print(f"⚠️ 未匹配到 job_id 的職缺數：{unmatched_jobs}")
    print(f"⚠️ 結構化未匹配技能種類數：{len(unmatched_skills)}")

    job_skill_df = pd.DataFrame(job_skill_records).drop_duplicates(subset=["job_id", "skill_id"])
    print(f"去重後：{len(job_skill_df)} 筆")

    if do_insert and len(job_skill_df) > 0:
        BATCH_SIZE = 500
        total_inserted = 0
        for i in range(0, len(job_skill_df), BATCH_SIZE):
            batch = job_skill_df.iloc[i : i + BATCH_SIZE].to_dict("records")
            try:
                supabase.table("job_skill_requirement").insert(batch).execute()
                total_inserted += len(batch)
                print(f"寫入 {total_inserted}/{len(job_skill_df)}")
            except Exception as e:
                print(f"❌ 批次 {i} 失敗：{e}")
        print(f"✅ 實際寫入 {total_inserted} 筆")

    if do_export_unmatched and unmatched_skills:
        out_path = os.path.join(DATA_DIR, "unmatched_skills.csv")
        pd.DataFrame({"skill_name": sorted(unmatched_skills), "skill_category": None, "synonyms": None, "notes": ""}).to_csv(
            out_path, index=False, encoding="utf-8-sig"
        )
        print(f"✅ 已匯出 {len(unmatched_skills)} 個未匹配技能到 {out_path}")

    resp = supabase.table("job_skill_requirement").select("*", count="exact").limit(1).execute()
    total = getattr(resp, "count", None) or 0
    print(f"✅ job_skill_requirement 總筆數：{total}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="階段九：寫入 job_skill_requirement")
    parser.add_argument("--no-insert", action="store_true", help="不寫入 DB，僅產出統計與 unmatched_skills.csv")
    parser.add_argument("--no-export-unmatched", action="store_true", help="不匯出 unmatched_skills.csv")
    args = parser.parse_args()
    main(do_insert=not args.no_insert, do_export_unmatched=not args.no_export_unmatched)
