# supabase_control 資料夾整理與 ipynb 轉 .py 規劃

## 一、現況摘要

| 檔案 | 用途 | 依賴 |
|------|------|------|
| `clear.ipynb` | 職缺清洗（依 cleaner步驟_v2.md）+ 寫入 company_info、job_posting | jobs_rows.csv, Erd/.env, supabase_connection |
| `resume_insert.ipynb` | 從 resume.csv 寫入 resume 表 | resume.csv, .env, supabase_connection |
| `stage9_job_skill_requirement.ipynb` | 從職缺萃取技能，寫入 job_skill_requirement | skill_master, job_posting, jobs_rows/jobs_cleaned |
| `qdrant.ipynb` | 建立 Qdrant collections（resume_vectors, job_vectors） | .env (QDRANT_*) |
| `course/course_clean_and_upload.ipynb` | 課程清洗（依 coursera_cleaning_steps.md）+ 寫入 course | Coursera_row_rows.csv, .env |
| `supabase_connection.py` | Supabase 連線共用模組 | .env |
| `scripts/vectorize_jobs.py` | 職缺向量化 → Qdrant | config.settings |
| `scripts/vectorize_resumes.py` | 履歷向量化 → Qdrant | config.settings |
| `scripts/verify_sync.py` | 驗證 Supabase ↔ Qdrant 同步 | config.settings |

> 說明文件中曾提及 `skill_write_evaluation.ipynb`，目前專案內未找到此檔；若之後補上，可一併納入同一套分類。

---

## 二、建議目錄結構

在**不更動現有 `scripts/`、`course/`、`config/`、`Erd/`、`survey_result/`** 的前提下，有兩種做法。

### 方案 A：全部收進 `scripts/`，用子資料夾分領域（推薦）

```
supabase_control/
├── config/                    # 維持
├── Erd/                       # 維持
├── survey_result/             # 維持
├── course/                    # 維持，只把 ipynb 換成 .py
│   ├── course_clean_and_upload.py   # 從 ipynb 轉出
│   ├── coursera_cleaning_steps.md
│   └── Coursera_row_rows.csv
├── scripts/
│   ├── jobs/                  # 職缺相關
│   │   ├── job_clean_and_upload.py      # 由 clear.ipynb 轉出
│   │   └── job_skill_requirement.py     # 由 stage9_job_skill_requirement.ipynb 轉出
│   ├── resume/
│   │   └── resume_insert.py            # 由 resume_insert.ipynb 轉出
│   ├── qdrant/
│   │   └── setup_collections.py       # 由 qdrant.ipynb 轉出
│   ├── vectorize_jobs.py      # 維持
│   ├── vectorize_resumes.py   # 維持
│   └── verify_sync.py        # 維持
├── supabase_connection.py     # 維持在根目錄，方便 import
├── main.py                    # 可改為 CLI 入口或保留
├── cleaner步驟_v2.md
├── jobs_rows.csv
└── ...
```

- **優點**：所有「可執行的腳本」都在 `scripts/`，結構單一；`course/` 只放課程專用程式與資料。
- **注意**：從 `scripts/jobs/`、`scripts/resume/` 等執行時，需確保可 import 到 `supabase_connection`（例如在 `scripts` 或專案根跑、或適度改 `sys.path`）。

### 方案 B：依「資料領域」在根目錄開資料夾

```
supabase_control/
├── config/
├── Erd/
├── survey_result/
├── jobs/                      # 職缺：清洗、寫入、技能
│   ├── job_clean_and_upload.py
│   └── job_skill_requirement.py
├── resume/
│   └── resume_insert.py
├── course/
│   ├── course_clean_and_upload.py
│   ├── coursera_cleaning_steps.md
│   └── Coursera_row_rows.csv
├── qdrant/
│   └── setup_collections.py
├── scripts/                   # 只放「向量化 + 驗證」
│   ├── vectorize_jobs.py
│   ├── vectorize_resumes.py
│   └── verify_sync.py
├── supabase_connection.py
├── main.py
└── ...
```

- **優點**：依領域分資料夾，職缺 / 履歷 / 課程 / Qdrant 一目了然。
- **缺點**：根目錄資料夾變多，與現有「向量化在 scripts」的習慣略有不同。

---

## 三、檔案對應與轉成 .py 的建議

