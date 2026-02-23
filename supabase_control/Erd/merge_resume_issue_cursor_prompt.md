# Cursor 任務：合併 RESUME_ISSUE → RESUME_ANALYSIS，同步更新所有文件

## 背景說明

產品確認不做「履歷問題單筆狀態追蹤」功能，因此：
- `RESUME_ISSUE` 子表的存在理由消失
- 將其所有欄位合併為一個 JSONB 欄位 `critical_issues` 存入 `RESUME_ANALYSIS`
- 刪除 `RESUME_ISSUE` 表與其在所有文件中的相關內容

需修改的檔案共四個：
1. Supabase SQL（資料庫操作）
2. `career_pilot_erd_readable.mermaid`
3. `career_pilot_ERD_欄位對齊總表.md`
4. `career_pilot說明文件v4_with_chinese.md`

---

## Task 1｜Supabase SQL Editor 執行

```sql
-- Step 1: 在 resume_analysis 新增 critical_issues 欄位
ALTER TABLE resume_analysis
    ADD COLUMN critical_issues JSONB;

-- Step 2: 刪除 resume_issue 子表
DROP TABLE IF EXISTS resume_issue;
```

`critical_issues` 存入格式為 `List[ResumeIssue]`：
```json
[
  {
    "section": "經歷",
    "original_text": "負責系統開發與維護",
    "issue_type": ["描述模糊", "缺乏量化證據"],
    "severity": ["明顯扣分"],
    "diagnosis_dimension": "工作成果可信度",
    "issue_reason": "HR 無法評估實際貢獻規模",
    "improvement_direction": ["補充負責的系統規模", "加入量化指標如 QPS、用戶數"]
  }
]
```

---

## Task 2｜修改 career_pilot_erd_readable.mermaid

### 2-1. 刪除 RESUME_ISSUE 與 RESUME_ANALYSIS 的關聯行

找到第 32 行，刪除整行：
```
RESUME_ANALYSIS ||--o{ RESUME_ISSUE : contains
```

### 2-2. 刪除 RESUME_ISSUE 整個表格定義區塊

找到並刪除以下整段（約第 333-345 行）：
```
    RESUME_ISSUE {
        bigserial issue_id PK "🔵 履歷生成"
        bigint analysis_id FK "NOT NULL"
        string section "VARCHAR(100) 履歷區塊（簡介/技能/經歷/專案/自傳）"
        text original_text "該區塊的原始文字"
        jsonb issue_type "List[str] 問題類型分類"
        jsonb severity "List[str] 嚴重程度"
        string diagnosis_dimension "VARCHAR(100)"
        text issue_reason "站在 HR/ATS 角度說明降低錄取率的原因"
        jsonb improvement_direction "List[str] 可執行的改善方向建議"
        int sort_order "DEFAULT 0"
        boolean is_resolved "DEFAULT FALSE"
    }
```

### 2-3. 在 RESUME_ANALYSIS 表格定義中新增 critical_issues 欄位

找到 `RESUME_ANALYSIS` 表格定義，在 `recommended_next_actions` 行之後、`llm_model_used` 行之前插入：
```
        jsonb critical_issues "List[ResumeIssue] 履歷各區塊問題條目，含 section/original_text/issue_type/severity/diagnosis_dimension/issue_reason/improvement_direction"
```

修改後 RESUME_ANALYSIS 區塊應為：
```
    RESUME_ANALYSIS {
        bigserial analysis_id PK "🔵 履歷生成"
        int resume_id FK "NOT NULL"
        int user_id FK "NOT NULL"
        int target_job_id FK "可選"
        text candidate_positioning "企業視角下此履歷代表的角色定位"
        text target_role_gap_summary "與目標職位的整體落差說明"
        jsonb overall_strengths "List[str] 最具說服力的優勢點"
        jsonb overall_weaknesses "List[str] 影響錄取率的核心弱點"
        string ats_risk_level "VARCHAR(20) low/medium/high"
        text screening_outcome_prediction "模擬 6-10 秒掃描後的篩選結果"
        jsonb recommended_next_actions "List[str] 可執行的下一步建議"
        jsonb critical_issues "List[ResumeIssue] 履歷各區塊問題條目，含 section/original_text/issue_type/severity/diagnosis_dimension/issue_reason/improvement_direction"
        string llm_model_used "VARCHAR(100)"
        string analysis_version "VARCHAR(10) DEFAULT '1.0'"
        timestamptz generated_at "NOT NULL, DEFAULT NOW()"
    }
```

---

## Task 3｜修改 career_pilot_ERD_欄位對齊總表.md

### 3-1. 找到「21. RESUME_ANALYSIS」章節的欄位表格

在表格最後一筆（`generated_at` 那行）之後，新增一行：

```
| critical_issues | 履歷問題清單 | Critical Issues | JSONB | 履歷各區塊的問題條目清單 List[ResumeIssue]，每筆含 section / original_text / issue_type / severity / diagnosis_dimension / issue_reason / improvement_direction | - |
```

