# 差距分析 API 測試流程說明 (Gap Analysis Testing Guide)

本文檔說明 `test_gap.py` 測試檔的使用與切換流程，該測試主要用於驗證 `POST /api/gap-analysis` 與 `GET /api/gap-analysis/<job_id>` 兩支 API 的行為，並說明其與背景 Worker 的協作機制。

## 1. 雙模式測試架構

為了兼顧開發速率與真實整合度，`test_gap.py` 支援兩種測試模式：

### 1.1 Mock 模式 (預設)
*   **觸發方式**：環境變數 `USE_REAL_ANALYSIS=false`。
*   **機制**：測試腳本會自行將 Mock 報告數據寫入 Redis，並模擬 Worker 已完成任務。適合快速驗證 API 回傳結構。

### 1.2 實際 LLM 模式 (Real Mode)
*   **觸發方式**：環境變數 `USE_REAL_ANALYSIS=true`。
*   **機制**：測試腳本會提交任務至 Redis，並等待實際運作的 `worker` 容器處理完畢。
*   **前置條件**：必須確保 `worker` 服務已啟動且能正常存取 LLM。

---

## 2. 測試環境準備

在測試過程中，系統會自動執行以下流程：
1.  **Mock 登入**：使用測試帳號獲取 Access Token (透過 Authorization: Bearer mock_token_ 識別)。
2.  **資料預熱**：直接在 Supabase `career_survey` 表中插入假數據 (問卷與人格特質)，確保落差分析模組有輸入資料可供處理。

---

## 3. 如何執行測試

### 3.1 基礎執行 (Mock 模式)
在 `backend/` 目錄下：
```bash
pytest test/test_gap.py -v -s
```

### 3.2 真實模式執行
**Windows (PowerShell):**
```powershell
$env:USE_REAL_ANALYSIS="true"; pytest test/test_gap.py -v -s
```

---

## 4. 非同步任務機制說明

*   **任務下發**：`POST /api/gap-analysis` 會建立一個隨機 Job ID，並透過 Celery 呼叫 `worker.tasks.process_career_analysis`。
*   **狀態輪詢**：前端/測試腳本會持續呼叫 `GET /api/gap-analysis/<job_id>`，直到 `status` 變為 `done` 或 `failed`。
*   **資料流向**：分析結果最終會存回 Redis Hash 中，鍵值為 `job:<job_id>`。

---

## 5. 常見問題 (Q&A)

*   **為什麼狀態一直停在 `processing`？**
    *   通常是因為 `worker` 容器沒有啟動，或是 `worker` 內部發生 `ModuleNotFoundError`。請檢查 `docker logs final-worker-1`。
*   **為什麼回傳 `User not found in DB`？**
    *   測試腳本需先建立測試帳號，請確保資料庫連線資訊 (`.env`) 正確。
*   **匯入路徑錯誤？**
    *   新架構下，所有後端測試應在 `/app` (backend/ 目錄) 執行，以確保 `sys.path` 能正確解析 `api` 與 `worker` 模組。
