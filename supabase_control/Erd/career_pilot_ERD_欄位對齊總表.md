## Career Pilot ERD 欄位對齊總表

> **產出日期**: 2026-01-24  
> **來源**: `supabase_control/Erd/career_pilot說明文件v4_with_chinese.md`  
> **說明**: 本文件僅彙整各資料表「欄位表格」，用於快速對齊欄位名稱/型態/約束條件/說明。

---

### 1.1 USER(使用者主表)

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| user_id | 使用者識別碼 | User ID | INT | 使用者唯一識別碼 | PRIMARY KEY |
| email | 電子郵件 | Email | VARCHAR(255) | 使用者電子郵件 | UNIQUE, NOT NULL |
| password_hash | 密碼雜湊值 | Password Hash | VARCHAR(255) | 密碼雜湊值 | NOT NULL |
| auth_provider | 認證提供者 | Authentication Provider | VARCHAR(50) | 認證提供者 (Email/LinkedIn/Google) | DEFAULT 'Email' |
| created_at | 建立時間 | Created At | DATETIME | 帳號建立時間 | NOT NULL |
| last_login | 最後登入時間 | Last Login | DATETIME | 最後登入時間 | - |
| is_active | 帳號啟用狀態 | Is Active | BOOLEAN | 帳號是否啟用 | DEFAULT TRUE |

---

### 1.2 USER_PROFILE(使用者個人檔案)

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
| privacy_settings | 隱私設定 | Privacy Settings | JSONB | 隱私設定 | - |
| updated_at | 更新時間 | Updated At | DATETIME | 最後更新時間 | - |

---

### 2.1 CAREER_SURVEY(職涯調查問卷)

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
   | questionnaire_response | 問卷填答結果 | Questionnaire Response | JSONB | 完整問卷填答（module_a/b/c/d 所有題目與答案）；產分析報告時可依需求用 GIN 索引取值 | GIN 索引 idx_survey_response_gin |
| completed_at | 完成時間 | Completed At | DATETIME | 完成時間 | - |
| updated_at | 更新時間 | Updated At | DATETIME | 更新時間 | - |

---

### 3.1 RESUME(履歷主表)🔵

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| resume_id | 履歷識別碼 | Resume ID | INT | 履歷識別碼 | PRIMARY KEY |
| user_id | 使用者識別碼 | User ID | INT | 關聯使用者 | FOREIGN KEY |
| template_id | 模板識別碼 | Template ID | INT | 使用的模板 | FOREIGN KEY |
| resume_type | 履歷類型 | Resume Type | VARCHAR(50) | 履歷類型 (uploaded/generated) | NOT NULL |
| structured_data | 結構化資料 | Structured Data | JSONB | 結構化履歷資料 | - |
| normalized_data | 標準化資料 | Normalized Data | JSONB | 標準化後資料 | - |
| vector_id | 向量識別碼 | Vector ID | UUID | 對應 Qdrant 中的 Point ID | - |
| is_embedded | 是否已向量化 | Is Embedded | BOOLEAN | 是否已完成向量化 | DEFAULT FALSE |
| is_primary | 主要履歷標記 | Is Primary | BOOLEAN | 是否為主要履歷 | DEFAULT FALSE |
| created_at | 建立時間 | Created At | DATETIME | 建立時間 | NOT NULL |
| updated_at | 更新時間 | Updated At | DATETIME | 更新時間 | - |

---

### 3.2 RESUME_VERSION(履歷版本)🔵

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| version_id | 版本識別碼 | Version ID | INT | 版本識別碼(全域唯一主鍵) | PRIMARY KEY |
| resume_id | 履歷識別碼 | Resume ID | INT | 關聯履歷 | FOREIGN KEY |
| version_number | 版本號碼 | Version Number | INT | 邏輯版本序號(第幾次修改,允許同一序號對應不同職缺) | NOT NULL |
| file_path | 檔案儲存路徑 | File Path | VARCHAR(255) | 該版本的檔案儲存路徑 | - |
| content | 版本內容 | Content | JSONB | 版本完整內容 | - |
| optimization_target | 優化目標職位 | Optimization Target | VARCHAR(100) | 優化目標職位 | - |
| created_at | 建立時間 | Created At | DATETIME | 建立時間 | NOT NULL |

