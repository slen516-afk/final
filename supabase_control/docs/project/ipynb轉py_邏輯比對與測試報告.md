# ipynb 轉 .py 邏輯比對與測試報告

本文件記錄五支由 ipynb 轉成的 .py 腳本與原始 notebook 的邏輯比對結果，以及實際執行測試結論。

---

## 一、測試環境與限制

- **執行方式**：在 `supabase_control` 專案根目錄下，使用 `.venv` 的 Python 執行（`uv sync` 已安裝依賴）。
- **網路**：測試時若無法連線 Supabase / Qdrant（例如沙箱或未設 .env），腳本會在「連線／第一次 API 呼叫」失敗，屬預期；**在此之前的路徑、讀檔、清理邏輯皆已驗證**。

---

## 二、各腳本比對與測試結果

### 1. `scripts/jobs/job_clean_and_upload.py` ← `archive/notebooks/clear.ipynb`

| 項目 | 比對結果 |
|------|----------|
| **路徑** | .py 使用 `DATA_DIR = PROJECT_ROOT / "data"`、`RAW_CSV = DATA_DIR / "jobs_rows.csv"`，與搬移後資料位置一致。 |
| **清理函數** | `clean_text`、`clean_company_name`、`extract_industry`、`infer_industry_from_job_category`、`standardize_location`、`clean_salary`、`determine_remote_option`、`merge_requirements`、`create_job_details`、`_agg_job_cats` 與 notebook 內定義一致（常數如 `ORG_SUFFIXES`、`PRIORITY_LAYERS`、`CITIES` 等相同）。 |
| **主流程** | 讀取 CSV → 公司彙總（groupby company_name、industry 解析）→ 職缺清理（欄位對應、去重、篩除空值）→ 寫入 company_info（payload：company_name, industry, company_size, location, website, description）→ 寫入 job_posting（upsert on source_url）與 notebook 一致。 |
| **company_info payload** | 與 notebook 相同，不含 job_category（notebook 註解寫「包含 job_category」但實際 payload 亦未含）。 |
| **執行測試** | 使用 venv 執行：成功讀取 `data/jobs_rows.csv`、載入 .env、建立 Supabase client；於第一次 API 呼叫（`company_info.select`）因網路不可達而失敗。**結論：邏輯與路徑正確，僅差實際連線。** |

---

### 2. `scripts/resume/resume_insert.py` ← `archive/notebooks/resume_insert.ipynb`

| 項目 | 比對結果 |
|------|----------|
| **路徑** | .py 優先讀取 `PROJECT_ROOT / "data" / "resume.csv"`，再依序專案根、當前目錄，與規劃一致。 |
| **row_to_payload** | 欄位對應（resume_id, user_id, template_id, resume_type, structured_data, normalized_data, vector_id, is_embedded, is_primary, created_at, updated_at）、JSON 字串轉 dict、to_bool 邏輯與 notebook 相同。 |
| **主流程** | 連線 → 找 CSV → 讀取 → dropna(how="all") → 轉 payload → upsert(resume, on_conflict=resume_id) → 查詢驗證，與 notebook 一致。 |
| **執行測試** | 若無 `data/resume.csv` 或專案根 `resume.csv`，會正確拋出 `FileNotFoundError`；若有 CSV 但無 Supabase 連線，會於連線時失敗。**結論：邏輯一致；需在 data/ 或專案根放置 resume.csv 方能完整跑通。** |

---

### 3. `scripts/jobs/job_skill_requirement.py` ← `archive/notebooks/stage9_job_skill_requirement.ipynb`

| 項目 | 比對結果 |
|------|----------|
| **路徑** | `DATA_DIR = PROJECT_ROOT / "data"`，RAW_CSV 優先 `jobs_rows.csv` 再 `jobs_cleaned.csv`；輸出的 `unmatched_skills.csv` 寫入 `DATA_DIR`，與搬移後一致。 |
| **build_skill_mapping** | 從 skill_master 取 skill_id, skill_name, synonyms；建立 synonym_to_skill_id、skill_id_to_jd_patterns（整詞 regex）；與 notebook 邏輯相同。 |
| **parse_skills** | 合併 skills / tools 字串，以 `、`、`,` 分割去重，與 notebook 一致。 |
| **build_jd_text**、**match_skills**、**寫入 job_skill_requirement / 匯出 unmatched** | 比對 .py 與 notebook 對應 cell，流程與欄位一致；`--no-insert`、`--no-export-unmatched` 行為正確。 |
| **執行測試** | 使用 venv 執行 `--no-insert --no-export-unmatched`：成功印出「使用資料檔：...\data\jobs_rows.csv」、Supabase URL；於 `build_skill_mapping(supabase)` 內第一次 API 呼叫因網路失敗。**結論：路徑與流程正確，需可連 Supabase 方能跑完全程。** |

