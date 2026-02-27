## Career Pilot 標註欄位與 Qdrant 同步規劃

### 目標

- **在 ERD / 資料庫 / Qdrant 之間建立一致的「已完成貼標」狀態 (`is_labeled`) 與六維分數 (D1–D6)。**
- **讓 Qdrant 語意搜尋可以直接用 `is_labeled = true` 與 D1–D6 做 filter。**

---

### 階段 A：ERD 文件更新

1. **更新 `career_pilot_erd_readable.mermaid`**
   - 在 `JOB_POSTING` 的欄位中新增：
     - `is_labeled: BOOLEAN`  
       - 說明：是否已完成六維能力貼標，預設 `false`。
2. **更新 `career_pilot說明文件v4_with_chinese.md`**
   - 在「5.2 JOB_POSTING(職缺資訊)」欄位表格中新增一列：
     - 欄位名稱：`is_labeled`
     - 中文名稱：是否已完成貼標
     - 英文：Is Labeled
     - 資料型態：`BOOLEAN`
     - 說明：是否已完成 D1–D6 能力貼標，預設 `FALSE`。
3. **更新 `career_pilot_ERD_欄位對齊總表.md`**
   - 將 `JOB_POSTING.is_labeled` 加入對齊表，與其他文件描述保持一致。

> 完成階段 A 後，三份 ERD 文件對「已完成貼標」的欄位會有一致定義。

---

### 階段 B：Supabase 資料庫 schema 與資料回填

1. **在 Supabase / Postgres 新增欄位**
   - 在 `job_posting` 資料表新增：
     - `is_labeled BOOLEAN NOT NULL DEFAULT FALSE`
   - 若有 migration 檔，記得紀錄此變更。
2. **回填既有已貼標資料**
   - 根據既有規則：「`d1_frontend` 不為 NULL 代表已貼標」。
   - 在資料庫執行 SQL（示意）：
     - `UPDATE job_posting SET is_labeled = TRUE WHERE d1_frontend IS NOT NULL;`
   - 確認：目前所有「六維有值」的職缺，其 `is_labeled` 皆為 `TRUE`，其他維持 `FALSE`。

> 完成階段 B 後，DB 端會有正確的 `is_labeled` 初始狀態，可作為 Qdrant 同步的唯一真實來源。

---

### 階段 C：貼標腳本更新（讓未來貼標自動維護 is_labeled）

1. **更新 `run_labeling_test.py`**
   - 在產生 `db_payload` 並更新資料庫的地方，新增：
     - `is_labeled = True`（僅在六維分數成功寫入時設為 `True`）。
   - 確保只有「AI 分析成功且六維分數寫入成功」時才更新 `is_labeled`。
2. **更新 `run_random_batch.py`**
   - 與 `run_labeling_test.py` 同樣邏輯：
     - 在成功寫入 `d1_frontend`～`d6_soft_skills` 後，同步將 `is_labeled` 更新為 `True`。

> 完成階段 C 後，所有「新完成貼標」的職缺在 DB 端都會自動被標記為 `is_labeled = TRUE`。

---

### 階段 D：向量化程式與 Qdrant payload schema 擴充

1. **擴充 Supabase 查詢欄位（`vectorize_jobs.py`）**
   - 在從 `job_posting` 撈資料的 `.select(...)` 中加入：
     - `is_labeled`
     - `d1_frontend`～`d6_soft_skills`（可選：若希望 Qdrant 內也帶能力分數）。
     - `role_type`、`role_name`（由貼標流程產生的職缺角色代碼與名稱，若希望 Qdrant 內也帶此欄位）。
   - **實作建議步驟：**
     1. 找到 `vectorize_jobs.py` 中對 `job_posting` 的 `.select(...)`，把上述欄位補進去。
     2. 確認這些欄位在 DB schema 中已存在（貼標腳本已經寫入 `role_type`、`role_name` 與 D1–D6）。
     3. 保持查詢條件 `.eq("is_embedded", False)` 與排序邏輯不變，只增加欄位輸出。
2. **擴充 `prepare_payload(job)`**
   - 新增以下欄位：
     - `is_labeled`: 直接使用 `job["is_labeled"]`（或 `job.get("is_labeled", False)`）。
     - `d1_frontend`～`d6_soft_skills`: 從 `job` 讀取並寫入 payload。
     - `role_type`: 從 `job["role_type"]`（或 `job.get("role_type")`）讀取並寫入 payload。
     - `role_name`: 從 `job["role_name"]`（或 `job.get("role_name")`）讀取並寫入 payload。
   - **實作建議步驟：**
     1. 在 `prepare_payload(job)` 回傳的 dict 中，將上述欄位加入 payload。
     2. 若未來有新增與貼標結果相關的欄位（例如其他分類結果），也一併從 `job` 帶入 payload。
3. **Qdrant 重新向量化策略說明**
   - 既有已向量化職缺：
     - 若 payload 中尚未有 `is_labeled` 與 D1–D6，就交由下一階段「同步腳本」補齊。
   - 新向量化的職缺：
     - 會直接帶入最新的 `is_labeled` 與 D1–D6（尚未貼標者 `is_labeled = FALSE`、D1–D6 可為 `NULL` 或不填）。

> 完成階段 D 後，所有新寫入 Qdrant 的點都會有完整 payload 結構。

---

### 階段 E：Qdrant payload 同步腳本設計

> 目的：在你「之後補貼標」或「剛完成標註一批職缺」後，透過腳本把 Qdrant payload 的 `is_labeled` 與 D1–D6 同步成最新狀態。

1. **腳本位置與名稱建議**
   - 放在 `supabase_control/scripts/labeling/` 目錄下，例如：
     - `sync_qdrant_job_labels.py`
