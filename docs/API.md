# Career Pilot API 規格說明書 (v2.0)

| **項目**          | **內容**                      |
| ----------------------- | ----------------------------------- |
| **文件版本**      | v2.0                                |
| **對應 ERD**      | v2.0                                |
| **Base URL**      | `/api`                            |
| **日期格式**      | ISO 8601 (`YYYY-MM-DDTHH:mm:ssZ`) |
| **回應格式**      | JSON                                |
| **Auth Provider** | Supabase                            |
| **Job Queue**     | Redis Stream (`cv_jobs`)            |

> [!IMPORTANT]
> v2.0 起，**分析模組 (D)** 與 **職缺意向模組 (B)** 改為 Redis Stream 非同步架構。
> 提交請求後回傳 `job_id`（HTTP 202），前端需**輪詢 (polling)** 取得結果。

---

## 1. A. 身份驗證模組 (Authentication)

本模組採用 **Supabase** 進行身份管理。所有受保護的 API (Protected) 需在 Header 帶入 Supabase 核發的 Access Token。

### 通用 Header 規範

| **Key**           | **Value**           | **說明**          |
| ----------------------- | ------------------------- | ----------------------- |
| **Authorization** | `Bearer <access_token>` | 必須包含 `Bearer`前綴 |

### A-01 用戶註冊

* **權限** : Public
* **Method** : `POST`
* **Path** : `/auth/register`

**Request Body**

```json
{
  "email": "user@example.com",
  "password": "your_password",
  "username": "your_username"
}
```

**Response Body (201 Created)**

```json
{
  "message": "註冊成功！請檢查您的信箱以驗證帳號。",
  "needsConfirmation": true
}
```

### A-02 用戶登入

* **權限** : Public
* **Method** : `POST`
* **Path** : `/auth/login`

**Request Body**

```json
{
  "email": "user@example.com",
  "password": "your_password"
}
```

**Response Body (200 OK)**

```json
{
  "user": {
    "id": "uuid-string",
    "role": "user"
  },
  "auth": {
    "accessToken": "eyJhbGci...",
    "refreshToken": "...",
    "expiresIn": 3600
  },
  "security": {
    "mfaRequired": false,
    "passwordExpired": false
  }
}
```

### A-03 取得個人資料

* **權限** : Protected
* **Method** : `GET`
* **Path** : `/auth/profile`

**Response Body (200 OK)** — 回傳 Supabase `users` table 該用戶的完整資料。

---

## 2. B. 職缺意向模組 (User Preference)

> **架構**: 提交問卷 → Redis Stream → cv_worker 處理 → 前端 Polling 取結果

### B-01 提交目標工作設定

* **權限** : Protected
* **Method** : `POST`
* **Path** : `/dream-jobs`
* **用途** : 儲存使用者職涯偏好，透過 Redis Stream 排隊進行分析。

| **請求部分** | **參數** | **類型** | **必填** | **說明**                      |
| ------------------ | -------------- | -------------- | -------------- | ----------------------------------- |
| **Header**   | Authorization  | String         | Yes            |                                     |
| **Body**     | module_a       | JSON           | Yes            | 專業技能 (Skills) |
| **Body**     | module_b       | JSON           | Yes            | 軟實力 (Soft Skills) |
| **Body**     | module_c       | JSON           | Yes            | 現況與目標 (Current Status) |
| **Body**     | module_d       | JSON           | Yes            | 價值觀與風格 (Values) |

**Response Body (202 Accepted)**

```json
{
  "job_id": "job_a1b2c3d4e5f6",
  "status": "queued"
}
```

### B-02 輪詢問卷分析進度

* **權限** : Protected
* **Method** : `GET`
* **Path** : `/dream-jobs/{job_id}`
* **用途** : 前端定時輪詢，取得問卷分析狀態與結果。

**Response Body (200 OK) — 進行中**

```json
{
  "job_id": "job_a1b2c3d4e5f6",
  "status": "processing",
  "created_at": "2026-02-24T08:00:00+00:00",
  "updated_at": "2026-02-24T08:00:05+00:00"
}
```

**Response Body (200 OK) — 完成**

```json
{
  "job_id": "job_a1b2c3d4e5f6",
  "status": "done",
  "created_at": "...",
  "updated_at": "...",
  "result": { "/* 分析結果 JSON */" : "..." }
}
```

**Response Body (200 OK) — 失敗**

```json
{
  "job_id": "job_a1b2c3d4e5f6",
  "status": "failed",
  "error": "超過重試上限 (3 次): ..."
}
```

### Job 狀態生命週期

```text
queued → processing → done
                   ↘ failed (送入 DLQ)
```

---

## 3. C. 履歷上傳與管理模組 (Resume Management)

對應資料表：`RESUME`, `UPLOAD_EVENT`, `OCR_RESULT`

### C-02 [路徑 B] 建立履歷 (表單填寫)

