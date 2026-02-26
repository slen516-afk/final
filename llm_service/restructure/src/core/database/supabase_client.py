import os
from supabase import create_client, Client
from dotenv import load_dotenv

# 自動載入 .env 檔案
load_dotenv()

def get_supabase_client() -> Client:
    """
    統一獲取 Supabase Client 的連線實例。
    從環境變數讀取 SUPABASE_URL 與 SUPABASE_SERVICE_ROLE_KEY (或 SUPABASE_KEY)。
    優先使用 Service Role Key 以獲得更高的操作權限（例如寫入權限）。
    """
    url = os.getenv("SUPABASE_URL")
    # 優先選擇 Service Role Key，若無則回退至 Anon Key
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("❌ 找不到 Supabase 連線資訊。請確認 .env 檔案中的 SUPABASE_URL 與 SUPABASE_SERVICE_ROLE_KEY 已設定。")
    
    try:
        # 初始化連線
        client = create_client(url, key)
        return client
    except Exception as e:
        print(f"❌ Supabase 連線失敗: {e}")
        raise

def get_next_version_number(user_id: str) -> str:
    """
    從資料庫獲取使用者目前的報告總量，並返回下一個版本號 (例如: "1.0", "2.0")。
    """
    try:
        client = get_supabase_client()
        # 假設報告存放在 'user_skill' 表
        # 使用 count="exact" 來獲取精確數量
        resp = (
            client
            .table("user_skill")
            .select("user_id", count="exact")
            .eq("user_id", user_id)
            .execute()
        )
        
        # 獲取總數，若為 None 則預設為 0
        count = resp.count if resp.count is not None else 0
        
        # 返回下一版 (例如: "1.0", "2.0", ...)
        return f"{float(count + 1)}"
        
    except Exception as e:
        print(f"⚠️ 獲取報告版本號失敗，預設回傳 1.0: {e}")
        return "1.0"
