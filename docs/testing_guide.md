# 整合測試執行說明文件 (Integration Testing Guide)

本文件說明如何執行與驗證前後端整合測試，包含「使用者初始化」與「職能圖譜」兩大核心模組，並特別針對當前的架構調整進行說明。

---

## 1. 環境準備

### 1.1 啟動容器服務
請確保 Docker 容器已正常啟動，特別是 `redis` 與 `worker` (Celery)。
```bash
docker compose up -d
```

### 1.2 背景手動啟動服務 (重要)
目前的 `docker-compose.yml` 中，`backend` 服務的 `command` 被設定為 `sleep infinity`。這意味著容器雖然在跑，但 Flask 伺服器並未自動啟動，需手動進入啟動以利 Debug。

**手動啟動 Flask：**
```bash
docker exec -it final-backend-1 python main.py
```
*(啟動後伺服器會監聽 8000 埠口。)*

### 1.3 設定測試權限
為了在測試環境中繞過 Supabase 的真實登入流程，後端已加入 **Mock Token 識別機制**。
*   當測試請求攜帶以 `mock_token_` 開頭的 Authorization Header 時，系統會自動將請求關聯至資料庫中的第一個可用使用者。

---

## 2. 執行測試腳本

### 2.1 執行「使用者初始化」整合測試
測試內容包含：履歷上傳 (Mock OCR)、職務偏好問卷提交、人格特質問卷提交。
```bash
cd frontend
npm test src/test/user_initialization.test.ts
```

### 2.2 執行「職能圖譜」整合測試
測試內容包含：發起職能落差分析、輪詢分析狀態 (Redis 整合)、取得最終結果。
```bash
cd frontend
npm test src/test/competency_map.test.ts
```

---

## 3. 核心技術架構與修正

### 3.1 前端 API 客戶端遷移 (Axios)
*   **問題**：Vitest (JSDOM) 環境下使用原生 `fetch` 搭配 `FormData` 時，會遺失 Boundary 訊息，導致後端 Flask 收不到檔案。
*   **修正**：`frontend/src/services/apiClient.ts` 已全面遷移至 **Axios**。Axios 會自動處理 `FormData` 的標頭，與後端對接更穩定。

### 3.2 匯入路徑標準化 (Module Imports)
*   **機制**：為了讓測試腳本與容器環境共用代碼，後端工作目錄設為 `/app`。
*   **解析**：`backend/main.py` 會自動將 `flask/` 目錄加入 `sys.path`。這使得無論在什麼路徑下執行，我們都能統一使用 `from api.auth import ...` 或 `from worker.tasks import ...` 而不需加 `flask.` 前綴。

### 3.3 後端 OCR & LLM Mock 支援
*   **OCR Mock**：設定環境變數 `MOCK_MODE=true` 時，`ResumeOCRService` 會跳過實際 PaddleOCR 流程，直接回傳預設的結構化數據，避免測試卡死在模型載入。
*   **問卷 Mock**：`test_gap.py` 會自動在資料庫插入必要的測試資料。

---

## 4. 常見問題排除 (Troubleshooting)

| 錯誤代碼 | 原因 | 解決方案 |
| :--- | :--- | :--- |
| **400: 沒有收到檔案** | 檔案上傳失敗 | 確保測試環境中使用 `apiClient.post` 傳送 `FormData`，且 File 物件已正確封裝。 |
| **401: Unauthorized** | Token 解析失敗 | 檢查測試腳本的 Token 是否以 `mock_token_` 開頭，或確認數據庫中至少有一位使用者。 |
| **500: Internal Error** | 前後端資料不一致 | 檢查 `docker logs final-backend-1`。常見原因為 `ocr_service` 載入模型失敗或欄位映射錯誤。 |
| **ImportError** | 模組找不到 | 確保是在 `/app` 目錄執行，且 `sys.path` 已正確包含 `flask/` 資料夾。 |

---

## 5. 快速恢復生產環境
若測試完成後需要恢復為自動啟動服務，請將 `docker-compose.yml` 中的 `backend` 服務調整回：
```yaml
command: python main.py
```
並重啟容器。
