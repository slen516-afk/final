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
| 6 | 上傳事件記錄 | UPLOAD_EVENT | 🔵 履歷生成 | 追蹤檔案上傳事件 |
| 7 | OCR 辨識結果 | OCR_RESULT | 🔵 履歷生成 | 儲存文件解析結果 |
| 8 | 公司資訊 | COMPANY_INFO | 🟢 職缺推薦 | 儲存企業基本資料 |
| 9 | 職缺資訊 | JOB_POSTING | 🟢 職缺推薦 | 儲存職缺詳細資訊 |
| 10 | 職缺技能需求 | JOB_SKILL_REQUIREMENT | 🟢 職缺推薦 | 定義職缺所需技能 |
| 11 | 技能主檔 | SKILL_MASTER | ⚪ 共用 | 技能標準化字典 |
| 12 | 使用者技能 | USER_SKILL | ⚪ 共用 | 記錄使用者擁有的技能 |
| 13 | 職缺媒合記錄 | JOB_MATCHING | 🟢 職缺推薦 | 記錄履歷與職缺的配對 |
| 14 | 媒合分數 | MATCH_SCORE | 🟢 職缺推薦 | 儲存配適度評分細節 |
| 15 | 投遞記錄 | APPLICATION_RECORD | 🟢 職缺推薦 | 追蹤求職投遞狀態 |
| 16 | 職涯分析報告 | CAREER_ANALYSIS_REPORT | 🟠 職能分析 | 儲存 AI 生成的分析報告 |
| 17 | Side Project 推薦 | SIDE_PROJECT_RECOMMENDATION | 🟠 職能分析 | 推薦學習專案 |
| 18 | 課程主表 | COURSE | 🟣 課程推薦 | 儲存推薦用課程（如 Coursera），依技能與職缺/職能落差分析匹配 |
| 19 | 履歷分析報告 | RESUME_ANALYSIS | 🔵 履歷生成 | 儲存 AI 對履歷的完整診斷分析結果，含各區塊問題清單（critical_issues） |
| 20 | 履歷優化結果 | RESUME_OPTIMIZATION | 🔵 履歷生成 | 儲存 AI 優化後的完整履歷內容 |
| 21 | 求職信 | COVER_LETTER | 🟢 職缺推薦 | 儲存針對特定職缺 AI 生成的求職信 |
| 22 | Agent 調用記錄 | AGENT_SESSION | ⚙️ 系統追蹤 | 記錄每次 Agent 調用的工具使用情況與效能指標 |

---

## 1. 使用者認證與基本資料表

### 1.1 USER(使用者主表)

**功能說明**:儲存使用者帳號、密碼與認證資訊,支援多種登入方式(Email/LinkedIn/Google)

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| user_id | 使用者識別碼 | User ID | INT | 使用者唯一識別碼 | PRIMARY KEY |
| auth_uid | 認證 UID | Auth UID | UUID | 對應 Supabase auth.users.id，作為與認證系統的橋接欄位 | UNIQUE, NOT NULL |
| email | 電子郵件 | Email | VARCHAR(255) | 使用者電子郵件 | UNIQUE, NOT NULL |
| password_hash | 密碼雜湊值 | Password Hash | VARCHAR(255) | 密碼雜湊值 | NOT NULL |
| auth_provider | 認證提供者 | Authentication Provider | VARCHAR(50) | 認證提供者 (Email/LinkedIn/Google) | DEFAULT 'Email' |
| created_at | 建立時間 | Created At | DATETIME | 帳號建立時間 | NOT NULL |
| last_login | 最後登入時間 | Last Login | DATETIME | 最後登入時間 | - |
| is_active | 帳號啟用狀態 | Is Active | BOOLEAN | 帳號是否啟用 | DEFAULT TRUE |
| optimization_quota_per_month | 每月優化次數上限 | Optimization Quota Per Month | INT | 每月可使用的履歷優化次數上限，0 表示不開放；後端以當月 RESUME_OPTIMIZATION 筆數與此值比較判斷是否允許 | DEFAULT 5 |

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
| avatar_url | 頭像網址 | Avatar URL | VARCHAR(500) | 使用者頭像圖片 URL | - |
| location | 所在地區 | Location | VARCHAR(100) | 所在地區 | - |
| years_of_experience | 工作年資 | Years of Experience | INT | 工作年資 | - |
| current_position | 目前職位 | Current Position | VARCHAR(100) | 目前職位 | - |
| education_background | 教育背景 | Education Background | TEXT | 教育背景 | - |
| privacy_settings | 隱私設定 | Privacy Settings | JSONB | 隱私設定 | - |
| updated_at | 更新時間 | Updated At | DATETIME | 最後更新時間 | - |

**設計說明**:
- 對應 Work Flow 的「Step2:專業個人檔案建構」
- **為何 USER 拆成 USER + USER_PROFILE**:
  - 帳密歸帳密:敏感認證資料獨立儲存
  - 檔案歸檔案:業務細節分開管理,查詢效能高
- **education_background 使用 TEXT**:教育背景可能包含校名、系所、榮譽獎項、研究論文題目等,長度變動極大
- **privacy_settings 使用 JSONB**:隱私設定包含多個開關(是否公開電話、是否允許 AI 分析、通知偏好等),結構多變且不常作為查詢條件
- **github_repo**:未來功能先保留,用於整合 GitHub 作品集

---

## 2. 職涯調查與問卷表

### 2.1 CAREER_SURVEY(職涯調查問卷)

