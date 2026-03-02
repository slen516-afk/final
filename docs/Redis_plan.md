# Redis Stream Job Queue for CV Analysis

將 `analysis.py` 從同步 mock 改為 **Redis Stream 排隊 + Worker 消化** 架構。

```text
[Frontend] → POST /api/analysis/tasks → [API Server] → XADD cv_jobs → [Worker x N] → DB
[Frontend] ← GET /api/analysis/jobs/{job_id}  ← [Redis/DB 查狀態]
```

---

## Proposed Changes

### Redis Infrastructure

#### [MODIFY] [docker-compose.yml](file:///d:/AIPE2_Goup/final/docker-compose.yml)

新增 `redis` service：

```yaml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
  networks:
    - default
```

`backend` service 加 `depends_on: [redis]` 和 `REDIS_URL=redis://redis:6379/0`。

---

#### [MODIFY] [requirements.txt](file:///d:/AIPE2_Goup/final/backend/requirements.txt)

新增：

```text
redis>=5.0.0
```

---

### Core Module

#### [NEW] [redis_client.py](file:///d:/AIPE2_Goup/final/backend/core/redis_client.py)

Redis 連線 singleton，跟 `supabase_client.py` 同層：

- `get_redis_client()` → 讀 `REDIS_URL` env var（預設 `redis://localhost:6379/0`）
- 全域 `redis_client` 實例

---

### API Layer

#### [MODIFY] [analysis.py](file:///d:/AIPE2_Goup/final/backend/flask/api/analysis.py)

**完全重寫**，核心改動：

| 端點 | 行為 |
|---|---|
| `POST /tasks` | 產生 `job_id`，存 job 狀態到 Redis Hash (`job:{job_id}`)，`XADD` 到 `cv_jobs` stream（payload 只帶 `job_id`, `cv_id`, `task_type`），回傳 `job_id` |
| `GET /jobs/<job_id>` | **新端點**，讀 Redis Hash `job:{job_id}`，回傳 `status` + `result`（如果 done）|
| `GET /tasks/<task_id>/status` | 保留，改讀 Redis Hash |
| `GET /tasks/<task_id>/results` | 保留，改讀 Redis Hash 裡的 `result` 欄位 |
| `GET /tasks/<task_id>/suggestions` | 保留，改讀 Redis Hash 裡的 `suggestions` 欄位 |

**Job 狀態 (Redis Hash `job:{job_id}`)**:

```text
status:    queued | processing | done | failed
user_id:   <uuid>
resume_id: <str>
survey_id: <str>
result:    <json string>  (done 時寫入)
error:     <str>          (failed 時寫入)
created_at: <timestamp>
updated_at: <timestamp>
```

**Queue payload** (小 & 安全)：只放 `job_id`, `task_type`。CV 原文在 DB，Worker 自己去查。

---

### Worker

#### [NEW] [cv_worker.py](file:///d:/AIPE2_Goup/final/backend/flask/worker/cv_worker.py)

獨立進程，`python -m worker.cv_worker` 啟動：

1. **XGROUP CREATE** `cv_jobs` group `cv_workers`（idempotent）
2. **Loop**: `XREADGROUP` 讀 pending 或新訊息
3. 更新 Hash status → `processing`
4. 呼叫 LLM / 職缺檢索 API（目前先 mock sleep）
5. 寫結果到 Redis Hash → status `done`
6. `XACK`

**重試 & DLQ**：

- payload 帶 `retry_count`，每次失敗 +1
- `retry_count >= 3` → `XADD cv_jobs_dlq` + status `failed` + `XACK`
- `retry_count < 3` → 重新 `XADD cv_jobs`（新 message ID）+ `XACK` 舊的

---

## Verification Plan

### Automated Tests

1. **Redis 啟動**：`docker compose up redis -d && docker compose exec redis redis-cli PING`
2. **單元跑 Worker**：

   ```powershell
   # 在 backend container 或本機
   python -m worker.cv_worker &   # 背景跑
   ```

3. **API 測試**：

   ```powershell
   # POST 建立任務
   curl -X POST http://localhost:5000/api/analysis/tasks -H "Content-Type: application/json" -H "Authorization: Bearer <token>" -d '{"resume_id":"r1","survey_id":"s1"}'
   # → 應回 202 + job_id

   # GET 查狀態
   curl http://localhost:5000/api/analysis/jobs/<job_id> -H "Authorization: Bearer <token>"
   # → status: queued → processing → done
   ```

