# Career Pilot ERD 修正規劃文件
> **用途**: 交付 Cursor 執行的完整 ERD 修正指令
> **產出日期**: 2026-02-20
> **依據**: 輸出結構定義.md × career_pilot說明文件v4 的欄位對照分析
> **優先順序**: 高優先 → 中優先 → 低優先

---

## 📋 修正總覽

| 優先級 | 任務 | 新增表格 | 影響範圍 |
|--------|------|----------|----------|
| 🔴 高優先 | 履歷分析結果持久化 | `RESUME_ANALYSIS` | RESUME (FK) |
| 🟡 中優先 | 履歷優化結果儲存 | `RESUME_OPTIMIZATION` | RESUME, RESUME_VERSION (FK) |
| 🟢 低優先 | 求職信儲存 | `COVER_LETTER` | USER, JOB_POSTING (FK) |
| 🟢 低優先 | Agent 調用追蹤 | `AGENT_SESSION` | USER, RESUME (FK) |

---

## 🔴 高優先：新增 RESUME_ANALYSIS 表

### 背景說明

`ResumeAnalysis` + `ResumeIssue` 是履歷診斷模組的核心輸出。目前 ERD 中 `RESUME` 表僅存原始資料，**完全沒有欄位承接 AI 分析結果**，導致每次都需重新呼叫 LLM，無法做歷史追蹤與快取。

### Step 1｜新增 `RESUME_ANALYSIS` 主表

**對應 Class**: `ResumeAnalysis`

```sql
CREATE TABLE RESUME_ANALYSIS (
    analysis_id         BIGSERIAL       PRIMARY KEY,
    resume_id           INT             NOT NULL,
    user_id             INT             NOT NULL,

    -- ResumeAnalysis 核心欄位
    candidate_positioning       TEXT,           -- 企業視角下此履歷『看起來像什麼角色』
    target_role_gap_summary     TEXT,           -- 與目標職位的整體落差說明
    overall_strengths           JSONB,          -- List[str] 最具說服力的優勢點
    overall_weaknesses          JSONB,          -- List[str] 影響錄取率的核心弱點
    ats_risk_level              VARCHAR(20),    -- 'low' | 'medium' | 'high'
    screening_outcome_prediction TEXT,          -- 模擬 6-10 秒快速掃描後的篩選結果
    recommended_next_actions    JSONB,          -- List[str] 下一步行動建議

    -- 目標職缺關聯（可選，分析時若有對應職缺則記錄）
    target_job_id               INT,

    -- 分析元資料
    llm_model_used              VARCHAR(100),   -- 記錄使用的 LLM 版本，便於追蹤
    analysis_version            VARCHAR(10)     DEFAULT '1.0',
    generated_at                TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    -- FK 約束
    CONSTRAINT fk_resume_analysis_resume
        FOREIGN KEY (resume_id) REFERENCES RESUME(resume_id) ON DELETE CASCADE,
    CONSTRAINT fk_resume_analysis_user
        FOREIGN KEY (user_id) REFERENCES USER(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_resume_analysis_job
        FOREIGN KEY (target_job_id) REFERENCES JOB_POSTING(job_id) ON DELETE SET NULL
);
```

**索引建議**:
```sql
CREATE INDEX idx_resume_analysis_resume_id ON RESUME_ANALYSIS(resume_id);
CREATE INDEX idx_resume_analysis_user_id ON RESUME_ANALYSIS(user_id);
CREATE INDEX idx_resume_analysis_generated_at ON RESUME_ANALYSIS(generated_at DESC);
```

---

### Step 2｜新增 `RESUME_ISSUE` 子表

**對應 Class**: `ResumeIssue`（ResumeAnalysis 的 `critical_issues` 欄位展開）

> **設計決策**: `critical_issues` 是 `List[ResumeIssue]`，每筆 Issue 結構複雜（含多個 List 子欄位），**獨立成子表**優於塞入 JSONB，原因：
> - 可依 `severity` 或 `section` 做條件篩選
> - 支援未來 Issue 狀態追蹤（已解決/未解決）
> - 可聚合分析哪個 section 最常出問題

