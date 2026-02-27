# AIPE02_01_Project_re 專案 - API 溝通協定與整合規範 (API Communication Protocol)

## 📌 1. 總覽與核心傳遞機制
本專案的 AI 功能模組（職涯分析、履歷處理、專案推薦、求職信）皆採用單一門面 (Facade) 架構設計，對外不直接暴露個別 Agent 端點。
統一由 **`CareerAgentManager`** 負責調度。

### 核心呼叫方式
無論是串接 FlaskAPI 或其他內部服務，呼叫 Agent Engine 的標準語法皆如下（注意：所有參數包含 `user_id` 皆統一包裝在 `user_input` 字典內）：

```python
from src.core.agent_engine.manager import CareerAgentManager

manager = CareerAgentManager()
result = manager.run_task(
    task_type_str="<對應模組任務代碼>", 
    user_input={
        "user_id": "<使用者唯一識別碼>",
        # 其他必須傳遞的各項字典參數 (依模組而定)
    }
)
```

<!-- ### 資料傳遞與撈取設計原則
為減輕前後端的傳輸負擔，本系統採用 **Agentic Workflow 原則**：
1. **API 傳送極簡化**：API 僅需透過 `user_input` 傳遞必要的辨識 ID（如 `user_id`, `job_id` 等）與短文本問卷。
2. **AI 工具自取化**：長篇幅數據（如完整的履歷文本、大筆的分析歷史、細部職缺描述）統一由各模組的 Agent 於背景「**自主向 Supabase 資料庫撈取**」。 -->

---

## 📌 2. 各模組 API 參數對照與輸出格式 (Schemas)
以下列出每個模組**實際會輸出給前端的完整 JSON 格式與必備 Key**，前端開發者可依照此結構進行串接與呈現。

### 模組 1：職涯分析 (Career Analysis)
負責量化評估能力與分析缺口。系統會依據填寫內容自動分流為「有經驗者」與「無經驗/轉職者」。

* **Task Type (`task_type_str`)**: `"career_analysis"`
* **API 必須傳遞參數 (`user_input` 字典內)**:
  * `user_id` (str, 必填): 使用者 UUID。
  * `survey_json` (str): 職能與經驗問卷填寫結果 (建議將 JSON 轉為字串)。
  * `trait_json` (str): 人格特質測驗結果 (建議將 JSON 轉為字串)。
* **輸出結果範例 (`CareerReport` Dict)**:
  ```json
  {
    "report_metadata": {
      "user_id": "123e4567-e89b-12d3... (str)",
      "timestamp": "2024-05-20T14:30:00.000Z (str)",
      "version": "1.0 (str)"
    },
    "preliminary_summary": {
      "core_insight": "一句話精闢總結使用者的職涯畫像，包含強項與隱憂 (str)"
    },
    "radar_chart": {
      "dimensions": [
        {
          "axis": "前端開發 (str)",
          "score": 3.5
        },
        {
          "axis": "後端開發 (str)",
          "score": 4.0
        }
        // ...總共 6 個維度 (前端開發, 後端開發, 運維部署, AI與數據, 工程品質, 軟實力)
      ]
    },
    "gap_analysis": {
      "current_status": {
        "self_assessment": "資深工程師 (Senior) (str)",
        "actual_level": "中階工程師 (Mid Level) (str)",
        "cognitive_bias": "針對硬實力的認知落差分析與補強建議 (str)"
      },
      "target_position": {
        "role": "後端工程師 (str)",
        "match_score": "75% (str)",
        "gap_description": "針對目標職位的落差分析 (若無經驗者則包含技能轉譯) (str)"
      }
    },
    "action_plan": {
      "short_term": "短期計畫 (1-3個月)，針對最急迫 Gap 的工具或語法 (str)",
      "mid_term": "中期計畫 (3-6個月)，針對專案經驗與進階框架的補強 (str)",
      "long_term": "長期計畫 (6個月以上)，針對架構思維、軟實力或跨領域整合 (str)"
    }
  }
  ```

---

### 模組 2：履歷分析與優化 (Resume Module)
包含「深度診斷」與「重寫優化」雙模組。

#### 2-1. 履歷分析 (Resume Analysis)
* **Task Type (`task_type_str`)**: `"resume_analysis"`
* **API 必須傳遞參數 (`user_input` 字典內)**:
  * `user_id` (str, 必填): 使用者 UUID。
* **輸出結果範例 (`ResumeAnalysis` Dict)**:
  ```json
  {
    "candidate_positioning": "說明企業視角下，這份履歷目前『看起來像什麼角色』 (str)",
    "target_role_gap_summary": "與目標職缺之間的整體落差說明 (str)",
    "overall_strengths": [
      "履歷中目前最具說服力、可保留的優勢點 (str)"
    ],
    "overall_weaknesses": [
      "整體最影響錄取率的核心弱點 (str)"
    ],
    "critical_issues": [
      {
        "section": "履歷區塊名稱，如: 經歷 (str)",
        "original_text": "使用者履歷中的原始文字內容 (str)",
        "issue_type": [
          "問題類型分類，如: 描述模糊 (str)"
        ],
        "severity": [
          "評估的嚴重程度，如: 明顯扣分 (str)"
        ],
        "diagnosis_dimension": "此問題主要影響的企業診斷面向 (str)",
        "issue_reason": "說明為何此問題會降低錄取率 (str)",
        "improvement_direction": [
          "可執行的改善方向 (列點式說明) (str)"
        ]
      }
    ],
    "ats_risk_level": "從 ATS 與第一輪篩選角度評估的整體風險等級 (如: 高) (str)",
    "screening_outcome_prediction": "模擬企業 6–10 秒掃描後，最可能的篩選結果與原因 (str)",
    "recommended_next_actions": [
      "給候選人的下一步行動建議 (str)"
    ]
  }
  ```