* **權限** : Protected
* **Method** : `POST`
* **Path** : `/resumes/form`
* **用途** : 接收前端表單填寫的完整履歷資料，直接存入資料庫，跳過 OCR 流程。

### 請求參數 (Request)

| **請求部分** | **參數名稱**   | **類型** | **必填** | **說明**                |
| ------------------ | -------------------- | -------------- | -------------- | ----------------------------- |
| **Header**   | Authorization        | String         | **Yes**  | Bearer Token (Supabase)       |
| **Body**     | survey_id           | Int            | No       | 關聯的問卷 ID（選填）        |
| **Body**     | **structured_data** | JSON           | **Yes**  | 完整的履歷結構物件 |

### Request Body 範例

```json
{
  "structured_data": {
    "basics": {
      "name": "王小明",
      "email": "wang@example.com",
      "phone": "0912345678",
      "location": "Taipei, Taiwan",
      "summary": "後端工程師，擁有 3 年 Python 開發經驗..."
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
        "description": "負責 API 開發與系統維護..."
      }
    ],
    "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
    "languages": ["Chinese (Native)", "English (Professional)"]
  }
}
```

### 回應參數 (Response) - 201 Created

| **參數名稱**    | **類型** | **說明**                           |
| --------------------- | -------------- | ---------------------------------------- |
| **resume_id**    | Int            | 新建立的履歷 ID                          |
| **status**      | String         | 固定回傳 `"completed"`(因無需等待 OCR) |
| **last_updated** | String         | 建立時間 (ISO 8601)                      |

```json
{
  "resume_id": 203,
  "status": "completed",
  "last_updated": "2026-01-30T10:00:00Z"
}
```

### C-04 取得履歷詳情

* **權限** : Protected
* **Method** : `GET`
* **Path** : `/resumes/{id}`

| **請求部分** | **參數** | **類型** | **必填** | **說明** |
| ------------------ | -------------- | -------------- | -------------- | -------------- |
| **Header**   | Authorization  | String         | Yes            |                |
| **Path**     | id             | Int            | Yes            | Resume ID      |

**Response Body (200 OK)**

```json
{
  "resume_id": 202,
  "user_id": "uuid-string",
  "template_id": 1,
  "resume_type": "general",
  "structured_data": {
    "personal_info": { "name": "王小明", "email": "wang@example.com" },
    "education": [{ "school": "台灣大學", "degree": "學士" }],
    "work_experience": [],
    "skills": ["Python", "Docker"]
  },
  "normalized_data": {},
  "vector_id": null,
  "is_embedded": false,
  "is_primary": true,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-02T00:00:00Z"
}
```

### C-05 用戶更新/確認履歷內容（全局覆蓋 → `resume_optimization`）

* **權限** : Protected
* **Method** : `PUT`
* **Path** : `/resumes/{id}`
* **用途** : 每次 PUT 會在 `resume_optimization` 新增一筆，`optimization_version` 整數自動遞增 (1, 2, 3...)。

| **請求部分** | **參數**   | **類型** | **必填** | **說明**          |
| ------------------ | ---------------- | -------------- | -------------- | ----------------------- |
| **Header**   | Authorization    | String         | Yes            |                         |
| **Path**     | id               | Int            | Yes            | Resume ID               |
| **Body**     | professional_summary | String      | No             | 專業總結 |
| **Body**     | professional_experience | list[str]  | No             | 工作經歷 (string array) |
| **Body**     | core_skills     | list[str]      | No             | 核心技能 (string array) |
| **Body**     | projects        | list[str]      | No             | 專案 (string array) |
| **Body**     | education       | list[str]      | No             | 學歷 (string array) |
| **Body**     | autobiography   | String         | No             | 自傳 |
| **Body**     | style_settings  | JSON           | No             | 視覺設定 (e.g. `{"color": "#1A73E8"}`) |

**Response Body (201 Created)**

```json
{
  "optimization_id": 15,
  "resume_id": 202,
  "optimization_version": "2",
  "template_color": "#1A73E8",
  "created_at": "2026-03-02T04:20:00+00:00"
}
```

---

## 4. D. 履歷分析模組 (Analysis)

> **架構**: 提交任務 → Redis Stream → cv_worker 處理 → 前端 Polling 取結果

對應資料表：`CAREER_ANALYSIS_REPORT`, `SKILL_GAP`

### D-01 啟動履歷分析任務

* **權限** : Protected
* **Method** : `POST`
* **Path** : `/analysis/tasks`
* **用途** : 觸發 AI 進行履歷分析或優化（任務排入 Redis Stream）。

| **請求部分** | **參數** | **類型** | **必填** | **說明** |
| ------------------ | -------------- | -------------- | -------------- | -------------- |
| **Header**   | Authorization  | String         | Yes            |                |
| **Body**     | task_type     | String         | **Yes**        | `resume_analysis`（D-03 分析建議）或 `resume_opt`（D-04 優化結果） |
| **Body**     | resume_id     | Int            | No             | 選填 metadata    |
| **Body**     | survey_id     | Int            | No             | 選填 metadata    |