```sql
CREATE TABLE RESUME_ISSUE (
    issue_id            BIGSERIAL       PRIMARY KEY,
    analysis_id         BIGINT          NOT NULL,   -- FK → RESUME_ANALYSIS

    -- ResumeIssue 欄位
    section             VARCHAR(100),               -- 履歷區塊名稱（簡介/技能/經歷/專案/自傳）
    original_text       TEXT,                       -- 該區塊原始文字，僅作分析依據不修改
    issue_type          JSONB,                      -- List[str] 問題類型分類
    severity            JSONB,                      -- List[str] 嚴重程度
    diagnosis_dimension VARCHAR(100),               -- 主要影響的企業診斷面向
    issue_reason        TEXT,                       -- 站在 HR/ATS 角度說明降低錄取率的原因
    improvement_direction JSONB,                    -- List[str] 可執行的改善方向

    -- 排序與狀態
    sort_order          INT             DEFAULT 0,  -- 依嚴重度排序的顯示順序
    is_resolved         BOOLEAN         DEFAULT FALSE, -- 使用者是否已處理此問題

    CONSTRAINT fk_resume_issue_analysis
        FOREIGN KEY (analysis_id) REFERENCES RESUME_ANALYSIS(analysis_id) ON DELETE CASCADE
);
```

**索引建議**:
```sql
CREATE INDEX idx_resume_issue_analysis_id ON RESUME_ISSUE(analysis_id);
CREATE INDEX idx_resume_issue_section ON RESUME_ISSUE(section);
CREATE INDEX idx_resume_issue_severity ON RESUME_ISSUE USING GIN(severity);
```

---

### Step 3｜更新 ERD 關聯說明（說明文件需同步修改）

在說明文件的「資料表關聯關係總覽」新增以下內容：

**一對多關係 (1:N)**:
| 主表 | 從表 | 說明 |
|------|------|------|
| RESUME | RESUME_ANALYSIS | 一份履歷可產生多次分析（針對不同職缺或時間點） |
| RESUME_ANALYSIS | RESUME_ISSUE | 一份分析報告包含多個問題條目 |

**選擇性關聯 (Optional FK)**:
| 主表 | 從表 | 說明 |
|------|------|------|
| JOB_POSTING | RESUME_ANALYSIS | 分析時若有對應目標職缺則記錄，否則為 NULL |

---

## 🟡 中優先：新增 RESUME_OPTIMIZATION 表

### 背景說明

`ResumeOptimization` 是 AI 優化後的完整履歷輸出。目前 `RESUME_VERSION.content (JSONB)` 語意上是「版本快照」而非「AI 優化結果」，**混用會造成版本管理邏輯混亂**，建議獨立成表。

**FK 設計邏輯**:
- `resume_id` → `RESUME`：確認這份優化屬於哪份原始履歷
- `version_id` → `RESUME_VERSION`：可選，若優化結果已存為新版本則關聯
- `target_job_id` → `JOB_POSTING`：可選，記錄此次優化是針對哪個職缺

### Step 4｜新增 `RESUME_OPTIMIZATION` 表

**對應 Class**: `ResumeOptimization`

```sql
CREATE TABLE RESUME_OPTIMIZATION (
    optimization_id         BIGSERIAL       PRIMARY KEY,
    resume_id               INT             NOT NULL,   -- FK → RESUME（必填）
    version_id              INT,                        -- FK → RESUME_VERSION（可選）
    user_id                 INT             NOT NULL,   -- FK → USER（避免多層 JOIN）
    target_job_id           INT,                        -- FK → JOB_POSTING（可選）

    -- ResumeOptimization 核心欄位
    -- 注意：name/phone/email/linkedin/github 為個人敏感資料，
    -- 不由 LLM 輸出寫入，此表不儲存，由前端從 USER_PROFILE 取得
    professional_summary    TEXT,                       -- 優化後的專業摘要
    professional_experience JSONB,                      -- List[dict] 優化後的工作經歷
    core_skills             JSONB,                      -- List[str] 萃取的核心技能關鍵字
    projects                JSONB,                      -- List[dict] 優化後的專案描述
    education               JSONB,                      -- List[str] 學歷資訊
    autobiography           TEXT,                       -- 優化後的完整自傳

    -- 優化元資料
    llm_model_used          VARCHAR(100),
    optimization_version    VARCHAR(10)     DEFAULT '1.0',
    created_at              TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    -- FK 約束
    CONSTRAINT fk_resume_optimization_resume
        FOREIGN KEY (resume_id) REFERENCES RESUME(resume_id) ON DELETE CASCADE,
    CONSTRAINT fk_resume_optimization_version
        FOREIGN KEY (version_id) REFERENCES RESUME_VERSION(version_id) ON DELETE SET NULL,
    CONSTRAINT fk_resume_optimization_user
        FOREIGN KEY (user_id) REFERENCES USER(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_resume_optimization_job
        FOREIGN KEY (target_job_id) REFERENCES JOB_POSTING(job_id) ON DELETE SET NULL
);
```

