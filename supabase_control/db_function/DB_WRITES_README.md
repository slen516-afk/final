# db_writes 使用說明

`db_function/db_writes.py` 提供「前端資料寫入 Supabase」的函數，後端 API 可直接 import 使用。風格與 `supabase_connection` 一致：可傳入既有 client，或由模組自動連線。

---

## 安裝與依賴

- 專案需能 import `db_function`（例如將 `supabase_control` 加入 PYTHONPATH）。
- 連線由同資料夾內 `supabase_connection` 提供。
- 需在 `supabase_control/` 或 `supabase_control/Erd/` 放好 `.env`，內含 `SUPABASE_URL` 與 `SUPABASE_SERVICE_ROLE_KEY`。

---

## 使用方式

```python
from db_function.db_writes import (
    insert_career_survey,
    upsert_user_profile,
    create_resume,
    create_resume_version,
    create_upload_event,
    add_user_skill,
    update_user_skill,
    save_cover_letter,
    mark_cover_letter_sent,
)
```

所有函數都支援關鍵字參數 `supabase=None`。不傳時會自動呼叫 `connect_to_supabase(test_connection=False)`；若後端已有連線，可傳入以共用。

---

## 函數一覽

| 情境           | 函數                     | 說明                         |
|----------------|--------------------------|------------------------------|
| 問卷提交       | `insert_career_survey`   | 寫入一筆職涯問卷             |
| 個人檔案       | `upsert_user_profile`    | 新增或更新使用者個人檔案     |
| 建立履歷       | `create_resume`          | 建立一筆履歷主檔             |
| 履歷版本       | `create_resume_version`  | 建立一筆履歷版本             |
| 上傳記錄       | `create_upload_event`    | 記錄上傳事件（檔名、路徑等） |
| 新增技能       | `add_user_skill`         | 新增一筆使用者技能           |
| 編輯技能       | `update_user_skill`      | 更新一筆使用者技能           |
| 儲存求職信     | `save_cover_letter`      | 儲存一筆求職信               |
| 標記已寄出     | `mark_cover_letter_sent` | 將求職信標記為已發送         |

---

## 詳細使用說明（以「上傳記錄」為例）

各函數邏輯相同：**後端收到前端資料 → 從 session/JWT 取得 `user_id` → 呼叫對應的 db_writes 函數 → 回傳寫入後的資料**。以下用 `create_upload_event` 示範，其餘函數用法類推。

### 呼叫時機

- 使用者上傳檔案後，後端已把檔案存到 Supabase Storage（或本機），要「記一筆上傳記錄」時呼叫。

### 必填參數

| 參數       | 型別 | 說明 |
|------------|------|------|
| `user_id`  | int  | 目前登入使用者 ID，由後端從 session/JWT 取得。 |
| `file_name`| str  | 檔案名稱（例如 `resume.pdf`）。 |
| `file_path`| str  | 儲存路徑（例如 Storage 的 path 或 URL）。 |

### 選填參數

| 參數          | 型別 | 預設值   | 說明 |
|---------------|------|----------|------|
| `upload_type` | str  | `"resume"` | 上傳類型，如 `resume` / `portfolio`。 |
| `metadata`    | dict | None     | 額外 JSON 中繼資料。 |
| `status`      | str  | `"pending"` | 初始狀態。 |
| `supabase`    | 客戶端 | None  | 不傳則自動連線。 |

### 回傳

- 寫入後的那一筆資料（dict），內含 `event_id`、`user_id`、`file_name`、`file_path`、`uploaded_at` 等。

### 可能錯誤

- `ValueError`：例如 `user_id` 非整數。
- `RuntimeError`：寫入失敗（例如權限或表不存在）。

### 後端怎麼接前端

1. 前端上傳檔案後，可再送一筆 POST（或在上傳 API 裡一併處理），帶 `file_name`、`file_path`、`upload_type` 等。
2. 後端從 session/JWT 取得 `current_user_id`，呼叫 `create_upload_event(user_id=current_user_id, file_name=..., file_path=..., ...)`。
3. 把回傳的 dict 用 `jsonify(result)` 回給前端，或只回 `event_id`。

**其他函數**（問卷、個人檔案、履歷、技能、求職信）用法相同：  
`payload` 或個別參數 = 前端送來的 JSON 或表單欄位；`user_id`（或 `resume_id`、`job_id` 等）由後端從登入狀態或 path 取得。可直接看 `db_writes.py` 裡各函數的 docstring。

---

## 範例（後端 API）

```python
# 問卷：後端收到 POST /api/survey
result = insert_career_survey(user_id=current_user_id, payload=request.json)

# 個人檔案：PUT /api/profile
result = upsert_user_profile(user_id=current_user_id, payload=request.json)

# 上傳：檔案已存到 Storage 後記錄
result = create_upload_event(
    user_id=current_user_id,
    file_name=file.filename,
    file_path=storage_path,
    upload_type="resume",
)

# 求職信：產生/儲存後
result = save_cover_letter(
    user_id=current_user_id,
    job_id=body["job_id"],
    subject=body["subject"],
    content=body["content"],
    resume_id=body.get("resume_id"),
)
```

---

## 測試與範例檔（本資料夾內）

- **`test_db_writes_manual.py`** — 最小可跑測試腳本：不接 Flask，直接呼叫一個 db_writes 函數（例如 `create_upload_event`），確認連線與寫入正常。執行方式：
  ```bash
  cd supabase_control
  python db_function/test_db_writes_manual.py
  ```
  或（從專案根目錄）：
  ```bash
  set PYTHONPATH=supabase_control
  python supabase_control/db_function/test_db_writes_manual.py
  ```

- **`flask_example.py`** — 最小 Flask 範例：只開一個 route（例如 POST 上傳記錄），收到 JSON 後呼叫 `create_upload_event` 並回傳結果。用來示範「後端怎麼接、怎麼呼叫、怎麼回傳」。需先安裝 `flask`（`pip install flask`）。執行方式：
  ```bash
  cd supabase_control
  python db_function/flask_example.py
  ```
  再用 Postman 或 curl 對 `http://127.0.0.1:5000/api/upload-event` 送 POST 測試。

以上兩個檔案邏輯與其他 db_writes 函數一致，測通一個即可類推到其他函數。

---

## 暫未實作（依需求後補）

- **應徵記錄**（`application_record`）：投遞職缺時寫入。
- **媒合已讀**（`job_matching`）：更新 `user_viewed`。
- **Agent 任務**（`agent_session`）：建立/更新 Agent 調用記錄。

以上可依相同風格在 `db_writes.py` 內新增對應函數。