**功能說明**:記錄使用者的職涯目標、技能自評與求職偏好,作為 AI 分析的重要輸入；問卷完整填答結果集中存放於 `questionnaire_response`，供後續產出分析報告時使用。

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| survey_id | 問卷識別碼 | Survey ID | INT | 問卷識別碼 | PRIMARY KEY |
| user_id | 使用者識別碼 | User ID | INT | 關聯使用者 | FOREIGN KEY |
| career_preference | 職涯偏好 | Career Preference | JSONB | 職涯偏好 (目標職位/產業) | - |
| skill_self_assessment | 技能自評 | Skill Self Assessment | JSONB | 技能自評 (1-10分) | - |
| salary_min | 最低薪資期待 | Minimum Salary | INT | 最低薪資期待 | - |
| salary_max | 最高薪資期待 | Maximum Salary | INT | 最高薪資期待 | - |
| location_preference | 工作地點偏好 | Location Preference | VARCHAR(100) | 工作地點偏好 | - |
| remote_preference | 遠端工作偏好 | Remote Work Preference | VARCHAR(50) | 遠端工作偏好 | - |
| career_motivation | 職涯轉換動機 | Career Motivation | JSONB | 職涯轉換動機 | - |
| questionnaire_response | 問卷填答結果 | Questionnaire Response | JSONB | 完整問卷填答結果（包含 module_a/b/c/d 所有題目與答案）；產分析報告時可依需求以 GIN 索引查詢取值 | GIN 索引 idx_survey_response_gin |
| completed_at | 完成時間 | Completed At | DATETIME | 完成時間 | - |
| updated_at | 更新時間 | Updated At | DATETIME | 更新時間 | - |

**設計說明**:
- 對應流程圖「動作: 選擇填寫職涯調查問卷」
- 支援 Release 2 的「問卷內容修改」功能
- **問卷結果存庫**：經組內討論，將完整問卷填答結果寫入資料庫（`questionnaire_response`），方便後續產出職涯分析報告時取用；查詢時可透過 `idx_survey_response_gin`（GIN 索引）對 JSONB 內欄位做條件篩選或取值，兼顧彈性與查詢效能。
- JSON 欄位格式範例:
  ```json
  {
    "career_preference": ["Backend Engineer", "Full-Stack Developer"],
    "skill_self_assessment": {"Python": 8, "JavaScript": 7},
    "career_motivation": "尋求更好的技術挑戰與成長機會"
  }
  ```
- **questionnaire_response 格式**：存儲 module_a / module_b / module_c / module_d 等各模組之題目與答案完整結構，具體 schema 依前端問卷設計而定。

---

## 3. 履歷相關表(核心)

### 3.1 RESUME(履歷主表)🔵

**功能說明**:儲存履歷核心資料,支援上傳與生成兩種來源,需進行向量化處理

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| resume_id | 履歷識別碼 | Resume ID | INT | 履歷識別碼 | PRIMARY KEY |
| user_id | 使用者識別碼 | User ID | INT | 關聯使用者 | FOREIGN KEY |
| resume_type | 履歷類型 | Resume Type | VARCHAR(50) | 履歷類型 (uploaded/generated) | NOT NULL |
| structured_data | 結構化資料 | Structured Data | JSONB | 結構化履歷資料 | - |
| normalized_data | 標準化資料 | Normalized Data | JSONB | 標準化後資料 | - |
| vector_id | 向量識別碼 | Vector ID | UUID | 對應 Qdrant 中的 Point ID | - |
| is_embedded | 是否已向量化 | Is Embedded | BOOLEAN | 是否已完成向量化 | DEFAULT FALSE |
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
| content | 版本內容 | Content | JSONB | 版本完整內容 | - |
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

### 3.4 RESUME_ANALYSIS(履歷分析報告)🔵

**功能說明**:儲存 AI 對履歷的完整診斷分析結果，包含候選人定位、優勢弱點、ATS 風險評估等，支援歷史追蹤與快取。

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| analysis_id | 分析識別碼 | Analysis ID | BIGSERIAL | 分析識別碼 | PRIMARY KEY |
| resume_id | 履歷識別碼 | Resume ID | INT | 關聯履歷 | FK → RESUME, NOT NULL |
| user_id | 使用者識別碼 | User ID | INT | 關聯使用者 | FK → USER, NOT NULL |
| candidate_positioning | 候選人定位 | Candidate Positioning | TEXT | 企業視角下此履歷代表的角色定位 | - |
| target_role_gap_summary | 目標職位落差摘要 | Target Role Gap Summary | TEXT | 與目標職位的整體落差說明 | - |
| overall_strengths | 整體優勢點 | Overall Strengths | JSONB | List[str] 最具說服力的優勢點 | - |
| overall_weaknesses | 整體弱勢點 | Overall Weaknesses | JSONB | List[str] 影響錄取率的核心弱點 | - |
| ats_risk_level | ATS風險等級 | ATS Risk Level | VARCHAR(20) | low / medium / high | - |
| screening_outcome_prediction | 快速篩選預測 | Screening Outcome Prediction | TEXT | 模擬 6-10 秒掃描後的篩選結果 | - |
| recommended_next_actions | 下一步行動建議 | Recommended Next Actions | JSONB | List[str] 可執行的下一步建議 | - |
| target_job_id | 目標職缺識別碼 | Target Job ID | INT | 分析對應的目標職缺（可選） | FK → JOB_POSTING |
| llm_model_used | 使用的 LLM 模型 | LLM Model Used | VARCHAR(100) | 產生此分析使用的 LLM 版本 | - |
| analysis_version | 分析版本 | Analysis Version | VARCHAR(10) | 分析 Schema 版本 | DEFAULT '1.0' |
| generated_at | 生成時間 | Generated At | TIMESTAMPTZ | 分析產生時間 | NOT NULL, DEFAULT NOW() |
| critical_issues | 履歷問題清單 | Critical Issues | JSONB | 履歷各區塊的問題條目清單，對應 ResumeIssue 結構：section（區塊名稱）/ original_text（原始文字）/ issue_type List[str]（問題類型）/ severity List[str]（嚴重程度）/ diagnosis_dimension（診斷面向）/ issue_reason（問題原因）/ improvement_direction List[str]（改善方向） | - |

**設計說明**:
- 對應流程圖「動作: AI 履歷診斷分析」
- **為何需要此表**: `RESUME` 表僅存原始資料，無法承接 AI 分析結果，導致每次需重新呼叫 LLM，無法做歷史追蹤與快取
- **一份履歷可產生多次分析**: 針對不同職缺或不同時間點的分析結果
- **target_job_id 為可選**: 分析時若有對應職缺則記錄，否則為 NULL
- **critical_issues 合併設計（v2.1）**：
  原 RESUME_ISSUE 子表因產品不做「單筆問題狀態追蹤」功能，已合併為 JSONB 欄位存入本表。
  好處：一次 SELECT 取得完整分析結果，無需 JOIN；寫入時一次完成。
  trade-off：無法對單一問題做條件篩選或狀態更新，若未來有此需求需重新拆表。