**索引建議**:
```sql
CREATE INDEX idx_resume_optimization_resume_id ON RESUME_OPTIMIZATION(resume_id);
CREATE INDEX idx_resume_optimization_user_id ON RESUME_OPTIMIZATION(user_id);
CREATE INDEX idx_resume_optimization_job_id ON RESUME_OPTIMIZATION(target_job_id);
```

---

### Step 5｜更新 ERD 關聯說明（說明文件需同步修改）

在說明文件的「資料表關聯關係總覽」新增：

**一對多關係 (1:N)**:
| 主表 | 從表 | 說明 |
|------|------|------|
| RESUME | RESUME_OPTIMIZATION | 一份原始履歷可產生多份優化版本（針對不同職缺） |
| RESUME_VERSION | RESUME_OPTIMIZATION | 一個版本可對應一份 AI 優化結果（可選） |

---

## 🟢 低優先：新增 COVER_LETTER 表

### 背景說明

`CoverLetter` 是針對特定職缺產生的求職信。需關聯 `USER`、`JOB_POSTING`，並記錄使用的履歷版本與 Agent 調用 Session。

### Step 6｜新增 `COVER_LETTER` 表

**對應 Class**: `CoverLetter`

```sql
CREATE TABLE COVER_LETTER (
    cover_letter_id     BIGSERIAL       PRIMARY KEY,
    user_id             INT             NOT NULL,   -- FK → USER
    job_id              INT             NOT NULL,   -- FK → JOB_POSTING
    resume_id           INT,                        -- FK → RESUME（可選，產生時使用的履歷）
    agent_session_id    BIGINT,                     -- FK → AGENT_SESSION（可選）

    -- CoverLetter 欄位
    subject             TEXT            NOT NULL,   -- 吸引人的郵件主旨
    content             TEXT            NOT NULL,   -- 完整求職信內容

    -- 元資料
    llm_model_used      VARCHAR(100),
    is_sent             BOOLEAN         DEFAULT FALSE,  -- 是否已實際發送
    sent_at             TIMESTAMPTZ,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    -- FK 約束
    CONSTRAINT fk_cover_letter_user
        FOREIGN KEY (user_id) REFERENCES USER(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_cover_letter_job
        FOREIGN KEY (job_id) REFERENCES JOB_POSTING(job_id) ON DELETE CASCADE,
    CONSTRAINT fk_cover_letter_resume
        FOREIGN KEY (resume_id) REFERENCES RESUME(resume_id) ON DELETE SET NULL,
    CONSTRAINT fk_cover_letter_session
        FOREIGN KEY (agent_session_id) REFERENCES AGENT_SESSION(session_id) ON DELETE SET NULL
);
```

> ⚠️ **注意**: `COVER_LETTER.agent_session_id` FK 指向 `AGENT_SESSION`，需在 Step 7 建立 `AGENT_SESSION` 後才能加入此約束。建議的 SQL 執行順序：先建 `AGENT_SESSION`，再建 `COVER_LETTER`。

**索引建議**:
```sql
CREATE INDEX idx_cover_letter_user_id ON COVER_LETTER(user_id);
CREATE INDEX idx_cover_letter_job_id ON COVER_LETTER(job_id);
```

---

## 🟢 低優先：新增 AGENT_SESSION 表

### 背景說明

`FinalAgentOutput` 是 Agent 單次調用的彙總輸出，涵蓋推薦職缺、履歷分析、履歷優化、Side Project、課程推薦、求職信等所有子模組的結果。**沒有 Session 記錄，就無法做行為追蹤、A/B 測試、調用成本分析與 Debug**。

### Step 7｜新增 `AGENT_SESSION` 表（應先於 COVER_LETTER 建立）

