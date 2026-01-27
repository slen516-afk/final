"""
Supabase 資料庫連線模組

這個模組提供連線到 Supabase 資料庫的函數，供所有組員使用。

使用方式:
    from supabase_connection import connect_to_supabase

    supabase = connect_to_supabase()
    result = supabase.table('company_info').select('*').limit(10).execute()
"""

import sys
import os
from dotenv import load_dotenv
from supabase import create_client, Client


def connect_to_supabase(env_path=None, test_connection=True):
    """
    連線到 Supabase 資料庫

    參數:
        env_path (str, optional): .env 檔案路徑。如果為 None，會依序嘗試：
            1. supabase_control/.env
            2. Erd/.env
            3. .env (當前目錄)
        test_connection (bool): 是否測試連線，預設為 True

    返回:
        Client: Supabase 客戶端物件

    範例:
        # 基本使用（自動尋找 .env）
        supabase = connect_to_supabase()

        # 指定 .env 路徑
        supabase = connect_to_supabase(env_path='path/to/.env')

        # 不測試連線（加快速度）
        supabase = connect_to_supabase(test_connection=False)

        # 使用連線
        result = supabase.table('company_info').select('*').limit(10).execute()

    異常:
        ValueError: 當無法從 .env 檔案讀取連線資訊時
        ConnectionError: 當 Supabase 連線失敗時
    """
    # 1. 清除模組快取中的 supabase（如果已導入，避免與本地 supabase.py 衝突）
    if 'supabase' in sys.modules:
        del sys.modules['supabase']

    # 2. 暫時重命名本地 supabase.py 以避免衝突
    current_dir = os.path.dirname(os.path.abspath(__file__))
    supabase_py_path = os.path.join(current_dir, 'supabase.py')
    supabase_bak_path = os.path.join(current_dir, 'supabase.py.bak')

    if os.path.exists(supabase_py_path) and not os.path.exists(supabase_bak_path):
        os.rename(supabase_py_path, supabase_bak_path)

    # 3. 載入環境變數
    if env_path is None:
        # 自動尋找 .env 檔案
        possible_paths = [
            os.path.join(current_dir, '.env'),  # supabase_control/.env
            os.path.join(current_dir, 'Erd', '.env'),  # supabase_control/Erd/.env
            '.env'  # 當前目錄
        ]

        env_path = None
        for path in possible_paths:
            if os.path.exists(path):
                env_path = path
                break

        if env_path is None:
            raise FileNotFoundError(
                "找不到 .env 檔案。請確認以下位置之一存在 .env 檔案：\n"
                f"  - {possible_paths[0]}\n"
                f"  - {possible_paths[1]}\n"
                f"  - {possible_paths[2]}"
            )

    load_dotenv(env_path)

    # 4. 取得 Supabase 連線資訊
    SUPABASE_URL = os.getenv('project_url')
    SUPABASE_KEY = os.getenv('service_role_key')

    # 也嘗試標準的環境變數名稱
    if not SUPABASE_URL:
        SUPABASE_URL = os.getenv('SUPABASE_URL')
    if not SUPABASE_KEY:
        SUPABASE_KEY = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(
            f"無法從 {env_path} 檔案讀取 Supabase 連線資訊\n"
            "請確認 .env 檔案包含以下任一組變數：\n"
            "  - project_url 和 service_role_key\n"
            "  - SUPABASE_URL 和 SUPABASE_KEY (或 SUPABASE_SERVICE_ROLE_KEY)"
        )

    # 5. 建立 Supabase 客戶端
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

        # 6. 測試連線（可選）
        if test_connection:
            test_result = supabase.table('company_info').select('company_id').limit(1).execute()
            print(f"✓ Supabase 連線成功！資料庫中現有 {len(test_result.data)} 筆公司資料（測試查詢）")
        else:
            print("✓ Supabase 連線成功！")

        return supabase

    except Exception as e:
        raise ConnectionError(
            f"Supabase 連線失敗: {str(e)}\n"
            "請檢查：\n"
            "1. SUPABASE_URL 是否正確\n"
            "2. SUPABASE_KEY 是否正確（必須是 service_role key）\n"
            "3. 網路連線是否正常\n"
            "4. 資料庫表是否已建立"
        ) from e


# 如果直接執行此檔案，進行測試
if __name__ == "__main__":
    print("=" * 60)
    print("測試 Supabase 連線函數")
    print("=" * 60)

    try:
        supabase = connect_to_supabase()
        print("\n✓ 函數測試成功！可以使用 supabase 變數進行資料庫操作")

        # 測試查詢
        result = supabase.table('company_info').select('company_id, company_name').limit(5).execute()
        print(f"\n✓ 測試查詢成功，取得 {len(result.data)} 筆資料")

    except Exception as e:
        print(f"\n✗ 函數測試失敗: {e}")
