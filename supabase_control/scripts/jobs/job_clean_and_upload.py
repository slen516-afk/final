"""
職缺資料清理與寫入 Supabase。
依 cleaner步驟_v2.md 清理 jobs_rows.csv，寫入 company_info、job_posting。
執行：工作目錄或腳本所在專案根為 supabase_control，具備 data/jobs_rows.csv、.env（或 Erd/.env）。
"""

import math
import os
import re
import json
import sys
from pathlib import Path

import pandas as pd
import numpy as np

# 專案根目錄 = supabase_control
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DATA_DIR = PROJECT_ROOT / "data"
RAW_CSV = DATA_DIR / "jobs_rows.csv"

# --- 清理函數（依 clear.ipynb）---
ORG_SUFFIXES = ["股份有限公司", "有限公司", "集團", "分公司", "財團法人"]
PRIORITY_LAYERS = {
    "tier_1_specific": [
        ("製造業", ["半導體製造", "製程", "產線", "封裝測試", "晶圓", "fab", "光電", "台積電"]),
        ("醫療", ["醫療器材", "醫藥", "生技", "藥廠", "醫檢", "診所", "醫院", "醫材", "醫電", "生醫", "製藥", "藥業"]),
        ("金融業", ["銀行", "保險", "證券", "投信", "金控", "金融", "控股", "資產管理"]),
    ],
    "tier_2_mixed": [
        ("資訊科技", ["軟體", "網路服務", "雲端", "ai應用", "資安", "系統整合"]),
        ("製造業", ["材料", "精密", "機械"]),
    ],
    "tier_3_generic": [
        ("資訊科技", ["科技", "資訊", "數位"]),
        ("服務業", ["服務"]),
    ],
}
CITIES = [
    "台北市", "新北市", "桃園市", "台中市", "台南市", "高雄市",
    "基隆市", "新竹市", "嘉義市",
    "新竹縣", "苗栗縣", "彰化縣", "南投縣", "雲林縣", "嘉義縣",
    "屏東縣", "宜蘭縣", "花蓮縣", "台東縣", "澎湖縣", "金門縣", "連江縣",
]
DISTRICT_SUFFIX = re.compile(r"^(.+?[區鄉鎮市])")
VALID_DISTRICTS = {"東區", "北區", "香山區", "西區"}
GARDEN_BLACKLIST = ["工業園區", "科學園區", "園區", "太空中心"]