2. **腳本主要行為**
   1. 從環境變數載入 Supabase / Qdrant 連線設定。
   2. 從 `job_posting` 撈出「需要同步」的職缺：
      - 條件建議（至少一種）：
        - `vector_id IS NOT NULL`（已向量化，Qdrant 有對應點）
        - 搭配一個時間條件或狀態條件，例如：
          - 最近 N 小時內 `updated_at` 有變動，且欄位包含 D1–D6、`role_type`、`role_name` 或 `is_labeled`。
          - 或：`is_labeled = TRUE` 但 Qdrant 尚未帶入（可透過本地 flag 或一次性全量同步）。
      - 查詢時一併選出以下欄位，作為同步來源：
        - `job_id`, `vector_id`
        - `is_labeled`
        - `role_type`, `role_name`
        - `d1_frontend`～`d6_soft_skills`
   3. 以批次處理方式迴圈這些職缺（**建議 `batch_size = 150`**）：
      - 每一批次的流程：
        - 從 Supabase 抓出接下來 `batch_size` 筆需要同步的職缺。
        - 對這一批組出對應的 payload dict（含 `is_labeled`、`role_type`、`role_name`、D1–D6）。
        - 呼叫 Qdrant 的 `set_payload` / `update_payload`，依 `vector_id` 更新 / 覆寫 payload。
      - 每一筆職缺在 Qdrant 端會被更新的欄位包含：
        - `is_labeled`
        - `role_type`
        - `role_name`
        - `d1_frontend`～`d6_soft_skills`
   4. 加入簡單日誌與進度列，方便追蹤（紀錄總筆數、每批耗時、錯誤重試等）。
3. **首次執行策略**
   - 第一次跑腳本時，可以先對「`vector_id IS NOT NULL` 且 `is_labeled = TRUE`」的所有職缺做一次**全量同步**：
     - 確保 Qdrant 內的點都具有正確的 `is_labeled = TRUE` 與六維分數。
   - 之後的日常運作可改為：
     - 依「最近更新時間」或手動指定一批 `job_id` 來跑增量同步。

> 完成階段 E 後，只要你在資料庫補貼標，執行一次同步腳本，就能讓 Qdrant payload 跟上最新狀態。

---

### 階段 F：搜尋端使用方式調整（概念 → 可實作範本）

1. **Qdrant 搜尋時加上 `is_labeled` 與 D1–D6 的 filter**
   - 只取已貼標職缺（基礎版）：
     - Qdrant filter JSON 範例：
       ```json
       {
         "must": [
           { "key": "is_labeled", "match": { "value": true } }
         ]
       }
       ```
   - 只取已貼標，且前端能力門檻 `D1 >= 3`（進階版）：
     - Qdrant filter JSON 範例：
       ```json
       {
         "must": [
           { "key": "is_labeled", "match": { "value": true } },
           { "key": "d1_frontend", "range": { "gte": 3 } }
         ]
       }
       ```
   - 多維度條件組合（例如 D1 >= 3 且 D4 >= 2）：
       ```json
       {
         "must": [
           { "key": "is_labeled", "match": { "value": true } },
           { "key": "d1_frontend", "range": { "gte": 3 } },
           { "key": "d4_ai_data", "range": { "gte": 2 } }
         ]
       }
       ```
   - 若在 Python 端呼叫 Qdrant（示意）：
       ```python
       from qdrant_client import QdrantClient, models

       client = QdrantClient(url=..., api_key=...)

       result = client.search(
           collection_name=settings.JOB_COLLECTION,
           query_vector=...,  # 由使用者查詢向量化後的向量
           limit=20,
           query_filter=models.Filter(
               must=[
                   models.FieldCondition(
                       key="is_labeled",
                       match=models.MatchValue(value=True),
                   ),
                   models.FieldCondition(
                       key="d1_frontend",
                       range=models.Range(gte=3),
                   ),
               ]
           ),
           with_payload=True,
       )
       ```
2. **搜尋結果回 DB 再確認（DB 作為最終真實來源，可選）**
   - 即使 payload 已有 `is_labeled` 與 D1–D6，若你希望在推薦/排序前再次確認最新狀態，可在取回 Qdrant 結果後：
     1. 取出前 N 筆候選職缺的 `job_id` 清單。
     2. 用 `job_id IN (...)` 回到 Supabase 查一次 `job_posting`，撈取最新的 `is_labeled` 與 D1–D6。
     3. 依照 DB 端資料做最終過濾與排序（例如再次濾掉 `is_labeled = FALSE`，或用最新 D1–D6 做權重計算）。
   - 此步驟可視為「保險機制」，在 payload 與 DB 有時間差時，仍以 DB 為準。

---

### 建議的執行順序總覽

1. **A：更新 ERD 三份文件**（新增 `JOB_POSTING.is_labeled` 定義）。
2. **B：在 Supabase / Postgres 新增 `job_posting.is_labeled` 欄位，並用 D1–D6 回填初始值。**
3. **C：更新貼標腳本 `run_labeling_test.py`、`run_random_batch.py`，讓未來貼標會自動維護 `is_labeled`。**
4. **D：更新向量化腳本 `vectorize_jobs.py` 的查詢欄位與 `prepare_payload`，讓新寫入 Qdrant 的點帶上 `is_labeled` 與六維分數。**
5. **E：撰寫並執行 `sync_qdrant_job_labels.py`：**
   - 先做一次「已向量化且已貼標職缺」的全量同步。
   - 之後每次補貼標完一批職缺後，再執行一次腳本做增量同步。
6. **F：在推薦 / 搜尋端改用 `is_labeled = true` 的 Qdrant filter（必要時再搭配 DB 最終校正）。**

以上是後續實作時的參考步驟與順序，你確認 OK 後即可依階段開始實作與調整。