**對應 Class**: `FinalAgentOutput`

```sql
CREATE TABLE AGENT_SESSION (
    session_id              BIGSERIAL       PRIMARY KEY,
    user_id                 INT             NOT NULL,   -- FK → USER
    resume_id               INT,                        -- FK → RESUME（可選）

    -- 觸發資訊
    trigger_type            VARCHAR(50),    -- 'job_match' | 'resume_analysis' | 'career_report' | 'full'
    user_input_summary      TEXT,           -- 使用者輸入的摘要（不儲存原文，保護隱私）

    -- FinalAgentOutput 各子模組是否被調用（工具調用追蹤）
    tool_job_match_called       BOOLEAN     DEFAULT FALSE,
    tool_resume_analysis_called BOOLEAN     DEFAULT FALSE,
    tool_resume_optimize_called BOOLEAN     DEFAULT FALSE,
    tool_skill_gap_called       BOOLEAN     DEFAULT FALSE,
    tool_side_project_called    BOOLEAN     DEFAULT FALSE,
    tool_course_recommend_called BOOLEAN    DEFAULT FALSE,
    tool_cover_letter_called    BOOLEAN     DEFAULT FALSE,

    -- 關聯各子模組的產出 ID（nullable，未調用的工具為 NULL）
    analysis_id             BIGINT,         -- FK → RESUME_ANALYSIS
    optimization_id         BIGINT,         -- FK → RESUME_OPTIMIZATION
    career_report_id        INT,            -- FK → CAREER_ANALYSIS_REPORT

    -- 推薦結果（輕量記錄，不重複存 JobItem 詳細資料）
    recommended_job_ids     JSONB,          -- List[int] 推薦的 job_id 清單
    recommended_course_ids  JSONB,          -- List[int] 推薦的 course_id 清單

    -- 執行效能追蹤
    total_tokens_used       INT,            -- 本次 Agent 調用消耗的總 token 數
    latency_ms              INT,            -- 總回應時間（毫秒）
    llm_model_used          VARCHAR(100),

    -- Session 狀態
    status                  VARCHAR(50)     DEFAULT 'completed',  -- 'running' | 'completed' | 'failed'
    error_message           TEXT,           -- 若 status='failed' 記錄錯誤原因

    created_at              TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    completed_at            TIMESTAMPTZ,

    -- FK 約束
    CONSTRAINT fk_agent_session_user
        FOREIGN KEY (user_id) REFERENCES USER(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_agent_session_resume
        FOREIGN KEY (resume_id) REFERENCES RESUME(resume_id) ON DELETE SET NULL,
    CONSTRAINT fk_agent_session_analysis
        FOREIGN KEY (analysis_id) REFERENCES RESUME_ANALYSIS(analysis_id) ON DELETE SET NULL,
    CONSTRAINT fk_agent_session_optimization
        FOREIGN KEY (optimization_id) REFERENCES RESUME_OPTIMIZATION(optimization_id) ON DELETE SET NULL,
    CONSTRAINT fk_agent_session_report
        FOREIGN KEY (career_report_id) REFERENCES CAREER_ANALYSIS_REPORT(report_id) ON DELETE SET NULL
);
```

**索引建議**:
```sql
CREATE INDEX idx_agent_session_user_id ON AGENT_SESSION(user_id);
CREATE INDEX idx_agent_session_created_at ON AGENT_SESSION(created_at DESC);
CREATE INDEX idx_agent_session_trigger_type ON AGENT_SESSION(trigger_type);
CREATE INDEX idx_agent_session_status ON AGENT_SESSION(status);
```

---

## 📋 SQL 執行順序（重要）

Cursor 執行時需按以下順序建立，避免 FK 依賴錯誤：

```
Step 1: CREATE TABLE RESUME_ANALYSIS
Step 2: CREATE TABLE RESUME_ISSUE
Step 3: CREATE TABLE RESUME_OPTIMIZATION
Step 4: CREATE TABLE AGENT_SESSION        ← 先於 COVER_LETTER
Step 5: CREATE TABLE COVER_LETTER         ← 依賴 AGENT_SESSION
```

---

## 📝 ERD 說明文件需同步更新的章節

### 1. 資料表索引（中英對照）表格 — 新增 5 筆

