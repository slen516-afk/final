# Coursera 課程資料清洗步驟

> **來源檔案**: `Coursera_row_rows.csv`  
> **用途**: 整理後供「依職缺 / 使用者問卷」做課程推薦  
> **說明**: 目前爬取皆為英文課程，故移除語言欄位；師資已移除，課程資訊欄位名為 course_information。

---

## 一、原始欄位一覽

| 欄位名       | 說明           | 清洗後處理     |
|-------------|----------------|----------------|
| ID          | 流水號         | 保留           |
| 主要技能名稱 | 主技能標籤     | 保留           |
| 課程名稱    | 課程標題       | 保留           |
| 評分        | 數字或混雜字串 | 標準化為數值   |
| 評論數      | 如 "43K reviews" | 標準化為整數 |
| Metadata    | 難度·類型·時長 | 可拆成 level / course_type |
| 課程網址    | URL            | 保留，可作唯一鍵 |
| 課程        | 與課程名稱重複 | 可刪除重複欄   |
| 技能        | 逗號分隔技能   | 標準化為 list  |
| 課程資訊    | 大綱/模組      | 對應 course_information |
| 師資        | 講師名稱       | **移除**       |
| 開課時間    | 如 Starts Feb 17 | **移除**     |
| 建議學習時間 | 如 1-3 Months / P2M | **標準化**（見 Step 8） |
| 學習時長    | 如 25 hours    | **不納入**（已移除 duration_hours 欄位） |
| 語言        | 如 en          | **移除**（僅保留英文課程，不再儲存此欄） |

---

## 二、清洗步驟（建議順序）

### Step 1：讀取與基本檢查

- 使用 `pandas.read_csv("Coursera_row_rows.csv")` 讀取。
- 若有欄位因內容逗號錯位，可加上 `quoting=csv.QUOTE_MINIMAL` 或檢查 `on_bad_lines`。
- 檢查：`df.shape`、`df.dtypes`、`df.isnull().sum()`，確認列數與缺失狀況。

### Step 2：移除「語言」與「開課時間」欄位

- **語言**：目前全部為英文課程，不需保留。  
  `df = df.drop(columns=["語言"])`
- **開課時間**：不納入課程推薦維度，一併移除。  
  `df = df.drop(columns=["開課時間"])`  
  若 Step 2 與其他欄位一起刪除，可寫成：`df = df.drop(columns=["語言", "開課時間"])`
- 若未來改為多語系，可改為「僅保留語言為 en 的列」再決定是否保留語言欄位。

### Step 3：刪除重複欄位（可選）

- 「課程」與「課程名稱」內容重複，可刪除其一，例如：  
  `df = df.drop(columns=["課程"])`  
  保留「課程名稱」作為唯一顯示名稱。

### Step 4：評分標準化（rating）

- 目標：得到 0～5 的數值欄位 `rating`。
- 若「評分」欄已為純數字（如 4.6），直接轉 `pd.to_numeric(..., errors="coerce")`。
- 若混雜文字（如 "4.6Rating"），用正則擷取第一個數字（如 `re.search(r"(\d+\.?\d*)", str(val))`），再轉 float；若值 > 5 則除以 10 再 cap 在 5。

### Step 5：評論數標準化（review_count）

- 目標：得到整數欄位 `review_count`，方便排序與篩選。
- 從「評論數」欄解析，例如：
  - 正則範例：`(\d+(?:\.\d+)?)\s*(K|M)?\s*reviews?`（忽略大小寫）
  - 若為 K 則數值 × 1000，M × 1000000；無單位則直接取數字。
- 無法解析的填 `NaN`，後續排序時可 `na_position="last"` 或排除。

### Step 6：技能欄標準化

- 「技能」欄為逗號分隔字串，建議轉成 list 或保留為可分割字串。
- 作法範例：`df["skill_list"] = df["技能"].str.split(r"\s*,\s*", regex=True)`，或 `apply(lambda x: [s.strip() for s in str(x).split(",")] if pd.notna(x) else [])`。
- 後續可對接 `SKILL_MASTER` 做 skill_id 對應，供職缺/問卷推薦比對。

### Step 7：Metadata 拆欄（可選）

- 若需依「難度」「類型」篩選，可從 Metadata 拆出：
  - **level**: 取 `Beginner` / `Intermediate` / `Advanced`（正則或 `str.extract`）。
  - **course_type**: 取 `Course` / `Specialization` / `Professional Certificate` / `Guided Project` 等。
