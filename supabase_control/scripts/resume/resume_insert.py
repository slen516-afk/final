"""
履歷資料寫入 Supabase。
從 resume.csv 讀取測試履歷，使用 supabase_connection 連線，寫入 resume 表。
執行條件：工作目錄或專案根為 supabase_control；resume.csv 在 data/ 或專案根；USER 表需有 user_id 1～10；resume_template 表需有 template_id 1。
"""

import sys
import json
from pathlib import Path

import pandas as pd

# 專案根目錄 = supabase_control
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from supabase_connection import connect_to_supabase


def to_bool(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return False
    if isinstance(v, bool):
        return v
    return str(v).strip().upper() == "TRUE"


def row_to_payload(row):
    """將 CSV 一列轉成 resume 表所需格式"""
    structured = row["structured_data"]
    normalized = row["normalized_data"]
    if isinstance(structured, str):
        try:
            structured = json.loads(structured)
        except json.JSONDecodeError:
            structured = None
    if isinstance(normalized, str):
        try:
            normalized = json.loads(normalized)
        except json.JSONDecodeError:
            normalized = None

    vid = row.get("vector_id")
    if pd.isna(vid) or (isinstance(vid, str) and not vid.strip()):
        vid = None
    else:
        vid = str(vid).strip()

    return {
        "resume_id": int(row["resume_id"]),
        "user_id": int(row["user_id"]),
        "template_id": int(row["template_id"]),
        "resume_type": str(row["resume_type"]),
        "structured_data": structured,
        "normalized_data": normalized,
        "vector_id": vid,
        "is_embedded": to_bool(row.get("is_embedded")),
        "is_primary": to_bool(row.get("is_primary")),
        "created_at": str(row["created_at"]) if pd.notna(row.get("created_at")) else None,
        "updated_at": str(row["updated_at"]) if pd.notna(row.get("updated_at")) else None,
    }


def main():
    supabase = connect_to_supabase()

    csv_path = PROJECT_ROOT / "data" / "resume.csv"
    if not csv_path.exists():
        csv_path = PROJECT_ROOT / "resume.csv"
    if not csv_path.exists():
        csv_path = Path.cwd() / "resume.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"找不到 resume.csv，請放在 {PROJECT_ROOT / 'data'} 或專案根或當前目錄")

    df = pd.read_csv(csv_path)
    df = df.dropna(how="all")
    print(f"✓ 載入 {len(df)} 筆履歷資料")

    rows = [row_to_payload(r) for _, r in df.iterrows()]
    print(f"✓ 轉換 {len(rows)} 筆 payload")

    success = 0
    failed = 0
    for r in rows:
        try:
            res = supabase.table("resume").upsert(
                r, on_conflict="resume_id", ignore_duplicates=False
            ).execute()
            if res.data:
                success += len(res.data)
            else:
                success += 1
        except Exception as e:
            print(f"❌ resume_id={r['resume_id']}: {e}")
            failed += 1

    print("--- 寫入結果 ---")
    print(f"✓ 成功: {success} 筆")
    print(f"❌ 失敗: {failed} 筆")

    verify = (
        supabase.table("resume")
        .select("resume_id, user_id, resume_type", count="exact")
        .limit(20)
        .execute()
    )
    total = getattr(verify, "count", None) or len(verify.data)
    print(f"📊 資料庫 resume 表總數: {total} 筆")
    print(pd.DataFrame(verify.data))


if __name__ == "__main__":
    main()
