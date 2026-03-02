# supabase_control

Career Pilot 後端資料控制：職缺、履歷、課程等資料的清洗、寫入 Supabase，以及向量化寫入 Qdrant。

---

## 環境需求

- Python ≥ 3.12
- 專案根目錄（`supabase_control`）下具備 `.env`，或使用 `Erd/.env`（需含 `SUPABASE_URL`、`SUPABASE_SERVICE_ROLE_KEY`；向量化腳本另需 `QDRANT_*`、OpenAI 等）

依賴安裝（建議使用 uv）：

```bash
cd supabase_control
uv sync
```

---

## 目錄結構

| 目錄 | 說明 |
|------|------|
| `config/` | 設定（如 `settings.py`） |
| `data/` | **CSV 資料檔**：`jobs_rows.csv`、`resume.csv`、`unmatched_skills.csv` 等；課程用 CSV 在 `data/course/` |
| `docs/` | 說明文件：向量化指南、清洗步驟、專案規劃等（見 `docs/vectorization/`、`docs/cleaning/`、`docs/project/`） |
| `archive/notebooks/` | 已轉成 .py 的原始 ipynb 備份 |
| `scripts/` | 可執行腳本：職缺／履歷／課程清洗與寫入、向量化、驗證等 |
| `course/` | 課程清洗與寫入（`course_clean_and_upload.py`） |
| `db_function/` | 供 API 使用的 DB 寫入函數（見 `db_function/DB_WRITES_README.md`） |
| `Erd/` | ERD、欄位對齊、資料庫結構說明 |

---

## 常用腳本（請在專案根 `supabase_control` 下執行）

| 腳本 | 說明 |
|------|------|
| `python scripts/jobs/job_clean_and_upload.py` | 依 `docs/cleaning/cleaner步驟_v2.md` 清理 `data/jobs_rows.csv`，寫入 `company_info`、`job_posting` |
| `python scripts/jobs/job_skill_requirement.py` | 從職缺萃取技能，寫入 `job_skill_requirement`；可加 `--no-insert`、`--no-export-unmatched` |
| `python scripts/resume/resume_insert.py` | 從 `data/resume.csv`（或專案根 `resume.csv`）寫入 `resume` 表 |
| `python course/course_clean_and_upload.py` | 依 `docs/cleaning/coursera_cleaning_steps.md` 清洗 `data/course/Coursera_row_rows.csv`，寫入 `course` |
| `python scripts/qdrant/setup_collections.py` | 建立／檢查 Qdrant collections（resume、job 等） |
| `python scripts/vectorize_jobs.py` | 職缺向量化寫入 Qdrant |
| `python scripts/vectorize_resumes.py` | 履歷向量化寫入 Qdrant |
| `python scripts/verify_sync.py` | 驗證 Supabase 與 Qdrant 同步 |

---

## 資料檔位置

- 輸入：`data/jobs_rows.csv`、`data/jobs_cleaned.csv`、`data/resume.csv`、`data/course/Coursera_row_rows.csv` 等
- 輸出：`job_skill_requirement.py` 會將未匹配技能寫入 `data/unmatched_skills.csv`

詳細欄位與流程見 `docs/cleaning/`、`docs/vectorization/` 與 `Erd/`。

---

## 更多說明

- 清洗與寫入步驟：`docs/cleaning/`
- 向量化流程：`docs/vectorization/career_pilot_vectorization_guide.md`
- DB 寫入 API：`db_function/DB_WRITES_README.md`
- 資料夾與腳本對應：`docs/project/資料夾整理與ipynb轉py規劃.md`、`搬移清單_方案二.md`
