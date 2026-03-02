# API 對接測試指南 (Postman)

本文件說明如何使用 Postman 測試 Career Pilot 的後端 API。

> [!IMPORTANT]
> v2.0 起，**分析 (D)** 與 **職缺意向 (B)** 模組改為非同步架構（Redis Stream）。
> 提交後回傳 `job_id`（HTTP 202），需輪詢取得結果。

## 前置準備

1. **啟動 Docker 環境**（需先啟動 Redis）

    ```bash
    docker compose up -d redis
    ```

2. **啟動後端 Flask 服務**

    在 `backend/flask` 目錄下執行：

    ```bash
    python app.py
    ```

    確認服務跑在 `http://127.0.0.1:5000`。

3. **啟動 Worker**（處理非同步任務）

    另開終端，在 `backend/flask` 目錄下：

    ```bash
    python -m worker.cv_worker
    ```

4. **取得 Access Token**

    所有 Protected API 都需要 Bearer Token。
    運行測試腳本取得 Token：

    ```bash
    cd backend/test
    python get_token.py
    ```

    輸入已註冊的 Email/Password (如無帳號請先註冊或手動在 Supabase 後台建立)。
    複製產生的 `Access Token`。

5. **設定 Postman Environment**

    建議在 Postman 設定 Environment Variables：
    - `base_url`: `http://127.0.0.1:5000/api`
    - `token`: `<貼上剛剛取得的 Access Token>`

---

## API 測試詳細步驟

### 1. 身份驗證 (Auth)

雖已有測試腳本，亦可透過 API 測試登入。

- **Register**
  - **Method**: `POST`
  - **URL**: `{{base_url}}/auth/register`
  - **Body (JSON)**:

        ```json
        {
          "email": "your_email@example.com",
          "password": "your_password",
          "username": "your_username"
        }
        ```

  - **預期結果 (201 Created)**: 回傳註冊成功訊息。

- **Login**
  - **Method**: `POST`
  - **URL**: `{{base_url}}/auth/login`
  - **Body (JSON)**:

        ```json
        {
          "email": "your_email@example.com",
          "password": "your_password"
        }
        ```

  - **預期結果 (200 OK)**: 回傳 `auth.accessToken`。

### 2. 職缺意向 (User Preference)

- **提交目標工作 (Create Survey) → 非同步**
  - **Method**: `POST`
  - **URL**: `{{base_url}}/dream-jobs`
  - **Header**:
    - `Authorization`: `Bearer {{token}}`
  - **Body (JSON)**:

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

  - **預期結果 (202 Accepted)**:

        ```json
        {
          "job_id": "job_a1b2c3d4e5f6",
          "status": "queued"
        }
        ```

- **輪詢問卷分析結果 (Poll)**
  - **Method**: `GET`
  - **URL**: `{{base_url}}/dream-jobs/{{job_id}}`
  - **Header**: `Bearer {{token}}`
  - **預期結果 (200 OK)**: `status` 為 `queued` → `processing` → `done`（含 `result`）或 `failed`（含 `error`）。

### 3. 履歷管理 (Resume)

- **建立履歷 (Form Mode)**
  - **Method**: `POST`
  - **URL**: `{{base_url}}/resumes/form`
  - **Header**:
    - `Authorization`: `Bearer {{token}}`
  - **Body (JSON)**:

        ```json
        {
          "structured_data": {
            "basics": {
              "name": "測試人員",
              "email": "test@example.com",
              "summary": "測試用簡歷"
            },
            "skills": ["Python", "Flask"],
            "education": [],
            "work_experience": []
          }
        }
        ```

  - **預期結果 (201 Created)**:

        ```json
        {
          "resume_id": 203,
          "status": "completed",
          "last_updated": "..."
        }
        ```

- **取得履歷詳情**
  - **Method**: `GET`
  - **URL**: `{{base_url}}/resumes/203`
  - **Header**: `Bearer {{token}}`
  - **預期結果 (200 OK)**: 回傳完整履歷資料（含 `structured_data`, `template_id`, ERD 欄位等）。

