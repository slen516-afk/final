"""
Backend 主程式

從 supabase_control 導入 Supabase 連線函數
"""

import sys
from pathlib import Path

# 將 supabase_control 目錄加入 Python 路徑，以便導入其中的模組
project_root = Path(__file__).parent.parent
supabase_control_path = str(project_root / 'supabase_control')
if supabase_control_path not in sys.path:
    sys.path.insert(0, supabase_control_path)

# 現在可以導入 supabase_control 中的函數
from supabase_connection import connect_to_supabase

# 使用範例
if __name__ == "__main__":
    print("=" * 60)
    print("Backend 服務啟動")
    print("=" * 60)
    
    try:
        # 連線到 Supabase
        supabase = connect_to_supabase()
        print("\n✓ Supabase 連線成功，可以使用 supabase 變數進行資料庫操作")
        
        # 範例：查詢公司資料
        result = supabase.table('company_info').select('*').limit(5).execute()
        print(f"\n✓ 查詢成功，取得 {len(result.data)} 筆資料\n")
        
        # 顯示資料內容
        if result.data:
            print("【資料庫內容】")
            print("-" * 60)
            for idx, company in enumerate(result.data, 1):
                print(f"\n第 {idx} 筆公司資料：")
                print(f"  company_id: {company.get('company_id')}")
                print(f"  company_name: {company.get('company_name')}")
                print(f"  industry: {company.get('industry')}")
                print(f"  company_size: {company.get('company_size')}")
                print(f"  location: {company.get('location')}")
                print(f"  website: {company.get('website')}")
                print(f"  created_at: {company.get('created_at')}")
        else:
            print("⚠️  資料庫中目前沒有公司資料")
        
    except Exception as e:
        print(f"\n✗ 連線失敗: {e}")
