#!/usr/bin/env python3
"""
計算「清洗前」統計，供 PPT 第二章「資料清洗前後對比」使用。
用法：在 supabase_control 目錄下執行
  python scripts/ppt_cleaning_before_after_stats.py
或指定 CSV：
  python scripts/ppt_cleaning_before_after_stats.py --csv data/jobs_rows.csv
"""
import re
import argparse
from pathlib import Path

import pandas as pd


def has_salary_range(s: str) -> bool:
    """原始 salary 是否為「可比較區間」（非空且非僅面議，即可解析出數字）。"""
    if pd.isna(s) or not str(s).strip():
        return False
    s = str(s).strip()
    if "面議" in s or "面谈" in s:
        if re.search(r"\d", s):  # 面議但混有數字仍算可解析
            return True
        return False  # 純面議 → 清洗前視為「無區間」
    if re.search(r"[\d,]+[\s~～\-－至到][\d,]+", s):
        return True
    if re.search(r"月薪\s*[\d,]+", s):
        return True
    if re.search(r"\d+\s*元", re.sub(r"[,，\s]", "", s)):
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description="PPT 清洗前統計")
    parser.add_argument("--csv", default="data/jobs_rows.csv", help="原始 CSV 路徑")
    args = parser.parse_args()
    base = Path(__file__).resolve().parent.parent
    csv_path = base / args.csv
    if not csv_path.exists():
        print(f"找不到檔案: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    n = len(df)

    # 職缺筆數
    n_jobs_before = n

    # 薪資：有填 salary 比例、有「可比較薪資區間」比例（非純面議）
    has_salary_filled = df["salary"].notna() & (df["salary"].astype(str).str.strip().str.len() > 0)
    n_has_salary = has_salary_filled.sum()
    pct_has_salary = round(n_has_salary / n * 100, 1) if n else 0

    salary_range_ok = df["salary"].apply(has_salary_range)
    n_salary_range = salary_range_ok.sum()
    pct_salary_range = round(n_salary_range / n * 100, 1) if n else 0

    # 關鍵欄位空缺
    key_cols = ["job_description", "company_name", "job_name", "url", "location"]
    missing = {c: df[c].isna() | (df[c].astype(str).str.strip().str.len() == 0) for c in key_cols if c in df.columns}
    n_missing_jd = missing.get("job_description", pd.Series(False, index=df.index)).sum()
    n_missing_company = missing.get("company_name", pd.Series(False, index=df.index)).sum()
    n_missing_title = missing.get("job_name", pd.Series(False, index=df.index)).sum()
    pct_complete = round((~df["job_description"].isna() & (df["job_description"].astype(str).str.len() > 0)).sum() / n * 100, 1) if n else 0

    # 重複（與 notebook 一致）
    dup_all = df.duplicated().sum()
    dup_cnj = df.duplicated(subset=["company_name", "job_name"], keep="first").sum()
    has_url = df["url"].notna() & (df["url"].astype(str).str.len() > 0)
    dup_url = df.loc[has_url].duplicated(subset=["url", "job_name"], keep="first").sum()

    # 地點：有 location 比例
    has_location = df["location"].notna() & (df["location"].astype(str).str.strip().str.len() > 0)
    pct_has_location = round(has_location.sum() / n * 100, 1) if n else 0

    print("=" * 60)
    print("【PPT 第二章】清洗前統計（請填入「清洗前」欄位）")
    print("=" * 60)
    print()
    print("一、建議放上 PPT 的對比表數值（清洗前）")
    print("-" * 50)
    print(f"  職缺筆數（清洗前）           : {n_jobs_before:,}")
    print(f"  有薪資區間比例（清洗前）     : {pct_salary_range}%  （有明確數字區間，不含純「面議」）")
    print(f"  有填 salary 比例（清洗前）   : {pct_has_salary}%  （可選用於補充說明）")
    print(f"  有地點 location 比例（清洗前）: {pct_has_location}%")
    print(f"  有 job_description 比例（清洗前）: {100 - round(n_missing_jd/n*100, 1) if n else 0}%")
    print()
    print("二、重複與資料品質（可簡要口頭說明）")
    print("-" * 50)
    print(f"  完全重複筆數     : {dup_all:,}")
    print(f"  (公司名, 職缺名) 重複: {dup_cnj:,}")
    print(f"  (url, 職缺名) 重複 : {dup_url:,}")
    print()
    print("三、缺失筆數（關鍵欄位，可選放）")
    print("-" * 50)
    print(f"  job_description 空缺: {n_missing_jd:,}")
    print(f"  company_name 空缺  : {n_missing_company:,}")
    print(f"  job_name 空缺      : {n_missing_title:,}")
    print()
    print("請將上述「清洗前」數值與 clear.ipynb 跑完後的「清洗後」數值")
    print("一併填入 PPT 的「清洗前後對比」表格。")
    print("=" * 60)


if __name__ == "__main__":
    main()