| 編號 | 中文表名 | 英文表名 | 功能模組 | 說明 |
|------|---------|---------|---------|------|
| 21 | 履歷分析報告 | RESUME_ANALYSIS | 🔵 履歷生成 | 儲存 AI 對履歷的完整診斷分析結果 |
| 22 | 履歷問題條目 | RESUME_ISSUE | 🔵 履歷生成 | RESUME_ANALYSIS 的子表，每筆對應一個履歷問題 |
| 23 | 履歷優化結果 | RESUME_OPTIMIZATION | 🔵 履歷生成 | 儲存 AI 優化後的完整履歷內容 |
| 24 | 求職信 | COVER_LETTER | 🟢 職缺推薦 | 儲存針對特定職缺 AI 生成的求職信 |
| 25 | Agent 調用記錄 | AGENT_SESSION | ⚙️ 系統追蹤 | 記錄每次 Agent 調用的工具使用情況與效能指標 |

### 2. 向量化處理說明 — 無需更動（新增表格皆無向量化需求）

### 3. 版本支援說明 — 新增至 Release 2

在「Release 2 - 完整功能」下補充：
- 履歷 AI 診斷分析 (RESUME_ANALYSIS, RESUME_ISSUE)
- 履歷 AI 優化結果儲存 (RESUME_OPTIMIZATION)

在「Release 3 - 未來規劃」下補充：
- 求職信生成與追蹤 (COVER_LETTER)
- Agent 調用行為追蹤 (AGENT_SESSION)

### 4. 資料流程說明 — 新增流程 C