---

### 3.5 RESUME_OPTIMIZATION(履歷優化結果)🔵

**功能說明**:儲存 AI 優化後的完整履歷內容，與 RESUME_VERSION 分離，避免版本管理邏輯混亂。

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| optimization_id | 優化識別碼 | Optimization ID | BIGSERIAL | 優化識別碼 | PRIMARY KEY |
| resume_id | 履歷識別碼 | Resume ID | INT | 關聯原始履歷 | FK → RESUME, NOT NULL |
| version_id | 版本識別碼 | Version ID | INT | 關聯履歷版本（可選） | FK → RESUME_VERSION |
| user_id | 使用者識別碼 | User ID | INT | 關聯使用者 | FK → USER, NOT NULL |
| professional_summary | 專業摘要 | Professional Summary | TEXT | 優化後的專業摘要 | - |
| professional_experience | 工作經歷 | Professional Experience | JSONB | List[dict] 優化後的工作經歷（含 STAR 原則） | - |
| core_skills | 核心技能 | Core Skills | JSONB | List[str] 萃取的核心技能關鍵字 | - |
| projects | 專案作品集 | Projects | JSONB | List[dict] 優化後的專案描述 | - |
| education | 學歷 | Education | JSONB | List[str] 最高學歷資訊 | - |
| autobiography | 自傳 | Autobiography | TEXT | 保留原風格的優化後完整自傳 | - |
| llm_model_used | 使用的 LLM 模型 | LLM Model Used | VARCHAR(100) | 產生此優化使用的 LLM 版本 | - |
| optimization_version | 優化版本 | Optimization Version | VARCHAR(10) | Schema 版本 | DEFAULT '1.0' |
| template_color | 樣板與配色 | Template & Color | JSONB | 用戶確認優化結果時選擇的履歷樣板與配色方案；存 template（樣板類型/名稱）與 color_scheme（所選配色名稱），結構見下方說明 | - |
| vector_id | 向量識別碼 | Vector ID | UUID | 對應 Qdrant optimized_resume_vectors 中的 Point ID，向量化腳本回填用 | - |
| is_embedded | 是否已向量化 | Is Embedded | BOOLEAN | 是否已寫入 Qdrant optimized_resume_vectors | DEFAULT FALSE |
| created_at | 建立時間 | Created At | TIMESTAMPTZ | 優化產生時間 | NOT NULL, DEFAULT NOW() |

**設計說明**:
- **為何獨立成表**: `RESUME_VERSION.content (JSONB)` 語意上是「版本快照」而非「AI 優化結果」，混用會造成版本管理邏輯混亂
- **FK 設計邏輯**:
  - `resume_id` → `RESUME`：確認這份優化屬於哪份原始履歷
  - `version_id` → `RESUME_VERSION`：可選，若優化結果已存為新版本則關聯
- **注意**: name/phone/email/linkedin/github 為個人敏感資料，不由 LLM 輸出寫入，此表不儲存，由前端從 USER_PROFILE 取得
- **向量化**: `vector_id`、`is_embedded` 供優化後履歷向量化腳本寫入 Qdrant `optimized_resume_vectors` 後回填，職缺推薦時可選擇以優化前/後履歷做比對

**template_color (JSONB) 結構說明**  
對應「選擇履歷樣板」流程：用戶選擇一樣板類型（如經典專業型、現代極簡型、創意視覺型）與一組配色方案，前端將所選結果寫入此欄位。建議結構：

| 鍵名 | 型態 | 說明 |
|------|------|------|
| template_key | string | 樣板識別碼，供程式對應（如 `corporate_classic`、`modern_minimalist`、`creative_portfolio`） |
| template_name_zh | string | 樣板中文名稱（如「經典專業型」「現代極簡型」「創意視覺型」） |
| template_name_en | string | 樣板英文名稱（如 The Corporate Classic、Modern Minimalist、Creative Portfolio），可選 |
| color_scheme_name | string | 用戶所選配色方案名稱（如「深海藍經典」） |
| color_hex | string | 所選配色之主色 hex（如 `#1e3a5f`），供前端渲染 |

**template_color 範例**（用戶選擇「現代極簡型」+ 某藍色配色）：
```json
{
  "template_key": "modern_minimalist",
  "template_name_zh": "現代極簡型",
  "template_name_en": "Modern Minimalist",
  "color_scheme_name": "深海藍經典",
  "color_hex": "#1e3a5f"
}
```

前端依 `template_key` 與 `color_hex` 決定版型與配色渲染。

**內建樣板與預設配色清單**  
目前規劃的樣板與主色 hex 如下，供前後端對齊（`template_key` 由前端實作時決定，建議依英文名稱或類型命名）：

- **corporate（經典專業型）**
  - 深海藍經典：`#1F3A5F`
  - 石墨灰商務：`#2E2E2E`
  - 酒紅權威：`#6A1B2E`
  - 深綠金融系：`#1B4332`

- **modern（現代極簡型）**
  - 科技藍：`#2563EB`
  - 冷灰＋電光綠：`#374151`
  - 黑白極簡：`#111111`
  - 靜謐藍灰：`#334155`

