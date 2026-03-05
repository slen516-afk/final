<!-- markdownlint-disable MD036 MD033 -->

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
2. [問卷作答 (Questionnaire Response)](#2-問卷作答-questionnaire-response)
3. [職缺意向 (User Preference)](#3-職缺意向-user-preference)
4. [履歷管理 (Resume)](#4-履歷管理-resume)
5. [履歷分析 (Analysis)](#5-履歷分析-analysis)
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
OPENAI_API_KEY=sk-....
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

## 2. 問卷作答 (Questionnaire Response)

### E-01 儲存問卷作答結果

- **權限**: Protected
- **Method**: `POST`
- **Path**: `/questionnaire-response`
- **用途**: 將前端完整問卷 JSON 存入 `career_survey.questionnaire_response`。若該使用者已有 survey 紀錄則更新，否則新增一筆。

| 參數         | 類型 | 必填 | 說明                         |
| ------------ | ---- | ---- | ---------------------------- |
| `module_a` | JSON | Yes  | 專業技能 (Skills, q1~q8)     |
| `module_b` | JSON | Yes  | 軟實力 (Soft Skills, q9~q15) |
| `module_c` | JSON | Yes  | 現況與目標 (q16~q19)         |
| `module_d` | JSON | Yes  | 價值觀與學習風格 (q20~q23)   |

**Request Body**

```json
{
  "module_a": {
    "q1_languages": [
      { "name": "Python", "score": 5 },
      { "name": "SQL", "score": 4 },
      { "name": "Git", "score": 4 }
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
    "q20_values_top3": [
      "technical_growth",
      "social_impact",
      "financial_reward"
    ],
    "q21_pressure": "consider_short_term",
    "q22_career_type": "specialist",
    "q23_learning_style": ["official_docs", "hands_on_projects"]
  }
}
```

**Response 201 Created**

```json
{
  "survey_id": 42,
  "status": "saved",
  "updated_at": "2026-03-05T17:47:54.400474+00:00"
}
```

**錯誤碼**

| HTTP Code | 情境                            |
| --------- | ------------------------------- |
| `400`   | Request body 為空或缺少必填模組 |
| `401`   | 未登入 / Token 無效             |
| `500`   | 資料庫寫入失敗                  |

### E-02 儲存人格特質結果

- **權限**: Protected
- **Method**: `POST`
- **Path**: `/personality`
- **用途**: 將前端計算完的人格特質 JSON 新增一筆至 `career_survey.personality`。同一個 user 可以有多筆紀錄。

| 參數                        | 類型      | 必填 | 說明                                |
| --------------------------- | --------- | ---- | ----------------------------------- |
| `trait_raw_responses`     | JSON      | No   | 每題原始作答 (`{"Q1": "C", ...}`) |
| `trait_calculation_debug` | JSON      | Yes  | 各維度原始分                        |
| `trait_normalized_scores` | JSON      | Yes  | 正規化後各維度分數 (0~100)          |
| `primary_archetype`       | String    | Yes  | 主要人格原型                        |
| `secondary_archetypes`    | list[str] | Yes  | 次要人格原型                        |
| `trait_created_at`        | String    | Yes  | 人格特質建立時間 (ISO 8601)         |

**Request Body**

```json
{
  "trait_raw_responses": {
    "Q1": "C",
    "Q2": "A",
    "Q3": "B",
    "Q4": "C",
    "Q5": "A",
    "Q6": "B",
    "Q7": "B",
    "Q8": "A",
    "Q9": "A",
    "Q10": "A"
  },
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
```

**Response 201 Created**

```json
{
  "survey_id": 42,
  "status": "saved",
  "updated_at": "2026-03-05T17:47:54.400474+00:00"
}
```

**錯誤碼**

| HTTP Code | 情境                                                       |
| --------- | ---------------------------------------------------------- |
| `400`   | Request body 為空或缺少 `trait_raw_responses` 等必填欄位 |
| `401`   | 未登入 / Token 無效                                        |
| `500`   | 資料庫寫入失敗                                             |

---

## 3. 職缺意向 (User Preference)

> **架構**: 提交問卷分析 → Redis Stream → cv_worker 處理 → 前端 Polling 取結果

### B-01 提交職能問卷

- **權限**: Protected
- **Method**: `POST`
- **Path**: `/dream-jobs`
- **用途**: 職涯偏好問卷，後端會直接從資料庫 `career_survey` 表中讀取最新的 `questionnaire_response` 和 `questionnaire_response`作為任務輸入。無須帶任何 Request Body。

**Request Body**

（無需 Request Body）

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

#### Job 狀態說明

| `status` (任務狀態) | 說明                                                                  |
| --------------------- | --------------------------------------------------------------------- |
| `queued`            | 任務已成功排入 Redis Stream，等待 Worker 處理。                       |
| `processing`        | Worker 已接手，正在向 LLM 發出請求並等待回應。                        |
| `done`              | 分析順利完成，可從回應取出 `result`，後端不會再重試此任務。         |
| `retrying`          | 發生可恢復的錯誤（如 timeout），將按照 Exponential Backoff 自動重試。 |
| `dlq`               | 發生不可恢復錯誤（如資料短缺）或達最大重試次數，已移至死信工作佇列。  |

**Response 200 OK — 進行中**

```json
{
  "job_id": "job_a1b2c3d4e5f6",
  "status": "processing",
  "created_at": "2026-03-05T17:47:54.400474+00:00",
  "updated_at": "2026-03-05T17:47:54.400474+00:00"
}
```

**Response 200 OK — 完成（`result` 為 `CareerReport` 結構）**

```json
{
    "created_at": "2026-03-05T17:49:01.531449+00:00",
    "job_id": "job_a1b2c3d4e5f6",
    "result": {
        "action_plan": {
            "long_term": "持續更新技術知識，參加技術社群活動或技術會議，提升專業能力與人脈。考慮進階學習如 DevOps 或雲端服務的相關技能，以擴展職涯發展空間。",
            "mid_term": "學習後端技術如 Node.js 或 Python 的 Flask/Django 框架，並掌握基本的數據庫操作技巧 (SQL/MongoDB)。參與開源專案或實習，累積實際專案經驗，提升職場競爭力。",
            "short_term": "學習基礎的前端開發技術如 HTML, CSS, JavaScript，並掌握至少一個前端框架如 React 或 Angular。參加線上課程或實作工作坊，增強實作能力，如 Codecademy 或 Coursera 的全端開發課程。"
        },
        "gap_analysis": {
            "current_status": {
                "actual_level": "轉職中/學習中 (Entry Level)",
                "cognitive_bias": "自評為轉職中，但缺乏實際的前後端開發經驗，建議學習基礎的前端技術如 HTML, CSS, JavaScript。",
                "self_assessment": "轉職中/學習中 (Entry Level)"
            },
            "target_position": {
                "gap_description": "【優勢 (Strengths)】：具備良好的資源管理與優先級排序技巧。 【劣勢 (Weaknesses)】：技術實作經驗不足，特別是在前後端開發領域。 【機會 (Opportunities)】：全端工程師在市場上的需求增加，特別是在新創公司與技術驅動型企業中。 【威脅 (Threats)】：市場對於具備即戰力的全端工程師需求較高，競爭激烈。 【核心落差 (Gap)】：缺乏實際的程式碼撰寫與調試經驗，建議參加線上課程或實作工作坊。",
                "match_score": "60%",
                "role": "全端工程師"
            }
        },
        "preliminary_summary": {
            "core_insight": "【產業洞察】：從目前的市場趨勢來看，科技領域中，全端工程師的需求正在不斷增加，特別是在快速開發和迭代的環境中。 【個人總結】：您在資源配置、優先級排序、需求分析以及跨部門協作等方面的經驗，非常適合全端開發的多元需求，這些能力將助您在全端職位中如魚得水。"
        },
        "radar_chart": {
            "dimensions": [
                {
                    "axis": "前端開發",
                    "score": 0.5
                },
                {
                    "axis": "後端開發",
                    "score": 0.5
                },
                {
                    "axis": "運維部署",
                    "score": 0.5
                },
                {
                    "axis": "AI與數據",
                    "score": 0.5
                },
                {
                    "axis": "工程品質",
                    "score": 1.0
                },
                {
                    "axis": "軟實力",
                    "score": 1.0
                }
            ]
        },
        "report_metadata": {
            "timestamp": "2026-03-05T17:49:02.606Z",
            "user_id": "21",
            "version": "2.0"
        }
    },
    "status": "done",
    "updated_at": "2026-03-05T17:49:52.402424+00:00"
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

## 4. 履歷管理 (Resume)

### C-02 建立履歷（寫入 `resume`）

- **權限**: Protected
- **Method**: `POST`
- **Path**: `/resumes/form`
- **用途**: 建立原始履歷並存入 `resume` table，表單填寫（`generic`）與 OCR 上傳（`uploaded`）均呼叫此 API。

#### 欄位說明

| 參數                                     | 類型       | 必填 | 說明                                                         |
| ---------------------------------------- | ---------- | ---- | ------------------------------------------------------------ |
| `resume_name`                          | String     | Yes  | 履歷名稱（顯示用）                                           |
| `resume_type`                          | String     | Yes  | 來源類型：`uploaded`（OCR 上傳）或 `generic`（表單填寫） |
| `structured_data`                      | JSON       | Yes  | 完整履歷結構物件                                             |
| `structured_data.basics`               | JSON       | Yes  | 基本資料（姓名、Email、電話、地址）                          |
| `structured_data.education`            | String     | No   | 學歷                                                         |
| `structured_data.work_experience`      | String     | No   | 工作經歷                                                     |
| `structured_data.skills`               | String     | No   | 技能                                                         |
| `structured_data.languages`            | list[JSON] | No   | 語言能力，每筆含 `language` / `level`                    |
| `structured_data.certificate_projects` | String     | No   | 證照與專案                                                   |
| `structured_data.portfolio`            | String     | No   | 作品集                                                       |
| `structured_data.autobiography`        | String     | No   | 自傳                                                         |
| `structured_data.others`               | String     | No   | 其他                                                         |

**Request Body**

```json
{
  "resume_name": "我的履歷1",
  "resume_type": "generic",
  "structured_data": {
    "basics": {
      "name": "測試人員",
      "email": "test@example.com",
      "phone": "0912345678",
      "location": "Taipei, Taiwan, K Street."
    },
    "education": "國立臺灣大學, 資訊管理系, 學士, 2024 畢業",
    "work_experience": "任職AA公司，擔任全端工程師。",
    "skills": "python和html",
    "languages": [
      { "language": "Chinese", "level": "Advanced" },
      { "language": "English", "level": "Intermediate" }
    ],
    "certificate_projects": "通知機器人:開發具備動態網頁資料抓取 (Web Scraping) 與自動化通知功能的 Discord 機器人，支援多頻道即時訊息同步。",
    "portfolio": "作品集",
    "autobiography": "全端工程師，3 年 Python/Flask 開發經驗",
    "others": "Github: https://github.com/dlin-backend-demo"
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
    "created_at": "2026-03-05T17:33:02+00:00",
    "is_embedded": false,
    "is_primary": true,
    "normalized_data": null,
    "resume_id": 203,
    "resume_name": "我的履歷1",
    "resume_type": "generic",
    "structured_data": {
        "autobiography": "全端工程師，3 年 Python/Flask 開發經驗",
        "basics": {
            "email": "test@example.com",
            "location": "Taipei, Taiwan, K Street.",
            "name": "測試人員",
            "phone": "0912345678"
        },
        "certificate_projects": "通知機器人:開發具備動態網頁資料抓取 (Web Scraping) 與自動化通知功能的 Discord 機器人，支援多頻道即時訊息同步。",
        "education": "國立臺灣大學, 資訊管理系, 學士, 2024 畢業",
        "languages": [
            {
                "language": "Chinese",
                "level": "Advanced"
            },
            {
                "language": "English",
                "level": "Intermediate"
            }
        ],
        "others": "Github: https://github.com/dlin-backend-demo",
        "portfolio": "作品集",
        "skills": "python和html",
        "work_experience": "任職AA公司，擔任全端工程師。"
    },
    "updated_at": "2026-03-05T17:33:02+00:00",
    "user_id": 21,
    "vector_id": null
}
```

### C-05 新增優化履歷（寫入 `resume_optimization`）

- **權限**: Protected
- **Method**: `PUT`
- **Path**: `/resumes/{id}`
- **用途**: 每次 PUT 在 `resume_optimization` 新增一筆，`optimization_version` 整數自動遞增 (1, 2, 3...)。`resume_name` 自動抓取原始履歷名稱加上 `_優化`。

| 參數                           | 類型      | 必填 | 說明                                                                                                                          |
| ------------------------------ | --------- | ---- | ----------------------------------------------------------------------------------------------------------------------------- |
| `professional_summary`       | String    | No   | 專業總結                                                                                                                      |
| `professional_experience`    | list[str] | No   | 工作經歷（字串陣列）。*(註：對應resume table `structured_data.work_experience`)*                                         |
| `core_skills`                | list[str] | No   | 核心技能。*(註：對應resume table `structured_data.skills` , `structured_data.languages`)*                             |
| `projects`                   | list[str] | No   | 專案。*(註：對應resume table `structured_data.certificate_projects` , `structured_data.portfolio`)*                    |
| `education`                  | list[str] | No   | 學歷。*(註：對應resume table `structured_data.education` )*                                                               |
| `autobiography`              | String    | No   | 自傳。*(註：對應resume table `structured_data.basics`, `structured_data.autobiography`, `structured_data.others`)* |
| `style_settings`             | JSON      | No   | 樣板設定（含 `template_id` 與 `style_color`）                                                                             |
| `style_settings.template_id` | Integer   | No   | 樣板 ID                                                                                                                       |
| `style_settings.style_color` | String    | No   | 主題色（Hex，如 `#1A73E8`）                                                                                                 |

**註：不需要傳入 `version_id`，後端會自動從 `resume_optimization` 撈取最新版號並 `+1`。**

**Request Body（完整範例）**

```json
{
  "professional_summary": "全端工程師，擁有 3 年 Python/Flask 與 React 開發經驗，主導日處理 50 萬請求後端系統重構，熟悉 CI/CD、容器化部署與雲端服務。",
  "professional_experience": [
    "Tech Corp | Senior Backend Developer | 2022-07 ~ Present | 主導 RESTful API 重構，回應時間從 800ms 降至 120ms；設計 Redis 快取層降低資料庫負載 60%",
    "Startup Inc. | Junior Developer | 2021-01 ~ 2022-06 | 開發內部管理後台（React + Flask），支援 50+ 使用者同時操作"
  ],
  "core_skills": [
    "Python",
    "Flask",
    "FastAPI",
    "React",
    "TypeScript",
    "PostgreSQL",
    "Redis",
    "Docker",
    "Kubernetes",
    "CI/CD",
    "REST API",
    "AWS"
  ],
  "projects": [
    "Career Pilot — AI 職涯規劃平台，整合 LLM 進行履歷分析，使用 Redis Stream 實作非同步任務佇列",
    "Smart Inventory System — 智慧庫存管理系統，FastAPI + Celery 處理批次匯入任務"
  ],
  "education": ["國立台灣大學 | 資訊工程學系 | 學士 | 2022-06"],
  "autobiography": "熱衷於解決複雜工程問題的全端工程師，主導核心系統微服務化重構，系統承載能力提升 4 倍。",
  "style_settings": {
    "template_id": 2,
    "style_color": "#1A73E8"
  }
}
```

**Response 201 Created**

```json
{
    "created_at": "2026-03-05T17:58:04.50012+00:00",
    "optimization_id": 22,
    "optimization_version": "5",
    "resume_id": 40,
    "resume_name": "我的履歷1_優化",
    "template_color": {
        "style_color": "#1A73E8",
        "template_id": 2
    }
}
```

---

## 5. 履歷分析 (Analysis)

> **架構**: 提交履歷分析任務 → Redis Stream → cv_worker 處理 → 前端 Polling 取結果

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

### D-02 輪詢任務進度

- **權限**: Protected
- **Method**: `GET`
- **Path**: `/analysis/jobs/{job_id}`
- **用途**: 一次取得完整狀態 + result + suggestions。

#### Job 狀態說明

| `status` (任務狀態) | 說明                                                                |
| --------------------- | ------------------------------------------------------------------- |
| `queued`            | 任務已成功排入 Redis Stream，等待 Worker 處理。                     |
| `processing`        | Worker 已接手，正在向 LLM 發出請求並等待回應。                      |
| `done`              | 分析或優化已完成，已將成果存回資料庫。                              |
| `retrying`          | LLM 或連線發生錯誤導致失敗，Worker 即將進行下一次指數退避的重試。   |
| `dlq`               | 連續超過 `MAX_RETRY` 次失敗或出現語法等不可恢復之錯誤，任務死亡。 |

**Response 200 OK — 處理中**

```json
{
  "job_id": "job_a1b2c3d4e5f6",
  "status": "processing",
  "created_at": "2026-03-05T17:47:54.400474+00:00",
  "updated_at": "2026-03-05T17:47:54.400474+00:00"
}
```

**Response 200 OK — 完成（`resume_analysis`）**

```json
{
    "created_at": "2026-03-05T18:02:19.629166+00:00",
    "job_id": "job_fd7ab79dbd20",
    "result": {},
    "status": "done",
    "suggestions": {
        "ats_risk_level": "中",
        "candidate_positioning": "從企業的角度來看，這份履歷目前看起來像是一位具備基礎技術能力的初階開發者，但缺乏明確的職涯目標和具體成就證明。",
        "critical_issues": [
            {
                "diagnosis_dimension": "證據力",
                "improvement_direction": [
                    "增加具體的數據和成就描述"
                ],
                "issue_reason": "缺乏具體數據使得招聘人員難以評估候選人的實際工作效能。",
                "issue_type": [
                    "缺乏量化證據"
                ],
                "original_text": "僅提及職位名稱，未提供具體數據或成就",
                "section": "工作經歷",
                "severity": [
                    "明顯扣分"
                ]
            },
            {
                "diagnosis_dimension": "ATS 關鍵字完整度",
                "improvement_direction": [
                    "擴充技能部分，增加更多技術關鍵字"
                ],
                "issue_reason": "缺少關鍵技術詞彙可能導致自動化系統篩選失敗。",
                "issue_type": [
                    "ATS 關鍵字缺失"
                ],
                "original_text": "僅提及 Python 和 HTML",
                "section": "技能",
                "severity": [
                    "明顯扣分"
                ]
            }
        ],
        "overall_strengths": [
            "涵蓋廣泛的個人資訊和技能",
            "具備基本的技術能力，如 Python 和 HTML"
        ],
        "overall_weaknesses": [
            "缺乏明確的段落分隔和標題，影響清晰度",
            "自傳部分過於簡略，未能充分展現個人能力",
            "工作經歷缺乏具體量化成果",
            "技能部分未涵蓋完整的技術關鍵字"
        ],
        "recommended_next_actions": [
            "增加履歷的排版清晰度，使用標題和段落分隔來強調各部分內容。",
            "在工作和專案描述中引入具體的數據和成就，增強證據力。",
            "擴充技能部分，增加更多技術關鍵字，提升ATS篩選通過率。",
            "建議在履歷中明確描述職涯目標，並強調與此目標相關的經歷和能力。"
        ],
        "screening_outcome_prediction": "由於缺乏量化成果和技術關鍵字，可能在初步篩選中被淘汰。",
        "target_role_gap_summary": "由於未指定目標職位，無法精確評估與目標職位的落差。然而，履歷中缺乏量化成果和技術關鍵字，可能影響申請後端工程師等技術職位的競爭力。"
    },
    "updated_at": "2026-03-05T18:03:15.073860+00:00"
}
```

**Response 200 OK — 完成（`resume_opt`）**

```json
{
    "created_at": "2026-03-05T18:09:47.341423+00:00",
    "job_id": "job_2d05394b4cf8",
    "result": {
        "autobiography": "作為一名全端工程師，我擁有三年的Python與Flask框架開發經驗，專注於構建高效能的網路應用程式與自動化工具。",
        "core_skills": [
            "Python",
            "HTML",
            "JavaScript",
            "Flask",
            "Web Scraping",
            "RESTful API設計"
        ],
        "education": [
            "國立臺灣大學\n  - 資訊管理系學士, 2024年畢業"
        ],
        "professional_experience": [
            "AA公司 - 全端工程師\n  - 情境: 公司需要提升其網站的動態數據抓取能力。\n  - 任務: 負責開發一個自動化的動態網頁資料抓取系統。\n  - 行動: 使用Python和Flask開發，並整合多頻道即時訊息同步功能。\n  - 結果: 成功提高了數據抓取效率30%，並提升了整體系統的穩定性。"
        ],
        "professional_summary": "作為一名全端工程師，我擁有三年的Python與Flask框架開發經驗，專注於構建高效能的網路應用程式與自動化工具。",
        "projects": [
            "通知機器人開發:\n  - 開發一個具備動態網頁資料抓取與自動化通知功能的Discord機器人。\n  - 支援多頻道即時訊息同步，有效提高了團隊的協作效率。"
        ]
    },
    "status": "done",
    "suggestions": {},
    "updated_at": "2026-03-05T18:10:53.241788+00:00"
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
           ├──► retrying (等待重試)
           └──► dlq (不可恢復錯誤/超過MAX_RETRY上限 → 死信佇列)
```

- **queued**: 已排入 Stream，等待 Worker 取走
- **processing**: Worker 正在處理（發送 LLM 請求）
- **done**: 處理完成，`result`/`suggestions` 已成功寫入
- **retrying**: Worker 遭遇例外，正在等待 `Exponential Backoff (2^n secs)` 後重新排隊。
- **dlq**: 發生非預期不可恢復的錯誤，或是重試次數已達 `MAX_RETRY` 上限，轉入 `cv_jobs_dlq` 佇列。

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
