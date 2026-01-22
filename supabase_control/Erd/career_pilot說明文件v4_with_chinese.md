# Career Pilot ERD 資料表說明文件

> **版本**:v2.0  
> **更新日期**:2026-01-21  
> **基於**:PRD、Work Flow、流程圖與架構圖設計

---

## 📋 目錄

1. [資料表索引(中英對照)](#資料表索引中英對照)
2. [使用者認證與基本資料表](#1-使用者認證與基本資料表)
3. [職涯調查與問卷表](#2-職涯調查與問卷表)
4. [履歷相關表(核心)](#3-履歷相關表核心)
5. [檔案上傳與 OCR 處理表](#4-檔案上傳與-ocr-處理表)
6. [職缺與公司資料表](#5-職缺與公司資料表)
7. [技能管理表](#6-技能管理表)
8. [職缺媒合與評分表](#7-職缺媒合與評分表)
9. [投遞追蹤表](#8-投遞追蹤表)
10. [職涯分析與技能發展表](#9-職涯分析與技能發展表)
11. [資料表關聯關係總覽](#資料表關聯關係總覽)
12. [資料流程說明](#資料流程說明)
13. [技術架構對應](#技術架構對應)
14. [向量化處理說明](#向量化處理說明)
15. [版本支援說明](#版本支援說明)
16. [設計原則](#設計原則)

---

## 資料表索引(中英對照)

| 編號 | 中文表名 | 英文表名 | 功能模組 | 說明 |
|-----|---------|---------|---------|------|
| 1 | 使用者主表 | USER | ⚪ 基礎 | 儲存使用者帳號與認證資訊 |
| 2 | 使用者個人檔案 | USER_PROFILE | ⚪ 基礎 | 儲存使用者詳細個人資料 |
| 3 | 職涯調查問卷 | CAREER_SURVEY | ⚪ 基礎 | 儲存使用者職涯目標與偏好 |
| 4 | 履歷主表 | RESUME | 🔵 履歷生成 | 儲存履歷核心資料 |
| 5 | 履歷版本 | RESUME_VERSION | 🔵 履歷生成 | 管理履歷多版本內容 |
| 6 | 履歷模板 | RESUME_TEMPLATE | 🔵 履歷生成 | 定義履歷格式與結構 |
| 7 | 上傳事件記錄 | UPLOAD_EVENT | 🔵 履歷生成 | 追蹤檔案上傳事件 |
| 8 | OCR 辨識結果 | OCR_RESULT | 🔵 履歷生成 | 儲存文件解析結果 |
| 9 | 公司資訊 | COMPANY_INFO | 🟢 職缺推薦 | 儲存企業基本資料 |
| 10 | 職缺資訊 | JOB_POSTING | 🟢 職缺推薦 | 儲存職缺詳細資訊 |
| 11 | 職缺技能需求 | JOB_SKILL_REQUIREMENT | 🟢 職缺推薦 | 定義職缺所需技能 |
| 12 | 技能主檔 | SKILL_MASTER | ⚪ 共用 | 技能標準化字典 |
| 13 | 使用者技能 | USER_SKILL | ⚪ 共用 | 記錄使用者擁有的技能 |
| 14 | 職缺媒合記錄 | JOB_MATCHING | 🟢 職缺推薦 | 記錄履歷與職缺的配對 |
| 15 | 媒合分數 | MATCH_SCORE | 🟢 職缺推薦 | 儲存配適度評分細節 |
| 16 | 投遞記錄 | APPLICATION_RECORD | 🟢 職缺推薦 | 追蹤求職投遞狀態 |
| 17 | 職涯分析報告 | CAREER_ANALYSIS_REPORT | 🟠 職能分析 | 儲存 AI 生成的分析報告 |
| 18 | 技能落差 | SKILL_GAP | 🟠 職能分析 | 識別技能缺口 |
| 19 | Side Project 推薦 | SIDE_PROJECT_RECOMMENDATION | 🟠 職能分析 | 推薦學習專案 |

---

## 1. 使用者認證與基本資料表

### 1.1 USER(使用者主表)

**功能說明**:儲存使用者帳號、密碼與認證資訊,支援多種登入方式(Email/LinkedIn/Google)

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| user_id | 使用者識別碼 | User ID | INT | 使用者唯一識別碼 | PRIMARY KEY |
| email | 電子郵件 | Email | VARCHAR(255) | 使用者電子郵件 | UNIQUE, NOT NULL |
| password_hash | 密碼雜湊值 | Password Hash | VARCHAR(255) | 密碼雜湊值 | NOT NULL |
| auth_provider | 認證提供者 | Authentication Provider | VARCHAR(50) | 認證提供者 (Email/LinkedIn/Google) | DEFAULT 'Email' |
| created_at | 建立時間 | Created At | DATETIME | 帳號建立時間 | NOT NULL |
| last_login | 最後登入時間 | Last Login | DATETIME | 最後登入時間 | - |
| is_active | 帳號啟用狀態 | Is Active | BOOLEAN | 帳號是否啟用 | DEFAULT TRUE |

**設計說明**:
- 對應流程圖「動作: 登入/註冊」步驟
- 架構圖中的 Auth Service (OAuth2/OIDC) 負責處理認證邏輯
- `password_hash` 使用 bcrypt 或 Argon2 加密

---

### 1.2 USER_PROFILE(使用者個人檔案)

**功能說明**:儲存使用者詳細個人資料,與敏感認證資料分離

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| profile_id | 個人檔案識別碼 | Profile ID | INT | 個人檔案識別碼 | PRIMARY KEY |
| user_id | 使用者識別碼 | User ID | INT | 關聯使用者 | FOREIGN KEY, UNIQUE |
| github_repo | GitHub 帳號 | GitHub Repository | VARCHAR(100) | GitHub 帳號網址 | - |
| full_name | 姓名 | Full Name | VARCHAR(100) | 使用者姓名 | - |
| location | 所在地區 | Location | VARCHAR(100) | 所在地區 | - |
| years_of_experience | 工作年資 | Years of Experience | INT | 工作年資 | - |
| current_position | 目前職位 | Current Position | VARCHAR(100) | 目前職位 | - |
| education_background | 教育背景 | Education Background | TEXT | 教育背景 | - |
| privacy_settings | 隱私設定 | Privacy Settings | JSON | 隱私設定 | - |
| updated_at | 更新時間 | Updated At | DATETIME | 最後更新時間 | - |

**設計說明**:
- 對應 Work Flow 的「Step2:專業個人檔案建構」
- **為何 USER 拆成 USER + USER_PROFILE**:
  - 帳密歸帳密:敏感認證資料獨立儲存
  - 檔案歸檔案:業務細節分開管理,查詢效能高
- **education_background 使用 TEXT**:教育背景可能包含校名、系所、榮譽獎項、研究論文題目等,長度變動極大
- **privacy_settings 使用 JSON**:隱私設定包含多個開關(是否公開電話、是否允許 AI 分析、通知偏好等),結構多變且不常作為查詢條件
- **github_repo**:未來功能先保留,用於整合 GitHub 作品集

---

## 2. 職涯調查與問卷表

### 2.1 CAREER_SURVEY(職涯調查問卷)

**功能說明**:記錄使用者的職涯目標、技能自評與求職偏好,作為 AI 分析的重要輸入

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| survey_id | 問卷識別碼 | Survey ID | INT | 問卷識別碼 | PRIMARY KEY |
| user_id | 使用者識別碼 | User ID | INT | 關聯使用者 | FOREIGN KEY |
| career_preference | 職涯偏好 | Career Preference | JSON | 職涯偏好 (目標職位/產業) | - |
| skill_self_assessment | 技能自評 | Skill Self Assessment | JSON | 技能自評 (1-10分) | - |
| salary_min | 最低薪資期待 | Minimum Salary | INT | 最低薪資期待 | - |
| salary_max | 最高薪資期待 | Maximum Salary | INT | 最高薪資期待 | - |
| location_preference | 工作地點偏好 | Location Preference | VARCHAR(100) | 工作地點偏好 | - |
| remote_preference | 遠端工作偏好 | Remote Work Preference | VARCHAR(50) | 遠端工作偏好 | - |
| career_motivation | 職涯轉換動機 | Career Motivation | JSON | 職涯轉換動機 | - |
| completed_at | 完成時間 | Completed At | DATETIME | 完成時間 | - |
| updated_at | 更新時間 | Updated At | DATETIME | 更新時間 | - |

**設計說明**:
- 對應流程圖「動作: 選擇填寫職涯調查問卷」
- 支援 Release 2 的「問卷內容修改」功能
- JSON 欄位格式範例:
  ```json
  {
    "career_preference": ["Backend Engineer", "Full-Stack Developer"],
    "skill_self_assessment": {"Python": 8, "JavaScript": 7},
    "career_motivation": "尋求更好的技術挑戰與成長機會"
  }
  ```

---

## 3. 履歷相關表(核心)

### 3.1 RESUME(履歷主表)🔵

**功能說明**:儲存履歷核心資料,支援上傳與生成兩種來源,需進行向量化處理

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| resume_id | 履歷識別碼 | Resume ID | INT | 履歷識別碼 | PRIMARY KEY |
| user_id | 使用者識別碼 | User ID | INT | 關聯使用者 | FOREIGN KEY |
| template_id | 模板識別碼 | Template ID | INT | 使用的模板 | FOREIGN KEY |
| resume_type | 履歷類型 | Resume Type | VARCHAR(50) | 履歷類型 (uploaded/generated) | NOT NULL |
| structured_data | 結構化資料 | Structured Data | JSON | 結構化履歷資料 | - |
| normalized_data | 標準化資料 | Normalized Data | JSON | 標準化後資料 | - |
| is_primary | 主要履歷標記 | Is Primary | BOOLEAN | 是否為主要履歷 | DEFAULT FALSE |
| created_at | 建立時間 | Created At | DATETIME | 建立時間 | NOT NULL |
| updated_at | 更新時間 | Updated At | DATETIME | 更新時間 | - |

**設計說明**:
- 對應流程圖「動作: 選擇資料/履歷輸入方式」
- **⚡ 需要向量化**:`structured_data` 內容會轉換為向量並存入 Qdrant
- **resume_type 說明**:
  - `uploaded`:使用者上傳的 PDF/Word 檔案
  - `generated`:由 AI 生成的履歷
- **structured_data vs normalized_data**:
  - `structured_data`:原始解析資料
  - `normalized_data`:經過標準化處理(統一技能名稱、日期格式等)

---

### 3.2 RESUME_VERSION(履歷版本)🔵

**功能說明**:管理履歷的多個版本,支援針對不同職缺優化內容

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| version_id | 版本識別碼 | Version ID | INT | 版本識別碼(全域唯一主鍵) | PRIMARY KEY |
| resume_id | 履歷識別碼 | Resume ID | INT | 關聯履歷 | FOREIGN KEY |
| version_number | 版本號碼 | Version Number | INT | 邏輯版本序號(第幾次修改,允許同一序號對應不同職缺) | NOT NULL |
| file_path | 檔案儲存路徑 | File Path | VARCHAR(255) | 該版本的檔案儲存路徑 | - |
| content | 版本內容 | Content | JSON | 版本完整內容 | - |
| optimization_target | 優化目標職位 | Optimization Target | VARCHAR(100) | 優化目標職位 | - |
| created_at | 建立時間 | Created At | DATETIME | 建立時間 | NOT NULL |

**設計說明**:
- 對應流程圖右側「動作: 用戶確認履歷修改」→「動作: 確認履歷並生成職缺名列表」
- **版本識別碼 vs 版本號碼**:
  - `version_id`: 每個版本的唯一編號，不會重複 (像身份證字號)
  - `version_number`: 第幾次修改，可以重複 (像第 1 版、第 2 版、第 3 版)
  - **為什麼會不同？**
    - 使用者第 2 次修改履歷時，可能同時針對「Google 職缺」和「Microsoft 職缺」各產生一個版本
    - 這兩個版本的 `version_id` 不同，但 `version_number` 都是 2
  - **資料約束**: `UNIQUE (resume_id, version_number, optimization_target)`  組成唯一鍵 同一份履歷、同一版本號、針對同一個職位，只能有一個記錄

---

### 3.3 RESUME_TEMPLATE(履歷模板)🔵

**功能說明**:定義履歷的格式與結構,支援不同產業與職位需求

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| template_id | 模板識別碼 | Template ID | INT | 模板識別碼 | PRIMARY KEY |
| template_name | 模板名稱 | Template Name | VARCHAR(100) | 模板名稱 | NOT NULL |
| template_type | 模板類型 | Template Type | VARCHAR(50) | 模板類型 (ATS/Creative/Standard) | - |
| template_structure | 模板結構 | Template Structure | JSON | 模板結構定義 | - |
| created_at | 建立時間 | Created At | DATETIME | 建立時間 | NOT NULL |

**設計說明**:
- 對應流程圖「動作: 用戶選擇履歷模板」
- **template_type 說明**:
  - `ATS`:適合自動篩選系統的簡潔格式
  - `Creative`:適合設計/行銷產業的視覺化格式
  - `Standard`:通用標準格式
- **template_structure 範例**:
  ```json
  {
    "sections": ["summary", "experience", "education", "skills"],
    "order": ["summary", "skills", "experience", "education"],
    "max_pages": 2
  }
  ```

---

## 4. 檔案上傳與 OCR 處理表

### 4.1 UPLOAD_EVENT(上傳事件記錄)🔵

**功能說明**:追蹤檔案上傳事件,支援非同步處理與錯誤追蹤

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| event_id | 事件識別碼 | Event ID | INT | 事件識別碼 | PRIMARY KEY |
| user_id | 使用者識別碼 | User ID | INT | 關聯使用者 | FOREIGN KEY |
| file_name | 檔案名稱 | File Name | VARCHAR(255) | 檔案名稱 | NOT NULL |
| file_path | 檔案儲存路徑 | File Path | VARCHAR(500) | 檔案儲存路徑 | NOT NULL |
| upload_type | 上傳類型 | Upload Type | VARCHAR(50) | 上傳類型 (resume/portfolio) | - |
| status | 處理狀態 | Status | VARCHAR(50) | 處理狀態 (pending/processing/completed/failed) | DEFAULT 'pending' |
| uploaded_at | 上傳時間 | Uploaded At | DATETIME | 上傳時間 | NOT NULL |
| metadata | 檔案中繼資料 | Metadata | JSON | 檔案中繼資料 | - |

**設計說明**:
- 對應流程圖「儲存原始檔案 & 發出 UploadEvent」
- **檔案儲存架構**:
  - 實際檔案 (PDF/Word) 儲存在 Blob Store (Supabase Storage)
  - 此表只記錄檔案路徑、名稱、狀態等中繼資料
  - 不在 PostgreSQL 資料庫存放大型二進位檔案（避免拖累查詢速度）
- **非同步處理流程**:
  - 檔案上傳 → 存入 Blob Store + 在此表記錄 → 發出事件
  - 後端服務監聽事件 → 執行 OCR 處理（用戶無需等待）
  - OCR 完成 → 更新 status 為 'completed'
- **為什麼需要 UPLOAD_EVENT**:
  - 非同步處理:OCR 可能需要數秒,不能阻塞使用者操作
  - 錯誤追蹤:記錄失敗的上傳事件,方便重試
  - 審計日誌:記錄所有檔案操作歷史

**架構說明**:
- PostgreSQL (Supabase): 結構化數據 (500MB 免費額度)
- Supabase Storage: 檔案儲存 (1GB 免費額度)
- Qdrant: 向量存儲 (履歷相似度搜尋)

---

### 4.2 OCR_RESULT(OCR 辨識結果)🔵

**功能說明**:儲存文件 OCR 解析結果與信心分數

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| ocr_id | OCR 識別碼 | OCR ID | INT | OCR 識別碼 | PRIMARY KEY |
| event_id | 事件識別碼 | Event ID | INT | 關聯上傳事件 | FOREIGN KEY |
| resume_id | 履歷識別碼 | Resume ID | INT | 關聯履歷 | FOREIGN KEY |
| raw_text | 原始文字 | Raw Text | TEXT | OCR 原始文字 | - |
| extracted_data | 結構化萃取資料 | Extracted Data | JSON | 結構化萃取資料 | - |
| confidence_score | 辨識信心分數 | Confidence Score | FLOAT | 辨識信心分數 (0-1)。IF confidence_score < 0.7: → 標記為需要人工審核 → 提醒用戶重新上傳清晰版本 | - |
| is_manual_review_needed | 是否需人工審核 | Is Manual Review Needed | BOOLEAN | 是否需人工審核。當 confidence_score < 0.7 時自動設為 TRUE | DEFAULT FALSE |
| ocr_status | OCR 狀態 | OCR Status | VARCHAR(50) | OCR 狀態 (success/failed/partial) | - |
| processed_at | 處理時間 | Processed At | DATETIME | 處理時間 | - |

**設計說明**:
- 對應流程圖「OCR Worker 觸發文件解析」
- 使用 Azure Document Intelligence 或 Tesseract OCR
- **confidence_score 處理邏輯**:
  - 當 `confidence_score < 0.7` 時，自動將 `is_manual_review_needed` 設為 `TRUE`
  - 系統會提醒用戶重新上傳清晰版本的檔案
  - 人工審核完成後，可手動將 `is_manual_review_needed` 設為 `FALSE`
- **extracted_data 範例**:
  ```json
  {
    "personal_info": {"name": "王小明", "email": "test@example.com"},
    "work_experience": [{"company": "ABC 科技", "position": "工程師"}],
    "skills": ["Python", "JavaScript"]
  }
  ```

---

## 5. 職缺與公司資料表

### 5.1 COMPANY_INFO(公司資訊)🟢

**功能說明**:儲存企業基本資料,支援職缺資訊關聯

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| company_id | 公司識別碼 | Company ID | INT | 公司識別碼 | PRIMARY KEY |
| company_name | 公司名稱 | Company Name | VARCHAR(200) | 公司名稱 | NOT NULL |
| industry | 產業類別 | Industry | VARCHAR(100) | 產業類別 | - |
| company_size | 公司規模 | Company Size | VARCHAR(50) | 公司規模 (1-50/51-200/201-500/501+) | - |
| location | 公司地點 | Location | VARCHAR(200) | 公司地點 | - |
| website | 公司網站 | Website | VARCHAR(500) | 公司網站 | - |
| description | 公司簡介 | Description | TEXT | 公司簡介 | - |
| created_at | 建立時間 | Created At | DATETIME | 建立時間 | - |

**設計說明**:
- 對應架構圖中的「Job Scraper Worker」爬蟲資料來源
- 支援從 104、Cake、LinkedIn 等平台爬取公司資訊
- **company_size 分級**:
  - `1-50`:新創小公司
  - `51-200`:中小企業
  - `201-500`:中型企業
  - `501+`:大型企業

---

### 5.2 JOB_POSTING(職缺資訊)🟢

**功能說明**:儲存職缺詳細資訊,需進行向量化處理以支援語意匹配

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| job_id | 職缺識別碼 | Job ID | INT | 職缺識別碼 | PRIMARY KEY |
| company_id | 公司識別碼 | Company ID | INT | 關聯公司 | FOREIGN KEY |
| job_title | 職缺標題 | Job Title | VARCHAR(200) | 職缺標題 | NOT NULL |
| job_description | 職缺描述 | Job Description | TEXT | 職缺描述 | - |
| requirements | 職缺要求 | Requirements | TEXT | 職缺要求 | - |
| salary_min | 最低薪資 | Minimum Salary | INT | 最低薪資 | - |
| salary_max | 最高薪資 | Maximum Salary | INT | 最高薪資 | - |
| location | 工作地點 | Location | VARCHAR(200) | 工作地點 | - |
| remote_option | 遠端工作選項 | Remote Option | VARCHAR(50) | 遠端工作選項 (on-site/hybrid/remote) | - |
| employment_type | 僱用類型 | Employment Type | VARCHAR(50) | 僱用類型 (full-time/part-time/contract) | - |
| experience_level | 經驗要求 | Experience Level | VARCHAR(50) | 經驗要求 (entry/mid/senior/whatever) | - |
| posted_date | 發布日期 | Posted Date | DATE | 發布日期 | - |
| deadline | 截止日期 | Deadline | DATE | 截止日期 | - |
| source_url | 來源網址 | Source URL | VARCHAR(500) | 來源網址 | - |
| is_active | 職缺啟用狀態 | Is Active | BOOLEAN | 職缺啟用狀態 | DEFAULT TRUE |
| created_at | 建立時間 | Created At | DATETIME | 建立時間 | - |

**設計說明**:
- 對應流程圖右側「動作: 確認履歷並生成職缺名列表」
- **⚡ 需要向量化**:`job_description + requirements` 會轉換為向量存入 Qdrant
- **remote_option 說明**:
  - `on-site`:需到辦公室
  - `hybrid`:混合辦公
  - `remote`:完全遠端
- **experience_level 說明**:
  - `entry`:新鮮人/1-3 年
  - `mid`:中階/3-7 年
  - `senior`:資深/7+ 年

---

## 6. 技能管理表

### 6.1 SKILL_MASTER(技能主檔)⚪

**功能說明**:技能標準化字典,統一技能名稱與分類

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| skill_id | 技能識別碼 | Skill ID | INT | 技能識別碼 | PRIMARY KEY |
| skill_name | 技能名稱 | Skill Name | VARCHAR(100) | 技能名稱 | UNIQUE, NOT NULL |
| skill_category | 技能分類 | Skill Category | VARCHAR(50) | 技能分類 (Programming/Framework/Tool/Soft) | - |
| synonyms | 同義詞 | Synonyms | JSON | 同義詞列表 | - |
| created_at | 建立時間 | Created At | DATETIME | 建立時間 | - |

**設計說明**:
- 解決技能名稱不一致問題(例如:`JS`、`JavaScript`、`javascript` 統一為 `JavaScript`)
- **skill_category 說明**:
  - `Programming`:程式語言(Python, Java, C++)
  - `Framework`:框架(React, Django, Spring)
  - `Tool`:工具(Git, Docker, AWS)
  - `Soft`:軟技能(Leadership, Communication)
- **synonyms 範例**:
  ```json
  {
    "JavaScript": ["JS", "js", "javascript", "ECMAScript"]
  }
  ```

---

### 6.2 JOB_SKILL_REQUIREMENT(職缺技能需求)🟢

**功能說明**:定義職缺所需技能與重要性

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| requirement_id | 需求識別碼 | Requirement ID | INT | 需求識別碼 | PRIMARY KEY |
| job_id | 職缺識別碼 | Job ID | INT | 關聯職缺 | FOREIGN KEY |
| skill_id | 技能識別碼 | Skill ID | INT | 關聯技能 | FOREIGN KEY |
| importance | 重要性 | Importance | VARCHAR(50) | 重要性 (required/preferred/nice-to-have) | - |
| proficiency_level | 熟練度要求 | Proficiency Level | INT | 熟練度要求 (1-10) | - |

**設計說明**:
- 對應流程圖「RAG Worker 向量檢索」的技能匹配邏輯
- **importance 說明**:
  - `required`:必要技能
  - `preferred`:優先考慮
  - `nice-to-have`:加分項目
- **proficiency_level**:1(初學)到 10(專家)

---

### 6.3 USER_SKILL(使用者技能)⚪

**功能說明**:記錄使用者擁有的技能與熟練度

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| user_skill_id | 使用者技能識別碼 | User Skill ID | INT | 使用者技能識別碼 | PRIMARY KEY |
| user_id | 使用者識別碼 | User ID | INT | 關聯使用者 | FOREIGN KEY |
| skill_id | 技能識別碼 | Skill ID | INT | 關聯技能 | FOREIGN KEY |
| proficiency_level | 熟練度 | Proficiency Level | INT | 熟練度 (1-10) | - |
| years_of_experience | 使用年資 | Years of Experience | FLOAT | 使用年資 | - |
| verified | 驗證狀態 | Verified | BOOLEAN | 驗證狀態 | DEFAULT FALSE |
| created_at | 建立時間 | Created At | DATETIME | 建立時間 | - |

**設計說明**:
- 從 CAREER_SURVEY 或 OCR_RESULT 自動提取技能
- **verified**:未來可整合 LinkedIn 或考試認證驗證技能真實性
- **proficiency_level 來源**:
  - 使用者自評(CAREER_SURVEY.skill_self_assessment)
  - 履歷推算(根據使用年資)
  - AI 評估(根據專案經驗)

---

## 7. 職缺媒合與評分表

### 7.1 JOB_MATCHING(職缺媒合記錄)🟢

**功能說明**:記錄履歷與職缺的配對結果

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| matching_id | 媒合識別碼 | Matching ID | INT | 媒合識別碼 | PRIMARY KEY |
| resume_id | 履歷識別碼 | Resume ID | INT | 關聯履歷 | FOREIGN KEY |
| job_id | 職缺識別碼 | Job ID | INT | 關聯職缺 | FOREIGN KEY |
| overall_match_score | 總體配適度分數 | Overall Match Score | FLOAT | 總體配適度分數 (0-100) | - |
| matching_algorithm | 媒合演算法 | Matching Algorithm | VARCHAR(50) | 媒合演算法 (vector/rule-based/hybrid) | - |
| matched_at | 媒合時間 | Matched At | DATETIME | 媒合時間 | - |

**設計說明**:
- 對應流程圖右側「RAG Worker 向量檢索」→「計算 Match Score」
- **matching_algorithm 說明**:
  - `vector`:純向量相似度(餘弦相似度)
  - `rule-based`:基於規則(技能數量、薪資、地點)
  - `hybrid`:混合演算法(向量 + 規則加權)

---

### 7.2 MATCH_SCORE(媒合分數)🟢

**功能說明**:儲存配適度評分細節,提供分數解釋

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| score_id | 分數識別碼 | Score ID | INT | 分數識別碼 | PRIMARY KEY |
| matching_id | 媒合識別碼 | Matching ID | INT | 關聯媒合記錄 | FOREIGN KEY |
| skill_match_score | 技能配適度分數 | Skill Match Score | FLOAT | 技能配適度分數 (0-100) | - |
| experience_match_score | 經驗配適度分數 | Experience Match Score | FLOAT | 經驗配適度分數 (0-100) | - |
| salary_match_score | 薪資配適度分數 | Salary Match Score | FLOAT | 薪資配適度分數 (0-100) | - |
| location_match_score | 地點配適度分數 | Location Match Score | FLOAT | 地點配適度分數 (0-100) | - |
| culture_fit_score | 文化契合度分數 | Culture Fit Score | FLOAT | 文化契合度分數 (0-100) | - |
| score_breakdown | 分數明細 | Score Breakdown | JSON | 分數明細說明 | - |
| created_at | 建立時間 | Created At | DATETIME | 建立時間 | - |

**設計說明**:
- 對應流程圖「顯示: 推薦職缺名單(依配適度排序)」
- 分數細項用於 UI 呈現(雷達圖、進度條)
- **score_breakdown 範例**:
  ```json
  {
    "matched_skills": ["Python", "Django"],
    "missing_skills": ["Kubernetes"],
    "salary_difference": "+10%",
    "location_note": "需到台北辦公"
  }
  ```

---

## 8. 投遞追蹤表

### 8.1 APPLICATION_RECORD(投遞記錄)🟢

**功能說明**:追蹤求職投遞狀態與進度

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| application_id | 投遞識別碼 | Application ID | INT | 投遞識別碼 | PRIMARY KEY |
| user_id | 使用者識別碼 | User ID | INT | 關聯使用者 | FOREIGN KEY |
| job_id | 職缺識別碼 | Job ID | INT | 關聯職缺 | FOREIGN KEY |
| version_id | 版本識別碼 | Version ID | INT | 使用的履歷版本 | FOREIGN KEY |
| application_status | 投遞狀態 | Application Status | VARCHAR(50) | 投遞狀態 (applied/viewed/interview/rejected/accepted) | DEFAULT 'applied' |
| applied_at | 投遞時間 | Applied At | DATETIME | 投遞時間 | NOT NULL |
| status_updated_at | 狀態更新時間 | Status Updated At | DATETIME | 狀態更新時間 | - |
| days_since_application | 投遞天數 | Days Since Application | INT | 投遞天數 | - |
| user_feedback | 使用者回報結果 | User Feedback | JSON | 使用者回報結果 | - |

**設計說明**:
- 對應 Work Flow 的「Step4: 履歷投遞」與「Step5: 投遞進度追蹤」
- 支援 Release 2 的「使用者回報投遞結果」功能
- **version_id 說明**:
  - 指向 `RESUME_VERSION.version_id`，精確記錄投遞時使用的履歷版本
  - 可追蹤不同版本對應的投遞結果，支援針對不同職缺使用不同版本履歷
- **application_status 狀態流**:
  - `applied`:已投遞
  - `viewed`:已讀取
  - `interview`:邀請面試
  - `rejected`:已拒絕
  - `accepted`:已錄取

---

## 9. 職涯分析與技能發展表

### 9.1 CAREER_ANALYSIS_REPORT(職涯分析報告)🟠

**功能說明**:儲存 AI 生成的職涯分析報告

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| report_id | 報告識別碼 | Report ID | INT | 報告識別碼 | PRIMARY KEY |
| survey_id | 問卷識別碼 | Survey ID | INT | 關聯問卷 | FOREIGN KEY |
| resume_id | 履歷識別碼 | Resume ID | INT | 關聯履歷 | FOREIGN KEY |
| skill_gap_analysis | 技能落差分析 | Skill Gap Analysis | JSON | 技能落差分析 | - |
| career_path_suggestions | 職涯路徑建議 | Career Path Suggestions | JSON | 職涯路徑建議 | - |
| market_insights | 市場洞察 | Market Insights | JSON | 市場洞察 | - |
| career_readiness_score | 職涯準備度分數 | Career Readiness Score | FLOAT | 職涯準備度分數 (0-100) | - |
| generated_at | 報告生成時間 | Generated At | DATETIME | 報告生成時間 | - |

**設計說明**:
- 對應流程圖右側「顯示: 職涯發展表板」→「動作: 檢視職能分析結果」
- 使用 AI LLM/NLP 生成分析報告
- **為什麼需要 CAREER_SURVEY + RESUME**:
  - `CAREER_SURVEY` 提供主觀意圖(想去的產業、期望薪資)
  - `RESUME` 提供客觀能力(實際技能、工作經驗)
  - 兩者結合才能產生有意義的分析報告

---

### 9.2 SKILL_GAP(技能落差)🟠

**功能說明**:識別技能缺口與學習優先順序

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| gap_id | 落差識別碼 | Gap ID | INT | 落差識別碼 | PRIMARY KEY |
| report_id | 報告識別碼 | Report ID | INT | 關聯分析報告 | FOREIGN KEY |
| skill_id | 技能識別碼 | Skill ID | INT | 關聯技能 | FOREIGN KEY |
| current_level | 目前等級 | Current Level | INT | 目前等級 (1-10) | - |
| target_level | 目標等級 | Target Level | INT | 目標等級 (1-10) | - |
| priority_rank | 優先順序 | Priority Rank | INT | 優先順序 | - |
| time_investment_hours | 預估投入時間 | Time Investment Hours | FLOAT | 預估投入時間 | - |
| skill_roi_score | 技能投資報酬率 | Skill ROI Score | FLOAT | 技能投資報酬率 | - |

**設計說明**:
- 對應 Work Flow 的「Step1: 技能落差分析」
- 由 AI 計算技能缺口優先排序
- **skill_roi_score**:評估學習該技能對職涯發展的投資報酬率

---

### 9.3 SIDE_PROJECT_RECOMMENDATION(Side Project 推薦)🟠

**功能說明**:推薦學習專案以填補技能落差

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| recommendation_id | 推薦識別碼 | Recommendation ID | INT | 推薦識別碼 | PRIMARY KEY |
| gap_id | 落差識別碼 | Gap ID | INT | 關聯技能落差 | FOREIGN KEY |
| project_name | 專案名稱 | Project Name | VARCHAR(200) | 專案名稱 | - |
| project_description | 專案描述 | Project Description | TEXT | 專案描述 | - |
| required_skills | 所需技能列表 | Required Skills | JSON | 所需技能列表 | - |
| difficulty_level | 難度等級 | Difficulty Level | VARCHAR(50) | 難度等級 (beginner/intermediate/advanced) | - |
| estimated_hours | 預估完成時數 | Estimated Hours | INT | 預估完成時數 | - |
| project_url | 專案參考連結 | Project URL | VARCHAR(500) | 專案參考連結 | - |
| created_at | 建立時間 | Created At | DATETIME | 建立時間 | - |

**設計說明**:
- 對應流程圖右側「動作: 檢視推薦 side project」
- 結合 PRD 提到的 Side Project Library
- **推薦邏輯**:根據 SKILL_GAP 的優先順序推薦相應難度的專案

---

## 資料表關聯關係總覽

### 一對一關係 (1:1)

| 主表 | 主表英文 | 從表 | 從表英文 | 說明 |
|-----|---------|------|---------|------|
| USER | User | USER_PROFILE | User Profile | 每位使用者有唯一的個人檔案 |
| JOB_MATCHING | Job Matching | MATCH_SCORE | Match Score | 每筆媒合記錄對應唯一的分數計算 |
| RESUME | Resume | OCR_RESULT | OCR Result | 每份上傳履歷對應一次 OCR 解析結果 |
| COMPANY_INFO | Company Info | JOB_POSTING | Job Posting | 每個職缺屬於一家公司 |

### 一對多關係 (1:N)

| 主表 | 主表英文 | 從表 | 從表英文 | 說明 |
|-----|---------|------|---------|------|
| USER | User | CAREER_SURVEY | Career Survey | 一位使用者可填寫多次問卷 |
| USER | User | RESUME | Resume | 一位使用者可建立多份履歷 |
| USER | User | APPLICATION_RECORD | Application Record | 一位使用者可投遞多個職缺 |
| USER | User | UPLOAD_EVENT | Upload Event | 一位使用者可上傳多個檔案 |
| RESUME | Resume | RESUME_VERSION | Resume Version | 一份履歷可有多個版本 |
| RESUME_VERSION | Resume Version | APPLICATION_RECORD | Application Record | 一個履歷版本可被多次投遞 |
| CAREER_SURVEY | Career Survey | CAREER_ANALYSIS_REPORT | Career Analysis Report | 一份問卷可生成多次分析報告 |
| CAREER_ANALYSIS_REPORT | Career Analysis Report | SKILL_GAP | Skill Gap | 一份報告可識別多個技能落差 |
| SKILL_GAP | Skill Gap | SIDE_PROJECT_RECOMMENDATION | Side Project Recommendation | 一個技能落差可推薦多個專案 |
| JOB_POSTING | Job Posting | JOB_MATCHING | Job Matching | 一個職缺可被多位求職者匹配 |
| JOB_POSTING | Job Posting | APPLICATION_RECORD | Application Record | 一個職缺可被多人投遞 |

### 多對多關係 (M:N)

| 表 A | 表 A 英文 | 中介表 | 中介表英文 | 表 B | 表 B 英文 | 說明 |
|------|----------|-------|-----------|------|----------|------|
| JOB_POSTING | Job Posting | JOB_SKILL_REQUIREMENT | Job Skill Requirement | SKILL_MASTER | Skill Master | 職缺可要求多種技能 |
| USER_PROFILE | User Profile | USER_SKILL | User Skill | SKILL_MASTER | Skill Master | 使用者可擁有多種技能 |

---

## 資料流程說明

### 流程 A:履歷建立與上傳

```
1. USER 註冊登入
   ↓
2. CAREER_SURVEY 填寫職涯問卷
   ↓
3. RESUME 選擇輸入方式:
   ├─ 填寫表單 → 直接存入 structured_data
   └─ 上傳檔案 → UPLOAD_EVENT → OCR_RESULT → 解析後存入 RESUME
   ↓
4. RESUME 內容標準化 → 存入 normalized_data
   ↓
5. ⚡ 向量化處理 → 存入 Qdrant Vector DB
```

### 流程 B:職缺媒合與分析

```
1. RESUME + CAREER_SURVEY
   ↓
2. 生成 CAREER_ANALYSIS_REPORT
   ↓
3. SKILL_GAP 識別技能落差
   ↓
4. SIDE_PROJECT_RECOMMENDATION 推薦專案
   ↓
5. JOB_MATCHING 職缺媒合(使用向量相似度)
   ↓
6. MATCH_SCORE 計算分數
   ↓
7. APPLICATION_RECORD 投遞追蹤
```

---

## 技術架構對應

### 資料儲存層

| 資料庫類型 | 資料庫類型英文 | 儲存內容 | 對應表 |
|-----------|--------------|---------|--------|
| **關聯式資料庫** | Relational DB (PostgreSQL) | 結構化業務資料 | 所有主要資料表 |
| **向量資料庫** | Vector DB (Qdrant) | 履歷與職缺語意向量 | RESUME, JOB_POSTING 的向量索引 |
| **物件儲存** | Blob Store (Azure Blob Storage) | 原始檔案 | UPLOAD_EVENT, RESUME 的 file_path |

### 處理服務層

| 服務 | 服務英文 | 功能 | 相關資料表 |
|------|---------|------|----------|
| **使用者資料服務** | User Profile Service | 使用者資料管理 | USER, USER_PROFILE, USER_SKILL |
| **履歷資料服務** | Resume Data Service | 履歷資料處理 | RESUME, RESUME_VERSION, OCR_RESULT |
| **認證服務** | Auth Service | 身份認證 | USER |
| **職缺爬蟲** | Job Scraper Worker | 職缺爬蟲 | JOB_POSTING, COMPANY_INFO |
| **OCR 處理** | OCR Worker | 文件解析 | OCR_RESULT |
| **RAG 檢索生成** | RAG Worker | 語意檢索與生成 | JOB_MATCHING, MATCH_SCORE |
| **流程編排** | Workflow Orchestrator | 流程編排 | 協調所有服務 |

### 外部 API 整合

| 外部系統 | 外部系統英文 | 用途 | 相關資料表 |
|---------|-------------|------|----------|
| **LLM API** | LLM API (OpenAI/Claude) | 履歷生成、分析報告 | RESUME, CAREER_ANALYSIS_REPORT |
| **職缺平台** | External Job Boards | 職缺來源 | JOB_POSTING |

---

## 向量化處理說明

### ⚡ 需要向量化的資料表

| 資料表 | 資料表英文 | 向量化欄位 | 向量維度 | 用途 |
|-------|----------|----------|---------|------|
| RESUME | Resume | structured_data / normalized_data | 1536 | 履歷語意搜尋與職缺匹配 |
| JOB_POSTING | Job Posting | job_description + requirements | 1536 | 職缺語意搜尋與履歷匹配 |

### 向量化流程

```
原始文字資料
    ↓
LLM Embedding API (OpenAI text-embedding-3-large)
    ↓
向量表示 (1536 維度浮點數陣列)
    ↓
存入 Qdrant Vector DB (以 resume_id/job_id 為索引)
    ↓
用於語意相似度計算(餘弦相似度)
```

### 使用時機

- **履歷 ↔ 職缺語意匹配**:計算兩者向量的餘弦相似度
- **相似履歷推薦**:找出向量空間中接近的履歷
- **職缺搜尋優化**:根據履歷向量檢索最相關職缺

---

## 版本支援說明

### ✅ MVP (Release 1) - 核心功能

- 使用者註冊與登入 (USER, USER_PROFILE)
- 履歷上傳與解析 (UPLOAD_EVENT, OCR_RESULT, RESUME)
- 職涯問卷填寫 (CAREER_SURVEY)
- 職缺媒合與評分 (JOB_MATCHING, MATCH_SCORE)
- 投遞記錄追蹤 (APPLICATION_RECORD)

### ✅ Release 2 - 完整功能

- 履歷多版本管理 (RESUME_VERSION)
- 職涯分析報告生成 (CAREER_ANALYSIS_REPORT)
- 技能落差分析 (SKILL_GAP)
- Side Project 推薦 (SIDE_PROJECT_RECOMMENDATION)
- 投遞結果回報 (APPLICATION_RECORD.user_feedback)

### 🔮 Release 3 - 未來規劃

- LinkedIn Profile 匯入(需擴充 USER.auth_provider)
- GitHub 作品集整合(使用 USER_PROFILE.github_repo)
- 面試追蹤系統(需新增 INTERVIEW_RECORD 表)
- 整合 104/Cake 平台帳號
- 一鍵投遞功能

---

## 設計原則

1. **模組化設計**:每個功能模組對應獨立的資料表群組
2. **可擴展性**:JSON 欄位預留未來功能擴充空間
3. **資料完整性**:使用外鍵約束確保資料一致性
4. **效能優化**:關鍵查詢欄位建立索引
5. **安全性**:敏感資料加密儲存(password_hash)
6. **向量化支援**:RESUME 與 JOB_POSTING 支援語意搜尋

---

**文件製作**:Career Pilot 資料組  
**最後更新**:2026-01-21  
**文件版本**:v2.0