- **更新履歷（全局覆蓋 → 寫入 `resume_optimization`）**

  每次 PUT 會在 `resume_optimization` 新增一筆，`optimization_version` 整數自動遞增 (1, 2, 3...)。

  - **Method**: `PUT`
  - **URL**: `{{base_url}}/resumes/203`
  - **Header**: `Bearer {{token}}`
  - **Body (JSON)**:

        ```json
        {
          "professional_summary": "全端工程師，3 年 Python/Flask 開發經驗...",
          "professional_experience": [
            "Tech Corp | Senior Backend Developer | 2022-07 ~ Present | 主導 RESTful API 重構...",
            "Startup Inc. | Junior Developer | 2021-01 ~ 2022-06 | 開發內部管理後台..."
          ],
          "core_skills": ["Python", "Flask", "Docker", "PostgreSQL"],
          "projects": [
            "Career Pilot — AI 職涯規劃平台，整合 LLM 進行履歷分析...",
            "Smart Inventory System — 智慧庫存管理系統..."
          ],
          "education": [
            "台灣大學 | 資工系 | 學士 | 2022-06"
          ],
          "autobiography": "我是一位熱衷於解決複雜工程問題的全端工程師...",
          "style_settings": { "color": "#1A73E8" }
        }
        ```

  - **預期結果 (201 Created)**: `optimization_id` + `optimization_version` (整數遞增)。

### 4. 履歷分析 (Analysis) — 非同步

- **啟動分析任務**
  - **Method**: `POST`
  - **URL**: `{{base_url}}/analysis/tasks`
  - **Header**: `Bearer {{token}}`
  - **Body (JSON)**:

        ```json
        {
          "task_type": "resume_analysis"
        }
        ```

    > `task_type` 支援 `resume_analysis`（取分析建議）或 `resume_opt`（取優化結果）。
    > `resume_id` 和 `survey_id` 為選填 metadata。

  - **預期結果 (202 Accepted)**:

        ```json
        {
          "job_id": "job_a1b2c3d4e5f6",
          "status": "queued"
        }
        ```

- **輪詢完整結果（推薦）**
  - **Method**: `GET`
  - **URL**: `{{base_url}}/analysis/jobs/{{job_id}}`
  - **Header**: `Bearer {{token}}`
  - **預期結果 (200 OK)**: 完成時 `status: "done"` 且含 `result` + `suggestions`。

- **查詢任務狀態（僅狀態）**
  - **Method**: `GET`
  - **URL**: `{{base_url}}/analysis/tasks/{{job_id}}/status`
  - **Header**: `Bearer {{token}}`
  - **預期結果 (200 OK)**: 回傳 `task_id` + `status`。

- **取得優化結果 (D-04, Results Only)**
  - **Method**: `GET`
  - **URL**: `{{base_url}}/analysis/tasks/{{job_id}}/results`
  - **Header**: `Bearer {{token}}`
  - **限制**: 僅限 `task_type: "resume_opt"` 的任務
  - **預期結果 (200 OK)** — 回傳 `ResumeOptimization` 結構：

        ```json
        {
          "professional_summary": "...",
          "professional_experience": ["公司A | 職稱 | 年資 | 描述..."],
          "core_skills": ["Python", "Flask"],
          "projects": ["專案名稱 — 描述..."],
          "education": ["學校 | 科系 | 學位 | 畢業時間"],
          "autobiography": "..."
        }
        ```

- **取得分析建議 (D-03, Suggestions Only)**
  - **Method**: `GET`
  - **URL**: `{{base_url}}/analysis/tasks/{{job_id}}/suggestions`
  - **Header**: `Bearer {{token}}`
  - **限制**: 僅限 `task_type: "resume_analysis"` 的任務
  - **預期結果 (200 OK)** — 回傳 `ResumeAnalysis` 結構：

        ```json
        {
          "candidate_positioning": "...",
          "target_role_gap_summary": "...",
          "overall_strengths": ["..."],
          "overall_weaknesses": ["..."],
          "critical_issues": [
            {
              "section": "技能專長",
              "original_text": "...",
              "issue_type": ["描述模糊"],
              "severity": ["可優化"],
              "diagnosis_dimension": "...",
              "issue_reason": "...",
              "improvement_direction": ["..."]
            }
          ],
          "ats_risk_level": "中",
          "screening_outcome_prediction": "...",
          "recommended_next_actions": ["..."]
        }
        ```