```
流程 C：Agent 完整調用流程

1. USER 觸發 Agent（求職匹配/履歷分析/全模式）
   ↓
2. AGENT_SESSION 建立（status='running'）
   ↓
3. 依 trigger_type 決定調用哪些工具：
   ├─ job_match → JOB_MATCHING + MATCH_SCORE
   ├─ resume_analysis → RESUME_ANALYSIS + RESUME_ISSUE
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

## 🗂️ 欄位對齊總表需新增的章節

在 `career_pilot_ERD_欄位對齊總表.md` 末尾補充以下四個新表的欄位對齊表：

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

### 22. RESUME_ISSUE（履歷問題條目）🔵

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| issue_id | 問題識別碼 | Issue ID | BIGSERIAL | 問題識別碼 | PRIMARY KEY |
| analysis_id | 分析識別碼 | Analysis ID | BIGINT | 關聯分析報告 | FK → RESUME_ANALYSIS, NOT NULL |
| section | 履歷區塊 | Section | VARCHAR(100) | 問題所在的履歷區塊（簡介/技能/經歷/專案/自傳） | - |
| original_text | 原始文字 | Original Text | TEXT | 該區塊的原始文字，僅作分析依據 | - |
| issue_type | 問題類型 | Issue Type | JSONB | List[str] 問題類型分類 | - |
| severity | 嚴重程度 | Severity | JSONB | List[str] 從企業篩選視角評估的嚴重程度 | - |
| diagnosis_dimension | 診斷面向 | Diagnosis Dimension | VARCHAR(100) | 此問題主要影響的企業診斷面向 | - |
| issue_reason | 問題原因 | Issue Reason | TEXT | 站在 HR/ATS 角度說明降低錄取率的原因 | - |
| improvement_direction | 改善方向 | Improvement Direction | JSONB | List[str] 可執行的改善方向建議 | - |
| sort_order | 排列順序 | Sort Order | INT | 依嚴重度排序的顯示順序 | DEFAULT 0 |
| is_resolved | 是否已解決 | Is Resolved | BOOLEAN | 使用者是否已處理此問題 | DEFAULT FALSE |

### 23. RESUME_OPTIMIZATION（履歷優化結果）🔵

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| optimization_id | 優化識別碼 | Optimization ID | BIGSERIAL | 優化識別碼 | PRIMARY KEY |
| resume_id | 履歷識別碼 | Resume ID | INT | 關聯原始履歷 | FK → RESUME, NOT NULL |
| version_id | 版本識別碼 | Version ID | INT | 關聯履歷版本（可選） | FK → RESUME_VERSION |
| user_id | 使用者識別碼 | User ID | INT | 關聯使用者 | FK → USER, NOT NULL |
| target_job_id | 目標職缺識別碼 | Target Job ID | INT | 優化針對的目標職缺（可選） | FK → JOB_POSTING |
| professional_summary | 專業摘要 | Professional Summary | TEXT | 優化後的專業摘要（含目標職缺關鍵字） | - |
| professional_experience | 工作經歷 | Professional Experience | JSONB | List[dict] 優化後的工作經歷（含 STAR 原則） | - |
| core_skills | 核心技能 | Core Skills | JSONB | List[str] 萃取的核心技能關鍵字 | - |
| projects | 專案作品集 | Projects | JSONB | List[dict] 優化後的專案描述 | - |
| education | 學歷 | Education | JSONB | List[str] 最高學歷資訊 | - |
| autobiography | 自傳 | Autobiography | TEXT | 保留原風格的優化後完整自傳 | - |
| llm_model_used | 使用的 LLM 模型 | LLM Model Used | VARCHAR(100) | 產生此優化使用的 LLM 版本 | - |
| optimization_version | 優化版本 | Optimization Version | VARCHAR(10) | Schema 版本 | DEFAULT '1.0' |
| created_at | 建立時間 | Created At | TIMESTAMPTZ | 優化產生時間 | NOT NULL, DEFAULT NOW() |

### 24. COVER_LETTER（求職信）🟢

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
|---------|---------|-----|---------|------|---------|
| cover_letter_id | 求職信識別碼 | Cover Letter ID | BIGSERIAL | 求職信識別碼 | PRIMARY KEY |
| user_id | 使用者識別碼 | User ID | INT | 關聯使用者 | FK → USER, NOT NULL |
| job_id | 職缺識別碼 | Job ID | INT | 針對的目標職缺 | FK → JOB_POSTING, NOT NULL |
| resume_id | 履歷識別碼 | Resume ID | INT | 產生時使用的履歷（可選） | FK → RESUME |
| agent_session_id | Session 識別碼 | Agent Session ID | BIGINT | 關聯的 Agent 調用 Session | FK → AGENT_SESSION |
| subject | 郵件主旨 | Subject | TEXT | 吸引人且專業的郵件主旨 | NOT NULL |
| content | 求職信內容 | Content | TEXT | 完整求職信正文 | NOT NULL |
| llm_model_used | 使用的 LLM 模型 | LLM Model Used | VARCHAR(100) | 產生此求職信使用的 LLM 版本 | - |
| is_sent | 是否已發送 | Is Sent | BOOLEAN | 是否已實際發送給企業 | DEFAULT FALSE |
| sent_at | 發送時間 | Sent At | TIMESTAMPTZ | 實際發送時間 | - |
| created_at | 建立時間 | Created At | TIMESTAMPTZ | 求職信產生時間 | NOT NULL, DEFAULT NOW() |

### 25. AGENT_SESSION（Agent 調用記錄）⚙️

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

---

## ✅ Cursor 執行 Checklist

```
[ ] Step 1: 建立 RESUME_ANALYSIS 表 + 索引
[ ] Step 2: 建立 RESUME_ISSUE 子表 + 索引
[ ] Step 3: 建立 RESUME_OPTIMIZATION 表 + 索引
[ ] Step 4: 建立 AGENT_SESSION 表 + 索引      ← 必須在 COVER_LETTER 前執行
[ ] Step 5: 建立 COVER_LETTER 表 + 索引
[ ] Step 6: 更新 career_pilot說明文件v4 — 資料表索引章節
[ ] Step 7: 更新 career_pilot說明文件v4 — 資料表關聯關係總覽章節
[ ] Step 8: 更新 career_pilot說明文件v4 — 版本支援說明章節
[ ] Step 9: 更新 career_pilot說明文件v4 — 新增流程 C（Agent 調用流程）
[ ] Step 10: 更新 career_pilot_ERD_欄位對齊總表.md — 補充第 21-25 表格
[ ] Step 11: 在 Supabase SQL Editor 執行全部 DDL 並驗證 FK 約束無錯誤
[ ] Step 12: 確認 RESUME_ISSUE 對 RESUME_ANALYSIS 的 CASCADE DELETE 行為正確
```

---

*文件版本: v1.0 | 產出日期: 2026-02-20 | 依據: 輸出結構定義.md × ERD v2.0 欄位對照分析*