- 拆完可保留原始 Metadata 或僅保留拆出欄位。

### Step 8：建議學習時間標準化（必做）

- **目標**：將「建議學習時間」與 Metadata 中的時長資訊統一成可篩選的格式。
- **來源**：
  - 欄位「建議學習時間」常見：`P1M`、`P2M`、`P3M`、`P4M`、`P6M`、`P7M` 等（P + 數字 + M = 月）。
  - Metadata 常見：`1 - 4 Weeks`、`1 - 3 Months`、`3 - 6 Months`、`Less Than 2 Hours`。
- **標準化規則**（產出欄位建議：`duration_suggested` 或拆成 `duration_min_weeks` / `duration_max_weeks`）：
  1. **P 開頭**：`P(\d+)M` → 轉成「N months」或數值 N（月），例如 P2M → `2 months` 或 `duration_months = 2`。
  2. **數字 - 數字 Months**：如 `1 - 3 Months` → 保留為 `1-3 months` 或拆成 `duration_months_min=1`, `duration_months_max=3`。
  3. **數字 - 數字 Weeks**：如 `1 - 4 Weeks` → 保留為 `1-4 weeks` 或換算成約 0.25–1 month（÷4.33）。
  4. **Less Than 2 Hours**：保留為 `< 2 hours` 或單獨標記為極短時長。
  5. 若「建議學習時間」為空但 Metadata 有時長，可從 Metadata 用正則擷取後套用上述規則，再寫回同一標準欄位。
- **建議產出**：統一為一字串欄位（如 `1-3 months`、`2 months`、`1-4 weeks`、`< 2 hours`），或改為兩欄數值（如 `duration_weeks_min`, `duration_weeks_max`）方便依使用者可投入時間篩選。

### Step 10：去重

- 以「課程網址」為唯一鍵：`df = df.drop_duplicates(subset=["課程網址"], keep="first")`。
- 若同一課程會對應多個「主要技能」列，需先決定：保留多列（一列一主技能）或合併為一列、技能存成 list。

### Step 11：缺失值與型別

- 必填：至少「課程名稱」「課程網址」「主要技能名稱」或「技能」不應整列全空；可刪除或標記。
- 課程資訊（course_information）可為空，保留即可。
- 將 `rating`、`review_count` 設為數值型。

### Step 12：輸出

- 輸出為整理後檔案，例如 `courses_cleaned.csv` 或 `courses_cleaned.parquet`。
- 若後續要做向量推薦，可另建一欄「合併文本」（課程名稱 + course_information + 技能字串）供 embedding 使用。

---

## 三、清洗後建議保留欄位（對照）

| 建議欄位名（英文） | 對應原始/處理方式 |
|-------------------|-------------------|
| id                | ID                |
| primary_skill     | 主要技能名稱      |
| course_name       | 課程名稱（刪除重複欄「課程」後） |
| rating            | 評分 → 數值       |
| review_count      | 評論數 → 整數     |
| metadata          | Metadata（或拆成 level, course_type） |
| url               | 課程網址          |
| skills            | 技能 → 字串或 list |
| course_information | 課程資訊（大綱/模組） |
| duration_suggested| 建議學習時間 → **標準化**（如 "1-3 months"、"2 months"、"1-4 weeks"、"< 2 hours"） |

**已移除**: `duration_hours`（學習時長小時數）、`instructor`（師資）、`語言`（全部英文課程，不再儲存）、`開課時間`。

### 常見寫入結果說明（對應來源）

| 寫入結果 | 原因 | 是否合理 |
|----------|------|----------|
| **skills 為空 list `[]`** | 來源「技能」欄為空或缺失（約 52 筆）。`to_skill_list` 會回傳 `[]`。 | ✅ 合理，照來源如實寫入。 |
| **rating = 0、review_count = 0** | 來源「評分」為 0、「評論數」為 "0 reviews"（多為新上架、尚無評分課程）。`parse_rating` / `parse_review_count` 正確解析為 0。 | ✅ 合理，若希望「無評分」顯示為 NULL 可再於應用層處理。 |

---

## 四、後續對接建議

- **職缺推薦**: 由 `JOB_SKILL_REQUIREMENT` 取得職缺技能，與課程的 `primary_skill` / `skills`（或 skill_ids）做匹配後排序（如依 rating、review_count）。
- **問卷/技能落差推薦**: 由 `CAREER_SURVEY.skill_self_assessment` 或 `SKILL_GAP` 取得要補的技能，同樣與課程技能匹配後排序。

