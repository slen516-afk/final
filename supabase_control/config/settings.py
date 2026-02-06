import os
from pathlib import Path
from dotenv import load_dotenv

# 從專案根目錄 (supabase_control) 載入 .env
_root = Path(__file__).resolve().parent.parent
load_dotenv(_root / ".env")
# 若專案根沒有 .env，可嘗試 Erd/.env（與 qdrant.ipynb 一致）
if not os.getenv("QDRANT_URL") and (_root / "Erd" / ".env").exists():
    load_dotenv(_root / "Erd" / ".env")


class Settings:
    # Qdrant
    QDRANT_URL = (os.getenv("QDRANT_URL") or "").strip()
    QDRANT_API_KEY = (os.getenv("QDRANT_API_KEY") or "").strip()

    # OpenAI
    OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
    EMBEDDING_MODEL = "text-embedding-3-large"
    EMBEDDING_DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSIONS", 1536))

    # Supabase（支援 SUPABASE_KEY 或 SUPABASE_SERVICE_ROLE_KEY）
    SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").strip()
    SUPABASE_KEY = (
        (os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or "").strip()
    )

    # 批次處理
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", 100))
    MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", 8000))
    RATE_LIMIT_DELAY = float(os.getenv("RATE_LIMIT_DELAY", 0.1))
    # 只跑幾批後停止（1 = 只跑 100 筆就結束，0 = 不限制跑完全部）
    MAX_BATCHES = int(os.getenv("MAX_BATCHES", "1"))

    # Collection 名稱
    JOB_COLLECTION = "job_vectors"
    RESUME_COLLECTION = "resume_vectors"


settings = Settings()