| 原 ipynb | 建議新檔名 | 建議位置（方案 A） | 說明 |
|----------|------------|--------------------|------|
| clear.ipynb | `job_clean_and_upload.py` | `scripts/jobs/` | 保留依 `cleaner步驟_v2.md` 的步驟註解，必要時用 `if __name__ == "__main__"` 分階段跑 |
| stage9_job_skill_requirement.ipynb | `job_skill_requirement.py` | `scripts/jobs/` | 技能映射、匹配、寫入 job_skill_requirement，可拆成函數方便單測 |
| resume_insert.ipynb | `resume_insert.py` | `scripts/resume/` | 讀 resume.csv、轉 payload、寫入 resume 表 |
| qdrant.ipynb | `setup_collections.py` | `scripts/qdrant/` | 只做建立/檢查 collections，可改用 `config.settings` 讀 QDRANT_* |
| course/course_clean_and_upload.ipynb | `course_clean_and_upload.py` | `course/` | 維持在 course，依 `coursera_cleaning_steps.md` 步驟，路徑改為依 `Path(__file__)` 解析 |

- **連線**：新 .py 一律改用 `from supabase_connection import connect_to_supabase`（或從專案根 `sys.path` 後 import），避免在腳本裡重複 `load_dotenv` + `create_client`；Qdrant 部分可與現有 `config.settings` 一致。
- **路徑**：建議用 `Path(__file__).resolve().parent` 推導專案根或 `course/`、資料檔位置，這樣從指令列或不同 cwd 執行都不會錯。

---

## 四、轉換時要注意的點

1. **執行順序與依賴**  
   - 職缺：`job_clean_and_upload.py` → `job_skill_requirement.py`（若有 skill_write_evaluation 再補在之前）。  
   - 向量：先跑 `setup_collections.py`，再跑 `vectorize_jobs.py` / `vectorize_resumes.py`。  
   可在各 .py 的 docstring 或 README 註明「建議執行順序」。

2. **文件與註解**  
   - `cleaner步驟_v2.md`、`coursera_cleaning_steps.md`、`career_pilot說明文件v4_with_chinese.md` 裡若有寫到 ipynb 檔名，改為對應的新 .py 檔名（例如 `clear.ipynb` → `scripts/jobs/job_clean_and_upload.py`）。

3. **是否保留 ipynb**  
   - 轉成 .py 後可選擇：  
     - 只保留 .py，刪除 ipynb；或  
     - 短期保留 ipynb 當備份，在檔名加後綴如 `clear_backup.ipynb`，之後再刪。

4. **survey_result/**  
   - 維持獨立，不一定要搬進 `scripts/`，除非你希望「所有會寫入 DB 的腳本」都收在 `scripts/` 底下再考慮子資料夾。

---

## 五、建議採用的方案與步驟

- **推薦方案 A**：全部腳本收在 `scripts/`，用 `scripts/jobs/`、`scripts/resume/`、`scripts/qdrant/` 分類，課程保留在 `course/` 並改為 `course_clean_and_upload.py`。
- **執行步驟建議**：  
  1. 在 `scripts/` 下建立 `jobs/`、`resume/`、`qdrant/`。  
  2. 依序把上述 5 個 ipynb 轉成 .py 並放到對應位置（路徑、import、config 統一）。  
  3. 用少量資料跑一輪，確認寫入 DB / Qdrant 與現有行為一致。  
  4. 更新文件中的檔名與路徑。  
  5. 決定是否刪除或重新命名舊 ipynb。

---

## 六、已執行結果（方案 A）

已依方案 A 完成以下轉換與測試：

| 新腳本 | 位置 | 測試結果 |
|--------|------|----------|
| `setup_collections.py` | `scripts/qdrant/` | 邏輯與 qdrant.ipynb 一致；需 QDRANT_URL / QDRANT_API_KEY 與可連線之 Qdrant 方能完整執行 |
| `resume_insert.py` | `scripts/resume/` | `row_to_payload` 與 ipynb 一致；執行需 resume.csv 與 Supabase |
| `job_skill_requirement.py` | `scripts/jobs/` | `parse_skills`、`build_jd_text` 等與 ipynb 一致；支援 `--no-insert`、`--no-export-unmatched` |
| `job_clean_and_upload.py` | `scripts/jobs/` | 清理函數與 clear.ipynb 一致；執行需 jobs_rows.csv 與 Supabase |
| `course_clean_and_upload.py` | `course/` | 清洗與寫入邏輯與 course_clean_and_upload.ipynb 一致；執行需 Coursera_row_rows.csv 與 Supabase |

**測試腳本**：`scripts/test_new_scripts.py`（在專案根 `supabase_control` 下以 `.venv` 執行：`python scripts/test_new_scripts.py`）

**建議**：舊 ipynb 可暫時保留作備份，確認新 .py 在實際環境跑過一輪後再刪除或改名。

---

*本文件僅供檢閱與決策，實際搬檔與轉換可依此規劃逐步執行。*