### 3-2. 刪除「22. RESUME_ISSUE（履歷問題條目）🔵」整個章節

找到以下標題並將**整個章節（標題 + 表格）完整刪除**：

```
### 22. RESUME_ISSUE（履歷問題條目）🔵

| 欄位名稱 | 中文名稱 | 英文 | 資料型態 | 說明 | 約束條件 |
...（整段表格）
```

### 3-3. 修正後續章節編號

刪除第 22 節後，將原本的章節編號往前移：
- 原 23. RESUME_OPTIMIZATION → 改為 22.
- 原 24. COVER_LETTER → 改為 23.
- 原 25. AGENT_SESSION → 改為 24.

---

## Task 4｜修改 career_pilot說明文件v4_with_chinese.md

### 4-1. 找到「資料表索引（中英對照）」表格

**刪除**以下這一行：
```
| 22 | 履歷問題條目 | RESUME_ISSUE | 🔵 履歷生成 | RESUME_ANALYSIS 的子表，每筆對應一個履歷問題 |
```

**修改** RESUME_ANALYSIS 的說明欄位：
將：
```
| 21 | 履歷分析報告 | RESUME_ANALYSIS | 🔵 履歷生成 | 儲存 AI 對履歷的完整診斷分析結果 |
```
改為：
```
| 21 | 履歷分析報告 | RESUME_ANALYSIS | 🔵 履歷生成 | 儲存 AI 對履歷的完整診斷分析結果，含各區塊問題清單（critical_issues） |
```

後續編號同步修正：
- 原 23. RESUME_OPTIMIZATION → 22.
- 原 24. COVER_LETTER → 23.
- 原 25. AGENT_SESSION → 24.

### 4-2. 找到 RESUME_ANALYSIS 的欄位說明表格

在表格最後一筆（`generated_at`）之後新增一行：

```
| critical_issues | 履歷問題清單 | Critical Issues | JSONB | 履歷各區塊的問題條目清單，對應 ResumeIssue 結構：section（區塊名稱）/ original_text（原始文字）/ issue_type List[str]（問題類型）/ severity List[str]（嚴重程度）/ diagnosis_dimension（診斷面向）/ issue_reason（問題原因）/ improvement_direction List[str]（改善方向） | - |
```

### 4-3. 找到「一對多關係 (1:N)」表格

**刪除**以下這一行：
```
| RESUME_ANALYSIS | Resume Analysis | RESUME_ISSUE | Resume Issue | 一份分析報告包含多個問題條目 |
```

### 4-4. 找到 RESUME_ANALYSIS 章節的設計說明

在「設計說明」段落中新增以下說明：

```
- **critical_issues 合併設計（v2.1）**：
  原 RESUME_ISSUE 子表因產品不做「單筆問題狀態追蹤」功能，已合併為 JSONB 欄位存入本表。
  好處：一次 SELECT 取得完整分析結果，無需 JOIN；寫入時一次完成。
  trade-off：無法對單一問題做條件篩選或狀態更新，若未來有此需求需重新拆表。
```

### 4-5. 找到「版本支援說明」章節，修正 Release 2 的描述

將：
```
- 履歷 AI 診斷分析 (RESUME_ANALYSIS, RESUME_ISSUE)
```
改為：
```
- 履歷 AI 診斷分析 (RESUME_ANALYSIS，含 critical_issues JSONB)
```

---

## ✅ Cursor 執行 Checklist

```
[ ] Task 1: Supabase SQL — ADD COLUMN critical_issues + DROP TABLE resume_issue
[ ] Task 2-1: mermaid — 刪除 RESUME_ANALYSIS ||--o{ RESUME_ISSUE 關聯行
[ ] Task 2-2: mermaid — 刪除 RESUME_ISSUE 整個表格定義區塊
[ ] Task 2-3: mermaid — 在 RESUME_ANALYSIS 表格新增 critical_issues 欄位
[ ] Task 3-1: 欄位對齊總表 — RESUME_ANALYSIS 表格新增 critical_issues 行
[ ] Task 3-2: 欄位對齊總表 — 刪除 22. RESUME_ISSUE 整個章節
[ ] Task 3-3: 欄位對齊總表 — 章節編號 23/24/25 → 22/23/24
[ ] Task 4-1: 說明文件 — 資料表索引表格刪除 RESUME_ISSUE 行 + 修正編號
[ ] Task 4-2: 說明文件 — RESUME_ANALYSIS 欄位表格新增 critical_issues 行
[ ] Task 4-3: 說明文件 — 一對多關係表格刪除 RESUME_ISSUE 行
[ ] Task 4-4: 說明文件 — RESUME_ANALYSIS 設計說明補充合併原因
[ ] Task 4-5: 說明文件 — 版本支援說明修正 Release 2 描述
```

---

*產出日期: 2026-02-22 | 修正版本: v2.1*
