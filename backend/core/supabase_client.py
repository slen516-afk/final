import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def get_supabase_client() -> Client:
    """
    初始化並回傳 Supabase Service Role Client。
    """
    url: str = os.getenv("SUPABASE_URL", "")
    key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

    if not url or not key:
        raise ValueError("缺少 Supabase 環境變數：SUPABASE_URL 或 SUPABASE_SERVICE_ROLE_KEY")

    return create_client(url, key)

# 全域實例供使用
supabase: Client = get_supabase_client()
