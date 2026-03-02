"""
Coursera 課程資料清洗與寫入 Supabase。
依 coursera_cleaning_steps.md 清洗 data/course/Coursera_row_rows.csv，寫入 course 表。
執行：工作目錄為 supabase_control 或 course；.env 設有 SUPABASE_URL、SUPABASE_SERVICE_ROLE_KEY；Supabase 已建立 course 表。
"""

import os
import re
import json
import sys
from pathlib import Path

import pandas as pd

# 專案根目錄 = supabase_control（若從 course 執行則為上層）
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
from supabase import create_client


def main():
    for p in [
        PROJECT_ROOT / "Erd" / ".env",
        PROJECT_ROOT / ".env",
        PROJECT_ROOT / "course" / ".env",
        Path("Erd/.env"),
        Path(".env"),
    ]:
        if p.exists():
            load_dotenv(p)
            break
    else:
        load_dotenv()

    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("請設定 SUPABASE_URL 與 SUPABASE_KEY（.env）")

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    COURSE_DIR = Path(__file__).resolve().parent
    RAW_CSV = PROJECT_ROOT / "data" / "course" / "Coursera_row_rows.csv"
    if not RAW_CSV.exists():
        RAW_CSV = COURSE_DIR / "Coursera_row_rows.csv"
    if not RAW_CSV.exists():
        RAW_CSV = PROJECT_ROOT / "course" / "Coursera_row_rows.csv"
    if not RAW_CSV.exists():
        raise FileNotFoundError(f"找不到 Coursera_row_rows.csv（請放在 data/course/ 或 course/）")

    print(f"資料目錄: {COURSE_DIR}")
    print(f"來源 CSV: {RAW_CSV}")
    print(f"Supabase: {SUPABASE_URL[:50]}...")

    df = pd.read_csv(RAW_CSV)
    print("shape:", df.shape)
    print("columns:", df.columns.tolist())

    df = df.drop(columns=["語言", "開課時間"], errors="ignore")
    df = df.drop(columns=["課程"], errors="ignore")

    def parse_rating(val):
        if pd.isna(val):
            return None
        m = re.search(r"(\d+\.?\d*)", str(val))
        if not m:
            return None
        r = float(m.group(1))
        return min(5.0, r) if r > 5 else r

    df["rating"] = df["評分"].apply(parse_rating)

    def parse_review_count(val):
        if pd.isna(val):
            return None
        s = str(val)
        m = re.search(r"([\d,]+(?:\.[\d]+)?)\s*(K|M)?\s*reviews?", s, re.I)
        if not m:
            return None
        n = float(m.group(1).replace(",", ""))
        k = (m.group(2) or "").upper()
        if k == "K":
            n *= 1000
        elif k == "M":
            n *= 1e6
        return int(n)

    df["review_count"] = df["評論數"].apply(parse_review_count)

    def to_skill_list(x):
        if pd.isna(x) or str(x).strip() == "":
            return []
        return [s.strip() for s in str(x).split(",") if s.strip()]

    df["skill_list"] = df["技能"].apply(to_skill_list)
    df["skills"] = df["skill_list"].apply(lambda x: x if isinstance(x, list) else [])

    meta = df["Metadata"].fillna("")
    df["level"] = meta.str.extract(r"(Beginner|Intermediate|Advanced)", expand=False)
    df["course_type"] = meta.str.extract(
        r"(Course|Specialization|Professional Certificate|Guided Project)", expand=False
    )

    def standardize_duration(row):
        sug = row.get("建議學習時間") if "建議學習時間" in row.index else None
        if pd.notna(sug) and str(sug).strip():
            s = str(sug).strip()
            m = re.match(r"P(\d+)M", s, re.I)
            if m:
                return f"{m.group(1)} months"
            if "month" in s.lower() or "months" in s.lower():
                return s
            if "week" in s.lower() or "weeks" in s.lower():
                return s
            if "hour" in s.lower():
                return s
            return s
        meta = str(row.get("Metadata", ""))
        if "Less Than 2 Hours" in meta:
            return "< 2 hours"
        m = re.search(r"(\d+)\s*-\s*(\d+)\s*(Weeks?|Months?)", meta, re.I)
        if m:
            return f"{m.group(1)}-{m.group(2)} {m.group(3).lower()}"
        m = re.search(r"(\d+)\s*(Weeks?|Months?)", meta, re.I)
        if m:
            return f"{m.group(1)} {m.group(2).lower()}"
        return None

    df["duration_suggested"] = df.apply(standardize_duration, axis=1)

    before = len(df)
    df = df.drop_duplicates(subset=["課程網址"], keep="first")
    print(f"去重前 {before} 筆，去重後 {len(df)} 筆")

    df = df.dropna(subset=["課程名稱", "課程網址"])

    out = pd.DataFrame()
    out["course_name"] = df["課程名稱"].astype(str)
    out["url"] = df["課程網址"].astype(str)
    out["primary_skill_name"] = df["主要技能名稱"].fillna("").astype(str)
    out["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    out["review_count"] = pd.to_numeric(df["review_count"], errors="coerce").astype("Int64")
    out["level"] = df["level"]
    out["course_type"] = df["course_type"]
    out["course_information"] = df["課程資訊"].fillna("").astype(str)
    out["duration_suggested"] = df["duration_suggested"]
    out["skills"] = df["skills"].apply(lambda x: x if isinstance(x, list) else [])
    out["source_platform"] = "Coursera"

    print("輸出筆數:", len(out))

    # skill_master 對照
    try:
        sm_resp = supabase.table("skill_master").select("skill_id, skill_name, synonyms").limit(5000).execute()
        sm_df = pd.DataFrame(sm_resp.data or [])
        name_to_skill_id = {}
        for _, row in sm_df.iterrows():
            sid = row["skill_id"]
            name = str(row["skill_name"]).strip()
            syn = row.get("synonyms")
            syn_list = []
            if syn is not None:
                if isinstance(syn, str):
                    try:
                        syn_list = json.loads(syn)
                    except Exception:
                        pass
                else:
                    syn_list = list(syn) if syn else []
            name_to_skill_id[name.lower()] = sid
            for s in syn_list:
                if s and str(s).strip():
                    name_to_skill_id[str(s).strip().lower()] = sid
        print(f"✅ skill_master 對照表 {len(name_to_skill_id)} 個名稱/同義詞")
    except Exception as e:
        print(f"⚠️ 無法讀取 skill_master（{e}），primary_skill_id 將為空")
        name_to_skill_id = {}

    rows = out.copy()
    rows["skills"] = rows["skills"].apply(lambda x: x if isinstance(x, list) else [])
    rows["primary_skill_id"] = (
        rows["primary_skill_name"].fillna("").astype(str).str.strip().str.lower().map(name_to_skill_id)
    )
    payload = rows.to_dict(orient="records")
    for r in payload:
        for k, v in r.items():
            if isinstance(v, (list, dict)):
                continue
            try:
                if pd.isna(v):
                    r[k] = None
            except (TypeError, ValueError):
                pass

    BATCH = 100
    for i in range(0, len(payload), BATCH):
        batch = payload[i : i + BATCH]
        try:
            supabase.table("course").upsert(batch, on_conflict="url").execute()
            print(f"Upsert 第 {i+1}～{min(i+BATCH, len(payload))} 筆")
        except Exception as e:
            print(f"批次 {i} 錯誤: {e}")
            raise

    print("寫入完成。（以 url 為唯一鍵，重跑會更新同 URL 的列）")
    resp = supabase.table("course").select("course_id, course_name, url, rating, review_count", count="exact").limit(5).execute()
    print("總筆數:", getattr(resp, "count", len(resp.data)))
    print(pd.DataFrame(resp.data))


if __name__ == "__main__":
    main()