- **creative（創意視覺型）**
  - 莫蘭迪粉橘：`#E07A5F`
  - 紫藍創意系：`#6D28D9`
  - 活力橘藍對比：`#F97316`
  - 黑底霓虹：`#0F172A`

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
| metadata | 檔案中繼資料 | Metadata | JSONB | 檔案中繼資料 | - |

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
| extracted_data | 結構化萃取資料 | Extracted Data | JSONB | 結構化萃取資料 | - |
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

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 |
|---------|---------|-----|---------|------|
| job_id | 職缺識別碼 | Job ID | INT | 職缺識別碼 |PRIMARY KEY|
| company_id | 公司識別碼 | Company ID | INT | 關聯公司 |
| job_category | 職缺類別 | Job Category | VARCHAR(100) | 職缺類別 | - |
| role_type | 職務類型 | Role Type | TEXT | 例如「前端工程師 / 後端工程師 / 全端」等職務大類 |
| role_name | 職務名稱標籤 | Role Name | TEXT | 更細緻的職務名稱或角色標籤 |
| d1_frontend | D1 前端工程 | D1 Frontend | NUMERIC | UI 實作、瀏覽器渲染、UX；分數 1~5 |
| d2_backend | D2 後端工程 | D2 Backend | NUMERIC | API 設計、資料庫設計、高併發處理；分數 1~5 |
| d3_devops | D3 雲端維運 | D3 DevOps/SRE | NUMERIC | Docker/K8s、CI/CD、雲端架構(AWS/GCP)；分數 1~5 |
| d4_ai_data | D4 AI與數據 | D4 AI & Data | NUMERIC | ETL、Python 資料分析、RAG/LLM、ML 模型；分數 1~5 |
| d5_quality | D5 品質與架構 | D5 Quality | NUMERIC | 單元測試、設計模式、SOLID、資安；Senior 關鍵向度；分數 1~5 |
| d6_soft_skills | D6 軟實力 | D6 Soft Skills | NUMERIC | 溝通協作、Agile/Scrum、商業思維；分數 1~5 |
| job_title | 職位名稱 | Job Title | VARCHAR(200) | 職位名稱 |
| job_description | 職缺描述 | Job Description | TEXT | 職缺描述 |
| requirements | 職缺要求 | Requirements | TEXT | 職缺要求 |
| vector_id | 向量識別碼 | Vector ID | UUID | 對應 Qdrant 中的 Point ID |
| is_embedded | 是否已向量化 | Is Embedded | BOOLEAN | 預設為 FALSE，代表是否已完成向量化 |
| is_labeled | 是否已完成貼標 | Is Labeled | BOOLEAN | 是否已完成 D1–D6 能力貼標，預設為 FALSE |
| salary_min | 最低薪資 | Minimum Salary | INT | 最低薪資 |
| salary_max | 最高薪資 | Maximum Salary | INT | 最高薪資 |
| full_address | 完整地址 | Full Address | VARCHAR(200) | 職缺完整地址資訊 |
| city | 城市 | City | VARCHAR(50) | 城市名稱，用於職缺硬篩選 |
| district | 地區 | District | VARCHAR(50) | 行政區名稱，用於職缺硬篩選 |
| remote_option | 遠端選項 | Remote Option | VARCHAR(50) | 遠端選項 |
| job_details | 詳細資訊 | Job Details | JSONB | 詳細資訊（福利、學歷、工時等） |
| source_platform | 來源平台 | Source Platform | VARCHAR(50) | 來源平台 |
| source_url | 來源網址 | Source URL | VARCHAR(500) | 來源網址 |
| posted_date | 發布日期 | Posted Date | DATE | 發布日期 |
| scraped_at | 爬取時間 | Scraped At | DATETIME | 爬取時間 |
| is_active | 是否有效 | Is Active | BOOLEAN | 是否有效 |

**設計說明**:
- 對應流程圖右側「動作: 確認履歷並生成職缺名列表」
- **⚡ 需要向量化**:`job_description + requirements` 會轉換為向量存入 Qdrant
- **地址欄位說明**:
  - `full_address`:儲存職缺完整地址資訊（例如：「台北市信義區信義路五段7號」），用於顯示詳細位置
  - `city`:城市名稱（例如：「台北市」、「新北市」），用於職缺硬篩選功能，支援快速篩選特定城市的職缺
  - `district`:行政區名稱（例如：「信義區」、「板橋區」），用於職缺硬篩選功能，支援精確篩選特定行政區的職缺
- **remote_option 說明**:
  - `on-site`:需到辦公室
  - `hybrid`:混合辦公
  - `remote`:完全遠端
- **維度定義 (Dimensions Definitions)** — 六個職能向度，分數 1~5（1=基本理解，5=專家/架構）：
  - **D1 前端工程**: UI 實作、瀏覽器渲染、UX；JD 若提及未列出的現代框架，依該框架在生態中的定位歸類。
  - **D2 後端工程**: API 設計、資料庫設計、高併發處理。
  - **D3 雲端維運**: Docker/K8s、CI/CD、雲端架構(AWS/GCP)。
  - **D4 AI與數據**: ETL、Python 資料分析、RAG/LLM 應用、ML 模型。
  - **D5 品質與架構**: 單元測試、設計模式、SOLID、資安意識；為區分 Senior 的關鍵向度，JD 強調「Clean Code」「Refactoring」時此項應給高分。
  - **D6 軟實力**: 溝通協作、Agile/Scrum、商業思維。
- **✅ 最終建議 (MVP)**:只新增一個 JSONB 欄位 `job_details`，把非固定欄位資訊集中存放
  - 欄位建議包含:福利、休假制度、工作時間、學歷要求、經驗要求、其他雜項(穿著、停車、餐費等)
  - 優點:✅ 最彈性 ✅ 爬蟲最簡單 ✅ 不確定的資訊都能塞
  - 未來:等資料穩定後，再視需要拆出重要欄位
  - `remote_option` 可保留；雇用類型/經驗要求等放入 `job_details`

```sql
ALTER TABLE JOB_POSTING 
ADD COLUMN job_details JSONB;
```

---

## 6. 技能管理表

### 6.1 SKILL_MASTER(技能主檔)⚪

**功能說明**:技能標準化字典,統一技能名稱與分類

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| skill_id | 技能識別碼 | Skill ID | INT | 技能識別碼 | PRIMARY KEY |
| skill_name | 技能名稱 | Skill Name | VARCHAR(100) | 技能名稱 | UNIQUE, NOT NULL |
| skill_category | 技能分類 | Skill Category | VARCHAR(50) | 技能分類 (Programming/Framework/Tool/Soft) | - |
| synonyms | 同義詞 | Synonyms | JSONB | 同義詞列表 | - |
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

### 6.4 COURSE(課程主表)🟣

