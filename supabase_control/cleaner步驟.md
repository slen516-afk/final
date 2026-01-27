# 職缺資料清理與寫入 Supabase 完整步驟

> **建立日期**: 2026-01-26  
> **資料來源**: `clear_data_rows.csv` (10,934 筆職缺資料)  
> **目標資料表**: `COMPANY_INFO`, `JOB_POSTING`

---

## 📋 目錄

1. [前置準備](#前置準備)
2. [階段一：資料探索與品質檢查](#階段一資料探索與品質檢查)
3. [階段二：資料清理函數定義](#階段二資料清理函數定義)
4. [階段三：清理公司資料 (COMPANY_INFO)](#階段三清理公司資料-company_info)
5. [階段四：清理職缺資料 (JOB_POSTING)](#階段四清理職缺資料-job_posting)
6. [階段五：資料驗證與統計](#階段五資料驗證與統計)
7. [階段六：準備 Supabase 連線](#階段六準備-supabase-連線)
8. [階段七：寫入 Supabase 資料庫](#階段七寫入-supabase-資料庫)
9. [階段八：匯出清理後的資料（備份）](#階段八匯出清理後的資料備份)

---

## 前置準備

### 1. 安裝必要套件

```bash
pip install pandas numpy supabase python-dotenv
```

### 2. 取得 Supabase 連線資訊

1. 登入 Supabase Dashboard
2. 前往 **Settings > API**
3. 取得以下資訊：
   - **Project URL**: `https://xxxxx.supabase.co`
   - **service_role key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (⚠️ 請妥善保管，勿外流)

### 3. 建立環境變數檔案（建議）

建立 `.env` 檔案（不要 commit 到 git）：

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 階段一：資料探索與品質檢查

### 目的
了解資料的品質狀況，找出需要清理的問題

### 檢查項目

1. **缺失值統計**
   - 檢查每個欄位的缺失值數量
   - 識別關鍵欄位（如 `company_name`, `job_name`, `job_description`）的缺失情況

2. **重複資料檢查**
   - 完全重複的筆數
   - 根據 `(company_name, job_name)` 組合的重複情況

3. **job_id 格式檢查**
   - 檢查是否有格式異常的 `job_id`（如包含特殊字元）

4. **公司名稱統計**
   - 總共有多少不重複的公司
   - 哪些公司有最多職缺

5. **薪資資料檢查**
   - `salary_min`, `salary_max` 的有效值數量
   - 薪資範圍是否合理

### 預期輸出
- 缺失值統計表
- 重複資料數量
- 異常資料範例
- 資料品質報告

---

## 階段二：資料清理函數定義

### 目的
定義所有清理資料所需的函數

### 函數清單

1. **`clean_text(text)`**
   - 清理文字：移除多餘空白、換行符、特殊字元
   - 處理 None/NaN 值

2. **`extract_industry(job_category)`**
   - 從 `job_category` 推斷產業類別
   - 對應到：資訊科技、服務業、商業、行銷、設計、管理、製造業等

3. **`parse_company_size(headcount)`**
   - 從 `headcount` 欄位解析公司規模
   - 對應到：1-50, 51-200, 201-500, 501+

4. **`standardize_location(city, district, location)`**
   - 標準化地點格式
   - 合併 `city` 和 `district` 欄位

5. **`determine_remote_option(location, job_type)`**
   - 判斷遠端工作選項
   - 返回：remote, hybrid, onsite

6. **`merge_requirements(row)`**
   - 合併所有要求欄位為單一 `requirements` 文字
   - 包含：work_exp, education, major, language, skills, tools, certificates, other_requirements

7. **`create_job_details(row)`**
   - 建立 `job_details` JSON 物件
   - 包含：work_time, vacation, start_work, business_trip, legal_benefits, other_benefits, raw_benefits

### 預期輸出
- 所有清理函數定義完成
- 可以開始使用這些函數清理資料

---

## 階段三：清理公司資料 (COMPANY_INFO)

### 目的
建立乾淨的公司主檔，準備寫入 `COMPANY_INFO` 表

### 處理步驟

1. **建立公司主檔**
   - 根據 `company_name` 分組
   - 從多筆職缺中提取公司資訊（取最常見的值）

2. **清理公司名稱**
   - 使用 `clean_text()` 清理公司名稱

3. **推斷產業類別**
   - 使用 `extract_industry()` 從 `job_category` 推斷

4. **解析公司規模**
   - 使用 `parse_company_size()` 從 `headcount` 解析

5. **標準化地點**
   - 使用 `standardize_location()` 合併地點資訊

6. **建立最終公司資料表**
   - 對應 ERD 欄位：
     - `company_name` (VARCHAR(200), NOT NULL)
     - `industry` (VARCHAR(100))
     - `company_size` (VARCHAR(50))
     - `location` (VARCHAR(200))
     - `website` (VARCHAR(500)) - 如果沒有資料設為 NULL
     - `description` (TEXT) - 如果沒有資料設為 NULL

7. **去重**
   - 根據 `company_name` 去重

### 預期輸出
- 清理後的公司資料 DataFrame
- 公司數量統計
- 前 5 筆公司資料預覽

---

## 階段四：清理職缺資料 (JOB_POSTING)

### 目的
建立乾淨的職缺資料，準備寫入 `JOB_POSTING` 表

### 處理步驟

1. **建立公司名稱對應表**
   - 建立 `company_name` → `company_id` 的對應（稍後會用實際的 company_id 取代）

2. **清理職缺標題**
   - `job_name` → `job_title`（使用 `clean_text()`）

3. **清理職缺描述**
   - 清理 `job_description`（移除多餘空白、HTML 標籤等）

4. **合併職缺要求**
   - 使用 `merge_requirements()` 合併所有要求欄位

5. **標準化地點**
   - 使用 `standardize_location()` 合併地點

6. **判斷遠端選項**
   - 使用 `determine_remote_option()` 判斷

7. **建立 job_details JSON**
   - 使用 `create_job_details()` 建立 JSON 物件

8. **處理日期欄位**
   - `update_date` → `posted_date` (DATE)
   - `created_at` → `scraped_at` (DATETIME)

9. **建立最終職缺資料表**
   - 對應 ERD 欄位：
     - `company_id` (INT, FOREIGN KEY) - 稍後從 COMPANY_INFO 取得
     - `job_title` (VARCHAR(200))
     - `job_description` (TEXT)
     - `requirements` (TEXT)
     - `salary_min` (INT)
     - `salary_max` (INT)
     - `location` (VARCHAR(100))
     - `remote_option` (VARCHAR(50))
     - `job_details` (JSON)
     - `source_platform` (VARCHAR(50)) - 設為 '104人力銀行'
     - `source_url` (VARCHAR(500)) - 如果沒有設為 NULL
     - `posted_date` (DATE)
     - `scraped_at` (DATETIME)
     - `is_active` (BOOLEAN) - 設為 TRUE
     - `is_embedded` (BOOLEAN) - 設為 FALSE
     - `vector_id` (UUID) - 設為 NULL（稍後向量化時填入）

10. **去重**
    - 根據 `(company_name, job_title, location)` 組合去重
    - 保留最新的資料（`keep='last'`）

11. **移除關鍵欄位為空的資料**
    - 移除 `company_name`, `job_title`, `job_description` 為空的資料

### 預期輸出
- 清理後的職缺資料 DataFrame
- 去重前後的數量統計
- 前 3 筆職缺資料預覽

---

## 階段五：資料驗證與統計

### 目的
驗證清理後的資料品質，確保可以安全寫入資料庫

### 驗證項目

1. **公司資料統計**
   - 總公司數
   - 有 `industry` 的公司數量
   - 有 `location` 的公司數量

2. **職缺資料統計**
   - 總職缺數
   - 有 `job_description` 的職缺數
   - 有 `requirements` 的職缺數
   - 有 `salary_min` 的職缺數
   - 有 `location` 的職缺數

3. **job_description 長度檢查**
   - 統計描述長度
   - 識別過短的描述（< 50 字）

4. **資料完整性檢查**
   - 檢查必填欄位是否有值
   - 檢查資料格式是否正確

### 預期輸出
- 完整的資料品質報告
- 異常資料清單（如果有）
- 清理前後對比統計

---

## 階段六：準備 Supabase 連線

### 目的
設定 Supabase 連線，準備寫入資料

### 步驟

1. **載入環境變數**（如果使用 .env）
   ```python
   from dotenv import load_dotenv
   import os
   load_dotenv()
   ```

2. **建立 Supabase 客戶端**
   ```python
   from supabase import create_client, Client
   
   SUPABASE_URL = os.getenv('SUPABASE_URL')  # 或直接寫入
   SUPABASE_KEY = os.getenv('SUPABASE_KEY')  # 或直接寫入
   
   supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
   ```

3. **測試連線**
   - 嘗試讀取一個簡單的查詢
   - 確認連線正常

### 預期輸出
- Supabase 客戶端建立成功
- 連線測試通過

---

## 階段七：寫入 Supabase 資料庫

### 目的
將清理後的資料寫入 Supabase 資料庫

### 寫入順序

⚠️ **重要**：必須按照以下順序寫入，因為有外鍵關聯

### 步驟 1：寫入 COMPANY_INFO

1. **遍歷清理後的公司資料**
2. **檢查公司是否已存在**
   - 使用 `company_name` 查詢
3. **如果不存在，插入新公司**
   - 插入所有欄位
   - 取得返回的 `company_id`
4. **如果已存在，取得現有的 `company_id`**
5. **建立 `company_name` → `company_id` 對應表**

**注意事項**：
- 使用 `service_role key` 才能寫入資料
- 處理可能的錯誤（如重複鍵、格式錯誤等）
- 記錄成功和失敗的數量

### 步驟 2：寫入 JOB_POSTING

1. **遍歷清理後的職缺資料**
2. **取得對應的 `company_id`**
   - 從步驟 1 建立的對應表中查找
3. **檢查職缺是否已存在**
   - 根據 `(company_id, job_title, location)` 查詢
4. **如果不存在，插入新職缺**
   - 插入所有欄位
   - 確保 `company_id` 正確關聯
5. **如果已存在，跳過或更新**（根據需求決定）

**注意事項**：
- 確保 `company_id` 存在（外鍵約束）
- 處理日期格式（轉換為 ISO 格式）
- 處理 JSON 欄位（`job_details`）
- 處理 NULL 值
- 批次處理時注意速率限制
- 記錄進度（每 100 筆顯示一次）

### 預期輸出
- 成功寫入的公司數量
- 成功寫入的職缺數量
- 錯誤清單（如果有）
- 執行時間統計

---

## 階段八：匯出清理後的資料（備份）

### 目的
將清理後的資料匯出為 CSV，作為備份

### 步驟

1. **匯出公司資料**
   - 檔名：`companies_cleaned.csv`
   - 編碼：`utf-8-sig`（支援 Excel 開啟）

2. **匯出職缺資料**
   - 檔名：`jobs_cleaned.csv`
   - 編碼：`utf-8-sig`

### 預期輸出
- 兩個 CSV 檔案
- 檔案大小統計

---

## 📝 執行檢查清單

在開始執行前，請確認：

- [ ] 已安裝所有必要套件
- [ ] 已取得 Supabase 連線資訊
- [ ] 已備份原始 CSV 檔案
- [ ] 已了解 ERD 設計（`career_pilot_ERD_欄位對齊總表.md`）
- [ ] 已確認資料庫表結構已建立

---

## ⚠️ 注意事項

1. **資料備份**
   - 執行前務必備份原始資料
   - 建議先在測試環境執行

2. **批次處理**
   - 如果資料量很大，考慮分批寫入
   - 注意 Supabase 的速率限制

3. **錯誤處理**
   - 記錄所有錯誤，不要因為少數錯誤就停止
   - 分析錯誤原因，修正後重新執行

4. **資料驗證**
   - 寫入後檢查資料是否正確
   - 確認外鍵關聯正確

5. **向量化狀態**
   - 所有職缺的 `is_embedded` 設為 `FALSE`
   - 稍後需要單獨執行向量化流程

---

## 🔄 後續步驟

寫入資料庫後，還需要：

1. **向量化處理**
   - 將 `job_description` 和 `requirements` 向量化
   - 寫入 Qdrant Vector DB
   - 更新 `is_embedded = TRUE` 和 `vector_id`

2. **資料驗證**
   - 在 Supabase Dashboard 檢查資料
   - 執行一些查詢確認資料正確性

3. **技能提取**（可選）
   - 從 `requirements` 中提取技能
   - 寫入 `SKILL_MASTER` 和 `JOB_SKILL_REQUIREMENT` 表

---

## 📞 問題排除

### 常見問題

1. **連線錯誤**
   - 檢查 URL 和 KEY 是否正確
   - 確認網路連線正常

2. **外鍵約束錯誤**
   - 確認先寫入 COMPANY_INFO
   - 確認 company_id 存在

3. **資料格式錯誤**
   - 檢查日期格式
   - 檢查 JSON 格式
   - 檢查數值型別

4. **重複鍵錯誤**
   - 確認去重邏輯正確
   - 檢查是否有唯一約束衝突

---

**準備好後，請告訴我從哪個階段開始執行！** 🚀