---

## 五、資料庫：新表、關聯鍵與寫入 Supabase

### Step 13：建立新表（course）

在 Supabase 建立課程主表，欄位對齊 ERD 風格（可稍後補進 `career_pilot_ERD_欄位對齊總表.md`）。

**建議表名**: `course`（課程主表）

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| course_id | 課程識別碼 | Course ID | INT / SERIAL | 課程唯一識別碼 | PRIMARY KEY |
| course_name | 課程名稱 | Course Name | VARCHAR(500) | 課程標題 | NOT NULL |
| url | 課程網址 | URL | VARCHAR(500) | Coursera 課程連結 | UNIQUE, NOT NULL |
| primary_skill_name | 主要技能名稱 | Primary Skill Name | VARCHAR(100) | 主技能標籤（可對應 skill_master.skill_name） | - |
| primary_skill_id | 主要技能識別碼 | Primary Skill ID | INT | 關聯技能主檔 | FOREIGN KEY → skill_master(skill_id) |
| rating | 評分 | Rating | NUMERIC(3,2) | 0～5 | - |
| review_count | 評論數 | Review Count | INT | 評論筆數 | - |
| level | 難度 | Level | VARCHAR(50) | Beginner / Intermediate / Advanced | - |
| course_type | 課程類型 | Course Type | VARCHAR(100) | Course / Specialization / Professional Certificate 等 | - |
| course_information | 課程資訊 | Course Information | TEXT | 大綱/模組 | - |
| duration_suggested | 建議學習時間 | Duration Suggested | VARCHAR(100) | 標準化字串（如 "1-3 months"） | - |
| skills | 技能列表 | Skills | JSONB | 技能名稱陣列，供推薦匹配 | - |
| source_platform | 來源平台 | Source Platform | VARCHAR(50) | 如 'Coursera' | DEFAULT 'Coursera' |
| created_at | 建立時間 | Created At | TIMESTAMPTZ | 寫入時間 | DEFAULT now() |

- 若尚未對接 `skill_master`，可先省略 `primary_skill_id`，僅留 `primary_skill_name`，待後續批次對應後再加 FK 與關聯表。

### Step 14：建立關聯鍵

- **course.primary_skill_id** → **skill_master.skill_id**（選填）：先以名稱對應，再寫入 skill_id。
  - **補填方式**：在 **course_clean_and_upload.ipynb** 最下方有「補上 primary_skill_id」一節：從 Supabase 讀取 `skill_master` 建立名稱（含同義詞）→ skill_id 對照，再對每筆 course 依 `primary_skill_name` 更新 `primary_skill_id`。若 `skill_master` 為空可先執行 `skill_write_evaluation.ipynb` 或手動補技能。
- **選配：多對多關聯表** `course_skill`（課程－技能）：若需依多個技能推薦，可新增：
  - `course_skill_id` (PK)、`course_id` (FK → course)、`skill_id` (FK → skill_master)。
  - 由清洗後的 `skills`（JSONB 陣列）拆條寫入，方便與 `job_skill_requirement` / `skill_gap` 做 JOIN 推薦。

在 Supabase SQL Editor 執行：

1. `CREATE TABLE course (...);`（見 Step 13 欄位）。
2. 若使用 `primary_skill_id`：`ALTER TABLE course ADD CONSTRAINT fk_course_primary_skill FOREIGN KEY (primary_skill_id) REFERENCES skill_master(skill_id);`
3. 若使用 `course_skill`：`CREATE TABLE course_skill (...);` 並建立對應 FK。

### Step 15：寫入 Supabase

- 將清洗後的 DataFrame 欄位對應到上表（欄位名改為 snake_case）。
- **第一次寫入即帶入 primary_skill_id**：寫入前從 `skill_master` 建立名稱（含同義詞）→ skill_id 對照，寫入時一併帶入，無需事後逐筆更新。
- **以 url 為唯一鍵 upsert**：表上有 `UNIQUE(url)`，寫入使用 `ON CONFLICT (url) DO UPDATE`。同一 URL 會更新既有列、不會重複插入；之後有新爬取資料時重跑寫入即可覆寫，避免重複。
- 建議批次寫入（例如每 100 筆一批），減少單次請求量。
- 寫入後查詢 `course` 筆數與抽樣幾筆，確認正確。

---

*文件建立後請先審核，再依此步驟實作 pandas 清洗腳本或 notebook；新表與關聯鍵可同步補進 ERD 欄位對齊總表。*