**功能說明**:儲存推薦用課程（如 Coursera），供「依職缺技能需求」或「依技能落差」推薦課程。以 **url** 為唯一鍵，寫入時 upsert 避免重複；第一次寫入即依 skill_master 帶入 primary_skill_id。

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| course_id | 課程識別碼 | Course ID | INT / BIGSERIAL | 課程唯一識別碼 | PRIMARY KEY |
| course_name | 課程名稱 | Course Name | VARCHAR(500) | 課程標題 | NOT NULL |
| url | 課程網址 | URL | VARCHAR(500) | 課程連結（如 Coursera） | UNIQUE, NOT NULL |
| primary_skill_name | 主要技能名稱 | Primary Skill Name | VARCHAR(100) | 主技能標籤（對應 skill_master.skill_name） | - |
| primary_skill_id | 主要技能識別碼 | Primary Skill ID | INT | 關聯技能主檔 | FOREIGN KEY → skill_master(skill_id) |
| rating | 評分 | Rating | NUMERIC(3,2) | 0～5 | - |
| review_count | 評論數 | Review Count | INT | 評論筆數 | - |
| level | 難度 | Level | VARCHAR(50) | Beginner / Intermediate / Advanced | - |
| course_type | 課程類型 | Course Type | VARCHAR(100) | Course / Specialization / Professional Certificate 等 | - |
| course_information | 課程資訊 | Course Information | TEXT | 大綱/模組 | - |
| duration_suggested | 建議學習時間 | Duration Suggested | VARCHAR(100) | 標準化字串（如 "1-3 months"） | - |
| skills | 技能列表 | Skills | JSONB | 技能名稱陣列，供推薦匹配 | - |
| role_type | 職務類型 | Role Type | TEXT | 六大職類貼標代碼（A-F），與 job_posting 一致 | - |
| role_name | 職務名稱標籤 | Role Name | TEXT | 對應職類名稱（如前端工程師、後端工程師） | - |
| source_platform | 來源平台 | Source Platform | VARCHAR(50) | 如 'Coursera' | DEFAULT 'Coursera' |
| created_at | 建立時間 | Created At | TIMESTAMPTZ | 寫入時間 | DEFAULT now() |

**設計說明**:
- **來源與寫入**: 由 `course_clean_and_upload.ipynb` 清洗 Coursera 等來源 CSV，以 url 為唯一鍵 upsert 寫入；新資料重跑即可覆寫同 URL，不重複插入。
- **與 skill_master 關聯**: primary_skill_id 指向 skill_master(skill_id)，寫入時依 primary_skill_name（含同義詞）對照帶入。
- **course_type 說明**（由來源 Metadata 拆出）：`Course` 單一課程、`Specialization` 專項課程、`Professional Certificate` 專業認證、`Guided Project` 導引專案；供篩選或顯示課程類型。
- **與其他表之邏輯關聯（無直接 FK）**:
  - **職缺推薦**: 由 JOB_SKILL_REQUIREMENT 取得職缺所需技能，與 COURSE 的 primary_skill_name / primary_skill_id 或 skills(JSONB) 匹配後排序推薦（如依 rating、review_count）。
  - **技能落差推薦**: 由 CAREER_ANALYSIS_REPORT.gap_analysis 或 CAREER_SURVEY.skill_self_assessment 取得要補的技能，與 COURSE 技能欄位匹配後推薦課程。

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
| matched_at | 媒合時間 | Matched At | DATETIME | 媒合時間 | NOT NULL |
| user_viewed | 使用者已查看 | User Viewed | BOOLEAN | 使用者是否已查看此媒合結果 | DEFAULT FALSE |
| matching_status | 媒合狀態 | Matching Status | VARCHAR(50) | 媒合狀態 (active/inactive) | DEFAULT 'active' |

**設計說明**:
- 對應流程圖右側「RAG Worker 向量檢索」→「計算 Match Score」
- **分數欄位**:`overall_match_score` 儲存總體配適度分數,其餘配適度分數細節都儲存在 MATCH_SCORE 表中
- **演算法欄位**:`matching_algorithm` 紀錄實際使用的演算法類型(例如 vector/rule-based/hybrid),有助於日後 A/B 測試與結果追蹤

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
| score_breakdown | 分數明細 | Score Breakdown | JSONB | 分數明細說明 | - |
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

### 7.3 COVER_LETTER(求職信)🟢

**功能說明**:儲存針對特定職缺 AI 生成的求職信，支援發送狀態追蹤與 Agent 調用關聯。

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| cover_letter_id | 求職信識別碼 | Cover Letter ID | BIGSERIAL | 求職信識別碼 | PRIMARY KEY |
| user_id | 使用者識別碼 | User ID | INT | 關聯使用者 | FK → USER, NOT NULL |
| job_id | 職缺識別碼 | Job ID | INT | 針對的目標職缺 | FK → JOB_POSTING, NOT NULL |
| resume_id | 履歷識別碼 | Resume ID | INT | 產生時使用的履歷（可選） | FK → RESUME |
| optimization_id | 優化識別碼 | Optimization ID | BIGINT | 產生時使用的履歷優化結果（可選） | FK → RESUME_OPTIMIZATION |
| agent_session_id | Session 識別碼 | Agent Session ID | BIGINT | 關聯的 Agent 調用 Session | FK → AGENT_SESSION |
| subject | 郵件主旨 | Subject | TEXT | 吸引人且專業的郵件主旨 | NOT NULL |
| content | 求職信內容 | Content | TEXT | 完整求職信正文 | NOT NULL |
| llm_model_used | 使用的 LLM 模型 | LLM Model Used | VARCHAR(100) | 產生此求職信使用的 LLM 版本 | - |
| is_sent | 是否已發送 | Is Sent | BOOLEAN | 是否已實際發送給企業 | DEFAULT FALSE |
| sent_at | 發送時間 | Sent At | TIMESTAMPTZ | 實際發送時間 | - |
| created_at | 建立時間 | Created At | TIMESTAMPTZ | 求職信產生時間 | NOT NULL, DEFAULT NOW() |

