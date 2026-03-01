# db_writes 使用說明

`db_function/db_writes.py` 提供「前端資料寫入 Supabase」的函數，後端 API 可直接 import 使用。風格與 `supabase_connection` 一致：可傳入既有 client，或由模組自動連線。

## 安裝與依賴

- 專案需能 import `db_function`（例如將 `supabase_control` 加入 PYTHONPATH）。
- 連線由同資料夾內 `supabase_connection` 提供。

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

## 函數一覽

| 情境           | 函數                     | 說明                         |
|----------------|--------------------------|------------------------------|
| 問卷提交       | `insert_career_survey`   | 寫入一筆職涯問卷             |
| 個人檔案       | `upsert_user_profile`    | 新增或更新使用者個人檔案     |
| 建立履歷       | `create_resume`          | 建立一筆履歷主檔             |
| 履歷版本       | `create_resume_version`   | 建立一筆履歷版本             |
| 上傳記錄       | `create_upload_event`     | 記錄上傳事件（檔名、路徑等） |
| 新增技能       | `add_user_skill`         | 新增一筆使用者技能           |
| 編輯技能       | `update_user_skill`      | 更新一筆使用者技能           |
| 儲存求職信     | `save_cover_letter`      | 儲存一筆求職信               |
| 標記已寄出     | `mark_cover_letter_sent` | 將求職信標記為已發送         |

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

## 暫未實作（依需求後補）

- **應徵記錄**（`application_record`）：投遞職缺時寫入。
- **媒合已讀**（`job_matching`）：更新 `user_viewed`。
- **Agent 任務**（`agent_session`）：建立/更新 Agent 調用記錄。

以上可依相同風格在 `db_writes.py` 內新增對應函數。
