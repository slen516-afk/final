# 🚀 Career Pilot 專案：Supabase 資料庫快速上手指南

> **產出日期**: 2026-01-24

---

## 📌 一、 核心架構概念

我們的資料採用「雙軌儲存」模式，確保結構化資料與向量搜尋能力並存：

1. **Supabase (PostgreSQL)**: 
   - 存放所有「結構化資料」（如：帳號、職缺文字、問卷、媒合分數）。
   - 所有資料表與欄位名稱嚴格對齊 `career_pilot_ERD_欄位對齊總表.md`。
2. **Qdrant Cloud (Vector DB)**: 
   - 存放「向量資料」，用於 AI 語意配對。
   - 透過 `vector_id` (UUID) 與 Supabase 進行跨庫關聯。

---

## 🛠️ 二、 組員常用操作指南

### 1. Table Editor (像 Excel 一樣操作)
* **位置**: 點選左側選單的「表格」圖示。
* **功能**: 
    - 直接手動新增 (`Insert row`) 或修改資料內容。
    - 點擊欄位名稱可進行過濾 (`Filter`) 或排序 (`Sort`)。
* **規範**: 禁止隨意更動 ID 或外鍵 (Foreign Key) 欄位，避免關聯斷裂。

### 2. SQL Editor (進階查詢)
* **位置**: 點選左側選單的 `>_` 圖示。
* **常用指令**:
    - **查看待處理職缺**: `SELECT * FROM JOB_POSTING WHERE is_embedded = FALSE;`
    - **檢查履歷版本**: `SELECT * FROM RESUME_VERSION WHERE resume_id = [目標ID];`

### 3. Storage (檔案倉庫)
* **位置**: 點選左側選單的「方框」圖示。
* **用途**: 存放使用者上傳的原始履歷 PDF/圖片。

---

## ⚠️ 三、 開發注意事項 (重要！)

1. **結論先行**: 資料庫是「真實之源」，代碼必須服從資料庫結構。
2. **向量狀態位元**: 
   - `is_embedded = FALSE`: 代表 AI 尚未處理該筆資料，不可進行語意搜尋。
   - `is_embedded = TRUE`: 代表資料已同步至 Qdrant。
3. **自動聯鎖刪除 (CASCADE)**: 
   - 我們設定了聯鎖刪除。刪除一個 `USER`，其對應的 `PROFILE` 與 `RESUME` 會自動消失，執行刪除前請務必確認。
4. **命名慣例**: 
   - 表名大寫（如 `USER`, `JOB_POSTING`）。
   - 欄位名小寫（如 `user_id`, `job_title`）。

---

## 🔑 四、 串接資訊 (API)

若需撰寫腳本串接，請至 **Settings > API** 取得：
* **Project URL**: API 連線位址。
* **anon (public) key**: 客戶端讀取用。
* **service_role key**: 後端處理用（勿外流）。

---

## 💡 老師的心法與口訣

* **先入庫，後同步**: 確保 SQL 拿到 ID 後，再將向量送進 Qdrant。
* **狀態標籤要看清**: `is_embedded` 是追蹤 是否向量畫進度的唯一依據。
* **雙向 ID 記心頭**: SQL 存 `vector_id`，Qdrant 存 SQL ID。