---

### 3.3 RESUME_TEMPLATE(履歷模板)🔵

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| template_id | 模板識別碼 | Template ID | INT | 模板識別碼 | PRIMARY KEY |
| template_name | 模板名稱 | Template Name | VARCHAR(100) | 模板名稱 | NOT NULL |
| template_type | 模板類型 | Template Type | VARCHAR(50) | 模板類型 (ATS/Creative/Standard) | - |
| template_structure | 模板結構 | Template Structure | JSONB | 模板結構定義 | - |
| created_at | 建立時間 | Created At | DATETIME | 建立時間 | NOT NULL |

---

### 4.1 UPLOAD_EVENT(上傳事件記錄)🔵

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

---

### 4.2 OCR_RESULT(OCR 辨識結果)🔵

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

---

### 5.1 COMPANY_INFO(公司資訊)🟢

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

---

### 5.2 JOB_POSTING(職缺資訊)🟢

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 |
|---------|---------|-----|---------|------|
| job_id | 職缺識別碼 | Job ID | INT | 職缺識別碼 | PRIMARY KEY |
| company_id | 公司識別碼 | Company ID | INT | 關聯公司 |
| job_category | 職缺類別 | Job Category | VARCHAR(100) | 職缺類別 | - |
| role_type | 職務類型 | Role Type | TEXT | 例如「前端工程師 / 後端工程師 / 全端」等職務大類 | - |
| role_name | 職務名稱標籤 | Role Name | TEXT | 更細緻的職務名稱或角色標籤 | - |
| d1_frontend | D1 前端工程 | D1 Frontend | NUMERIC | UI 實作、瀏覽器渲染、UX；分數 1~5（1=基本理解, 5=專家/架構） | - |
| d2_backend | D2 後端工程 | D2 Backend | NUMERIC | API 設計、資料庫設計、高併發處理；分數 1~5 | - |
| d3_devops | D3 雲端維運 | D3 DevOps/SRE | NUMERIC | Docker/K8s、CI/CD、雲端架構(AWS/GCP)；分數 1~5 | - |
| d4_ai_data | D4 AI與數據 | D4 AI & Data | NUMERIC | ETL、Python 資料分析、RAG/LLM、ML 模型；分數 1~5 | - |
| d5_quality | D5 品質與架構 | D5 Quality | NUMERIC | 單元測試、設計模式、SOLID、資安意識；Senior 關鍵向度；分數 1~5 | - |
| d6_soft_skills | D6 軟實力 | D6 Soft Skills | NUMERIC | 溝通協作、Agile/Scrum、商業思維；分數 1~5 | - |
| job_title | 職位名稱 | Job Title | VARCHAR(200) | 職位名稱 |
| job_description | 職缺描述 | Job Description | TEXT | 職缺描述 |
| requirements | 職缺要求 | Requirements | TEXT | 職缺要求 |
| vector_id | 向量識別碼 | Vector ID | UUID | 對應 Qdrant 中的 Point ID |
| is_embedded | 是否已向量化 | Is Embedded | BOOLEAN | 預設為 FALSE，代表是否已完成向量化 |
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

---

### 6.1 SKILL_MASTER(技能主檔)⚪

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| skill_id | 技能識別碼 | Skill ID | INT | 技能識別碼 | PRIMARY KEY |
| skill_name | 技能名稱 | Skill Name | VARCHAR(100) | 技能名稱 | UNIQUE, NOT NULL |
| skill_category | 技能分類 | Skill Category | VARCHAR(50) | 技能分類 (Programming/Framework/Tool/Soft) | - |
| synonyms | 同義詞 | Synonyms | JSONB | 同義詞列表 | - |
| created_at | 建立時間 | Created At | DATETIME | 建立時間 | - |