**設計說明**:
- 對應流程圖「動作: 生成求職信」
- **FK 設計邏輯**:
  - `user_id` → `USER`：必填，確認求職信屬於哪位使用者
  - `job_id` → `JOB_POSTING`：必填，針對的目標職缺
  - `resume_id` → `RESUME`：可選，產生時使用的原始履歷
  - `optimization_id` → `RESUME_OPTIMIZATION`：可選，產生時使用的履歷優化結果（以優化版生成求職信時填寫）
  - `agent_session_id` → `AGENT_SESSION`：可選，若由 Agent 產生則關聯 Session
- **注意**: `COVER_LETTER.agent_session_id` FK 指向 `AGENT_SESSION`，需在建立 `AGENT_SESSION` 後才能加入此約束

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
| user_feedback | 使用者回報結果 | User Feedback | JSONB | 使用者回報結果 | - |

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

**功能說明**:儲存 AI 生成的職涯分析報告，含初步摘要、雷達圖、職能落差與行動計畫

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| report_id | 報告識別碼 | Report ID | INT | 報告識別碼 | PRIMARY KEY |
| survey_id | 問卷識別碼 | Survey ID | INT | 關聯問卷 | FOREIGN KEY |
| resume_id | 履歷識別碼 | Resume ID | INT | 關聯履歷 | FOREIGN KEY |
| target_position | 目標職位 | Target Position | JSONB | LLM 分析報告中識別出的目標職位資訊 | - |
| skill_gap_analysis | 技能落差分析 | Skill Gap Analysis | JSONB | 技術性技能缺口細節 | - |
| career_path_suggestions | 職涯路徑建議 | Career Path Suggestions | JSONB | 職涯路徑多條選項 | - |
| market_insights | 市場洞察 | Market Insights | JSONB | 市場洞察 | - |
| career_readiness_score | 職涯準備度分數 | Career Readiness Score | FLOAT | 職涯準備度分數 (0-100) | - |
| generated_at | 報告生成時間 | Generated At | DATETIME | 報告生成時間 | NOT NULL |
| user_id | 使用者識別碼 | User ID | INT | 直接關聯用戶（避免多層 JOIN） | FOREIGN KEY |
| report_version | 報告版本 | Report Version | VARCHAR(10) | 報告 Schema 版本 | DEFAULT '1.0' |
| preliminary_summary | 初步摘要 | Preliminary Summary | JSONB | 存 `{"core_insight": "..."}` | - |
| radar_chart | 雷達圖 | Radar Chart | JSONB | 雷達圖完整結構 | - |
| gap_analysis | 職能落差分析 | Gap Analysis | JSONB | 職能落差完整結構 | - |
| action_plan | 行動計畫 | Action Plan | JSONB | 短中長期行動計畫 | - |

**設計說明**:
- 對應流程圖右側「顯示: 職涯發展表板」→「動作: 檢視職能分析結果」
- 使用 AI LLM/NLP 生成分析報告
- **為什麼需要 CAREER_SURVEY + RESUME**:
  - `CAREER_SURVEY` 提供主觀意圖(想去的產業、期望薪資)
  - `RESUME` 提供客觀能力(實際技能、工作經驗)
  - 兩者結合才能產生有意義的分析報告
- **新增欄位與報告 JSON 對應**:
  - `user_id`: 對應 `report_metadata.user_id`，直接關聯用戶，查詢時不需多層 JOIN
  - `report_version`: 對應 `report_metadata.version`，便於未來 Schema 演進
  - `target_position`: 儲存 LLM 分析報告中識別出的目標職位資訊，用於快速查詢與顯示使用者期望的職位方向
  - `preliminary_summary`、`radar_chart`、`gap_analysis`、`action_plan`: 分別儲存報告內對應區塊的完整 JSONB，滿足快速上線與彈性儲存

---

### 9.2 SIDE_PROJECT_RECOMMENDATION（Side Project 推薦）🟠

**功能說明**：推薦學習專案以填補技能落差，對應 SideProject 輸出結構，含完整的分階段實作規劃

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| recommendation_id | 推薦識別碼 | Recommendation ID | INT | 推薦識別碼 | PRIMARY KEY |
| report_id | 報告識別碼 | Report ID | INT | 關聯職涯分析報告 | FOREIGN KEY → CAREER_ANALYSIS_REPORT(report_id) |
| user_id | 使用者識別碼 | User ID | INT | 關聯使用者（冗餘欄位，便於依使用者查詢與 RLS） | FOREIGN KEY → USER(user_id) |
| project_name | 專案名稱 | Project Name | VARCHAR(200) | 專案名稱，需具專業感能清楚體現核心價值 | - |
| tech_stack | 使用技術清單 | Tech Stack | JSONB | 完整技術棧清單（後端、資料庫、部署、容器化等）List[str] | - |
| difficulty | 實作困難程度 | Difficulty | TEXT | 格式：'難度等級 (低/中/高) \| 預估開發週期（含部署與測試）'，並簡述主要挑戰點 | - |
| capability_gaps_addressed | 對應補強的能力缺口 | Capability Gaps Addressed | JSONB | 此專案主要補強的能力缺口清單（對應求職弱項）List[str] | - |
| project_phases | 專案分階段規劃 | Project Phases | JSONB | 分階段實作規劃 List[ProjectPhase]，結構見下方說明 | - |
| overall_resume_impact | 對履歷競爭力的提升說明 | Overall Resume Impact | TEXT | 整個專案完成後對履歷競爭力的整體提升說明 | - |
| created_at | 建立時間 | Created At | TIMESTAMPTZ | 建立時間 | DEFAULT now() |

**設計說明**：
- 對應流程圖右側「動作: 檢視推薦 side project」
- 對應輸出結構定義 `SideProject` Class
- **欄位修正紀錄（v2.1）**：
  - `required_skills` 改名為 `tech_stack`
  - `difficulty_level` 改名為 `difficulty` 並改為 TEXT：輸出格式包含難度等級與時程評估的完整字串，VARCHAR(50) 不足
  - 新增 `overall_resume_impact` 儲存對履歷競爭力的提升說明（模型輸出不含 project_description / estimated_hours / project_url，已從表結構移除）
