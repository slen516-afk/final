#!/usr/bin/env python3
"""
匯出「原始 CSV 醜樣子」樣本，供 PPT 清洗前後對比截圖用。
輸出：data/ppt_raw_sample.csv（UTF-8 BOM，Excel 可正確開啟）
用法：在 supabase_control 下執行  python scripts/ppt_export_raw_sample.py
"""
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
RAW_CSV = BASE / "data" / "jobs_rows.csv"
OUT_CSV = BASE / "data" / "ppt_raw_sample.csv"

# 只取最能表現「醜」的欄位：空缺、面議、地點寫法不一、描述過長
COLS = ["job_name", "company_name", "company_url", "salary", "location", "job_description"]
MAX_ROWS = 6
DESC_MAX = 55  # 字元數，讓表格不會太寬，截圖時一屏能看完

def main():
    if not RAW_CSV.exists():
        print(f"找不到 {RAW_CSV}")
        return
    df = pd.read_csv(RAW_CSV, nrows=MAX_ROWS)
    # 只保留要展示的欄位
    sub = df[COLS].copy()
    # 空缺顯示為 (空)，方便截圖時一眼看出
    sub["company_url"] = sub["company_url"].fillna("(空)")
    sub["job_description"] = (
        sub["job_description"]
        .fillna("(空)")
        .astype(str)
        .str.replace("\r\n", " ", regex=False)
        .str.replace("\n", " ", regex=False)
    )
    # 描述過長就截斷，表現「長短不一、難直接用的感覺」
    def truncate(s):
        s = str(s).strip()
        if len(s) <= DESC_MAX:
            return s
        return s[:DESC_MAX] + "…"
    sub["job_description"] = sub["job_description"].apply(truncate)
    # 寫出 UTF-8 BOM，Excel 開才不會亂碼
    sub.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    print(f"已寫入 {OUT_CSV}")
    print("建議：用 Excel 開啟 → 調整欄寬、凍結首列 → 截圖「前幾筆」放 PPT 左側當「清洗前」。")

if __name__ == "__main__":
    main()
