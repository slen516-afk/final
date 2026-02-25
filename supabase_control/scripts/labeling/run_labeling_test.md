# 文件：`run_labeling_test.py`

## 總覽

此腳本的核心功能是**對指定的職缺進行 AI 自動化標籤（Labeling）**。它會讀取 Supabase 資料庫中 `job_posting` 表格的特定職缺資料，透過 OpenAI GPT 模型進行分析，並將分析結果（六維能力向量和職位分類）寫回資料庫，同時生成一份詳細的本地 JSON 報告。

這是一個手動、精準測試的工具，適用於當你想要驗證特定幾筆職缺的分析效果時使用。

## 功能詳解

1.  **初始化**：
    *   載入 `.env` 檔案中的環境變數 (`SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `OPENAI_API_KEY`)。
    *   建立 Supabase 和 OpenAI 的客戶端。

2.  **資料定義 (Pydantic Schema)**：
    *   定義 `JobCompetencyVector` 作為輸出結構，確保 LLM 回傳的資料格式一致。
    *   包含六個維度的能力分數（`d1` 到 `d6`）、職位分類代碼 (`role_type`) 與名稱 (`role_name`)，以及 AI 的評分理由 (`reasoning`)。
    *   內建驗證器，確保分數範圍在 1.0 至 5.0 之間，且角色代碼為 A-F 之一。

3.  **Prompt 設計**：
    *   系統提示 (System Prompt) 將 LLM 設定為一位資深的軟體工程架構師。
    *   明確定義了六大維度（D1-D6）的評分標準。
    *   提供了**衝突處理協議 (Conflict Resolution Protocol)**，指導 LLM 在職缺標題與內容不符時，應優先以「職缺描述」為準。

4.  **處理流程 (`process_specific_jobs`)**：
    *   接收一個包含 `job_id` 的列表作為輸入。
    *   從 Supabase 查詢這些 ID 對應的職缺，並過濾掉已經評分過的資料 (d1\_frontend is not null)。
    *   對於每一筆職缺，調用 LLM 鏈 (Chain) 進行分析。
    *   **雙軌輸出**：
        *   **軌道 A (寫入 Supabase)**：將分析出的六維能力分數和角色分類更新回 `job_posting` 表格的對應欄位。
        *   **軌道 B (本地儲存)**：將包含評分理由、執行時間等更完整的分析結果，儲存於一個 Python 串列中。
    *   所有職缺處理完畢後，將串列中的完整結果寫入一個以時間戳命名的 `.json` 檔案中，存放於目前腳本所在的目錄。

## 使用方法

### 前置設定

1.  **環境變數**：請在 **supabase_control** 專案根目錄下建立 `.env`，並包含：
    ```bash
    SUPABASE_URL="YOUR_SUPABASE_URL"
    SUPABASE_SERVICE_ROLE_KEY="YOUR_SUPABASE_SERVICE_KEY"
    OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
    ```
    腳本會自動從 `supabase_control/.env` 載入（與執行時所在目錄無關）。

### 執行步驟

1.  **指定測試目標**：
    *   打開 `run_labeling_test.py`，在檔案最下方 `if __name__ == "__main__":` 區塊中修改 `test_ids`，填入要測試的 `job_id`。
    ```python
    test_ids = [11, 12, 13, ...]  # 從 Supabase job_posting 複製的 ID
    process_specific_jobs(test_ids)
    ```

2.  **執行腳本**（請在 **supabase_control** 目錄下執行）：
    ```bash
    cd supabase_control
    python scripts/labeling/run_labeling_test.py
    ```

### 預期輸出

*   **終端機**：每個 ID 的處理進度、耗時與角色名稱。
*   **Supabase**：對應資料列的 `role_type`, `role_name`, `d1`～`d6` 會被更新。
*   **本地檔案**：在 **scripts/labeling/** 下會產生 `labeling_result_YYYYMMDD_HHMMSS.json`，內含每筆職缺的完整分析。
