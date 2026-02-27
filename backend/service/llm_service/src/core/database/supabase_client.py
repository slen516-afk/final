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
        # 使用 count="exact" 來獲取精確數量
        resp = (
            client
            .table("career_analysis_report")
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

def get_latest_resume(user_id: str) -> str:
    """
    根據 user_id 獲取最新的履歷內容 (JSON 格式字串)。
    """
    try:
        client = get_supabase_client()
        # 查詢 resume 表，按時間降序排列，取第 1 筆
        response = (
            client
            .table("resume") \
          .select("structured_data") \
          .eq("user_id", user_id) \
          .order("created_at", desc=True) \
          .limit(1) \
          .single() \
          .execute()
        )
        
        if not response.data:
            return "❌ 找不到該使用者的履歷紀錄。"
        
        # 確保回傳的是 JSON 格式字串 (若資料庫存的是物件)
        import json
        resume_data = response.data.get("structured_data")
        if isinstance(resume_data, dict):
            return json.dumps(resume_data, ensure_ascii=False)
        return str(resume_data)
        
    except Exception as e:
        return f"❌ 獲取履歷失敗: {str(e)}"
