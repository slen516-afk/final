# 文件 `run_random_batch.py` 說明

這份文件旨在說明 `run_random_batch.py` 腳本的功能、設計思路以及如何使用它。

## 總覽

`run_random_batch.py` 的主要目標是從 Supabase 資料庫中隨機選取一批「尚未處理」的職缺，並對其進行自動化標籤作業。

這個腳本解決了在大量資料中，需要隨機抽樣進行測試或漸進式處理的需求，避免了每次都從頭開始或手動挑選資料的麻煩。

## 核心功能

腳本的核心運作流程如下：

1.  **初始化**:
    *   讀取 `.env` 檔案中的環境變數，以安全地取得 Supabase 的連線URL和金鑰。
    *   建立 Supabase 客戶端連線。

2.  **隨機選取未處理的 ID**:
    *   透過 `get_random_unprocessed_ids` 函數，從 `job_posting` 資料表中查詢 `d1_frontend` 欄位為 `NULL` 的資料。這表示該筆資料尚未被標籤系統處理過。
    *   為了提高效率和隨機性，腳本會先撈取一個較大的「候選池」(預設 `pool_size=100`)。
    *   接著，從這個候選池中，再隨機抽取最終要處理的數量 (預設 `batch_size=10`)。
    *   如果未處理的資料總數少於 `batch_size`，則會處理所有剩餘的資料。

3.  **執行標籤作業**:
    *   取得隨機 ID 列表後，腳本會呼叫從 `run_labeling_test.py` 匯入的 `process_specific_jobs` 函數。
    *   將選中的職缺 ID 和目標資料表名稱 (`job_posting`) 傳遞給該函數，以執行實際的分析和標籤更新作業。

## 如何使用

### 1. 環境設定

-   **相依套件**：在 **supabase_control** 專案下安裝依賴（例如 `uv sync` 或 `pip install -r requirements.txt`），需包含 `python-dotenv`、`supabase`、`langchain-openai` 等。
-   **環境變數**：在 **supabase_control** 根目錄建立 `.env`，並設定：
    ```env
    SUPABASE_URL="YOUR_SUPABASE_URL"
    SUPABASE_SERVICE_ROLE_KEY="YOUR_SUPABASE_SERVICE_KEY"
    OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
    ```
    （貼標會呼叫 OpenAI，故需要 `OPENAI_API_KEY`。）
-   **相依腳本**：`run_labeling_test.py` 需與本腳本同放在 `scripts/labeling/` 下，本腳本會引用其中的 `process_specific_jobs`。

### 2. 執行腳本（抓 500 筆職缺貼標）

在 **supabase_control** 目錄下執行：

```bash
cd supabase_control
python scripts/labeling/run_random_batch.py
```

預設會從資料庫中撈取 **1000 筆**未貼標職缺當候選池，再從中**隨機抽 500 筆**進行 AI 貼標。執行後會：
1. 顯示從資料庫撈取的候選筆數。
2. 顯示隨機抽出的 ID 數量與列表。
3. 呼叫 `process_specific_jobs` 進行分析並寫回 Supabase，同時在 `scripts/labeling/` 下產生 JSON 報告。
4. 若已無未處理職缺，會提示並結束。

### 3. 參數調整

在 `run_random_batch.py` 的 `if __name__ == "__main__":` 區塊可調整：

-   **batch_size**：本次要貼標的筆數（預設 500）。
-   **pool_size**：候選池大小，建議 ≥ batch_size，越大隨機性越好（預設 1000）。

```python
# 範例：改為每次 200 筆
random_ids = get_random_unprocessed_ids(batch_size=200, pool_size=500)
```