**Response Body (202 Accepted)**

```json
{
  "job_id": "job_a1b2c3d4e5f6",
  "status": "queued"
}
```

### D-02a 輪詢任務進度（推薦）

* **權限** : Protected
* **Method** : `GET`
* **Path** : `/analysis/jobs/{job_id}`
* **用途** : 前端定時輪詢，一次取得完整狀態 + 結果。

**Response Body (200 OK) — 處理中**

```json
{
  "job_id": "job_a1b2c3d4e5f6",
  "status": "processing",
  "created_at": "...",
  "updated_at": "..."
}
```

**Response Body (200 OK) — 完成**

```json
{
  "job_id": "job_a1b2c3d4e5f6",
  "status": "done",
  "created_at": "...",
  "updated_at": "...",
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
      "section_improvements": [...],
      "overall_feedback": "..."
    },
    "skill_gap_analysis": [
      { "skill": "Kubernetes", "priority": "High" },
      { "skill": "React", "priority": "Medium" }
    ]
  }
}
```

**Response Body (200 OK) — 失敗**

```json
{
  "job_id": "job_a1b2c3d4e5f6",
  "status": "failed",
  "error": "超過重試上限 (3 次): ..."
}
```

### D-02b 查詢任務狀態（僅狀態）

* **權限** : Protected
* **Method** : `GET`
* **Path** : `/analysis/tasks/{task_id}/status`

```json
{
  "task_id": "job_a1b2c3d4e5f6",
  "status": "processing"
}
```

### D-03 取得履歷分析建議 (Suggestions Only)

* **權限** : Protected
* **Method** : `GET`
* **Path** : `/analysis/tasks/{task_id}/suggestions`
* **用途** : 取得 `task_type: "resume_analysis"` 時的產出建議。

> 僅限 `task_type: "resume_analysis"` 的任務，否則回傳 **400**。
> 若尚未完成，回傳 **202** 並帶 `"message": "尚未完成"`。

**Response Body (200 OK)** — `ResumeAnalysis` 結構

```json
{
  "candidate_positioning": "企業視角下這份履歷目前看起來像...",
  "target_role_gap_summary": "與目標職位之間的整體落差...",
  "overall_strengths": ["履歷中最具說服力的優勢點"],
  "overall_weaknesses": ["整體最影響錄取率的核心弱點"],
  "critical_issues": [
    {
      "section": "技能專長",
      "original_text": "使用者履歷中的原始文字",
      "issue_type": ["描述模糊", "ATS 關鍵字缺失"],
      "severity": ["可優化"],
      "diagnosis_dimension": "...",
      "issue_reason": "...",
      "improvement_direction": ["可執行的改善方向"]
    }
  ],
  "ats_risk_level": "中",
  "screening_outcome_prediction": "模擬企業 6–10 秒快速掃描後的篩選結果...",
  "recommended_next_actions": ["下一步行動建議"]
}
```

### D-04 取得履歷優化結果 (Results Only)

* **權限** : Protected
* **Method** : `GET`
* **Path** : `/analysis/tasks/{task_id}/results`
* **用途** : 取得 `task_type: "resume_opt"` 時模型生成的完整履歷結果。

> 僅限 `task_type: "resume_opt"` 的任務，否則回傳 **400**。
> 若尚未完成，回傳 **202** 並帶 `"message": "尚未完成"`。

**Response Body (200 OK)** — `ResumeOptimization` 結構

```json
{
  "professional_summary": "精簡的專業總結，包含核心價值與推薦職缺的關鍵字",
  "professional_experience": [
    "公司名稱 | 職稱 | 年資 | 以 STAR 原則重新撰寫的工作描述"
  ],
  "core_skills": ["Python", "Flask", "Docker", "PostgreSQL", "CI/CD", "REST API"],
  "projects": [
    "專案名稱 — 優化後的專案描述，強調技術棧與量化成果"
  ],
  "education": [
    "學校名稱 | 科系 | 學位 | 畢業時間"
  ],
  "autobiography": "保留使用者原本風格的優化後完整自傳"
}
```

---

## 5. E. 輸出模組 (Export)

### E-01 匯出履歷文件

* **權限** : Protected
* **Method** : `GET`
* **Path** : `/resumes/{id}/export`
* **用途** : 從 `resume_optimization` 取最新（或指定版本）優化履歷，下載 PDF/DOCX/JSON。

| **請求部分** | **參數** | **類型** | **必填** | **說明**     |
| ------------------ | -------------- | -------------- | -------------- | ------------------ |
| **Header**   | Authorization  | String         | Yes            |                    |
| **Query**    | format         | String         | No             | `pdf`（預設）、`docx`、`json` |
| **Query**    | version        | String         | No             | 指定優化版本，未帶則取最新 |

**Response (200 OK)**

* **Content-Type** : `application/pdf`（PDF）、`application/vnd.openxmlformats-.../document`（DOCX）、`application/json`（JSON）