- **`project_phases` JSONB 結構定義**（對應 `ProjectPhase` Class）：
  ```json
  [
    {
      "phase_name": "Phase 1: 核心 API 與資料庫設計 (MVP Backend)",
      "phase_goal": "建立可運作的後端服務與資料模型",
      "tasks": [
        "設計 RESTful API 端點",
        "建立 PostgreSQL schema",
        "實作基本 CRUD 操作"
      ],
      "resume_value": "獨立設計並實作高併發 RESTful API，支援每秒 500 筆請求處理"
    }
  ]
  ```
- **`capability_gaps_addressed` 範例**：
  ```json
  ["Kubernetes 部署", "CI/CD 流程設計", "系統監控與告警"]
  ```
- **`tech_stack` 範例**：
  ```json
  ["FastAPI", "PostgreSQL", "Redis", "Docker", "GitHub Actions"]
  ```
- **推薦邏輯**：根據 CAREER_ANALYSIS_REPORT.gap_analysis 中的職能落差優先順序，由 AI 產生對應難度與技術棧的專案規劃

---

### 9.4 AGENT_SESSION(Agent 調用記錄)⚙️

**功能說明**:記錄每次 Agent 調用的工具使用情況與效能指標，支援行為追蹤、A/B 測試、調用成本分析與 Debug。

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| session_id | Session 識別碼 | Session ID | BIGSERIAL | Session 識別碼 | PRIMARY KEY |
| user_id | 使用者識別碼 | User ID | INT | 關聯使用者 | FK → USER, NOT NULL |
| resume_id | 履歷識別碼 | Resume ID | INT | 使用的履歷（可選） | FK → RESUME |
| trigger_type | 觸發類型 | Trigger Type | VARCHAR(50) | job_match / resume_analysis / career_report / full | - |
| user_input_summary | 使用者輸入摘要 | User Input Summary | TEXT | 使用者輸入的摘要（隱私保護，不存原文） | - |
| tool_job_match_called | 職缺媒合工具調用 | Tool Job Match Called | BOOLEAN | 是否調用職缺媒合工具 | DEFAULT FALSE |
| tool_resume_analysis_called | 履歷分析工具調用 | Tool Resume Analysis Called | BOOLEAN | 是否調用履歷分析工具 | DEFAULT FALSE |
| tool_resume_optimize_called | 履歷優化工具調用 | Tool Resume Optimize Called | BOOLEAN | 是否調用履歷優化工具 | DEFAULT FALSE |
| tool_skill_gap_called | 技能落差工具調用 | Tool Skill Gap Called | BOOLEAN | 是否調用技能落差分析工具 | DEFAULT FALSE |
| tool_side_project_called | Side Project 工具調用 | Tool Side Project Called | BOOLEAN | 是否調用 Side Project 推薦工具 | DEFAULT FALSE |
| tool_course_recommend_called | 課程推薦工具調用 | Tool Course Recommend Called | BOOLEAN | 是否調用課程推薦工具 | DEFAULT FALSE |
| tool_cover_letter_called | 求職信工具調用 | Tool Cover Letter Called | BOOLEAN | 是否調用求職信生成工具 | DEFAULT FALSE |
| analysis_id | 分析識別碼 | Analysis ID | BIGINT | 關聯的履歷分析結果 | FK → RESUME_ANALYSIS |
| optimization_id | 優化識別碼 | Optimization ID | BIGINT | 關聯的履歷優化結果 | FK → RESUME_OPTIMIZATION |
| career_report_id | 職涯報告識別碼 | Career Report ID | INT | 關聯的職涯分析報告 | FK → CAREER_ANALYSIS_REPORT |
| recommended_job_ids | 推薦職缺 ID 清單 | Recommended Job IDs | JSONB | List[int] 推薦的 job_id | - |
| recommended_course_ids | 推薦課程 ID 清單 | Recommended Course IDs | JSONB | List[int] 推薦的 course_id | - |
| total_tokens_used | 消耗 Token 數 | Total Tokens Used | INT | 本次調用消耗的總 token 數 | - |
| latency_ms | 回應時間 | Latency MS | INT | 總回應時間（毫秒） | - |
| llm_model_used | 使用的 LLM 模型 | LLM Model Used | VARCHAR(100) | 本次調用使用的 LLM 版本 | - |
| status | Session 狀態 | Status | VARCHAR(50) | running / completed / failed | DEFAULT 'completed' |
| error_message | 錯誤訊息 | Error Message | TEXT | 失敗時的錯誤原因 | - |
| created_at | 建立時間 | Created At | TIMESTAMPTZ | Session 開始時間 | NOT NULL, DEFAULT NOW() |
| completed_at | 完成時間 | Completed At | TIMESTAMPTZ | Session 完成時間 | - |

**設計說明**:
- 對應流程圖「流程 C: Agent 完整調用流程」
- **為何需要此表**: `FinalAgentOutput` 是 Agent 單次調用的彙總輸出，沒有 Session 記錄就無法做行為追蹤、A/B 測試、調用成本分析與 Debug
- **工具調用追蹤**: 透過 `tool_*_called` 布林欄位記錄哪些工具被調用
- **關聯各子模組產出**: 透過 `analysis_id`、`optimization_id`、`career_report_id` 關聯各子模組的產出 ID（nullable，未調用的工具為 NULL）
- **推薦結果輕量記錄**: `recommended_job_ids` 和 `recommended_course_ids` 僅記錄 ID 清單，不重複存詳細資料
- **執行效能追蹤**: `total_tokens_used` 和 `latency_ms` 用於成本分析與效能優化

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
| USER | User | CAREER_ANALYSIS_REPORT | Career Analysis Report | 一位使用者可擁有多份分析報告（經由 user_id） |
| RESUME | Resume | RESUME_VERSION | Resume Version | 一份履歷可有多個版本 |
| RESUME_VERSION | Resume Version | APPLICATION_RECORD | Application Record | 一個履歷版本可被多次投遞 |
| RESUME | Resume | RESUME_ANALYSIS | Resume Analysis | 一份履歷可產生多次分析（針對不同職缺或時間點） |
| RESUME | Resume | RESUME_OPTIMIZATION | Resume Optimization | 一份原始履歷可產生多份優化版本 |
| RESUME_VERSION | Resume Version | RESUME_OPTIMIZATION | Resume Optimization | 一個版本可對應一份 AI 優化結果（可選） |
| CAREER_SURVEY | Career Survey | CAREER_ANALYSIS_REPORT | Career Analysis Report | 一份問卷可生成多次分析報告 |
| CAREER_ANALYSIS_REPORT | Career Analysis Report | SIDE_PROJECT_RECOMMENDATION | Side Project Recommendation | 一份職涯報告可推薦多個 Side Project |
| JOB_POSTING | Job Posting | JOB_MATCHING | Job Matching | 一個職缺可被多位求職者匹配 |
| JOB_POSTING | Job Posting | APPLICATION_RECORD | Application Record | 一個職缺可被多人投遞 |
| JOB_POSTING | Job Posting | RESUME_ANALYSIS | Resume Analysis | 一個職缺可對應多份履歷分析（選擇性關聯） |
| JOB_POSTING | Job Posting | COVER_LETTER | Cover Letter | 一個職缺可產生多封求職信 |
| USER | User | COVER_LETTER | Cover Letter | 一位使用者可產生多封求職信 |
| USER | User | AGENT_SESSION | Agent Session | 一位使用者可觸發多次 Agent 調用 |
| SKILL_MASTER | Skill Master | COURSE | Course | 一個技能可對應多門課程（primary_skill_id） |

