# API 完整驗證手冊（CV 端到端測試）

從 VSCode 開 Docker → 啟動服務 → 測試所有 API → 檢查結果的完整流程。

---

## 目錄

1. [環境需求](#1-環境需求)
2. [Docker 啟動流程](#2-docker-啟動流程)
3. [Flask 服務啟動](#3-flask-服務啟動)
4. [Worker 啟動](#4-worker-啟動)
5. [取得 Access Token](#5-取得-access-token)
6. [API 測試流程](#6-api-測試流程)
7. [注意事項與除錯](#7-注意事項與除錯)

---

## 1. 環境需求

| 項目 | 版本/說明 |
|------|-----------|
| Docker Desktop | 已安裝並運行 |
| Python | 3.10+ |
| VSCode | 已安裝 Docker Extension（選配） |
| Postman / curl | 用來打 API |
| `.env` 檔 | 放在 `backend/` 下，包含 Supabase 金鑰 |

### `.env` 範例（放 `backend/.env`）

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOi...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOi...
```

> [!CAUTION]
> `.env` **不可提交至 Git**。確認 `.gitignore` 已包含 `.env`。

---

## 2. Docker 啟動流程

### 2.1 在 VSCode 開啟 Terminal

按 `` Ctrl+` `` 開啟整合終端，或 `Terminal > New Terminal`。

### 2.2 啟動 Redis 容器

```powershell
# 移動到專案根目錄
cd d:\AIPE2_Goup\final

# 只啟動 Redis（背景模式）
docker compose up -d redis
```

確認 Redis 正常：

```powershell
docker compose ps
```

預期輸出：

```
NAME           SERVICE   STATUS    PORTS
final-redis-1  redis     running   0.0.0.0:6379->6379/tcp
```

### 2.3 驗證 Redis 連線

```powershell
docker exec -it final-redis-1 redis-cli ping
```

回傳 `PONG` 即成功。

### 2.4 （選配）啟動完整 Docker 環境

如果需要 frontend、OCR 等服務一起開：

```powershell
docker compose up -d
```

> [!NOTE]
> 本測試流程只需要 **Redis 容器**。Flask 和 Worker 跑在本機（非 Docker 內），
> 因為開發階段需要即時修改 code + 看 console log。

---

## 3. Flask 服務啟動

### 3.1 安裝 Python 相依

```powershell
cd d:\AIPE2_Goup\final\backend
pip install -r requirements.txt
```

### 3.2 啟動 Flask

```powershell
cd d:\AIPE2_Goup\final\backend\flask
python app.py
```

預期輸出：

```
------------------------------------------------
[System] 正在初始化 Flask 伺服器...
[System] 正在預載入 Qwen 模型...
[System]  模型載入完成！
------------------------------------------------

====== 目前註冊的所有 API 路徑 ======
auth.register: /api/auth/register
auth.login: /api/auth/login
user_preference.create_career_survey: /api/dream-jobs
analysis.start_analysis_task: /api/analysis/tasks
...
 * Running on http://127.0.0.1:5000
```

> [!WARNING]
> 如果 Qwen 模型載入失敗（記憶體不足或找不到），Flask 仍會繼續啟動，
> 但 OCR 功能會不可用。**不影響本次 API 測試**。

> [!TIP]
> 如果出現 `SUPABASE_URL 或 SUPABASE_SERVICE_ROLE_KEY` 錯誤，
> 代表 `backend/.env` 檔案不存在或內容缺失。

---

## 4. Worker 啟動

**另開一個 VSCode Terminal**（點 Terminal 右上角的 `+`）。

```powershell
cd d:\AIPE2_Goup\final\backend\flask
python -m worker.cv_worker
```

預期輸出：

```
[Worker] 建立 consumer group 'cv_workers' on 'cv_jobs'
[Worker worker-abc123] 啟動，等待任務... (stream=cv_jobs, group=cv_workers)
```

> [!IMPORTANT]
> Worker 必須在 Flask 之外獨立跑。它是消費 Redis Stream 的常駐進程。
> 不開 Worker = 任務永遠卡在 `queued`，不會變成 `done`。

---

## 5. 取得 Access Token

另開第三個 Terminal：

```powershell
cd d:\AIPE2_Goup\final\backend\test
python get_token.py
```

按提示輸入 Email 和 Password（已在 Supabase 註冊的帳號）。

```
=== Supabase Access Token Generator ===
Enter Email: test@example.com
Enter Password: ****
Login Successful!
------------------------------------------------------------
Access Token:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
------------------------------------------------------------
Expires In: 3600
User ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**複製 Access Token**，後續 Postman 要用。

> [!NOTE]
> Token 有效期限預設 **3600 秒（1 小時）**，過期需要重新登入取得。

---

## 6. API 測試流程

### Postman 準備

在 Postman 設定 Environment Variables：

| Variable | Value |
|----------|-------|
| `base_url` | `http://127.0.0.1:5000/api` |
| `token` | `<貼上 Access Token>` |

所有 Protected API 的 Header 都要加：

```
Authorization: Bearer {{token}}
```

---

### 6.1 Auth — 身份驗證

#### 註冊

```
POST {{base_url}}/auth/register
```

```json
{
  "email": "newuser@example.com",
  "password": "StrongP@ss123",
  "username": "testuser"
}
```

✅ 預期 `201` — 回傳 `"message": "註冊成功！請檢查您的信箱以驗證帳號。"`

#### 登入

```
POST {{base_url}}/auth/login
```

```json
{
  "email": "newuser@example.com",
  "password": "StrongP@ss123"
}
```

✅ 預期 `200` — 回傳 `auth.accessToken`（可用此 token 替換 Postman 的 `{{token}}`）

---

### 6.2 User Preference — 職缺意向（非同步）

#### Step 1: 提交問卷

```
POST {{base_url}}/dream-jobs
Authorization: Bearer {{token}}
```

```json
{
  "module_a": {
    "q1_languages": [{"name": "Python", "score": 2}],
    "q2_frontend": "基礎 HTML/CSS"
  },
  "module_b": {
    "q9_troubleshoot": "善用 Log 與搜尋引擎"
  },
  "module_c": {
    "q17_target_role": "資料科學家"
  },
  "module_d": {
    "q20_values_top3": ["薪資報酬"]
  }
}
```

✅ 預期 `202 Accepted`：

```json
{
  "job_id": "job_xxxxxxxxxxxx",
  "status": "queued"
}
```

**記下 `job_id`。**

#### Step 2: 輪詢結果

```
GET {{base_url}}/dream-jobs/{{job_id}}
Authorization: Bearer {{token}}
```

重複呼叫，直到 `status` 從 `queued` → `processing` → `done`：

✅ 完成時 `200`：

```json
{
  "job_id": "job_xxxxxxxxxxxx",
  "status": "done",
  "result": { "/* 分析結果 */" : "..." },
  "created_at": "...",
  "updated_at": "..."
}
```

❌ 失敗時 `200`（`status: "failed"`）：

```json
{
  "job_id": "job_xxxxxxxxxxxx",
  "status": "failed",
  "error": "超過重試上限 (3 次): ..."
}
```

> [!WARNING]
> 若 Worker 未啟動，`status` 會永遠停在 `queued`。

---

### 6.3 Resume — 履歷管理

#### 建立履歷

```
POST {{base_url}}/resumes/form
Authorization: Bearer {{token}}
```

```json
{
  "survey_id": 101,
  "structured_data": {
    "basics": {
      "name": "測試人員",
      "email": "test@example.com",
      "phone": "0912345678",
      "summary": "全端工程師，3 年 Python 經驗"
    },
    "education": [
      {
        "school": "台灣大學",
        "degree": "資訊工程學士",
        "start_date": "2018-09",
        "end_date": "2022-06"
      }
    ],
    "work_experience": [
      {
        "company": "Tech Corp",
        "position": "Backend Developer",
        "start_date": "2022-07",
        "end_date": "Present",
        "description": "負責 API 開發與系統維護"
      }
    ],
    "skills": ["Python", "Flask", "Docker", "PostgreSQL"],
    "languages": ["Chinese (Native)", "English (Professional)"]
  }
}
```

✅ 預期 `201`：

```json
{
  "resume_id": 203,
  "status": "completed",
  "last_updated": "2026-02-24T10:00:00Z"
}
```

#### 取得履歷

```
GET {{base_url}}/resumes/203
Authorization: Bearer {{token}}
```

✅ 預期 `200` — 回傳完整履歷 JSON（含 `structured_data`、`template_id`、ERD 欄位等）。

#### 更新履歷

```
PUT {{base_url}}/resumes/203
Authorization: Bearer {{token}}
```

```json
{
  "structured_data": {
    "basics": { "name": "更新後的名字" }
  },
  "template_id": 2,
  "style_settings": { "color": "#FF5733" }
}
```

✅ 預期 `200`：

```json
{
  "resume_id": 203,
  "updated_at": "...",
  "saved_settings": {
    "template_id": 2,
    "style_settings": { "color": "#FF5733" }
  }
}
```

#### 匯出履歷

```
GET {{base_url}}/resumes/203/export?format=pdf
Authorization: Bearer {{token}}
```

✅ 預期 `200` — Content-Type: `application/pdf`（目前為 Mock，回傳文字）。

---

### 6.4 Analysis — 履歷分析（非同步）

#### Step 1: 啟動分析任務

```
POST {{base_url}}/analysis/tasks
Authorization: Bearer {{token}}
```

```json
{
  "resume_id": 203,
  "survey_id": 101,
  "task_type": "resume_analysis" // 可傳入 resume_analysis (D-04建議) 或 resume_opt (D-03結果)
}
```

✅ 預期 `202 Accepted`：

```json
{
  "job_id": "job_xxxxxxxxxxxx",
  "status": "queued"
}
```

**記下 `job_id`。**

#### Step 2: 輪詢進度（推薦：一次取全部）

```
GET {{base_url}}/analysis/jobs/{{job_id}}
Authorization: Bearer {{token}}
```

✅ 完成時 `200`：

```json
{
  "job_id": "job_xxxxxxxxxxxx",
  "status": "done",
  "result": {
    "career_readiness_score": 85.0,
    "market_insights": {
      "summary": "後端工程師職缺近期需求增加...",
      "matched_keywords": ["Python", "Flask", "API Design"],
      "missing_keywords": ["Docker", "Kubernetes", "CI/CD"]
    }
  },
  "suggestions": {
    "career_path_suggestions": {
      "section_improvements": [
        {"section": "Experience", "suggestion": "建議加入量化數據..."},
        {"section": "Skills", "suggestion": "建議依熟練度分類..."}
      ],
      "overall_feedback": "整體履歷結構清晰..."
    },
    "skill_gap_analysis": [
      {"skill": "Kubernetes", "priority": "High"},
      {"skill": "React", "priority": "Medium"}
    ]
  }
}
```

#### Step 2 (替代): 個別查詢

查詢狀態：

```
GET {{base_url}}/analysis/tasks/{{job_id}}/status
```

查詢生成結果 (對應 `task_type: "resume_opt"`)：

```
GET {{base_url}}/analysis/tasks/{{job_id}}/results
```

查詢分析建議 (對應 `task_type: "resume_analysis"`)：

```
GET {{base_url}}/analysis/tasks/{{job_id}}/suggestions
```

> [!NOTE]
> `results` 和 `suggestions` 在任務尚未完成時會回傳 `202`，
> body 含 `"message": "尚未完成"`。

---

## 7. 注意事項與除錯

### 常見問題

| 問題 | 原因 | 解法 |
|------|------|------|
| `Connection refused` on Redis | Redis 容器沒起來 | `docker compose up -d redis` |
| Flask 啟動報 `SUPABASE_URL` 錯誤 | `.env` 缺少或路徑錯 | 確認 `backend/.env` 存在且有正確的金鑰 |
| API 回 `401 請先登入` | Token 過期或格式錯 | 重跑 `get_token.py`，注意 Header 是 `Bearer <token>` |
| 任務一直卡 `queued` | Worker 沒啟動 | 另開 Terminal 跑 `python -m worker.cv_worker` |
| 任務 `failed` | Worker 處理出錯（可能是 LLM 未注入） | 檢查 Worker Terminal 的錯誤訊息 |
| `BUSYGROUP` 警告 | Consumer Group 已存在 | 正常現象，不影響功能 |
| Port 5000 已佔用 | 另一個 Flask 還在跑 | 關掉舊的 Flask 進程 |
| Docker 起不來 | Docker Desktop 沒開 | 啟動 Docker Desktop，等到 running |

### 架構總覽

```
┌──────────────┐     POST /dream-jobs       ┌──────────────┐
│              │     POST /analysis/tasks    │              │
│   Postman    │ ──────────────────────────► │  Flask App   │
│   (Client)   │ ◄────────────────────────── │  :5000       │
│              │     202 { job_id }          │              │
└──────────────┘                            └──────┬───────┘
                                                   │ XADD
                                                   ▼
                                            ┌──────────────┐
                                            │  Redis       │
                                            │  Stream      │
                                            │  cv_jobs     │
                                            └──────┬───────┘
                                                   │ XREADGROUP
                                                   ▼
┌──────────────┐     GET /analysis/jobs/x    ┌──────────────┐
│              │ ──────────────────────────► │              │
│   Postman    │ ◄────────────────────────── │  cv_worker   │
│   (Poll)     │     200 { status: done }   │  (常駐進程)   │
└──────────────┘                            └──────────────┘
```

### Redis 資料結構

| Key Pattern | Type | 說明 |
|-------------|------|------|
| `job:{job_id}` | Hash | 任務狀態、輸入資料、結果 |
| `cv_jobs` | Stream | 任務佇列 |
| `cv_jobs_dlq` | Stream | 死信佇列（超過 3 次重試） |

### Job 狀態生命週期

```
queued ──► processing ──► done
                     └──► failed → cv_jobs_dlq (DLQ)
```

- **queued**: 已排入 Stream，等待 Worker 取走
- **processing**: Worker 正在處理
- **done**: 處理完成，`result` 和 `suggestions` 已寫入
- **failed**: 超過 MAX_RETRY (3) 次，訊息轉入 DLQ

### 停止服務

```powershell
# 停止 Worker（按 Ctrl+C）

# 停止 Flask（按 Ctrl+C）

# 停止 Docker
docker compose down
```

### 清除 Redis 資料（需要時）

```powershell
docker exec -it final-redis-1 redis-cli FLUSHALL
```