---

### 6.2 JOB_SKILL_REQUIREMENT(職缺技能需求)🟢

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| requirement_id | 需求識別碼 | Requirement ID | INT | 需求識別碼 | PRIMARY KEY |
| job_id | 職缺識別碼 | Job ID | INT | 關聯職缺 | FOREIGN KEY |
| skill_id | 技能識別碼 | Skill ID | INT | 關聯技能 | FOREIGN KEY |
| importance | 重要性 | Importance | VARCHAR(50) | 重要性 (required/preferred/nice-to-have) | - |
| proficiency_level | 熟練度要求 | Proficiency Level | INT | 熟練度要求 (1-10) | - |

---

### 6.3 USER_SKILL(使用者技能)⚪

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| user_skill_id | 使用者技能識別碼 | User Skill ID | INT | 使用者技能識別碼 | PRIMARY KEY |
| user_id | 使用者識別碼 | User ID | INT | 關聯使用者 | FOREIGN KEY |
| skill_id | 技能識別碼 | Skill ID | INT | 關聯技能 | FOREIGN KEY |
| proficiency_level | 熟練度 | Proficiency Level | INT | 熟練度 (1-10) | - |
| years_of_experience | 使用年資 | Years of Experience | FLOAT | 使用年資 | - |
| verified | 驗證狀態 | Verified | BOOLEAN | 驗證狀態 | DEFAULT FALSE |
| created_at | 建立時間 | Created At | DATETIME | 建立時間 | - |

---

### 6.4 COURSE(課程主表)🟣

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| course_id | 課程識別碼 | Course ID | INT / BIGSERIAL | 課程唯一識別碼 | PRIMARY KEY |
| course_name | 課程名稱 | Course Name | VARCHAR(500) | 課程標題 | NOT NULL |
| url | 課程網址 | URL | VARCHAR(500) | 課程連結（如 Coursera）；寫入以 url 為唯一鍵 upsert，避免重複 | UNIQUE, NOT NULL |
| primary_skill_name | 主要技能名稱 | Primary Skill Name | VARCHAR(100) | 主技能標籤（對應 skill_master.skill_name） | - |
| primary_skill_id | 主要技能識別碼 | Primary Skill ID | INT | 關聯技能主檔 | FOREIGN KEY → skill_master(skill_id) |
| rating | 評分 | Rating | NUMERIC(3,2) | 0～5 | - |
| review_count | 評論數 | Review Count | INT | 評論筆數 | - |
| level | 難度 | Level | VARCHAR(50) | Beginner / Intermediate / Advanced | - |
| course_type | 課程類型 | Course Type | VARCHAR(100) | Course / Specialization / Professional Certificate 等 | - |
| course_information | 課程資訊 | Course Information | TEXT | 大綱/模組 | - |
| duration_suggested | 建議學習時間 | Duration Suggested | VARCHAR(100) | 標準化字串（如 "1-3 months"） | - |
| skills | 技能列表 | Skills | JSONB | 技能名稱陣列，供職缺/技能落差推薦匹配 | - |
| role_type | 職務類型 | Role Type | TEXT | 六大職類貼標代碼（A-F），與 job_posting 一致 | - |
| role_name | 職務名稱標籤 | Role Name | TEXT | 對應職類名稱（如前端工程師、後端工程師） | - |
| source_platform | 來源平台 | Source Platform | VARCHAR(50) | 如 'Coursera' | DEFAULT 'Coursera' |
| created_at | 建立時間 | Created At | TIMESTAMPTZ | 寫入時間 | DEFAULT now() |

---

