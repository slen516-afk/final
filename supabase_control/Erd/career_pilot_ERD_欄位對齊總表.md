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

### 9.2 SKILL_GAP(技能落差)🟠

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

---

### 9.3 SIDE_PROJECT_RECOMMENDATION(Side Project 推薦)🟠

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| recommendation_id | 推薦識別碼 | Recommendation ID | INT | 推薦識別碼 | PRIMARY KEY |
| gap_id | 落差識別碼 | Gap ID | INT | 關聯技能落差 | FOREIGN KEY |
| project_name | 專案名稱 | Project Name | VARCHAR(200) | 專案名稱 | - |
| project_description | 專案描述 | Project Description | TEXT | 專案描述 | - |
| required_skills | 所需技能列表 | Required Skills | JSONB | 所需技能列表 | - |
| difficulty_level | 難度等級 | Difficulty Level | VARCHAR(50) | 難度等級 (beginner/intermediate/advanced) | - |
| estimated_hours | 預估完成時數 | Estimated Hours | INT | 預估完成時數 | - |
| project_url | 專案參考連結 | Project URL | VARCHAR(500) | 專案參考連結 | - |
| created_at | 建立時間 | Created At | DATETIME | 建立時間 | - |

