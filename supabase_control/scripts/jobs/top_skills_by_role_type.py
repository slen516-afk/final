"""
依「六大職類」彙總已貼標職缺的技能出現次數，產出每個職類 (role_type) 的前 6 項重要技能。

資料來源：Supabase
- job_posting（is_labeled=true, role_type 有值）
- job_skill_requirement（job_id, skill_id）
- skill_master（skill_id, skill_name）

產出：JSON（供前端/API）+ 可選 CSV。
使用方式：
  python top_skills_by_role_type.py
  python top_skills_by_role_type.py --no-export-csv
  python top_skills_by_role_type.py --top-n 10
"""

import os
import json
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
from supabase import create_client

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

DATA_DIR = PROJECT_ROOT / "data"
ROLE_NAME_MAPPING = {
    "A": "前端工程師",
    "B": "後端工程師",
    "C": "全端工程師",
    "D": "資料科學家/數據分析師",
    "E": "AI/演算法工程師",
    "F": "DevOps/SRE工程師",
}


def fetch_labeled_jobs(supabase_client):
    """已貼標且 role_type 不為空的職缺：job_id, role_type"""
    resp = (
        supabase_client.table("job_posting")
        .select("job_id, role_type")
        .eq("is_labeled", True)
        .not_.is_("role_type", "null")
        .execute()
    )
    return pd.DataFrame(resp.data or [])


def fetch_job_skills(supabase_client):
    """job_skill_requirement 全表（或可加 limit，依資料量調整）"""
    all_data = []
    offset = 0
    page_size = 5000
    while True:
        resp = (
            supabase_client.table("job_skill_requirement")
            .select("job_id, skill_id")
            .range(offset, offset + page_size - 1)
            .execute()
        )
        chunk = resp.data or []
        if not chunk:
            break
        all_data.extend(chunk)
        if len(chunk) < page_size:
            break
        offset += page_size
    return pd.DataFrame(all_data)


def fetch_skill_master(supabase_client):
    """skill_master: skill_id -> skill_name"""
    resp = supabase_client.table("skill_master").select("skill_id, skill_name").execute()
    return pd.DataFrame(resp.data or [])


def compute_top_skills_per_role(jobs_df, job_skills_df, skill_master_df, top_n=6):
    """
    依 role_type 彙總每個 skill_id 的職缺數，取每職類前 top_n 個技能。
    回傳格式：{ "A": [{"skill_id": 1, "skill_name": "Python", "job_count": 100}, ...], ... }
    """
    if jobs_df.empty or job_skills_df.empty:
        return {k: [] for k in ROLE_NAME_MAPPING}

    # job_posting 與 job_skill_requirement 以 job_id 合併，只保留有技能的已貼標職缺
    merged = job_skills_df.merge(jobs_df, on="job_id", how="inner")
    # 依 role_type, skill_id 計數（每筆代表一個職缺–技能對）
    agg = merged.groupby(["role_type", "skill_id"], as_index=False).size().rename(columns={"size": "job_count"})
    # 補上 skill_name
    agg = agg.merge(skill_master_df, on="skill_id", how="left")
    agg["skill_name"] = agg["skill_name"].fillna("(未知)")

    result = {}
    for role in ROLE_NAME_MAPPING:
        sub = agg[agg["role_type"] == role].sort_values("job_count", ascending=False).head(top_n)
        result[role] = sub[["skill_id", "skill_name", "job_count"]].to_dict("records")
    return result


def export_json(data, out_path):
    """寫入 JSON，含 role_name 方便前端顯示"""
    payload = {
        "role_type_top_skills": data,
        "role_names": ROLE_NAME_MAPPING,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON 已寫入：{out_path}")


def export_csv(data, out_path):
    """攤平為 CSV：role_type, role_name, rank, skill_id, skill_name, job_count"""
    rows = []
    for role_type, skills in data.items():
        role_name = ROLE_NAME_MAPPING.get(role_type, "")
        for rank, s in enumerate(skills, start=1):
            rows.append({
                "role_type": role_type,
                "role_name": role_name,
                "rank": rank,
                "skill_id": s["skill_id"],
                "skill_name": s["skill_name"],
                "job_count": s["job_count"],
            })
    pd.DataFrame(rows).to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"✅ CSV 已寫入：{out_path}")


def main(top_n=6, export_csv_flag=True):
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("讀取已貼標職缺...")
    jobs_df = fetch_labeled_jobs(supabase)
    print(f"  已貼標職缺數：{len(jobs_df)}")

    print("讀取職缺–技能關聯...")
    job_skills_df = fetch_job_skills(supabase)
    print(f"  job_skill_requirement 筆數：{len(job_skills_df)}")

    print("讀取技能主檔...")
    skill_master_df = fetch_skill_master(supabase)
    print(f"  skill_master 筆數：{len(skill_master_df)}")

    data = compute_top_skills_per_role(jobs_df, job_skills_df, skill_master_df, top_n=top_n)

    json_path = DATA_DIR / "role_type_top_skills.json"
    export_json(data, json_path)

    if export_csv_flag:
        csv_path = DATA_DIR / "role_type_top_skills.csv"
        export_csv(data, csv_path)

    print("\n各職類前 {} 項技能摘要：".format(top_n))
    for role_type, skills in data.items():
        names = [s["skill_name"] for s in skills]
        print(f"  {role_type} {ROLE_NAME_MAPPING.get(role_type, '')}: {names}")

    return data


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="依六大職類產出前 N 項重要技能（JSON + 可選 CSV）")
    parser.add_argument("--top-n", type=int, default=6, help="每個職類取前幾項技能（預設 6）")
    parser.add_argument("--no-export-csv", action="store_true", help="不產出 CSV，僅 JSON")
    args = parser.parse_args()
    main(top_n=args.top_n, export_csv_flag=not args.no_export_csv)
