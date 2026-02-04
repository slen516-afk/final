# Career Pilot 向量化作業手冊

> **版本**: v1.0  
> **更新日期**: 2026-02-04  
> **適用對象**: 資料工程團隊  
> **前置條件**: Qdrant Collections 已建立完成

---

## 📋 目錄

1. [作業流程總覽](#作業流程總覽)
2. [環境準備](#環境準備)
3. [資料庫欄位對應關係](#資料庫欄位對應關係)
4. [批次向量化腳本](#批次向量化腳本)
5. [驗證與監控](#驗證與監控)
6. [錯誤處理與復原](#錯誤處理與復原)
7. [FAQ](#faq)

---

## 作業流程總覽

### 整體架構圖

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: 資料提取 (Supabase PostgreSQL)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ SELECT job_id, job_description, requirements,        │   │
│  │        job_title, city, district, remote_option,     │   │
│  │        salary_min, salary_max                        │   │
│  │ FROM job_posting                                     │   │
│  │ WHERE is_embedded = FALSE                            │   │
│  │ LIMIT 100 OFFSET ?                                   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 2: 文本處理與向量化 (OpenAI API)                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 1. 合併文本: job_title + job_description +          │   │
│  │             requirements                             │   │
│  │ 2. 截斷: 保留前 8000 字元 (避免 token 超限)         │   │
│  │ 3. 調用 API: text-embedding-3-large (1536 維)       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 3: 向量存儲 (Qdrant Cloud)                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ PointStruct(                                         │   │
│  │   id = UUID (新生成),                                │   │
│  │   vector = [1536 維浮點數陣列],                      │   │
│  │   payload = {                                        │   │
│  │     "job_id": 123,                                   │   │
│  │     "job_title": "...",                              │   │
│  │     "city": "台北市",        # ← 硬篩選條件          │   │
│  │     "district": "信義區",    # ← 硬篩選條件          │   │
│  │     "remote_option": "hybrid", # ← 硬篩選條件       │   │
│  │     "salary_min": 60000,     # ← 硬篩選條件          │   │
│  │     "salary_max": 90000      # ← 硬篩選條件          │   │
│  │   }                                                  │   │
│  │ )                                                    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 4: 回寫關聯資訊 (Supabase PostgreSQL)                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ UPDATE job_posting                                   │   │
│  │ SET vector_id = 'uuid-string',                       │   │
│  │     is_embedded = TRUE                               │   │
│  │ WHERE job_id = 123                                   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 資料流向說明

| 階段 | 資料來源 | 資料去向 | 關鍵欄位 |
|------|---------|---------|---------|
| **提取** | Supabase `job_posting` | 記憶體 | `job_id`, `job_description`, `requirements`, `salary_min`, `salary_max` |
| **向量化** | 記憶體文本 | OpenAI API | 合併後的文本字串 |
| **存儲** | OpenAI 回傳向量 | Qdrant `job_vectors` | `vector` (1536 維), `payload` (含薪資範圍) |
| **回寫** | Qdrant `point.id` | Supabase `job_posting.vector_id` | UUID 字串 + `is_embedded=TRUE` |

---

## 環境準備

### Step 1: 安裝 Python 套件

```bash
pip install qdrant-client==1.7.0 \
            openai==1.10.0 \
            supabase==2.3.0 \
            python-dotenv==1.0.0 \
            tqdm==4.66.0
```

### Step 2: 建立專案結構

```
career_pilot/
├── .env                      # 環境變數 (絕對不要上傳 Git)
├── .gitignore               # Git 忽略清單
├── config/
│   └── settings.py          # 配置管理
├── scripts/
│   ├── setup_qdrant.py      # Collection 初始化 (已完成)
│   ├── vectorize_jobs.py    # 職缺向量化主程式
│   ├── vectorize_resumes.py # 履歷向量化主程式 (未來)
│   └── verify_sync.py       # 同步驗證工具
└── logs/
    └── vectorization.log    # 執行日誌
```

### Step 3: 建立 `.gitignore`

```gitignore
# 環境變數
.env
.env.*

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# 日誌
logs/*.log

# IDE
.vscode/
.idea/
*.swp
*.swo
```

### Step 4: 配置環境變數 (`.env`)

```env
# ============ Qdrant Cloud ============
QDRANT_URL=https://0c6a8a5c-e773-4580-b02f-bd914b109ca3.us-east4-0.gcp.cloud.qdrant.io
QDRANT_API_KEY=你的完整API_Key

# ============ OpenAI ============
OPENAI_API_KEY=sk-proj-你的Key

# ============ Supabase ============
SUPABASE_URL=https://你的專案.supabase.co
SUPABASE_KEY=你的Service_Role_Key

# ============ 批次處理參數 ============
BATCH_SIZE=100                # 每批處理筆數
MAX_TEXT_LENGTH=8000          # 文本截斷長度
EMBEDDING_DIMENSIONS=1536     # 向量維度
RATE_LIMIT_DELAY=0.1          # API 調用間隔 (秒)
```

### Step 5: 建立配置管理 (`config/settings.py`)

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Qdrant
    QDRANT_URL = os.getenv("QDRANT_URL")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    EMBEDDING_MODEL = "text-embedding-3-large"
    EMBEDDING_DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSIONS", 1536))
    
    # Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # 批次處理
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", 100))
    MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", 8000))
    RATE_LIMIT_DELAY = float(os.getenv("RATE_LIMIT_DELAY", 0.1))
    
    # Collection 名稱
    JOB_COLLECTION = "job_vectors"
    RESUME_COLLECTION = "resume_vectors"

settings = Settings()
```

---

## 資料庫欄位對應關係

### Supabase `job_posting` 表結構（與 ERD 對應）

根據 **ERD 5.2 JOB_POSTING** 設計：

| 欄位名稱 | 資料型態 | 說明 | 向量化階段用途 |
|---------|---------|------|--------------|
| `job_id` | INT (PK) | 職缺識別碼 | **關聯鍵**：寫入 Qdrant Payload |
| `job_title` | VARCHAR(200) | 職位名稱 | **向量化來源** + Payload |
| `job_description` | TEXT | 職缺描述 | **向量化來源**（主要） |
| `requirements` | TEXT | 職缺要求 | **向量化來源**（主要） |
| `city` | VARCHAR(50) | 城市 | **硬篩選條件**：寫入 Payload |
| `district` | VARCHAR(50) | 行政區 | **硬篩選條件**：寫入 Payload |
| `remote_option` | VARCHAR(50) | 遠端選項 | **硬篩選條件**：寫入 Payload |
| `salary_min` | INT | 最低薪資 | **硬篩選條件**：寫入 Payload |
| `salary_max` | INT | 最高薪資 | **硬篩選條件**：寫入 Payload |
| `vector_id` | UUID | Qdrant Point ID | **回寫目標**：向量化完成後填入 |
| `is_embedded` | BOOLEAN | 是否已向量化 | **狀態標記**：完成後設為 TRUE |

### Qdrant `job_vectors` Collection 結構

```python
# Point 結構設計
{
    "id": "550e8400-e29b-41d4-a716-446655440000",  # UUID 字串
    "vector": [0.123, -0.456, ...],  # 1536 維浮點數陣列
    "payload": {
        # ========== 必要欄位（關聯鍵） ==========
        "job_id": 123,  # INT - 對應 Supabase 主鍵
        
        # ========== 顯示欄位 ==========
        "job_title": "Python 後端工程師",  # VARCHAR(200)
        
        # ========== 硬篩選條件 ==========
        "city": "台北市",           # VARCHAR(50) - 可為 NULL
        "district": "信義區",        # VARCHAR(50) - 可為 NULL
        "remote_option": "hybrid",  # VARCHAR(50) - 可為 NULL
        "salary_min": 60000,        # INT - 可為 NULL
        "salary_max": 90000         # INT - 可為 NULL
    }
}
```

### 硬篩選邏輯說明（含薪資範圍）

使用者搜尋時可指定以下條件：

| 篩選條件 | Payload 欄位 | 篩選邏輯 | 範例 |
|---------|------------|---------|------|
| **期望地區** | `city` | 完全匹配 | 只顯示「台北市」的職缺 |
| **行政區** | `district` | 完全匹配 | 只顯示「信義區」的職缺 |
| **遠端工作** | `remote_option` | 完全匹配 | 只顯示「hybrid」或「remote」 |
| **期望薪資** | `salary_min`, `salary_max` | **範圍交集** | 使用者期望 70K，篩選出薪資範圍涵蓋 70K 的職缺 |

#### 薪資範圍篩選邏輯（重要！）

假設使用者期望薪資為 **70,000 元**：

```python
# 篩選條件：職缺的薪資範圍必須「包含」使用者期望
# 邏輯：salary_min <= 70000 <= salary_max

Filter(
    must=[
        FieldCondition(
            key="salary_min",
            range=RangeCondition(lte=70000)  # 最低薪資 <= 70K
        ),
        FieldCondition(
            key="salary_max",
            range=RangeCondition(gte=70000)  # 最高薪資 >= 70K
        )
    ]
)
```

**範例說明**：

| 職缺 | salary_min | salary_max | 是否符合（期望 70K） | 原因 |
|------|-----------|-----------|-------------------|------|
| A | 60,000 | 80,000 | ✅ 符合 | 60K ≤ 70K ≤ 80K |
| B | 50,000 | 65,000 | ❌ 不符合 | 65K < 70K（薪資上限過低） |
| C | 75,000 | 100,000 | ❌ 不符合 | 75K > 70K（薪資下限過高） |
| D | NULL | NULL | ⚠️ 不篩選 | 薪資未公開，保留在結果中 |

### 資料完整性約束

根據 ERD 設計，以下欄位允許 `NULL`：

| 欄位 | NULL 處理策略 |
|------|--------------|
| `job_description` | 若為 NULL，使用空字串 `""` |
| `requirements` | 若為 NULL，使用空字串 `""` |
| `city` | 保持 NULL，Payload 存為 `None` |
| `district` | 保持 NULL，Payload 存為 `None` |
| `remote_option` | 保持 NULL，Payload 存為 `None` |
| `salary_min` | 保持 NULL，Payload 存為 `None` |
| `salary_max` | 保持 NULL，Payload 存為 `None` |

**關鍵原則**：
- **向量化來源欄位**（`job_description`, `requirements`）不能全為空，否則跳過
- **硬篩選欄位**（`city`, `district`, `remote_option`, `salary_min`, `salary_max`）允許 NULL，搜尋時不過濾

---

## 批次向量化腳本

### 主程式 (`scripts/vectorize_jobs.py`)

```python
"""
Career Pilot 職缺向量化主程式
功能：
1. 從 Supabase 批次提取未向量化職缺
2. 調用 OpenAI API 進行向量化
3. 寫入 Qdrant 並回寫 vector_id 到 Supabase
"""

import sys
import time
import uuid
import logging
from typing import List, Dict, Optional
from datetime import datetime

from openai import OpenAI
from supabase import create_client, Client
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from tqdm import tqdm

# 載入配置
sys.path.append('..')
from config.settings import settings

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../logs/vectorization.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============ 初始化客戶端 ============
openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
qdrant_client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY
)

# ============ 核心函數 ============

def get_embedding(text: str) -> List[float]:
    """
    調用 OpenAI Embedding API
    
    Args:
        text: 待向量化的文本
        
    Returns:
        1536 維向量陣列
        
    Raises:
        Exception: API 調用失敗
    """
    try:
        response = openai_client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=text,
            dimensions=settings.EMBEDDING_DIMENSIONS
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"❌ Embedding API 失敗: {e}")
        raise


def prepare_job_text(job: Dict) -> str:
    """
    準備職缺文本（符合 ERD 設計）
    
    Args:
        job: Supabase 查詢結果（單筆職缺）
        
    Returns:
        合併後的文本字串
    """
    # 處理可能為 NULL 的欄位
    title = job.get('job_title') or ""
    description = job.get('job_description') or ""
    requirements = job.get('requirements') or ""
    
    # 合併文本
    combined_text = f"{title}\n{description}\n{requirements}"
    
    # 截斷（避免 token 超限）
    if len(combined_text) > settings.MAX_TEXT_LENGTH:
        combined_text = combined_text[:settings.MAX_TEXT_LENGTH]
        logger.warning(f"⚠️  job_id {job['job_id']} 文本過長，已截斷至 {settings.MAX_TEXT_LENGTH} 字元")
    
    return combined_text.strip()


def prepare_payload(job: Dict) -> Dict:
    """
    準備 Qdrant Payload（符合 ERD 設計，含薪資範圍）
    
    Args:
        job: Supabase 查詢結果（單筆職缺）
        
    Returns:
        Payload 字典
    """
    return {
        "job_id": job['job_id'],
        "job_title": job.get('job_title'),
        "city": job.get('city'),                    # 可為 None
        "district": job.get('district'),            # 可為 None
        "remote_option": job.get('remote_option'),  # 可為 None
        "salary_min": job.get('salary_min'),        # 可為 None (新增)
        "salary_max": job.get('salary_max')         # 可為 None (新增)
    }


def vectorize_batch(offset: int, limit: int = None) -> int:
    """
    處理單一批次
    
    Args:
        offset: 起始位置
        limit: 批次大小（預設使用 settings.BATCH_SIZE）
        
    Returns:
        成功處理的筆數
    """
    if limit is None:
        limit = settings.BATCH_SIZE
    
    # ========== Step 1: 從 Supabase 提取資料 ==========
    try:
        response = supabase.table("job_posting") \
            .select("job_id, job_title, job_description, requirements, city, district, remote_option, salary_min, salary_max") \
            .eq("is_embedded", False) \
            .range(offset, offset + limit - 1) \
            .execute()
        
        jobs = response.data
        if not jobs:
            return 0
            
    except Exception as e:
        logger.error(f"❌ Supabase 查詢失敗 (offset={offset}): {e}")
        return 0
    
    # ========== Step 2: 批次向量化與準備 Points ==========
    points = []
    update_records = []
    
    for job in jobs:
        job_id = job['job_id']
        
        try:
            # 準備文本
            text = prepare_job_text(job)
            if not text:
                logger.warning(f"⚠️  job_id {job_id}: 文本為空，跳過")
                continue
            
            # 向量化
            vector = get_embedding(text)
            vector_id = str(uuid.uuid4())
            
            # 準備 Qdrant Point
            points.append(PointStruct(
                id=vector_id,
                vector=vector,
                payload=prepare_payload(job)
            ))
            
            # 準備 Supabase 更新記錄
            update_records.append({
                "job_id": job_id,
                "vector_id": vector_id
            })
            
            # 速率限制
            time.sleep(settings.RATE_LIMIT_DELAY)
            
        except Exception as e:
            logger.error(f"❌ job_id {job_id} 處理失敗: {e}")
            continue
    
    # ========== Step 3: 批次寫入 Qdrant ==========
    if points:
        try:
            qdrant_client.upsert(
                collection_name=settings.JOB_COLLECTION,
                points=points
            )
            logger.info(f"✅ Qdrant 寫入 {len(points)} 筆")
        except Exception as e:
            logger.error(f"❌ Qdrant 批次寫入失敗: {e}")
            return 0
    
    # ========== Step 4: 批次更新 Supabase ==========
    success_count = 0
    for record in update_records:
        try:
            supabase.table("job_posting") \
                .update({
                    "vector_id": record["vector_id"],
                    "is_embedded": True
                }) \
                .eq("job_id", record["job_id"]) \
                .execute()
            success_count += 1
        except Exception as e:
            logger.error(f"❌ job_id {record['job_id']} 回寫失敗: {e}")
    
    logger.info(f"✅ Supabase 更新 {success_count}/{len(update_records)} 筆")
    return success_count


def main():
    """主流程"""
    logger.info("=" * 60)
    logger.info("Career Pilot 職缺向量化作業")
    logger.info(f"執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    # ========== 計算待處理總數 ==========
    try:
        count_response = supabase.table("job_posting") \
            .select("job_id", count="exact") \
            .eq("is_embedded", False) \
            .execute()
        total_jobs = count_response.count
    except Exception as e:
        logger.error(f"❌ 無法取得待處理筆數: {e}")
        return
    
    if total_jobs == 0:
        logger.info("✅ 所有職缺已完成向量化")
        return
    
    logger.info(f"📊 待處理職缺總數: {total_jobs}")
    logger.info(f"⚙️  批次大小: {settings.BATCH_SIZE}")
    
    # 估算成本
    estimated_cost = (total_jobs * 600 * 0.13) / 1_000_000  # 假設平均 600 tokens
    logger.info(f"💰 預估成本: ${estimated_cost:.2f} USD")
    
    # 使用者確認
    confirm = input("\n是否繼續執行？(y/n): ")
    if confirm.lower() != 'y':
        logger.info("❌ 使用者取消作業")
        return
    
    # ========== 批次處理迴圈 ==========
    total_processed = 0
    offset = 0
    
    with tqdm(total=total_jobs, desc="向量化進度") as pbar:
        while total_processed < total_jobs:
            processed = vectorize_batch(offset, settings.BATCH_SIZE)
            
            if processed == 0:
                logger.warning(f"⚠️  offset {offset} 處理失敗，嘗試跳過...")
                offset += settings.BATCH_SIZE
                continue
            
            total_processed += processed
            offset += settings.BATCH_SIZE
            pbar.update(processed)
            
            logger.info(f"📈 進度: {total_processed}/{total_jobs} ({total_processed/total_jobs*100:.1f}%)")
    
    # ========== 完成報告 ==========
    logger.info("=" * 60)
    logger.info(f"🎉 向量化作業完成！")
    logger.info(f"✅ 成功處理: {total_processed} 筆")
    logger.info(f"❌ 失敗/跳過: {total_jobs - total_processed} 筆")
    logger.info("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("\n⚠️  使用者中斷作業")
    except Exception as e:
        logger.error(f"❌ 未預期錯誤: {e}", exc_info=True)
```

---

## 驗證與監控

### 驗證腳本 (`scripts/verify_sync.py`)

```python
"""
驗證 Supabase 與 Qdrant 同步狀態
"""

import sys
from supabase import create_client
from qdrant_client import QdrantClient

sys.path.append('..')
from config.settings import settings

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
qdrant = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)

print("=" * 60)
print("Supabase ↔ Qdrant 同步驗證")
print("=" * 60)

# ========== 1. 統計資料 ==========
# Supabase 統計
supabase_total = supabase.table("job_posting").select("job_id", count="exact").execute().count
supabase_embedded = supabase.table("job_posting").select("job_id", count="exact").eq("is_embedded", True).execute().count

# Qdrant 統計
qdrant_info = qdrant.get_collection(settings.JOB_COLLECTION)

print(f"\n📊 資料統計:")
print(f"  Supabase 總職缺數: {supabase_total}")
print(f"  Supabase 已向量化: {supabase_embedded} ({supabase_embedded/supabase_total*100:.1f}%)")
print(f"  Qdrant 向量總數:   {qdrant_info.points_count}")

# ========== 2. 一致性檢查 ==========
if supabase_embedded != qdrant_info.points_count:
    print(f"\n⚠️  警告：資料不一致！")
    print(f"  差異: {abs(supabase_embedded - qdrant_info.points_count)} 筆")
else:
    print(f"\n✅ 資料一致")

# ========== 3. 抽查驗證（含薪資欄位） ==========
print(f"\n🔍 抽查驗證 (隨機 5 筆):")
samples = supabase.table("job_posting") \
    .select("job_id, vector_id, job_title, salary_min, salary_max") \
    .eq("is_embedded", True) \
    .limit(5) \
    .execute()

for i, sample in enumerate(samples.data, 1):
    try:
        # 檢查 Qdrant 是否存在對應 Point
        point = qdrant.retrieve(
            collection_name=settings.JOB_COLLECTION,
            ids=[sample["vector_id"]]
        )
        
        if point:
            payload = point[0].payload
            payload_job_id = payload.get("job_id")
            payload_salary = f"{payload.get('salary_min', 'N/A')} - {payload.get('salary_max', 'N/A')}"
            
            match = "✅" if payload_job_id == sample["job_id"] else "❌"
            print(f"  {i}. job_id={sample['job_id']} | vector_id={sample['vector_id'][:8]}... | 薪資: {payload_salary} {match}")
        else:
            print(f"  {i}. job_id={sample['job_id']} ❌ Qdrant 找不到對應 Point")
            
    except Exception as e:
        print(f"  {i}. job_id={sample['job_id']} ❌ 錯誤: {e}")

print("=" * 60)
```

### 執行驗證

```bash
cd scripts
python verify_sync.py
```

**預期輸出**：
```
============================================================
Supabase ↔ Qdrant 同步驗證
============================================================

📊 資料統計:
  Supabase 總職缺數: 8000
  Supabase 已向量化: 8000 (100.0%)
  Qdrant 向量總數:   8000

✅ 資料一致

🔍 抽查驗證 (隨機 5 筆):
  1. job_id=123 | vector_id=550e8400... | 薪資: 60000 - 90000 ✅
  2. job_id=456 | vector_id=7c9e6679... | 薪資: 50000 - 80000 ✅
  3. job_id=789 | vector_id=3b241101... | 薪資: N/A - N/A ✅
  4. job_id=1012 | vector_id=d9428888... | 薪資: 70000 - 100000 ✅
  5. job_id=1345 | vector_id=fd6f14f8... | 薪資: 55000 - 75000 ✅
============================================================
```

---

## 搜尋 API 範例（含薪資篩選）

### Flask 路由實作 (`app.py`)

```python
from flask import Flask, request, jsonify
from openai import OpenAI
from supabase import create_client
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, Range

from config.settings import settings

app = Flask(__name__)

# 初始化
openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
qdrant = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)

def get_embedding(text: str):
    return openai_client.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=text,
        dimensions=settings.EMBEDDING_DIMENSIONS
    ).data[0].embedding


@app.route('/search_jobs', methods=['POST'])
def search_jobs():
    """
    職缺搜尋 API（含薪資範圍篩選）
    
    Request Body:
    {
        "resume_text": "Python 後端工程師 5 年經驗",
        "city": "台北市",           # 可選
        "remote_option": "hybrid",  # 可選
        "expected_salary": 70000    # 可選（期望薪資）
    }
    """
    data = request.json
    resume_text = data.get('resume_text')
    city = data.get('city')
    remote_option = data.get('remote_option')
    expected_salary = data.get('expected_salary')  # 新增
    
    # 1. 向量化履歷
    resume_vector = get_embedding(resume_text)
    
    # 2. 建立過濾條件
    filters = []
    
    if city:
        filters.append(FieldCondition(
            key="city",
            match=MatchValue(value=city)
        ))
    
    if remote_option:
        filters.append(FieldCondition(
            key="remote_option",
            match=MatchValue(value=remote_option)
        ))
    
    # 薪資範圍篩選（新增）
    if expected_salary:
        filters.append(FieldCondition(
            key="salary_min",
            range=Range(lte=expected_salary)  # 最低薪資 <= 期望
        ))
        filters.append(FieldCondition(
            key="salary_max",
            range=Range(gte=expected_salary)  # 最高薪資 >= 期望
        ))
    
    query_filter = Filter(must=filters) if filters else None
    
    # 3. 向量搜尋
    results = qdrant.search(
        collection_name=settings.JOB_COLLECTION,
        query_vector=resume_vector,
        query_filter=query_filter,
        limit=10
    )
    
    # 4. 提取 job_id 並從 Supabase 取得完整資料
    job_ids = [hit.payload["job_id"] for hit in results]
    jobs = supabase.table("job_posting") \
        .select("*, company_info(company_name)") \
        .in_("job_id", job_ids) \
        .execute()
    
    return jsonify({
        "total": len(jobs.data),
        "jobs": jobs.data
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

### 測試搜尋（含薪資篩選）

```bash
curl -X POST http://localhost:5000/search_jobs \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Python 後端工程師 5 年經驗 熟悉 Django FastAPI",
    "city": "台北市",
    "remote_option": "hybrid",
    "expected_salary": 70000
  }'
```

**預期回應**：
```json
{
  "total": 8,
  "jobs": [
    {
      "job_id": 123,
      "job_title": "Senior Python Backend Engineer",
      "company_info": {
        "company_name": "ABC 科技"
      },
      "salary_min": 60000,
      "salary_max": 90000,
      "city": "台北市",
      "remote_option": "hybrid"
    }
    // ... 更多職缺
  ]
}
```

---

## 錯誤處理與復原

### 常見錯誤場景

#### 1. OpenAI API Rate Limit

**錯誤訊息**：
```
openai.RateLimitError: Rate limit reached for requests
```

**解決方案**：
```python
# 在 .env 中調整速率
RATE_LIMIT_DELAY=0.5  # 增加到 0.5 秒
```

#### 2. Supabase 連線逾時

**錯誤訊息**：
```
supabase.exceptions.APIError: Timeout
```

**解決方案**：
```python
# 減少批次大小
BATCH_SIZE=50  # 從 100 降到 50
```

#### 3. 向量維度不匹配

**錯誤訊息**：
```
qdrant_client.exceptions.UnexpectedResponse: Wrong vector size
```

**檢查方式**：
```python
# 驗證向量維度
vector = get_embedding("測試文本")
print(f"向量維度: {len(vector)}")  # 應為 1536
```

#### 4. 薪資欄位型態錯誤

**錯誤訊息**：
```
TypeError: '<=' not supported between instances of 'str' and 'int'
```

**原因**：Supabase 中 `salary_min`/`salary_max` 被錯誤設定為 VARCHAR

**解決方案**：
```sql
-- 在 Supabase SQL Editor 中執行
ALTER TABLE job_posting 
ALTER COLUMN salary_min TYPE INTEGER USING salary_min::integer,
ALTER COLUMN salary_max TYPE INTEGER USING salary_max::integer;
```

### 中斷後復原

若作業中途失敗，直接重新執行即可：

```bash
python vectorize_jobs.py
```

**原因**：腳本會自動跳過 `is_embedded=TRUE` 的資料，從失敗點繼續。

---

## FAQ

### Q1: 為什麼薪資欄位也要放入 Payload？

**答**：
- 薪資是重要的硬篩選條件，使用者期望只看到薪資範圍符合的職缺
- 若不放入 Payload，需要先從 Qdrant 取得所有相似職缺，再回 Supabase 過濾薪資
- 這會導致**浪費向量運算**且**結果不可控**（過濾後可能剩不到 10 筆）

### Q2: 薪資為 NULL 的職缺如何處理？

**答**：
- Payload 中保持 `salary_min: None`、`salary_max: None`
- 搜尋時若使用者指定期望薪資，這些職缺會被**自動排除**
- 若使用者未指定期望薪資，則不套用薪資篩選條件，保留所有職缺

### Q3: 如何支援「薪資面議」的職缺？

**方案 A**：在 Supabase 新增欄位 `is_negotiable: BOOLEAN`

```python
# Payload 設計
payload = {
    "salary_min": None,
    "salary_max": None,
    "is_negotiable": True  # 標記為面議
}

# 搜尋邏輯修改
filters = []
if expected_salary and not include_negotiable:
    filters.append(...)  # 原本的薪資範圍篩選
```

**方案 B**：使用特殊值表示（如 `-1` 或 `999999999`）

### Q4: 向量化失敗如何重試單筆資料？

```python
# 手動重試指定 job_id
def retry_single_job(job_id: int):
    # 重置狀態
    supabase.table("job_posting") \
        .update({"is_embedded": False, "vector_id": None}) \
        .eq("job_id", job_id) \
        .execute()
    
    # 重新向量化
    vectorize_batch(offset=0, limit=1)
```

### Q5: 如何監控 OpenAI API 用量？

前往 [OpenAI Usage Dashboard](https://platform.openai.com/usage) 查看：
- 當日已用金額
- Token 消耗量
- API 調用次數

### Q6: 8000 筆資料的實際成本？

**計算**：
```
假設：每筆職缺平均 300 字（中文） ≈ 600 tokens
總 tokens = 8000 × 600 = 4,800,000 tokens
成本 = 4.8M tokens × $0.13 / 1M = $0.62 USD
```

**結論**：約 **$0.60-0.80 USD**，你的 $5 餘額綽綽有餘。

---

## 執行檢查清單

### 執行前檢查

- [ ] 已建立 Qdrant Collections（`resume_vectors`, `job_vectors`）
- [ ] 已配置 `.env` 檔案（API Keys 正確）
- [ ] 已安裝所有 Python 套件
- [ ] Supabase 中 `salary_min`/`salary_max` 欄位型態為 `INTEGER`
- [ ] OpenAI 帳戶餘額 ≥ $1 USD

### 執行步驟

```bash
# 1. 建立目錄結構
mkdir -p config scripts logs

# 2. 建立配置檔案
# (複製本文件中的 config/settings.py)

# 3. 執行向量化
cd scripts
python vectorize_jobs.py

# 4. 驗證結果
python verify_sync.py
```

### 執行後驗證

- [ ] Supabase `is_embedded=TRUE` 筆數 = Qdrant `points_count`
- [ ] 抽查 5 筆職缺的 `vector_id` 在 Qdrant 中存在
- [ ] Payload 中包含 `salary_min` 和 `salary_max`
- [ ] 日誌檔案無 ERROR 級別錯誤

---

## 下一步行動

1. ✅ **執行向量化**
   ```bash
   cd scripts
   python vectorize_jobs.py
   ```

2. ✅ **驗證同步**
   ```bash
   python verify_sync.py
   ```

3. ⏭️ **開發搜尋 API**（下階段任務）
   - 實作 Flask 路由
   - 整合 Qdrant 搜尋 + Supabase 查詢
   - 加入完整硬篩選邏輯（地區/遠端/薪資）

4. ⏭️ **履歷向量化**
   - 複製 `vectorize_jobs.py` 並修改為 `vectorize_resumes.py`
   - 調整欄位對應（`RESUME` 表）
   - 處理 `structured_data` 的 JSON 結構

---

**文件製作**: Career Pilot 資料工程組  
**最後更新**: 2026-02-04  
**版本**: v1.0