### 7.1 JOB_MATCHING(職缺媒合記錄)🟢

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| matching_id | 媒合識別碼 | Matching ID | INT | 媒合識別碼 | PRIMARY KEY |
| resume_id | 履歷識別碼 | Resume ID | INT | 關聯履歷 | FOREIGN KEY |
| job_id | 職缺識別碼 | Job ID | INT | 關聯職缺 | FOREIGN KEY |
| overall_match_score | 總體配適度分數 | Overall Match Score | FLOAT | 總體配適度分數 (0-100) | - |
| matching_algorithm | 媒合演算法 | Matching Algorithm | VARCHAR(50) | 媒合演算法 (vector/rule-based/hybrid) | - |
| matched_at | 媒合時間 | Matched At | DATETIME | 媒合時間 | - |
| user_viewed | 使用者已查看 | User Viewed | BOOLEAN | 使用者是否已查看此媒合結果 | DEFAULT FALSE |
| matching_status | 媒合狀態 | Matching Status | VARCHAR(50) | 媒合狀態 (active/inactive) | DEFAULT 'active' |

---

### 7.2 MATCH_SCORE(媒合分數)🟢

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

---

### 8.1 APPLICATION_RECORD(投遞記錄)🟢

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

---

### 9.1 CAREER_ANALYSIS_REPORT(職涯分析報告)🟠

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| report_id | 報告識別碼 | Report ID | INT | 報告識別碼 | PRIMARY KEY |
| survey_id | 問卷識別碼 | Survey ID | INT | 關聯問卷 | FOREIGN KEY |
| resume_id | 履歷識別碼 | Resume ID | INT | 關聯履歷 | FOREIGN KEY |
| target_position | 目標職位 | Target Position | VARCHAR(200) | LLM 分析報告中識別出的目標職位資訊 | - |
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

---

### 9.2 SIDE_PROJECT_RECOMMENDATION（Side Project 推薦）🟠

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| recommendation_id | 推薦識別碼 | Recommendation ID | INT | 推薦識別碼 | PRIMARY KEY |
| report_id | 報告識別碼 | Report ID | INT | 關聯職涯分析報告 | FOREIGN KEY → career_analysis_report(report_id) |
| user_id | 使用者識別碼 | User ID | INT | 關聯使用者（冗餘欄位，便於查詢與 RLS） | FOREIGN KEY → user(user_id) |
| project_name | 專案名稱 | Project Name | VARCHAR(200) | 專案名稱，需具專業感能清楚體現核心價值 | - |
| tech_stack | 使用技術清單 | Tech Stack | JSONB | 完整技術棧清單（後端、資料庫、部署、容器化等）List[str] | - |
| difficulty | 實作困難程度 | Difficulty | TEXT | 格式：'難度等級 (低/中/高) \| 預估開發週期（含部署與測試）'，並簡述主要挑戰點 | - |
| capability_gaps_addressed | 對應補強的能力缺口 | Capability Gaps Addressed | JSONB | 此專案主要補強的能力缺口清單（對應求職弱項）List[str] | - |
| project_phases | 專案分階段規劃 | Project Phases | JSONB | 分階段實作規劃，每階段含 phase_name / phase_goal / tasks / resume_value；結構見下方 | - |
| overall_resume_impact | 對履歷競爭力的提升說明 | Overall Resume Impact | TEXT | 整個專案完成後對履歷競爭力的整體提升說明 | - |
| created_at | 建立時間 | Created At | TIMESTAMPTZ | 建立時間 | DEFAULT now() |

---

### 21. RESUME_ANALYSIS（履歷分析報告）🔵

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
| critical_issues | 履歷問題清單 | Critical Issues | JSONB | 履歷各區塊的問題條目清單 List[ResumeIssue]，每筆含 section / original_text / issue_type / severity / diagnosis_dimension / issue_reason / improvement_direction | - |

---

### 22. RESUME_OPTIMIZATION（履歷優化結果）🔵

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
| created_at | 建立時間 | Created At | TIMESTAMPTZ | 優化產生時間 | NOT NULL, DEFAULT NOW() |

---

### 23. COVER_LETTER（求職信）🟢

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

---

### 24. AGENT_SESSION（Agent 調用記錄）⚙️

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

