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
          "survey_id": 101,
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

- **更新履歷**
  - **Method**: `PUT`
  - **URL**: `{{base_url}}/resumes/203`
  - **Header**: `Bearer {{token}}`
  - **Body (JSON)**:

        ```json
        {
          "structured_data": {
             "basics": { "name": "更新後的名字" }
          },
          "template_id": 2,
          "style_settings": {
              "color": "#FF5733"
          }
        }
        ```

  - **預期結果 (200 OK)**: `updated_at` 更新, 回傳 `saved_settings`。

### 4. 履歷分析 (Analysis) — 非同步

- **啟動分析任務**
  - **Method**: `POST`
  - **URL**: `{{base_url}}/analysis/tasks`
  - **Header**: `Bearer {{token}}`
  - **Body (JSON)**:

        ```json
        {
          "resume_id": 203,
          "survey_id": 101,
          "task_type": "resume_analysis" // 可帶入 resume_analysis (取建議) 或 resume_opt (取結果)
        }
        ```

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

- **取得優化結果 (Results Only)**
  - **Method**: `GET`
  - **URL**: `{{base_url}}/analysis/tasks/{{job_id}}/results`
  - **Header**: `Bearer {{token}}`
  - **預期結果 (200 OK)**:

        ```json
        {
          "career_readiness_score": 85.0,
          "market_insights": { ... },
          "matched_keywords": [...],
          "missing_keywords": [...]
        }
        ```

- **取得優化建議 (Suggestions Only)**
  - **Method**: `GET`
  - **URL**: `{{base_url}}/analysis/tasks/{{job_id}}/suggestions`
  - **Header**: `Bearer {{token}}`
  - **預期結果 (200 OK)**:

        ```json
        {
          "career_path_suggestions": { ... },
          "skill_gap_analysis": [...]
        }
        ```
