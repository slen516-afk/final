import os
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# 自動載入 .env 檔案
load_dotenv()

def get_qdrant_client() -> QdrantClient:
    """
    統一獲取 Qdrant Client 的連線實例。
    從環境變數讀取 QDRANT_URL 與 QDRANT_API_KEY。
    支援 Cloud 版 (需要 API Key) 與 Local Docker 版 (API Key 可為空)。
    """
    url = os.getenv("QDRANT_URL")
    api_key = os.getenv("QDRANT_API_KEY")
    
    if not url:
        raise ValueError("❌ 找不到 Qdrant 連線資訊。請確認 .env 檔案中的 QDRANT_URL 已設定。")
    
    # 建立連線實例
    try:
        client = QdrantClient(url=url, api_key=api_key)
        return client
    except Exception as e:
        print(f"❌ Qdrant 連線失敗: {e}")
        raise