#### 2-2. 履歷優化 (Resume Optimization)
* **Task Type (`task_type_str`)**: `"resume_opt"`
* **API 必須傳遞參數 (`user_input` 字典內)**:
  * `user_id` (str, 必填): 使用者 UUID。
* **輸出結果範例 (`ResumeOptimization` Dict)**:
  ```json
  {
    "professional_summary": "精簡的專業總結，需包含核心價值與關鍵字 (str)",
    "core_skills": [
      "技能關鍵字，如 Python (str)",
      "Docker (str)"
    ],
    "professional_experience": [
      "優化後的經歷列表 (以 STAR 原則重新撰寫的 description) (str)"
    ],
    "projects": [
      "優化後的專案描述，強調技術棧與量化成果 (str)"
    ],
    "education": [
      "最高及次高學歷資訊列表 (包含學校、學系、學位與畢業時間) (str)"
    ],
    "autobiography": "保留使用者原本風格的優化後完整自傳 (str)"
  }
  ```

---

### 模組 3：Side Project 推薦 (Project Recommendation)
根據缺口建議具體可行的實作專案。

* **Task Type (`task_type_str`)**: `"project_rec"`
* **API 必須傳遞參數 (`user_input` 字典內)**:
  * `user_id` (str, 必填): 使用者 UUID。
* **輸出結果範例 (`SideProject` Dict)**:
  ```json
  {
    "project_name": "具專業感的專案名稱 (str)",
    "capability_gaps_addressed": [
      "此專案主要補強的能力缺口清單 (str)"
    ],
    "tech_stack": [
      "完整技術棧清單，如 FastAPI, Redis (str)"
    ],
    "project_phases": [
      {
        "phase_name": "階段名稱，如: Phase 1: 核心 API (str)",
        "phase_goal": "此階段的核心目標 (str)",
        "tasks": [
          "此階段需完成的具體任務清單 (str)"
        ],
        "resume_value": "此階段完成後，可直接寫進履歷的一段敘述 (str)"
      }
    ],
    "overall_resume_impact": "整個專案開發完成後，對履歷競爭力的整體提升說明 (str)",
    "difficulty": "難度等級與時程評估，如: 高難度 | 預估 1.5 個月 (str)"
  }
  ```

---

### 模組 4：求職信生成 (Cover Letter)
根據優化後的履歷與職缺描述，產生客製化推薦信。

* **Task Type (`task_type_str`)**: `"cover_letter"`
* **API 必須傳遞參數 (`user_input` 字典內)**:
  * `user_id` (str, 必填): 使用者 UUID。
  * `job_id` (str, 必填): 目標招募職缺 UUID。
  * `optimization_id` (str, 選填): 要選用的「優化後履歷」版本 UUID。
* **輸出結果範例 (`CoverLetter` Dict)**:
  ```json
  {
    "subject": "吸引人且專業的郵件主旨，包含職位名稱與核心賣點 (str)",
    "content": "求職信完整正文，包含問候、價值對標、行動呼籲，不含任何 Markdown 標記 (str)"
  }
  ```

---

## 📌 3. API 回應與例外處理機制

### 成功回應 (Success Response)
引擎執行完畢後，`manager.run_task()` 會統一攔截 Agent 產出的亂碼字串，**保證回傳的必然是 Python `Dict` 結構**（已通過 Pydantic 嚴格轉換）。
呼叫端 (FastAPI Router) 只需直接以 `JSONResponse` 回傳該 Dict 即可。此外，`manager` 也會於背景自動將結果寫入 Supabase 中對應的 Table（依綁定的 `user_id` / `job_id` / `resume_id` 紀錄）。

### 潛在錯誤 (Exceptions)
1. **傳參缺失**: 當 API 呼叫端漏傳了 `user_input` 內的必填欄位 (如 `user_id`, `job_id`)，引擎在方法開頭就會攔截並回覆錯誤字串字典（如 `{"status": "error", "message": "..."}`）。
2. **Database Error**: 若 `user_id` 給錯，導致 Tools 撈不到資料庫裡的舊資料，Agent 可能會因為無法進行比對而產生出劣質幻覺，或直接回傳「找不到該用戶資料」的錯誤訊息字串。
3. **LLM Error**: 若 OpenAI API 遭遇暫時性 Timeout，LangChain/CrewAI 會嘗試 Auto-Retry，若超過次數則會拋出連接例外。