4. **DLQ 驗證**：手動讓 Worker 的處理邏輯 raise exception 3 次，確認訊息進 `cv_jobs_dlq`。

### Manual Verification

請你在本機 `docker compose up redis -d` 之後跑 Flask + Worker，用 curl 或 Postman 測上面的流程。

---

# 實作結果 Walkthrough

## 改了什麼

| 檔案 | 動作 | 說明 |
|---|---|---|
| `docker-compose.yml` | MODIFY | 新增 `redis` service + backend `depends_on` & `REDIS_URL` |
| `backend/requirements.txt` | MODIFY | 加 `redis>=5.0.0` |
| `backend/core/redis_client.py` | NEW | Redis singleton + stream/group/DLQ 常數 |
| `backend/flask/api/analysis.py` | REWRITE | POST → XADD 排隊，GET 讀 Redis Hash |
| `backend/flask/worker/cv_worker.py` | NEW | XREADGROUP consumer + retry ≤3 + DLQ |

## 架構流程

```text
POST /api/analysis/tasks  →  Redis Hash (status=queued) + XADD cv_jobs
                                    ↓
                           Worker XREADGROUP
                           status → processing
                           (LLM call — 目前 mock sleep 3s)
                           status → done / failed
                                    ↓
GET /api/analysis/jobs/{job_id}  ←  讀 Redis Hash 回傳 status + result
```

**DLQ**: 失敗 ≥3 次 → `XADD cv_jobs_dlq` + status `failed`

## 怎麼跑

```powershell
# 1. 啟 Redis
docker compose up redis -d

# 2. 啟 Flask
cd backend/flask
python app.py

# 3. 開 Worker（可多開）
cd backend/flask
python -m worker.cv_worker

# 4. 測試
curl -X POST http://localhost:5000/api/analysis/tasks `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer <token>" `
  -d '{"resume_id":"r1","survey_id":"s1"}'
# → {"job_id":"job_xxxx","status":"queued"}

curl http://localhost:5000/api/analysis/jobs/job_xxxx `
  -H "Authorization: Bearer <token>"
# → status: queued → processing → done
```

---

# 測試計畫 Walkthrough

## 測試架構

- **pytest** + **fakeredis**：不需 Docker 即可跑全部 unit tests
- **Mock Supabase auth**：`conftest.py` patches `supabase.auth.get_user`，`@login_required` 用 `Bearer fake-token` 即可通過
- **cv_worker Mock**：`from API_test_main import run_analysis` 已註解，改用 `_run_analysis()` stub，測試時 monkeypatch 覆蓋

## 新增 / 修改檔案

| 檔案 | 動作 | 說明 |
|---|---|---|
| `tests/conftest.py` | NEW | fakeredis + mock Supabase auth + Flask client fixtures |
| `tests/test_redis_client.py` | NEW | 4 tests（constants, factory, env override, integration ping） |
| `tests/test_analysis.py` | NEW | 13 tests（5 endpoints 全覆蓋） |
| `tests/test_resume.py` | NEW | 9 tests（4 endpoints 全覆蓋） |
| `tests/test_user_preference.py` | NEW | 8 tests（2 queue-based endpoints） |
| `tests/test_cv_worker.py` | NEW | 9 tests（ensure_group / process_job / handle_message + retry + DLQ） |
| `cv_worker.py` | MODIFY | `run_analysis` → `_run_analysis()` stub；移除 `time.sleep(3)` |
| `requirements.txt` | MODIFY | 加 `pytest>=7.0`, `fakeredis>=2.20` |

## 測試結果

```text
42 passed, 1 failed in 5.39s
```

唯一 failure 是 `test_redis_ping`（integration test，需 Docker Redis）。

## 怎麼跑

```powershell
cd backend/flask

# Unit tests only（不需 Docker）
python -m pytest tests/ -v -m "not integration"

# Full suite（先啟 Redis）
docker compose up -d redis
python -m pytest tests/ -v
```

## 設計重點

- **`_run_analysis()` stub**：正式環境只要取消註解 `cv_worker.py` 裡的兩行即可恢復真串 LLM
- **fakeredis**：CI / local dev 零外部依賴
- **Auth bypass**：`conftest.py` 用 `SimpleNamespace(id="user-test-001")` 模擬 Supabase user