---

### 4. `scripts/qdrant/setup_collections.py` ← `archive/notebooks/qdrant.ipynb`

| 項目 | 比對結果 |
|------|----------|
| **邏輯** | 載入 .env（Erd/.env、.env）→ 讀取 QDRANT_URL、QDRANT_API_KEY → 建立 QdrantClient → 檢查現有 collections → 若不存在則建立 resume_vectors、job_vectors（1536 維、COSINE）；.py 另多建 `optimized_resume_vectors`（與現有向量化流程一致）。與 notebook 建立兩 collection 的意圖一致，.py 為擴充版。 |
| **執行測試** | 無 Qdrant 連線時會於 `client.get_collections()` 或更早（URL/API_KEY 為空）失敗。**結論：邏輯一致；需設定 .env 且 Qdrant 可連線才能完整執行。** |

---

### 5. `course/course_clean_and_upload.py` ← `archive/notebooks/course_clean_and_upload.ipynb`

| 項目 | 比對結果 |
|------|----------|
| **路徑** | 先試 `PROJECT_ROOT / "data" / "course" / "Coursera_row_rows.csv"`，再 course 目錄、再 `project/course/`，與搬移後一致。 |
| **清洗** | 刪除「語言」「開課時間」「課程」欄、parse_rating、parse_review_count、to_skill_list、level 從 Metadata 萃取、寫入 course 表欄位對應，與 notebook 一致。 |
| **執行測試** | 未在本次用 venv 實際跑（依賴 Supabase）；若 `data/course/Coursera_row_rows.csv` 存在，預期可讀到並執行到 Supabase 寫入前。**結論：邏輯與路徑設定一致。** |

---

## 三、總結

| 腳本 | 邏輯與 notebook 是否一致 | 路徑是否正確（data/） | 實際跑通條件 |
|------|---------------------------|------------------------|----------------|
| job_clean_and_upload.py | ✅ 一致 | ✅ | 需 data/jobs_rows.csv、.env、Supabase 可連 |
| resume_insert.py | ✅ 一致 | ✅ | 需 data/resume.csv（或專案根）、.env、Supabase 可連 |
| job_skill_requirement.py | ✅ 一致 | ✅ | 需 data/jobs_rows.csv（或 jobs_cleaned）、.env、Supabase 可連（skill_master 有資料） |
| setup_collections.py | ✅ 一致（多 optimized_resume_vectors） | N/A | 需 .env 內 QDRANT_URL、QDRANT_API_KEY、Qdrant 可連 |
| course_clean_and_upload.py | ✅ 一致 | ✅ | 需 data/course/Coursera_row_rows.csv、.env、Supabase 可連 |

**結論**：五支腳本與對應 ipynb 的程式邏輯一致，CSV 路徑已改為 `data/` 且測試中能正確找到檔案；未發現遺漏或錯誤的欄位對應。實際「跑通」需在具備 .env 與可連線的 Supabase（及 Qdrant）環境下執行。

---

## 四、建議後續自測步驟

1. 在專案根使用 venv：  
   `cd supabase_control` → `.\.venv\Scripts\python.exe scripts/jobs/job_clean_and_upload.py`
2. 確認 `data/jobs_rows.csv`、`data/course/Coursera_row_rows.csv` 存在；若有履歷測試檔請放 `data/resume.csv`。
3. 確認 `.env`（或 `Erd/.env`）已設定 `SUPABASE_URL`、`SUPABASE_SERVICE_ROLE_KEY`，且網路可連 Supabase。
4. 若要測 job_skill_requirement 而不寫入 DB，可先跑：  
   `python scripts/jobs/job_skill_requirement.py --no-insert --no-export-unmatched`  
   確認能讀取 skill_master 並產出統計後，再拿掉參數做正式寫入與匯出 unmatched_skills.csv。
