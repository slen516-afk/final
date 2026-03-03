# Career Pilot 後端履歷 API 文件 (v2.0)

| 項目          | 內容                                |
| ------------- | ----------------------------------- |
| 文件版本      | v2.0                                |
| Base URL      | `/api`                            |
| 日期格式      | ISO 8601 (`YYYY-MM-DDTHH:mm:ssZ`) |
| 回應格式      | JSON                                |
| Auth Provider | Supabase                            |
| Job Queue     | Redis Stream (`cv_jobs`)          |

> [!IMPORTANT]
> **分析模組 (D)** 與 **職缺意向模組 (B)** 為 Redis Stream 非同步架構。
> 提交請求後回傳 `job_id`（HTTP 202），前端每10~20秒需**輪詢 (polling)** 取得結果。

---

## 目錄

1. [環境準備](#1-環境準備)
2. [職缺意向 (User Preference)](#2-職缺意向-user-preference)
3. [履歷管理 (Resume)](#3-履歷管理-resume)
4. [履歷分析 (Analysis)](#4-履歷分析-analysis)
5. [匯出 (Export)](#5-匯出-export)
6. [架構說明與除錯](#6-架構說明與除錯)

---

## 1. 環境準備

### 1.1 所需環境

| 項目           | 版本/說明                                |
| -------------- | ---------------------------------------- |
| Docker Desktop | 已安裝並運行                             |
| Python         | 3.10+                                    |
| Postman / curl | 用來打 API                               |
| `.env` 檔    | 放在 `backend/` 下，包含 Supabase 金鑰 |

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOi...
```

> [!CAUTION]
> `.env` **不可提交至 Git**。確認 `.gitignore` 已包含 `.env`。

### 1.2 啟動 Redis

```powershell
docker compose up -d redis
```

### 1.3 啟動 Flask

```powershell
cd .\final\backend\
python main.py
```

### 1.4 啟動 Worker

**另開一個 Terminal**：

```powershell
cd .\final\backend\flask
# 如要啟動mock模式
# CMD: set MOCK_MODE=true
# PowerShell: $env:MOCK_MODE="true"
python -m worker.cv_worker
```

### 1.5 取得 Access Token

```powershell
cd .final\backend\test\
python get_token.py
```

> [!NOTE]
> Token 有效期限 **3600 秒（1 小時）**，過期需重新取得。

### 1.6 Postman 環境設定

| Variable     | Value                         |
| ------------ | ----------------------------- |
| `base_url` | `http://127.0.0.1:8000/api` |
| `token`    | `<貼上 Access Token>`       |

所有 Protected API Header：

```http
Authorization: Bearer {{token}}
```

---

## 2. 職缺意向 (User Preference)

> **架構**: 提交問卷 → Redis Stream → cv_worker 處理 → 前端 Polling 取結果

### B-01 提交職能問卷

- **權限**: Protected
- **Method**: `POST`
- **Path**: `/dream-jobs`
- **用途**: 職涯偏好問卷，直接照 model 要求格式傳入，不做額外處理。

| 參數           | 類型 | 必填 | 說明                         |
| -------------- | ---- | ---- | ---------------------------- |
| `module_a`   | JSON | Yes  | 專業技能 (Skills, q1~q8)     |
| `module_b`   | JSON | Yes  | 軟實力 (Soft Skills, q9~q15) |
| `module_c`   | JSON | Yes  | 現況與目標 (q16~q19)         |
| `module_d`   | JSON | Yes  | 價值觀與學習風格 (q20~q23)   |
| `trait_data` | JSON | No   | 人格特質分析結果             |

**Request Body（完整範例）**

```json
{
  "module_a": {
    "q1_languages": [
      {"name": "Python", "score": 5},
      {"name": "SQL",    "score": 4},
      {"name": "Git",    "score": 4}
    ],
    "q2_frontend": "unfamiliar",
    "q3_backend": "distributed_system",
    "q4_database": ["rdbms_sql", "key_value_cache"],
    "q5_devops": "k8s_cicd",
    "q6_ai_data": "api_consumer",
    "q7_security": "framework_default",
    "q8_domain": "電子商務"
  },
  "module_b": {
    "q9_troubleshoot": "incident_analysis",
    "q10_tech_choice": "tradeoff_analysis",
    "q11_communication": "alternative_solution",
    "q12_code_review": "architecture_solid",
    "q13_learning": "deep_dive_sharing",
    "q14_process": "process_optimization",
    "q15_english": "global_comm"
  },
  "module_c": {
    "q16_current_level": "senior",
    "q17_target_role": "backend",
    "q18_industry": "product_company",
    "q19_search_status": "passive_open"
  },
  "module_d": {
    "q20_values_top3": ["technical_growth", "social_impact", "financial_reward"],
    "q21_pressure": "consider_short_term",
    "q22_career_type": "specialist",
    "q23_learning_style": ["official_docs", "hands_on_projects"]
  },
  "trait_data": {
    "trait_raw_responses": {"Q1": "C", "Q2": "A", "Q3": "B", "Q4": "C", "Q5": "A", "Q6": "B", "Q7": "B", "Q8": "A", "Q9": "A", "Q10": "A"},
    "trait_calculation_debug": {
      "structure_raw": 10,
      "ambiguity_raw": 0,
      "decision_raw": 2,
      "learning_raw": 4,
      "transfer_raw": 5
    },
    "trait_normalized_scores": {
      "structure": 95,
      "ambiguity": 35,
      "decision": 50,
      "learning": 60,
      "transfer": 85
    },
    "primary_archetype": "STRUCTURE_ARCHITECT",
    "secondary_archetypes": ["CROSS_DOMAIN_INTEGRATOR"],
    "trait_created_at": "2026-02-15T10:00:00Z"
  }
}
```

**Response 202 Accepted**

```json
{
  "job_id": "job_a1b2c3d4e5f6",
  "status": "queued"
}
```

### B-02 輪詢問卷分析結果

- **權限**: Protected
- **Method**: `GET`
- **Path**: `/dream-jobs/{job_id}`

**Response 200 OK — 進行中**

```json
{
  "job_id": "job_a1b2c3d4e5f6",
  "status": "processing",
  "created_at": "2026-03-02T06:56:11+00:00",
  "updated_at": "2026-03-02T06:56:15+00:00"
}
```

**Response 200 OK — 完成（`result` 為 `CareerReport` 結構）**

```json
{
  "job_id": "job_a1b2c3d4e5f6",
  "status": "done",
  "result": {
    "report_metadata": {
      "user_id": "2",
      "timestamp": "2026-03-02T06:56:11.634Z",
      "version": "1.0"
    },
    "preliminary_summary": {
      "core_insight": "使用者在前端開發方面具有豐富的經驗，特別是在使用 React 和 Vue.js 上，並且有實際的優化經驗，這是其在市場中的競爭優勢。"
    },
    "radar_chart": {
      "dimensions": [
        {"axis": "前端開發", "score": 4.0},
        {"axis": "後端開發", "score": 2.3},
        {"axis": "運維部署", "score": 2.0},
        {"axis": "AI與數據", "score": 0.5},
        {"axis": "工程品質", "score": 3.0},
        {"axis": "軟實力",   "score": 3.0}
      ]
    },
    "gap_analysis": {
      "current_status": {
        "self_assessment": "中階工程師 (Mid Level)",
        "actual_level": "中階工程師 (Mid Level)",
        "cognitive_bias": "使用者自評為中階工程師，與實際技術評估一致。然而後端開發經驗不足，建議加強 Node.js 或其他後端框架。"
      },
      "target_position": {
        "role": "領航員分析您適合的職類為 - 前端工程師",
        "match_score": "89%",
        "gap_description": "後端開發經驗不足，對運維和安全性知識的掌握也相對有限。需要加強 Node.js、CI/CD 和雲服務的了解。"
      }
    },
    "action_plan": {
      "short_term": "參加 Node.js 或 Express.js 的線上課程，並開始使用這些技術開發小型後端應用。",
      "mid_term": "加入全棧開發專案，嘗試使用 Docker 和 CI/CD 工具來部署應用。",
      "long_term": "考取相關的雲服務證照（如 AWS Certified Developer）。"
    }
  },
  "created_at": "2026-03-02T06:56:11+00:00",
  "updated_at": "2026-03-02T06:58:30+00:00"
}
```

**Response 200 OK — 失敗**

```json
{
  "job_id": "job_a1b2c3d4e5f6",
  "status": "failed",
  "error": "超過重試上限 (3 次): ..."
}
```

> [!WARNING]
> 若 Worker 未啟動，`status` 會永遠停在 `queued`。

---

## 3. 履歷管理 (Resume)

### C-02 建立履歷（表單填寫）

- **權限**: Protected
- **Method**: `POST`
- **Path**: `/resumes/form`

| 參數                | 類型 | 必填 | 說明             |
| ------------------- | ---- | ---- | ---------------- |
| `structured_data` | JSON | Yes  | 完整履歷結構物件 |

**Request Body**

```json
{
  "structured_data": {
    "basics": {
      "name": "測試人員",
      "email": "test@example.com",
      "phone": "0912345678",
      "location": "Taipei, Taiwan",
      "summary": "全端工程師，3 年 Python/Flask 開發經驗"
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

**Response 201 Created**

```json
{
  "resume_id": 203,
  "status": "completed",
  "last_updated": "2026-03-02T10:00:00Z"
}
```

### C-04 取得履歷詳情

- **權限**: Protected
- **Method**: `GET`
- **Path**: `/resumes/{id}`

**Response 200 OK**

```json
{
  "resume_id": 203,
  "user_id": "uuid-string",
  "template_id": 1,
  "resume_type": "general",
  "structured_data": {
    "basics": {"name": "測試人員", "email": "test@example.com"},
    "education": [{"school": "台灣大學", "degree": "學士"}],
    "work_experience": [{"company": "Tech Corp", "position": "Backend Developer"}],
    "skills": ["Python", "Flask", "Docker"]
  },
  "is_primary": true,
  "created_at": "2026-03-02T10:00:00Z",
  "updated_at": "2026-03-02T10:00:00Z"
}
```

### C-05 更新履歷（寫入 `resume_optimization`）

- **權限**: Protected
- **Method**: `PUT`
- **Path**: `/resumes/{id}`
- **用途**: 每次 PUT 在 `resume_optimization` 新增一筆，`optimization_version` 整數自動遞增 (1, 2, 3...)。

| 參數                        | 類型      | 必填 | 說明                                    |
| --------------------------- | --------- | ---- | --------------------------------------- |
| `professional_summary`    | String    | No   | 專業總結                                |
| `professional_experience` | list[str] | No   | 工作經歷（字串陣列）                    |
| `core_skills`             | list[str] | No   | 核心技能                                |
| `projects`                | list[str] | No   | 專案                                    |
| `education`               | list[str] | No   | 學歷                                    |
| `autobiography`           | String    | No   | 自傳                                    |
| `style_settings`          | JSON      | No   | 視覺設定（如 `{"color": "#1A73E8"}`） |

**Request Body（完整範例）**

```json
{
  "professional_summary": "全端工程師，擁有 3 年 Python/Flask 與 React 開發經驗，主導日處理 50 萬請求後端系統重構，熟悉 CI/CD、容器化部署與雲端服務。",
  "professional_experience": [
    "Tech Corp | Senior Backend Developer | 2022-07 ~ Present | 主導 RESTful API 重構，回應時間從 800ms 降至 120ms；設計 Redis 快取層降低資料庫負載 60%",
    "Startup Inc. | Junior Developer | 2021-01 ~ 2022-06 | 開發內部管理後台（React + Flask），支援 50+ 使用者同時操作"
  ],
  "core_skills": [
    "Python", "Flask", "FastAPI", "React", "TypeScript",
    "PostgreSQL", "Redis", "Docker", "Kubernetes", "CI/CD", "REST API", "AWS"
  ],
  "projects": [
    "Career Pilot — AI 職涯規劃平台，整合 LLM 進行履歷分析，使用 Redis Stream 實作非同步任務佇列",
    "Smart Inventory System — 智慧庫存管理系統，FastAPI + Celery 處理批次匯入任務"
  ],
  "education": [
    "國立台灣大學 | 資訊工程學系 | 學士 | 2022-06"
  ],
  "autobiography": "熱衷於解決複雜工程問題的全端工程師，主導核心系統微服務化重構，系統承載能力提升 4 倍。",
  "style_settings": {
    "color": "#1A73E8"
  }
}
```

**Response 201 Created**

```json
{
  "optimization_id": 15,
  "resume_id": 203,
  "optimization_version": "2",
  "template_color": "#1A73E8",
  "created_at": "2026-03-02T04:20:00+00:00"
}
```

### C-06 取得某份履歷的所有優化版本列表

- **權限**: Protected
- **Method**: `GET`
- **Path**: `/resumes/{id}/versions`
- **用途**: 取得該履歷所有的優化版本紀錄，依版號遞減排序（最新的在最前）。

**Response 200 OK**

```json
{
  "resume_id": 203,
  "versions": [
    {
      "optimization_id": 15,
      "optimization_version": "2",
      "template_color": "#1A73E8",
      "created_at": "2026-03-02T04:20:00+00:00"
    },
    {
      "optimization_id": 14,
      "optimization_version": "1",
      "template_color": null,
      "created_at": "2026-03-02T04:15:00+00:00"
    }
  ]
}
```

### C-07 取得特定版本的優化履歷內容

- **權限**: Protected
- **Method**: `GET`
- **Path**: `/resumes/{id}/versions/{version}`
- **用途**: 取得特定版本號的完整優化履歷資料。

**Response 200 OK**

```json
{
  "optimization_id": 15,
  "resume_id": 203,
  "user_id": 2,
  "optimization_version": "2",
  "professional_summary": "全端工程師...",
  "professional_experience": [
    "Tech Corp | Senior Backend Developer"
  ],
  "core_skills": ["Python", "Flask", "React"],
  "projects": ["Career Pilot"],
  "education": ["國立台灣大學"],
  "autobiography": "熱衷工程問題...",
  "template_color": "#1A73E8",
  "created_at": "2026-03-02T04:20:00+00:00"
}
```

**錯誤碼**

| HTTP Code | 情境                             |
| --------- | -------------------------------- |
| `404`   | 找不到該版本 (Version not found) |

---

## 4. 履歷分析 (Analysis)

> **架構**: 提交任務 → Redis Stream → cv_worker 處理 → 前端 Polling 取結果

### D-01 啟動履歷分析任務

- **權限**: Protected
- **Method**: `POST`
- **Path**: `/analysis/tasks`
- **用途**: 觸發 AI 進行履歷分析或優化（任務排入 Redis Stream）。

| 參數          | 類型   | 必填          | 說明                                                                   |
| ------------- | ------ | ------------- | ---------------------------------------------------------------------- |
| `task_type` | String | **Yes** | `resume_analysis`（D-03 分析建議）或 `resume_opt`（D-04 優化結果） |

**Request Body**

```json
{
  "task_type": "resume_analysis"
}
```

**Response 202 Accepted**

```json
{
  "job_id": "job_a1b2c3d4e5f6",
  "status": "queued"
}
```

### D-02a 輪詢任務進度

- **權限**: Protected
- **Method**: `GET`
- **Path**: `/analysis/jobs/{job_id}`
- **用途**: 一次取得完整狀態 + result + suggestions。

**Response 200 OK — 處理中**

```json
{
  "job_id": "job_a1b2c3d4e5f6",
  "status": "processing",
  "created_at": "2026-03-02T08:00:00+00:00",
  "updated_at": "2026-03-02T08:00:05+00:00"
}
```

**Response 200 OK — 完成（`resume_analysis`）**

```json
{
  "job_id": "job_a1b2c3d4e5f6",
  "status": "done",
  "result": {},
  "suggestions": {
    "candidate_positioning": "企業視角下這份履歷目前看起來像一位具備紮實後端基礎的中階開發者...",
    "target_role_gap_summary": "與目標後端工程師職位的整體落差主要在 K8s 與 CI/CD 實操經驗...",
    "overall_strengths": ["Python/Flask 後端經驗紮實", "有量化成果描述"],
    "overall_weaknesses": ["缺乏容器編排與雲端部署實際案例"],
    "critical_issues": [
      {
        "section": "技能專長",
        "original_text": "熟悉 Docker",
        "issue_type": ["描述模糊", "ATS 關鍵字缺失"],
        "severity": ["可優化"],
        "diagnosis_dimension": "技術深度",
        "issue_reason": "僅列出工具名稱，未說明使用場景與規模",
        "improvement_direction": ["改為：使用 Docker 容器化 3 個微服務，部署至 AWS ECS"]
      }
    ],
    "ats_risk_level": "中",
    "screening_outcome_prediction": "企業 6 秒快速掃描後，後端技能區塊具備基本吸引力，但缺少量化結果...",
    "recommended_next_actions": ["補充 Docker/K8s 實際部署案例", "在工作經歷加入量化數據"]
  },
  "created_at": "2026-03-02T08:00:00+00:00",
  "updated_at": "2026-03-02T08:02:10+00:00"
}
```

**Response 200 OK — 完成（`resume_opt`）**

```json
{
  "job_id": "job_a1b2c3d4e5f6",
  "status": "done",
  "result": {
    "professional_summary": "精簡的專業總結，包含核心價值與推薦職缺的關鍵字",
    "professional_experience": [
      "Tech Corp | Senior Backend Developer | 2022-07 ~ Present | 主導 RESTful API 重構，回應時間從 800ms 降至 120ms"
    ],
    "core_skills": ["Python", "Flask", "Docker", "PostgreSQL", "CI/CD", "REST API"],
    "projects": [
      "Career Pilot — AI 職涯規劃平台，整合 LLM 進行履歷分析，Redis Stream 非同步架構"
    ],
    "education": ["國立台灣大學 | 資訊工程學系 | 學士 | 2022-06"],
    "autobiography": "保留使用者原本風格的優化後完整自傳"
  },
  "suggestions": {},
  "created_at": "2026-03-02T08:00:00+00:00",
  "updated_at": "2026-03-02T08:02:10+00:00"
}
```

**Response 200 OK — 失敗**

```json
{
  "job_id": "job_a1b2c3d4e5f6",
  "status": "failed",
  "error": "超過重試上限 (3 次): ..."
}
```

---

## 5. 匯出 (Export)

### E-01 匯出履歷文件

- **權限**: Protected
- **Method**: `GET`
- **Path**: `/resumes/{id}/export`
- **用途**: 從 `resume_optimization` 取最新（或指定版本）優化履歷，下載 PDF/DOCX。

```http
GET /api/resumes/{resume_id}/export?format={pdf|docx}
Authorization: Bearer <token>
```

**Query Parameters**

| 參數        | 必填 | 預設    | 說明                                 |
| ----------- | ---- | ------- | ------------------------------------ |
| `format`  | 否   | `pdf` | 匯出格式：`pdf`、`docx`          |
| `version` | 否   |         | 指定優化版本號（整數），未帶則取最新 |

**Response — PDF**

- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename=resume_{id}.pdf`
- 回傳 PDF 二進位串流

**Response — DOCX**

- Content-Type: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- Content-Disposition: `attachment; filename=resume_{id}.docx`
- 回傳 DOCX 二進位串流

**錯誤碼**

| HTTP Code | 情境                         |
| --------- | ---------------------------- |
| `400`   | 不支援的 format              |
| `401`   | 未登入 / Token 失效          |
| `404`   | 找不到履歷 或 不屬於該使用者 |
| `500`   | 伺服器錯誤                   |

> **注意**：不要在 Headers 手動加 `Accept`，讓 Postman 自動處理即可。
>
> **相依套件**：`fpdf2`（PDF）、`python-docx`（DOCX）

---

## 6. 架構說明與除錯

### 系統架構圖

```text
┌──────────────┐   POST /dream-jobs          ┌──────────────┐
│              │   POST /analysis/tasks      │              │
│   Client     │ ─────────────────────────► │  Flask App   │
│  (Postman)   │ ◄───────────────────────── │  :8000       │
│              │   202 { job_id }            │              │
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
┌──────────────┐   GET /analysis/jobs/{id}  ┌──────────────┐
│   Client     │ ─────────────────────────► │ cv_worker    │
│   (Poll)     │ ◄───────────────────────── │ (常駐進程)    │
└──────────────┘   200 { status: done }    └──────────────┘
```

### Redis 資料結構

| Key Pattern      | Type   | 說明                      |
| ---------------- | ------ | ------------------------- |
| `job:{job_id}` | Hash   | 任務狀態、輸入資料、結果  |
| `cv_jobs`      | Stream | 任務佇列                  |
| `cv_jobs_dlq`  | Stream | 死信佇列（超過 3 次重試） |

### Job 狀態生命週期

```text
queued ──► processing ──► done
                     └──► failed → cv_jobs_dlq (DLQ)
```

- **queued**: 已排入 Stream，等待 Worker 取走
- **processing**: Worker 正在處理
- **done**: 處理完成，`result`/`suggestions` 已寫入
- **failed**: 超過 MAX_RETRY (3 次)，訊息轉入 DLQ

### 常見問題

| 問題                               | 原因                  | 解法                                                     |
| ---------------------------------- | --------------------- | -------------------------------------------------------- |
| `Connection refused` on Redis    | Redis 容器沒起來      | `docker compose up -d redis`                           |
| Flask 啟動報 `SUPABASE_URL` 錯誤 | `.env` 缺少或路徑錯 | 確認 `backend/.env` 存在且有正確的金鑰                 |
| API 回 `401 請先登入`            | Token 過期或格式錯    | 重跑 `get_token.py`，注意 Header 是 `Bearer <token>` |
| 任務一直卡 `queued`              | Worker 沒啟動         | 另開 Terminal 跑 `python -m flask.worker.cv_worker`    |
| 任務 `failed`                    | Worker 處理出錯       | 檢查 Worker Terminal 的錯誤訊息                          |
| `BUSYGROUP` 警告                 | Consumer Group 已存在 | 正常現象，不影響功能                                     |
| Port 8000 已佔用                   | 另一個 Flask 還在跑   | 關掉舊的 Flask 進程                                      |

### 停止服務

```powershell
# 停止 Worker（按 Ctrl+C）
# 停止 Flask（按 Ctrl+C）
# 停止 Docker
docker compose down

# 清除 Redis 資料（需要時）
docker exec -it final-redis-1 redis-cli FLUSHALL
```
