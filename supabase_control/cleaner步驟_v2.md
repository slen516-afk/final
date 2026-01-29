# 職缺資料清理與寫入 Supabase 完整步驟

> **建立日期**: 2026-01-26  
> **更新日期**: 2026-01-29 (新增階段九：技能提取)  
> **資料來源**: `clear_data_rows.csv` (10,934 筆職缺資料)  
> **目標資料表**: `COMPANY_INFO`, `JOB_POSTING`, `JOB_SKILL_REQUIREMENT`

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
10. [階段九：提取技能需求 (JOB_SKILL_REQUIREMENT)](#階段九提取技能需求-job_skill_requirement)
11. [後續步驟](#後續步驟)

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
   - 若資料含 `source_url`，可另檢查 `(source_url, job_name)` 重複（與寫入時重複判定一致）

3. **job_id 格式檢查**
   - 檢查是否有格式異常的 `job_id`（如包含特殊字元）

4. **公司名稱統計**
   - 總共有多少不重複的公司
   - 哪些公司有最多職缺

5. **薪資資料檢查**
   - `salary_min`, `salary_max` 的有效值數量
   - 薪資範圍是否合理

6. **`headcount` 欄位說明**
   - 代表**職缺需求人數**，非公司人數；不用於公司規模，後續清理不解析此欄位。

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

2. **`extract_industry(company_name)`**
   - 從 **公司名稱** 推斷產業類別（較 job_category 不易錯亂）
   - 對應到：資訊科技、服務業、商業、行銷、設計、管理、製造業等

3. **`standardize_location(city, district, location)`**
   - 輸出三個欄位：`(full_address, city, district)`
   - **full_address**：存放完整原始地址（合併 city、district、location 等）
   - **city**、**district**：從原始地址拆出城市與地區，供後續硬篩選使用

4. **`clean_salary(salary_raw)`**
   - 薪資資料清理，供寫入 ERD 的 `salary_min`、`salary_max`
   - **待遇面議**：`salary_min`、`salary_max` 皆設為 `40000`
   - **區間**（如 `30000~45000`）：解析出 `min`、`max` 分別寫入

5. **`determine_remote_option(location, job_type)`**
   - 判斷遠端工作選項
   - 返回：remote, hybrid, onsite
   - 職缺使用時可傳入 `full_address`（或原始地址相關欄位）與 `job_type`

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
   - 使用 `extract_industry(company_name)` 從 **公司名稱** 推斷

4. **公司規模與地點**
   - **company_size**、**location** 皆先設為 **NULL**
   - 若之後要爬公司資料，再重新寫入；目前皆用 null 值

5. **建立最終公司資料表**
   - 對應 ERD 欄位：
     - `company_name` (VARCHAR(200), NOT NULL)
     - `industry` (VARCHAR(100))
     - `company_size` (VARCHAR(50)) — 目前 NULL
     - `location` (VARCHAR(200)) — 目前 NULL
     - `website` (VARCHAR(500)) - 如果沒有資料設為 NULL
     - `description` (TEXT) - 如果沒有資料設為 NULL

6. **去重**
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
   - 使用 `standardize_location(city, district, location)` 產出 `(full_address, city, district)`
   - 職缺表**沒有**單一 `location` 欄位，僅有 `full_address`、`city`、`district`

6. **薪資清理**
   - 使用 `clean_salary()` 處理原始薪資
   - 待遇面議 → `salary_min`、`salary_max` 皆 40000；區間則解析 min / max 寫入

7. **判斷遠端選項**
   - 使用 `determine_remote_option()` 判斷（可傳入 `full_address` 或相關欄位與 `job_type`）

8. **建立 job_details JSON**
   - 使用 `create_job_details()` 建立 JSON 物件

9. **處理日期欄位**
   - `update_date` → `posted_date` (DATE)
   - `created_at` → `scraped_at` (DATETIME)

10. **建立最終職缺資料表**
    - 對應 ERD 欄位：
      - `company_id` (INT, FOREIGN KEY) - 稍後從 COMPANY_INFO 取得
      - `job_title` (VARCHAR(200))
      - `job_description` (TEXT)
      - `requirements` (TEXT)
      - `salary_min` (INT)
      - `salary_max` (INT)
      - **`full_address`** (VARCHAR) — 完整原始地址
      - **`city`** (VARCHAR) — 城市，供硬篩選
      - **`district`** (VARCHAR) — 地區，供硬篩選
      - `remote_option` (VARCHAR(50))
      - `job_details` (JSON)
      - `source_platform` (VARCHAR(50)) - 設為 '104人力銀行'
      - `source_url` (VARCHAR(500)) - 如果沒有設為 NULL
      - `posted_date` (DATE)
      - `scraped_at` (DATETIME)
      - `is_active` (BOOLEAN) - 設為 TRUE
      - `is_embedded` (BOOLEAN) - 設為 FALSE
      - `vector_id` (UUID) - 設為 NULL（稍後向量化時填入）

11. **去重**（與寫入時重複判定邏輯對齊）
    - **有 `source_url` 時**：依 **`(source_url, job_title)`** 去重
    - **無 `source_url` 時**：依 **`(company_name, job_title, full_address)`** 去重
    - 保留最新的資料（`keep='last'`）

12. **移除關鍵欄位為空的資料**
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
   - （`company_size`、`location` 目前皆 NULL，暫不統計）

2. **職缺資料統計**
   - 總職缺數
   - 有 `job_description` 的職缺數
   - 有 `requirements` 的職缺數
   - 有 `salary_min` / `salary_max` 的職缺數
   - 有 `full_address`、`city`、`district` 的職缺數

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
3. **確認資料庫是否有重複職缺（重複判定邏輯）**
   - **有 `source_url` 時**（新爬資料通常有 URL）：以 **`source_url` + `job_title`** 混和對照
     - 查詢 DB 是否已有相同 `(source_url, job_title)` 的職缺
     - 同平台同一連結 = 同一職缺，最精準，適合增量爬取
   - **無 `source_url` 時**（NULL）：改以 **`(company_id, job_title, full_address)`** 查詢
   - 若查得到 → 視為重複，**跳過或更新**（根據需求決定）；若查不到 → 插入
4. **若判定為不重複，插入新職缺**
   - 插入所有欄位
   - 確保 `company_id` 正確關聯
5. **若判定為重複**
   - 跳過，或依需求改為更新該筆（例如更新 `posted_date`、`is_active` 等）

**注意事項**：
- 確保 `company_id` 存在（外鍵約束）
- 寫入時務必帶入 `source_url`（有則填，無則 NULL），以便重複判定與後續增量爬取
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

## 階段九：提取技能需求 (JOB_SKILL_REQUIREMENT)

### 目的
從職缺的 `skills`、`tools` 欄位提取技能，建立職缺與技能的多對多關聯

### 前置條件
- ✅ SKILL_MASTER 表已建立並填入核心技能（約 50-100 個）
- ✅ JOB_POSTING 已寫入資料庫
- ✅ 已取得 job_id 與 skill_id 的對應關係

---

### 步驟 1：建立技能映射表

**目的**：從 SKILL_MASTER 建立「技能名稱 → skill_id」的查找表，支援同義詞匹配

```python
from supabase import create_client
import json
import pandas as pd

# 1. 從 Supabase 讀取 SKILL_MASTER
response = supabase.table('SKILL_MASTER').select('skill_id, skill_name, synonyms').execute()
skill_master_df = pd.DataFrame(response.data)

print(f"✅ 讀取了 {len(skill_master_df)} 個技能")

# 2. 建立同義詞反向索引（包含標準名稱 + 所有同義詞）
synonym_to_skill_id = {}

for _, row in skill_master_df.iterrows():
    skill_id = row['skill_id']
    skill_name = row['skill_name']
    synonyms_raw = row['synonyms']
    
    # 處理 synonyms（可能是 JSON 字串或已解析的列表）
    if synonyms_raw:
        if isinstance(synonyms_raw, str):
            synonyms = json.loads(synonyms_raw)
        else:
            synonyms = synonyms_raw
    else:
        synonyms = []
    
    # 標準名稱本身（忽略大小寫）
    synonym_to_skill_id[skill_name.lower()] = skill_id
    
    # 所有同義詞
    for syn in synonyms:
        synonym_to_skill_id[syn.lower()] = skill_id

print(f"✅ 建立了 {len(synonym_to_skill_id)} 個技能映射（含同義詞）")
```

---

### 步驟 2：從 raw_data 提取技能

**資料來源**：
- `skills` 欄位（主要技能，如："Python, Java, SQL"）
- `tools` 欄位（工具技能，如："Git, Docker, AWS"）

```python
# 1. 讀取原始資料（假設已清理好的 DataFrame）
raw_df = pd.read_csv('clear_data_rows.csv')

print(f"✅ 讀取了 {len(raw_df)} 筆原始職缺資料")

# 2. 解析技能字串為列表
def parse_skills(skills_str, tools_str):
    """
    合併 skills 和 tools 欄位，拆分為技能列表
    
    輸入範例：
    - skills_str: "Python, Java, SQL"
    - tools_str: "Git, Docker"
    
    輸出：["Python", "Java", "SQL", "Git", "Docker"]
    """
    all_skills = []
    
    # 處理 skills 欄位
    if pd.notna(skills_str) and str(skills_str).strip():
        skills = [s.strip() for s in str(skills_str).split(',')]
        all_skills.extend(skills)
    
    # 處理 tools 欄位
    if pd.notna(tools_str) and str(tools_str).strip():
        tools = [t.strip() for t in str(tools_str).split(',')]
        all_skills.extend(tools)
    
    # 去重（保留順序）
    return list(dict.fromkeys(all_skills))

# 3. 應用到 DataFrame
raw_df['parsed_skills'] = raw_df.apply(
    lambda row: parse_skills(row.get('skills'), row.get('tools')), 
    axis=1
)

# 統計
total_skills = sum(len(skills) for skills in raw_df['parsed_skills'])
avg_skills = total_skills / len(raw_df)

print(f"✅ 解析了 {len(raw_df)} 筆職缺的技能")
print(f"📊 平均每個職缺有 {avg_skills:.1f} 個技能")
```

---

### 步驟 3：匹配技能並建立關聯記錄

**匹配邏輯**：
- 精確匹配：直接從 `synonym_to_skill_id` 查找
- 未匹配的技能記錄下來，供後續補充

```python
# 1. 從 Supabase 讀取 JOB_POSTING（取得 job_id）
print("讀取 JOB_POSTING 資料...")
job_response = supabase.table('JOB_POSTING').select('job_id, company_id, job_title').execute()
job_posting_df = pd.DataFrame(job_response.data)

# 2. 讀取 COMPANY_INFO（取得 company_name）
print("讀取 COMPANY_INFO 資料...")
company_response = supabase.table('COMPANY_INFO').select('company_id, company_name').execute()
company_df = pd.DataFrame(company_response.data)

# 3. 合併以取得 (company_name, job_title) → job_id 的映射
job_with_company = job_posting_df.merge(company_df, on='company_id')
job_mapping = {}
for _, row in job_with_company.iterrows():
    key = (row['company_name'], row['job_title'])
    job_mapping[key] = row['job_id']

print(f"✅ 建立了 {len(job_mapping)} 個職缺映射")

# 4. 匹配技能並建立關聯
job_skill_records = []
unmatched_skills = set()
unmatched_jobs = 0

for _, row in raw_df.iterrows():
    company_name = row['company_name']
    job_title = row['job_name']  # 注意：原始資料用 job_name
    
    # 取得對應的 job_id
    job_id = job_mapping.get((company_name, job_title))
    
    if not job_id:
        unmatched_jobs += 1
        continue
    
    # 解析技能並匹配
    for skill_name in row['parsed_skills']:
        # 忽略空白或過短的技能名稱
        if not skill_name or len(skill_name) < 2:
            continue
            
        skill_id = synonym_to_skill_id.get(skill_name.lower())
        
        if skill_id:
            job_skill_records.append({
                'job_id': job_id,
                'skill_id': skill_id,
                'importance': 'required',  # 預設為必要技能
                'proficiency_level': None  # 原始資料無此資訊
            })
        else:
            unmatched_skills.add(skill_name)

print(f"\n✅ 成功匹配 {len(job_skill_records)} 筆技能需求")
print(f"⚠️ 未匹配職缺數：{unmatched_jobs} 筆（可能是公司名稱或職稱不一致）")
print(f"⚠️ 未匹配技能數：{len(unmatched_skills)} 個")

# 顯示前 10 個未匹配技能
if unmatched_skills:
    print(f"\n未匹配技能範例：{list(unmatched_skills)[:10]}")
```

---

### 步驟 4：去重並寫入 JOB_SKILL_REQUIREMENT

**去重邏輯**：同一職缺不應有重複技能

```python
# 1. 轉為 DataFrame 並去重
job_skill_df = pd.DataFrame(job_skill_records)

if len(job_skill_df) == 0:
    print("❌ 沒有可寫入的技能需求記錄")
else:
    print(f"去重前：{len(job_skill_df)} 筆")
    job_skill_df = job_skill_df.drop_duplicates(subset=['job_id', 'skill_id'])
    print(f"✅ 去重後剩餘 {len(job_skill_df)} 筆唯一關聯")
    
    # 2. 批次寫入 Supabase（避免單筆寫入過慢）
    BATCH_SIZE = 500
    total_inserted = 0
    errors = []
    
    for i in range(0, len(job_skill_df), BATCH_SIZE):
        batch = job_skill_df.iloc[i:i+BATCH_SIZE].to_dict('records')
        
        try:
            response = supabase.table('JOB_SKILL_REQUIREMENT').insert(batch).execute()
            total_inserted += len(batch)
            print(f"進度：{total_inserted}/{len(job_skill_df)} ({total_inserted/len(job_skill_df)*100:.1f}%)")
        except Exception as e:
            errors.append((i, str(e)))
            print(f"❌ 批次 {i}-{i+BATCH_SIZE} 寫入失敗：{e}")
    
    print(f"\n✅ 成功寫入 {total_inserted} 筆技能需求")
    if errors:
        print(f"❌ 失敗批次數：{len(errors)}")
```

---

### 步驟 5：處理未匹配技能（補充 SKILL_MASTER）

**未匹配技能**：原始資料中有，但 SKILL_MASTER 沒有的技能

```python
# 1. 匯出未匹配技能清單
if unmatched_skills:
    unmatched_df = pd.DataFrame({
        'skill_name': sorted(list(unmatched_skills)),
        'skill_category': None,  # 需手動分類
        'synonyms': None,
        'notes': ''  # 可手動填寫備註
    })
    
    unmatched_df.to_csv('unmatched_skills.csv', index=False, encoding='utf-8-sig')
    
    print(f"\n✅ 已匯出 {len(unmatched_skills)} 個未匹配技能到 unmatched_skills.csv")
    print("📝 處理建議：")
    print("   1. 檢查拼寫錯誤（如 'Pyhton' → 'Python'）")
    print("   2. 檢查同義詞（如 'JS' → 應加入 JavaScript 的 synonyms）")
    print("   3. 確認是否為新技能（需新增到 SKILL_MASTER）")
    print("   4. 過濾無意義文字（如 '等'、'相關經驗'）")
    print("\n請手動分類後補充到 SKILL_MASTER，然後重新執行步驟 3-4")
else:
    print("✅ 所有技能都已匹配，無需補充")
```

---

### 步驟 6：驗證寫入結果

執行以下 SQL 檢查資料正確性：

```sql
-- 1. 檢查技能需求總數
SELECT COUNT(*) as total_requirements 
FROM JOB_SKILL_REQUIREMENT;

-- 2. 檢查每個職缺平均有多少技能
SELECT AVG(skill_count) as avg_skills_per_job
FROM (
    SELECT job_id, COUNT(*) as skill_count
    FROM JOB_SKILL_REQUIREMENT
    GROUP BY job_id
) sub;

-- 3. 檢查最常見的技能（前 20 名）
SELECT sm.skill_name, sm.skill_category, COUNT(*) as job_count
FROM JOB_SKILL_REQUIREMENT jsr
JOIN SKILL_MASTER sm ON jsr.skill_id = sm.skill_id
GROUP BY sm.skill_name, sm.skill_category
ORDER BY job_count DESC
LIMIT 20;

-- 4. 檢查是否有孤立的技能（沒有任何職缺需求）
SELECT skill_name, skill_category
FROM SKILL_MASTER
WHERE skill_id NOT IN (
    SELECT DISTINCT skill_id 
    FROM JOB_SKILL_REQUIREMENT
);

-- 5. 檢查技能需求分布（按類別統計）
SELECT sm.skill_category, COUNT(*) as requirement_count
FROM JOB_SKILL_REQUIREMENT jsr
JOIN SKILL_MASTER sm ON jsr.skill_id = sm.skill_id
GROUP BY sm.skill_category
ORDER BY requirement_count DESC;
```

**在 Python 中執行驗證**：

```python
# 驗證統計
print("\n" + "="*50)
print("驗證統計")
print("="*50)

# 總數
total_req = supabase.table('JOB_SKILL_REQUIREMENT').select('*', count='exact').execute()
print(f"✅ 技能需求總數：{total_req.count}")

# 最常見技能（需要手動執行 SQL 或用 pandas 處理）
print("\n📊 前 10 大熱門技能：")
response = supabase.rpc('get_top_skills', {'limit_count': 10}).execute()
# 注意：這需要在 Supabase 中建立 RPC 函數，或用 Python 處理

print("\n✅ 驗證完成")
```

---

### 預期輸出

1. **成功寫入的技能需求數量**
   - 範例：9,876 筆 JOB_SKILL_REQUIREMENT 記錄

2. **未匹配技能清單**
   - CSV 檔案：`unmatched_skills.csv`
   - 包含約 50-200 個需補充的技能

3. **統計報告**
   ```
   ✅ 匹配成功：8,600 筆技能需求
   ✅ 匹配率：87.3%
   ⚠️ 未匹配職缺：12 筆（可能是公司名稱不一致）
   ⚠️ 未匹配技能：156 個（需補充 SKILL_MASTER）
   📊 平均每個職缺：5.2 個技能
   ```

---

### 常見問題

**Q1：為什麼有些職缺沒有匹配到 job_id？**
- 可能原因：
  1. company_name 或 job_title 在清理過程中被修改
  2. 寫入 JOB_POSTING 時跳過了某些職缺（重複或資料不完整）
- 解決方法：
  - 檢查 `clean_text()` 函數是否過度清理
  - 比對原始資料與資料庫中的公司名稱和職稱

**Q2：未匹配技能太多怎麼辦？**
- 優先處理策略：
  1. 先處理出現次數 > 10 的技能（高頻技能優先）
  2. 使用 LLM 輔助分類（批次處理）
  3. 建立同義詞規則（如 "JS" → "JavaScript"）
- 範例代碼：
  ```python
  # 統計未匹配技能的出現頻率
  skill_freq = {}
  for skills in raw_df['parsed_skills']:
      for skill in skills:
          if skill in unmatched_skills:
              skill_freq[skill] = skill_freq.get(skill, 0) + 1
  
  # 按頻率排序
  sorted_skills = sorted(skill_freq.items(), key=lambda x: x[1], reverse=True)
  print("前 20 個高頻未匹配技能：")
  for skill, freq in sorted_skills[:20]:
      print(f"  {skill}: {freq} 次")
  ```

**Q3：如何更新已寫入的技能需求？**
- 刪除舊資料：
  ```python
  # 刪除特定職缺的技能需求
  job_ids_to_update = [123, 456, 789]
  for job_id in job_ids_to_update:
      supabase.table('JOB_SKILL_REQUIREMENT')\
             .delete()\
             .eq('job_id', job_id)\
             .execute()
  ```
- 重新執行步驟 3-4

**Q4：如何批次補充 SKILL_MASTER？**
```python
# 假設已手動分類好 unmatched_skills.csv
new_skills_df = pd.read_csv('unmatched_skills_classified.csv')

# 批次插入
new_skills = new_skills_df.to_dict('records')
response = supabase.table('SKILL_MASTER').insert(new_skills).execute()
print(f"✅ 新增了 {len(new_skills)} 個技能到 SKILL_MASTER")

# 重新執行步驟 1-4
```

---

### 後續優化（可選）

1. **自動分類未匹配技能（使用 LLM）**
   ```python
   from openai import OpenAI
   
   client = OpenAI(api_key='your-api-key')
   
   def classify_skill(skill_name):
       prompt = f"""
       技能名稱：{skill_name}
       
       請判斷此技能的分類（Programming/Framework/Tool/Soft）並提供同義詞。
       
       輸出 JSON 格式：
       {{
           "skill_name": "標準化名稱",
           "skill_category": "分類",
           "synonyms": ["同義詞1", "同義詞2"]
       }}
       """
       
       response = client.chat.completions.create(
           model="gpt-4",
           messages=[{"role": "user", "content": prompt}]
       )
       return json.loads(response.choices[0].message.content)
   
   # 批次分類
   classified_skills = []
   for skill in list(unmatched_skills)[:50]:  # 先處理前 50 個
       result = classify_skill(skill)
       classified_skills.append(result)
   ```

2. **importance 自動判定**
   - 根據技能在 `requirements` 中的位置判斷重要性
   - 關鍵字匹配（如「必備」→ required，「加分」→ nice-to-have）

3. **proficiency_level 推測**
   - 從「3 年以上」等文字推測熟練度要求
   - 使用正則表達式提取年資要求

---

## 後續步驟

階段九完成後，還需要：

1. **向量化處理**
   - 將 `job_description` 和 `requirements` 向量化
   - 寫入 Qdrant Vector DB
   - 更新 `is_embedded = TRUE` 和 `vector_id`

2. **資料驗證**
   - 在 Supabase Dashboard 檢查資料
   - 執行一些查詢確認資料正確性

3. **補充遺漏技能**
   - 處理 `unmatched_skills.csv`
   - 更新 SKILL_MASTER
   - 重新執行階段九的步驟 3-4

---

## 📝 執行檢查清單

在開始執行前，請確認：

- [ ] 已安裝所有必要套件
- [ ] 已取得 Supabase 連線資訊
- [ ] 已備份原始 CSV 檔案
- [ ] 已了解 ERD 設計（`career_pilot_ERD_欄位對齊總表.md`）
- [ ] 已確認資料庫表結構已建立（包含 SKILL_MASTER）
- [ ] 已填入 SKILL_MASTER 基礎資料（50-100 個核心技能）

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

6. **技能匹配率**
   - 目標匹配率：> 85%
   - 如果匹配率過低（< 70%），檢查 SKILL_MASTER 是否缺少常見技能

---

## 📞 問題排除

### 常見問題

1. **連線錯誤**
   - 檢查 URL 和 KEY 是否正確
   - 確認網路連線正常

2. **外鍵約束錯誤**
   - 確認先寫入 COMPANY_INFO
   - 確認 company_id 存在
   - 確認 skill_id 存在（階段九）

3. **資料格式錯誤**
   - 檢查日期格式
   - 檢查 JSON 格式
   - 檢查數值型別

4. **重複鍵錯誤**
   - 確認寫入前依 `source_url`+`job_title`（有 URL）或 `(company_id, job_title, full_address)`（無 URL）查詢是否已存在
   - 檢查是否有唯一約束衝突
   - JOB_SKILL_REQUIREMENT：確認 `(job_id, skill_id)` 組合唯一

5. **技能匹配問題**
   - 檢查 SKILL_MASTER 是否有足夠的核心技能
   - 檢查同義詞是否設定正確
   - 檢查技能名稱是否有多餘空白

---

**準備好後，請告訴我從哪個階段開始執行！** 🚀
