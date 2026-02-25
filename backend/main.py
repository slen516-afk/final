# 負責環境初始化、路徑設定，並作為專案唯一的啟動入口

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime


# ====== 1. 環境初始化 (路徑修正) ======
# 取得 backend 資料夾的絕對路徑
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# 取得專案根目錄並加入 supabase_control 路徑
project_root = backend_dir.parent
sys.path.insert(0, str(project_root / "supabase_control"))

# 後端環境變數應放置於 backend 資料夾下的 .env 檔案中
# 載入 .env 變數
load_dotenv(backend_dir / ".env")


# Supabase 連線測試
try:
    from core.supabase_client import supabase

    print("[System] 成功引入 Supabase Client")

except Exception as e:
    print(f"✗ [Database] Supabase 連線失敗: {e}")

# 建立 Flask App實例
# 修改為絕對路徑
current_dir = os.path.dirname(os.path.abspath(__file__))

# 將flask資料夾鎖定在sys.path中，確保不會因為其他同名模組而衝突
flask_folder_path = os.path.join(current_dir, "flask")

# 將flask資料夾加入sys.path，優先於其他路徑，確保正確引入Flask相關模組
sys.path.insert(0, flask_folder_path)
from app import create_app
app = create_app()



if __name__ == "__main__":
    # 啟動 Flask App
    print("=" * 60)
    print("Career Pilot API啟動中")
    print("=" * 60)
    app.run(debug=True)

"""   
    # 印出所有所有可用的路由資訊，便於debug和測試
    print(f"{'Endpoint':<30} | {'Methods':<15} | {'URL Rule'}")
    print("-" * 60)
    for rule in app.url_map.iter_rules():
        print(f"Endpoint: {rule.endpoint:25} Route: {rule}")
"""
"""
    # 資料庫連線測試
    try:
        # 連線到 Supabase
        supabase = connect_to_supabase()
        print("\n✓ Supabase 連線成功，可以使用 supabase 變數進行資料庫操作")

        # 範例：查詢公司資料
        result = supabase.table("company_info").select("*").limit(5).execute()
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
"""