def clean_text(text):
    if pd.isna(text) or text is None:
        return None
    s = str(text).strip()
    s = re.sub(r"[\r\n]+", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s if s else None


def clean_company_name(company_name):
    if pd.isna(company_name) or not str(company_name).strip():
        return None
    name = str(company_name).strip()
    for suffix in ORG_SUFFIXES:
        if name.endswith(suffix):
            name = name[: -len(suffix)].strip()
        while suffix in name:
            name = name.replace(suffix, " ").strip()
    return name if name else None


def extract_industry(company_name, job_category=None):
    if pd.isna(company_name) or not str(company_name).strip():
        return None
    name = clean_company_name(company_name)
    if not name:
        return None
    name_lower = name.lower()
    for industry, keywords in PRIORITY_LAYERS["tier_1_specific"]:
        kws = [kw for kw in keywords if not (industry == "金融業" and kw == "銀行" and "人力銀行" in name_lower)]
        if any(kw in name_lower for kw in kws):
            return industry
    for industry, keywords in PRIORITY_LAYERS["tier_2_mixed"]:
        if any(kw in name_lower for kw in keywords):
            return industry
    for industry, keywords in PRIORITY_LAYERS["tier_3_generic"]:
        if any(kw in name_lower for kw in keywords):
            return industry
    if job_category is not None and str(job_category).strip():
        return infer_industry_from_job_category(job_category)
    return None


def infer_industry_from_job_category(job_categories_text):
    if pd.isna(job_categories_text) or not str(job_categories_text).strip():
        return None
    s = str(job_categories_text).strip().lower()
    manufacturing_kw = ["製造", "產線", "設備", "製程", "機構工程", "半導體", "光電", "pcb", "smt", "品保", "倉管", "生產", "焊接", "cnc", "製程工程師", "設備工程師", "生產管理", "品管", "qc", "qe", "ie", "me", "廠務", "生產線", "作業員"]
    medical_kw = ["醫護", "護理", "藥師", "醫檢", "醫事", "醫師", "護理師", "醫檢師", "醫療器材", "醫學工程", "臨床", "復健"]
    keywords = [
        ("資訊科技", ["軟體", "程式", "系統分析", "internet", "mis", "韌體", "資料庫", "資安", "演算法", "dba", "bios", "全端", "後端", "前端", "資料科學", "大數據", "雲端", "devops", "sre", "嵌入式", "網管", "qa"]),
        ("製造業", manufacturing_kw),
        ("金融業", ["金融", "銀行", "保險", "證券", "理財", "風控", "精算", "授信", "櫃員"]),
        ("醫療", medical_kw),
        ("行銷", ["行銷", "廣告", "媒體", "電商", "社群", "文案", "企劃", "數位行銷"]),
        ("商業", ["人資", "人力資源", "會計", "財務", "審計", "業務", "客服", "採購", "行政", "總務", "秘書", "法務", "顧問"]),
        ("設計", ["設計", "ui", "ux", "平面", "工業設計", "視覺"]),
        ("教育", ["教師", "講師", "教練", "補習", "教材", "教學"]),
    ]
    for industry, kws in keywords:
        if any(kw in s for kw in kws):
            return industry
    return None


def standardize_location(city, district, location):
    parts = [x for x in [city, district, location] if pd.notna(x) and str(x).strip()]
    full = "".join(str(p).strip() for p in parts) if parts else None
    if not full:
        return None, None, None
    city_val, district_val = None, None
    for c in CITIES:
        if full.startswith(c):
            city_val = c
            rest = full[len(c) :].strip()
            if rest.startswith(c):
                rest = rest[len(c) :].strip()
            if city_val in ["新竹市", "嘉義市"]:
                for valid_d in VALID_DISTRICTS:
                    if rest.startswith(valid_d):
                        district_val = valid_d
                        break
            else:
                m = DISTRICT_SUFFIX.match(rest)
                if m:
                    candidate = m.group(1).strip()
                    if not any(b in candidate for b in GARDEN_BLACKLIST):
                        district_val = candidate
                if not district_val and rest:
                    tok = re.match(r"^([^\d路街段巷弄號]+?[區鄉鎮市])", rest)
                    if tok:
                        candidate = tok.group(1).strip()
                        if not any(b in candidate for b in GARDEN_BLACKLIST):
                            district_val = candidate
            break
    return full, city_val, district_val


def _parse_int(s):
    if not s:
        return None
    return int(re.sub(r"[,，\s]", "", str(s)))


def clean_salary(salary_raw):
    if pd.isna(salary_raw) or not str(salary_raw).strip():
        return None, None
    s = str(salary_raw).strip()
    if "面議" in s or "面谈" in s:
        return 40000, 40000
    s_clean = re.sub(r"[,，\s]", "", s)
    mm = re.search(r"([\d,]+)\s*[~～\-－至到]\s*([\d,]+)", s)
    if mm:
        lo, hi = _parse_int(mm.group(1)), _parse_int(mm.group(2))
        if lo is not None and hi is not None:
            return (min(lo, hi), max(lo, hi))
    single = re.search(r"月薪\s*([\d,]+)", s)
    if single:
        v = _parse_int(single.group(1))
        if v is not None:
            return (v, v)
    num = re.search(r"(\d+)\s*元", s_clean)
    if num:
        return (int(num.group(1)), 999999)
    return None, None


def determine_remote_option(addr, job_type):
    if pd.notna(job_type) and "遠端" in str(job_type):
        return "remote"
    if pd.notna(job_type) and " hybrid" in str(job_type).lower():
        return "hybrid"
    addr_str = str(addr) if pd.notna(addr) else ""
    if "遠端" in addr_str or "remote" in addr_str.lower():
        return "remote"
    if "混合" in addr_str or "hybrid" in addr_str.lower():
        return "hybrid"
    return "onsite"


def merge_requirements(row):
    keys = ["work_exp", "education", "major", "language", "skills", "tools", "certificates", "other_requirements"]
    parts = []
    for k in keys:
        v = row.get(k)
        if pd.notna(v) and str(v).strip():
            parts.append(str(v).strip())
    return "\n".join(parts) if parts else None


def create_job_details(row):
    keys = ["work_time", "vacation", "start_work", "business_trip", "legal_benefits", "other_benefits", "raw_benefits"]
    d = {}
    for k in keys:
        v = row.get(k)
        if pd.notna(v) and str(v).strip():
            d[k] = str(v).strip()
    return d if d else None


def _agg_job_cats(x):
    parts = x.dropna().astype(str).str.strip()
    parts = parts[parts.str.len() > 0].unique()
    return " | ".join(parts) if len(parts) else ""


def main():
    from dotenv import load_dotenv
    from supabase import create_client

    for p in [PROJECT_ROOT / "Erd" / ".env", PROJECT_ROOT / ".env", Path("supabase_control/Erd/.env")]:
        if p.exists():
            load_dotenv(p)
            break
    else:
        load_dotenv()

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("請在 .env 設定 SUPABASE_URL 和 SUPABASE_SERVICE_ROLE_KEY")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    _ = supabase.table("company_info").select("company_id").limit(1).execute()
    print("✓ Supabase 連線成功")

    if not RAW_CSV.exists():
        raise FileNotFoundError(f"找不到 {RAW_CSV}")

    df_raw = pd.read_csv(RAW_CSV)
    print(f"✓ 載入 {len(df_raw):,} 筆原始資料")
    print(f"欄位: {list(df_raw.columns)}")

    # 公司主檔
    company_agg = df_raw.groupby("company_name", as_index=False).agg(
        company_name=("company_name", "first"),
        job_categories=("job_category", _agg_job_cats),
    )
    company_agg["company_name"] = company_agg["company_name"].apply(clean_text)
    company_agg = company_agg[company_agg["company_name"].notna() & (company_agg["company_name"].str.len() > 0)]

    def _resolve_industry(row):
        ind = extract_industry(row["company_name"])
        if ind is not None:
            return ind
        ind = infer_industry_from_job_category(row["job_categories"])
        if ind is not None:
            return ind
        return "未分類"

    company_agg["industry"] = company_agg.apply(_resolve_industry, axis=1)
    company_agg["company_size"] = None
    company_agg["location"] = None
    company_agg["website"] = None
    company_agg["description"] = None
    df_company = company_agg[
        ["company_name", "industry", "job_categories", "company_size", "location", "website", "description"]
    ].copy()
    df_company.rename(columns={"job_categories": "job_category"}, inplace=True)
    df_company = df_company.drop_duplicates(subset=["company_name"]).reset_index(drop=True)
    print(f"✓ 公司主檔 {len(df_company):,} 家 | 有 industry（非未分類）: {(df_company['industry'] != '未分類').sum():,}")

    # 職缺清理
    df_jobs = df_raw.copy()
    df_jobs["company_name"] = df_jobs["company_name"].apply(clean_text)
    df_jobs["job_title"] = df_jobs["job_name"].apply(clean_text)
    df_jobs["job_description"] = df_jobs["job_description"].apply(clean_text)
    df_jobs["job_category"] = df_jobs["job_category"].apply(clean_text)
    df_jobs["requirements"] = df_jobs.apply(merge_requirements, axis=1)
    loc_out = df_jobs.apply(lambda r: standardize_location(None, None, r.get("location")), axis=1)
    df_jobs["full_address"] = [x[0] for x in loc_out]
    df_jobs["city"] = [x[1] for x in loc_out]
    df_jobs["district"] = [x[2] for x in loc_out]
    sal_out = df_jobs["salary"].apply(clean_salary)
    df_jobs["salary_min"] = [x[0] for x in sal_out]
    df_jobs["salary_max"] = [x[1] for x in sal_out]
    df_jobs["remote_option"] = df_jobs.apply(lambda r: determine_remote_option(r.get("full_address"), r.get("job_type")), axis=1)
    df_jobs["job_details"] = df_jobs.apply(create_job_details, axis=1)
    df_jobs["posted_date"] = pd.to_datetime(df_jobs["update_date"], errors="coerce").dt.date
    df_jobs["scraped_at"] = pd.to_datetime(df_jobs["created_at"], errors="coerce")
    df_jobs["source_platform"] = "104人力銀行"
    df_jobs["source_url"] = df_jobs["url"].where(df_jobs["url"].notna() & (df_jobs["url"].astype(str).str.len() > 0))
    df_jobs["is_active"] = True
    df_jobs["is_embedded"] = False

    has_url = df_jobs["source_url"].notna() & (df_jobs["source_url"].astype(str).str.len() > 0)
    df_with_url_raw = df_jobs[has_url].copy().sort_values("posted_date", ascending=False, na_position="last")
    df_with_url = df_with_url_raw.drop_duplicates(subset=["source_url"], keep="first")
    df_no_url = df_jobs[~has_url].drop_duplicates(subset=["company_name", "job_title", "full_address"], keep="last")
    df_jobs = pd.concat([df_with_url, df_no_url], ignore_index=True)
    df_jobs = df_jobs[
        df_jobs["company_name"].notna() & (df_jobs["company_name"].astype(str).str.len() > 0)
        & df_jobs["job_title"].notna() & (df_jobs["job_title"].astype(str).str.len() > 0)
        & df_jobs["job_description"].notna() & (df_jobs["job_description"].astype(str).str.len() > 0)
    ].copy()
    print(f"✓ 去重並移除空值後 {len(df_jobs):,} 筆職缺")

    # 寫入 company_info
    def _json_safe(v):
        if v is None:
            return None
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            return None
        if hasattr(v, "__float__") and pd.isna(v):
            return None
        return v

    # 相容 pandas < 2.2：用 apply 做逐欄清理
    for c in df_company.columns:
        if df_company[c].dtype == object:
            df_company[c] = df_company[c].apply(lambda x: x.strip() if isinstance(x, str) else x)
    df_company = df_company.where(pd.notnull(df_company), None).replace("", None)

    existing_data = supabase.table("company_info").select("company_name", "company_id").limit(10000).execute()
    company_name_to_id = {d["company_name"]: d["company_id"] for d in existing_data.data}

    to_insert = []
    for _, row in df_company.iterrows():
        cname = row["company_name"]
        if cname in company_name_to_id:
            continue
        payload = {k: _json_safe(row.get(k)) for k in ["company_name", "industry", "company_size", "location", "website", "description"]}
        to_insert.append(payload)

    success_count = 0
    fail_count = 0
    if to_insert:
        for i in range(0, len(to_insert), 500):
            batch_data = to_insert[i : i + 500]
            try:
                ins_res = supabase.table("company_info").insert(batch_data).execute()
                if ins_res.data:
                    success_count += len(ins_res.data)
                    for d in ins_res.data:
                        company_name_to_id[d["company_name"]] = d["company_id"]
            except Exception as e:
                print(f"❌ 批量寫入發生錯誤: {e}")
                fail_count = len(to_insert) - success_count
                break

    _res = supabase.table("company_info").select("company_name", "company_id").limit(10000).execute()
    company_name_to_id = {d["company_name"]: d["company_id"] for d in _res.data}
    try:
        _count_res = supabase.table("company_info").select("*", count="exact").limit(1).execute()
        db_total = getattr(_count_res, "count", None) or len(company_name_to_id)
    except Exception:
        db_total = len(company_name_to_id)
    print(f"--- 公司處理回報 ---")
    print(f"✓ 成功新增: {success_count} 筆 | 已存在跳過: {len(df_company) - len(to_insert)} 筆 | 寫入失敗: {fail_count} 筆")
    print(f"📊 資料庫目前總計: {db_total} 家公司")

    # 寫入 job_posting
    for c in df_jobs.columns:
        if df_jobs[c].dtype == object:
            df_jobs[c] = df_jobs[c].apply(lambda x: x.strip() if isinstance(x, str) else x)
    df_jobs = df_jobs.where(pd.notnull(df_jobs), None)
    df_jobs["salary_min"] = pd.to_numeric(df_jobs["salary_min"], errors="coerce").fillna(0).astype(int)
    df_jobs["salary_max"] = pd.to_numeric(df_jobs["salary_max"], errors="coerce").fillna(0).astype(int)
    df_jobs["is_active"] = df_jobs["is_active"].map(lambda x: True if x is None else bool(x))

    existing_jobs = supabase.table("job_posting").select("source_url", "job_title", "company_id", "full_address").limit(10000).execute()
    db_rows = existing_jobs.data or []
    existing_fingerprints_addr = {
        (d.get("company_id"), d.get("job_title"), d.get("full_address"))
        for d in db_rows
        if not d.get("source_url") and d.get("job_title")
    }

    def _serialize_dt(v):
        if v is None or (hasattr(v, "__float__") and pd.isna(v)):
            return None
        if hasattr(v, "isoformat"):
            return v.isoformat()
        return str(v) if v is not None else None

    def _json_safe_job(v):
        if v is None:
            return None
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            return None
        if hasattr(v, "__float__") and pd.isna(v):
            return None
        if hasattr(v, "isoformat"):
            return v.isoformat()
        if isinstance(v, dict):
            return {k: _json_safe_job(vv) for k, vv in v.items()}
        return v

    to_insert_jobs = []
    job_skip = 0
    job_skip_no_company = 0
    for _, row in df_jobs.iterrows():
        cname = row.get("company_name")
        cid = company_name_to_id.get(cname)
        if not cid:
            job_skip_no_company += 1
            continue
        src_url = row.get("source_url")
        title = row.get("job_title")
        addr = row.get("full_address")
        if not src_url:
            if (cid, title, addr) in existing_fingerprints_addr:
                job_skip += 1
                continue
        payload = {
            "company_id": cid,
            "job_title": title,
            "job_category": row.get("job_category"),
            "job_description": row.get("job_description"),
            "requirements": row.get("requirements"),
            "salary_min": int(row["salary_min"]),
            "salary_max": int(row["salary_max"]),
            "full_address": addr,
            "city": row.get("city"),
            "district": row.get("district"),
            "remote_option": row.get("remote_option"),
            "job_details": row.get("job_details") if isinstance(row.get("job_details"), dict) else None,
            "source_platform": row.get("source_platform") or "104人力銀行",
            "source_url": src_url,
            "posted_date": _serialize_dt(row.get("posted_date")),
            "scraped_at": _serialize_dt(row.get("scraped_at")),
            "is_active": row.get("is_active"),
        }
        payload = {k: _json_safe_job(v) for k, v in payload.items()}
        to_insert_jobs.append(payload)

    job_ok = 0
    job_err = 0
    if to_insert_jobs:
        for i in range(0, len(to_insert_jobs), 500):
            batch_data = to_insert_jobs[i : i + 500]
            try:
                ins_res = supabase.table("job_posting").upsert(
                    batch_data, on_conflict="source_url", ignore_duplicates=False
                ).execute()
                if ins_res.data:
                    job_ok += len(ins_res.data)
            except Exception as e:
                print(f"❌ 批量寫入錯誤: {e}")
                job_err = len(to_insert_jobs) - job_ok
                break
    try:
        _count_res = supabase.table("job_posting").select("*", count="exact").limit(1).execute()
        job_db_total = getattr(_count_res, "count", None) or (len(db_rows) + job_ok)
    except Exception:
        job_db_total = len(db_rows) + job_ok
    print(f"--- 職缺處理回報 (Upsert 模式) ---")
    print(f"✓ 成功處理（新增/更新）: {job_ok} 筆")
    print(f"⏭️ 跳過重複（無 source_url 且已存在）: {job_skip} 筆")
    print(f"⏭️ 跳過（找不到公司 ID）: {job_skip_no_company} 筆")
    print(f"❌ 寫入失敗: {job_err} 筆")
    print(f"📊 資料庫目前職缺總數: {job_db_total:,} 筆")


if __name__ == "__main__":
    main()
