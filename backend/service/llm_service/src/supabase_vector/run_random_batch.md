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

-   **相依套件**: 確保已安裝 `requirements.txt` 中所列的套件，特別是 `python-dotenv` 和 `supabase`。
-   **環境變數**:
    -   在專案根目錄下建立一個 `.env` 檔案。
    -   在檔案中設定以下兩個變數：
        ```env
        SUPABASE_URL="YOUR_SUPABASE_URL"
        SUPABASE_SERVICE_ROLE_KEY="YOUR_SUPABASE_SERVICE_KEY"
        ```
-   **相依腳本**: 確保 `run_labeling_test.py` 檔案與此腳本位於同一目錄下，因為本腳本需要引用其中的 `process_specific_jobs` 函數。

### 2. 執行腳本

直接透過 Python 執行此腳本即可：

```bash
python src/supabase_vector/run_random_batch.py
```

執行後，腳本將會：
1.  顯示正在從資料庫撈取候選名單。
2.  報告撈取到的候選筆數。
3.  報告最終隨機抽出的 ID 數量及列表。
4.  開始執行主程式的標籤分析作業。
5.  如果資料庫中所有職缺都已處理完畢，腳本會顯示相應訊息並終止。

### 3. 參數調整

你可以在 `if __name__ == "__main__":` 區塊中，或直接在 `get_random_unprocessed_ids` 函數的預設值中，調整以下參數：

-   `batch_size`: 每次執行要處理的職缺數量。
-   `pool_size`: 用於隨機抽樣的候選池大小。較大的 `pool_size` 可以提供更好的隨機性，但會稍微增加資料庫查詢的時間。

```python
if __name__ == "__main__":
    # 範例：調整為每次處理 5 筆資料
    random_ids = get_random_unprocessed_ids(batch_size=5)
    
    if random_ids:
        # ...
```