### 選擇性關聯 (Optional FK)

| 主表 | 主表英文 | 從表 | 從表英文 | 說明 |
|-----|---------|------|---------|------|
| JOB_POSTING | Job Posting | RESUME_ANALYSIS | Resume Analysis | 分析時若有對應目標職缺則記錄，否則為 NULL |
| RESUME_VERSION | Resume Version | RESUME_OPTIMIZATION | Resume Optimization | 優化結果若已存為新版本則關聯，否則為 NULL |
| RESUME | Resume | COVER_LETTER | Cover Letter | 產生求職信時使用的履歷（可選） |
| RESUME_OPTIMIZATION | Resume Optimization | COVER_LETTER | Cover Letter | 產生求職信時使用的履歷優化結果（可選） |
| AGENT_SESSION | Agent Session | COVER_LETTER | Cover Letter | 求職信若由 Agent 產生則關聯 Session（可選） |
| RESUME_ANALYSIS | Resume Analysis | AGENT_SESSION | Agent Session | Session 若調用履歷分析工具則關聯（可選） |
| RESUME_OPTIMIZATION | Resume Optimization | AGENT_SESSION | Agent Session | Session 若調用履歷優化工具則關聯（可選） |
| CAREER_ANALYSIS_REPORT | Career Analysis Report | AGENT_SESSION | Agent Session | Session 若調用職涯報告工具則關聯（可選） |

### 多對多關係 (M:N)

| 表 A | 表 A 英文 | 中介表 | 中介表英文 | 表 B | 表 B 英文 | 說明 |
|------|----------|-------|-----------|------|----------|------|
| JOB_POSTING | Job Posting | JOB_SKILL_REQUIREMENT | Job Skill Requirement | SKILL_MASTER | Skill Master | 職缺可要求多種技能 |
| USER_PROFILE | User Profile | USER_SKILL | User Skill | SKILL_MASTER | Skill Master | 使用者可擁有多種技能 |

**邏輯關聯（無中介表，依欄位匹配）**:
- **COURSE** 與 **JOB_SKILL_REQUIREMENT** / **CAREER_ANALYSIS_REPORT.gap_analysis**：透過 COURSE.primary_skill_id、COURSE.skills(JSONB) 與技能主檔對應，供「依職缺所需技能」或「依職能落差分析結果」推薦課程；實作時由應用層依 skill_id 或技能名稱匹配。

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
2. 生成 CAREER_ANALYSIS_REPORT（含 gap_analysis 職能落差結構）
   ↓
3. 根據 gap_analysis 識別技能落差與優先順序
   ↓
4. SIDE_PROJECT_RECOMMENDATION 推薦專案
   ↓
5. JOB_MATCHING 職缺媒合(使用向量相似度)
   ↓
6. MATCH_SCORE 計算分數
   ↓
7. APPLICATION_RECORD 投遞追蹤
```

### 流程 C:Agent 完整調用流程

```
1. USER 觸發 Agent（求職匹配/履歷分析/全模式）
   ↓
2. AGENT_SESSION 建立（status='running'）
   ↓
3. 依 trigger_type 決定調用哪些工具：
   ├─ job_match → JOB_MATCHING + MATCH_SCORE
   ├─ resume_analysis → RESUME_ANALYSIS（含 critical_issues）
   ├─ resume_optimize → RESUME_OPTIMIZATION
   ├─ side_project → SIDE_PROJECT_RECOMMENDATION
   ├─ course_recommend → COURSE（查詢）
   └─ cover_letter → COVER_LETTER
   ↓
4. AGENT_SESSION 更新（關聯各子模組 ID + token 用量 + latency）
   ↓
5. AGENT_SESSION.status 更新為 'completed'
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
- 履歷 AI 診斷分析 (RESUME_ANALYSIS，含 critical_issues JSONB)
- 履歷 AI 優化結果儲存 (RESUME_OPTIMIZATION)

### 🔮 Release 3 - 未來規劃

- LinkedIn Profile 匯入(需擴充 USER.auth_provider)
- GitHub 作品集整合(使用 USER_PROFILE.github_repo)
- 面試追蹤系統(需新增 INTERVIEW_RECORD 表)
- 整合 104/Cake 平台帳號
- 一鍵投遞功能
- 求職信生成與追蹤 (COVER_LETTER)
- Agent 調用行為追蹤 (AGENT_SESSION)

---

## 設計原則

1. **模組化設計**:每個功能模組對應獨立的資料表群組
2. **可擴展性**:JSONB 欄位預留未來功能擴充空間
3. **資料完整性**:使用外鍵約束確保資料一致性
4. **效能優化**:關鍵查詢欄位建立索引
5. **安全性**:敏感資料加密儲存(password_hash)
6. **向量化支援**:RESUME 與 JOB_POSTING 支援語意搜尋

---

**文件製作**:Career Pilot 資料組  
**最後更新**:2026-01-21  
**文件版本**:v2.0
