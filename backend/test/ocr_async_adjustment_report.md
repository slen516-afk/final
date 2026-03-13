# Celery 任務中心遷移與 OCR 非同步化總結報告

## 1. 修改摘要
本次調整已完成將 **OCR (Resume Analysis)** 服務遷移至 Celery 非同步架構，並統一了後端 AI 任務的狀態追蹤機制 (Redis Job Tracking)。

### 調整清單：
- **後端 API (`resume_processing.py`)**:
    - `/upload` 轉換為非同步模式：上傳檔案後立即返回 `job_id` (202 Accepted)，不再同步等待 OCR 辨識。
    - 引入 `worker.tasks.analyze_resume_async`。
- **Celery Worker (`tasks.py`)**:
    - 實作 `analyze_resume_async` 任務。
    - **數據映射 (Mapping)**: 將原本位於 API 層的 OCR 數據轉換邏輯遷移至 Worker，減輕 API 負擔並確保前端獲得一致的結構化數據。
    - **狀態寫回**: 任務成功/失敗後，將結果寫回 Redis (`job:{id}`)，以便前端輪詢。
- **類型一致性性修正**:
    - 統一所有 Celery 任務中的 `user_id` 類型為 `int` (對齊資料庫外鍵型別)。
    - 修正 `process_resume_analysis` 與 `process_cover_letter` 的呼叫參數。
- **前端進度控制 (`useAsyncTask.js`)**:
    - 實作「每 3 次輪詢前進一個區段」的邏輯，避免進度條與背景任務完成時間落差過大（視覺排隊感優化）。

## 2. 測試驗證結果

### Celery 連通性測試
- 運行 `backend/test/test_celery_connectivity.py`
- **結果**: 成功發送並追蹤 `process_cover_letter` 與 `process_resume_analysis` 任務。

### OCR 非同步流測試
- 運行 `backend/test/test_ocr_async.py` (模擬前端上傳與輪詢)
- **測試流程**:
    1. 發送測試檔案路徑與 `job_id` 給 Worker。
    2. 輪詢 Redis 狀態。
- **結果**: 
    - Worker 成功接收 `analyze_resume_async` 並在隔離進程中運行 PaddleOCR (Fallback 備援機制亦運作正常)。
    - Redis 狀態由 `processing` 轉為 `done`。
    - 輸出結果包含正確的映射欄位 (`name`, `skills`, `experience` 等)。

## 3. 已知限制與後續建議
1. **檔案 Volume 掛載**: 宿主機與 Container 之間的 `uploads` 資料夾必須正確掛載，否則 Worker 無法存取 API 存下的檔案。測試環境已確認工作目錄為 `/app`。
2. **環境變數**: 確保 `.env` 中的 `REDIS_URL` 在容器內外都能正確解析（容器內使用 `redis:6379`, 宿主機測試建議手動指定為 `localhost:6379`）。

---
**本次調整已完成，系統現在能更流暢地處理高負載的 OCR 辨識任務。**
