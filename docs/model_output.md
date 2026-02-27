<aside>
📌

LLM的輸出結構定義方法基本是基於字典形式{ key : value }

</aside>

## 缺口分析報告

Class name：CareerReport

* ❗格式詳細說明：
  * 輸出之 json 格式範例：
    {
    "report_metadata": {
    "version": "1.0","動態生成的報告版本號，反映該使用者的報告計數 (例如: 1.0, 2.0)")
    "timestamp": "2026-01-31T09:06:40.500648",
    "user_id": "dev_001"
    },
    "preliminary_summary": {
    "core_insight": "具備後端高併發架構優化與工程品質的強項，並熟悉AI與前端框架，但運維部署能力較弱，需補強以達成技術主管/架構師目標。"
    },
    "radar_chart": {
    "dimensions": [
    {
    "axis": "前端開發",
    "score": 3.0
    },
    {
    "axis": "後端開發",
    "score": 4.0
    },
    {
    "axis": "運維部署",
    "score": 2.0
    },
    {
    "axis": "AI與數據",
    "score": 3.0
    },
    {
    "axis": "工程品質",
    "score": 4.0
    },
    {
    "axis": "軟實力",
    "score": 3.5
    }
    ]
    },
    "gap_analysis": {
    "current_status": {
    "self_assessment": "D. 資深工程師 (Senior, 5年以上)",
    "actual_level": "Mid-to-Senior",
    "cognitive_bias": "使用者自評為資深工程師，與系統評估的 Mid-to-Senior 水平相符，顯示自我認知較為準確，無明顯高估或低估。"
    },
    "target_position": {
    "role": "E. 技術主管/架構師(Lead/Architect)",
    "match_score": "65%",
    "gap_description": "目前後端與工程品質表現較佳，但運維部署與軟實力尚有提升空間，尤其在領導力與跨團隊協作能力需加強，才能符合技術主管/架構師的職務要求。"
    }
    },
    "action_plan": {
    "priority_items": [
    {
    "category": "技術提升",
    "action": "加強運維與部署技能，深入學習 Kubernetes 與 CI/CD 流程，提升系統穩定性與自動化能力。",
    "recommendation_type": "實作專案"
    },
    {
    "category": "軟實力",
    "action": "持續深化底層原理研究，並透過技術分享與 Code Audit 強化影響力與技術領導力。",
    "recommendation_type": "課程"
    }
    ],
    "learning_resource_preference": "實作專案做中學，透過實際參與大型架構設計與團隊協作專案，提升技術與領導力。"
    }
    }
  * 說明：
    * 最外層物件: 包含五個主要的鍵(key)。
      * report_metadata (object): 報告的元數據。
        * version, timestamp, user_id 皆為 string。
      * preliminary_summary (object): 初步的核心摘要。
        * core_insight 為 string。
      * radar_chart (object): 雷達圖數據。
        * dimensions 是一個 array，其中每個元素都是一個包含兩個鍵的 object：
          * axis (string): 維度名稱。
          * score (float): 該維度的分數。
      * gap_analysis (object): 使用者現狀與目標的差距分析。
        * current_status (object): 現狀評估。
          * self_assessment, actual_level, cognitive_bias 皆為 string。
        * target_position (object): 目標職位分析。
          * role, match_score, gap_description 皆為 string (請注意 match_score 是帶有 '%'
            的字串，例如 "78%"）。
      * action_plan (object): 基於分析的行動計畫。
        * priority_items 是一個 array，其中每個元素都是一個包含三個鍵的 object：
          * category, action, recommendation_type 皆為 string。
        * learning_resource_preference 為 string。

| 中文       | 英文(key)    | 輸出內容型別(value) | 給AI的prompt描述                             | 結果範例                                                                                                     |
| ---------- | ------------ | ------------------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| 整體結果   | core_insight | str                 | 一句話核心洞察，包含優勢與阻礙年薪突破的關鍵 | 具備資深後端與工程品質能力，且熟悉多種技術棧，但運維部署相對薄弱，需加強領導力與架構設計以達成技術主管目標。 |
| 全端雷達圖 | radar_chart  | dict                |                                              |                                                                                                              |

(包含名稱為 dimension 的 list 包裹各維度的 dict；
維度與分數分別為：str、float) | 維度名稱與分數 | "dimensions": [
{
"axis": "前端開發",
"score": 3.0
},
{
"axis": "後端開發",
"score": 4.0
},
{
"axis": "運維部署",
"score": 2.0
},
{
"axis": "AI與數據",
"score": 3.0
},
{
"axis": "工程品質",
"score": 4.0
},
{
"axis": "軟實力",
"score": 3.5
}
] |
| 自評職級 | self_assessment | str | 使用者自評職級 | 資深工程師 (Senior, 5年以上) |
| 評估職級 | actual_level | str | 使用者自評職級 | Mid-to-Senior Engineer |
| 認知偏差說明 | industry | str | 認知偏差說明 | 使用者自評為資深工程師，但系統評分顯示其技術深度與廣度尚未完全達到資深頂尖水平，尤其在運維部署與軟實力方面存在提升空間，可能高估自身在跨領域整合與 領導能力的成熟度。 |
| 目標職位類型 | role | str | 目標職位名稱 | 技術主管/架構師(Lead/Architect) |
| 匹配度 | match_scor | str | 匹配度百分比 | 65% |
| 落差分析 | gap_description | str | 具體落差描述 | 目前技術能力在後端與工程品質較強，但運維部署與軟實力尚有 不足，且缺乏明確的領導經驗與跨團隊協作實績，需加強系統架構設計、團隊管理與商業價值評估能 力，才能順利轉型為技術主管或架構師。 |
| 行動計畫 | action_plane | (包含名稱為 priority_items 的 list，包裹 dict；
dict 中的內容均為 | 據 Q23 產生的學習資源偏好建議 | 參與或主導跨部門大型系統架構設計專案，強化高併發系統與運維自動化能力 |

## 履歷分析

Class name：ResumeAnalysis

| 中文             | 英文(key)                    | 輸出內容型別(value) | 給AI的prompt描述                                         |
| ---------------- | ---------------------------- | ------------------- | -------------------------------------------------------- |
| 原始履歷的定位   | candidate_positioning        | str                 | 說明企業視角下，這份履歷目前『看起來像什麼角色』         |
| 與目標職缺的落差 | target_role_gap_summary      | str                 | 與目標職位（如後端工程師）之間的整體落差說明             |
| 整體優勢點       | overall_strengths            | List[str]           | 履歷中目前最具說服力、可保留的優勢點                     |
| 整體弱勢點       | overall_weaknesses           | List[str]           | 整體最影響錄取率的核心弱點                               |
| 修正問題清單     | critical_issues              | List[ResumeIssue]   | 需要優先修正的關鍵問題清單（依嚴重度排序）               |
| ATS篩選風險等級  | ats_risk_level               | str                 | 從 ATS 與第一輪篩選角度評估的整體風險等級(如:低/中/高)   |
| 預測快速篩選結果 | screening_outcome_prediction | str                 | 模擬企業 6–10 秒快速掃描後，最可能的篩選結果與原因      |
| 下一步行動建議   | recommended_next_actions     | List[str]           | 不涉及代寫的前提下，給候選人的下一步行動建議，列點式說明 |

Class name：ResumeIssue

| 中文             | 英文(key)             | 輸出內容型別(value) | 給AI的prompt描述                                                                        |
| ---------------- | --------------------- | ------------------- | --------------------------------------------------------------------------------------- |
| 履歷區塊名稱     | section               | str                 | 履歷區塊名稱，如: 簡介、技能專長、專案、經歷、自傳                                      |
| 履歷區塊原文內容 | original_text         | str                 | 使用者履歷中的原始文字內容，僅作為分析依據，不做任何評論說明，禁止修改                  |
| 問題類型         | issue_type            | List[str]           | 問題類型分類（如：描述模糊、缺乏量化證據、ATS 關鍵字缺失、與目標職位不一致）,並詳加說明 |
| 問題程度         | severity              | List[str]           | 從企業篩選視角評估的嚴重程度(如：可優化、明顯扣分、直接刷掉、不修基本不用投),並詳加說明 |
| 企業診斷面向     | diagnosis_dimension   | str                 | 此問題主要影響的企業診斷面向                                                            |
| 問題原因         | issue_reason          | str                 | 站在企業 / HR / ATS 角度，說明為何此問題會降低錄取率                                    |
| 改善方向建議     | improvement_direction | List[str]           | 可執行的改善方向，列點式說明（只說『該補什麼證據或結構』，不代寫內容）                  |

## 履歷優化生成

Class name：ResumeOptimization

| 中文 | 英文(key) | 輸出內容型別(value) | 預設值

| (使用者未提供資料時) | 給AI的prompt描述        |                     |                      |                                                                                                     |
| -------------------- | ----------------------- | ------------------- | -------------------- | --------------------------------------------------------------------------------------------------- |
| 姓名                 | name                    | str                 |                      |                                                                                                     |
| 電話                 | phone                   | str                 |                      |                                                                                                     |
| Email                | email                   | str                 |                      |                                                                                                     |
| LinkedIn             | linkedln                | str                 |                      |                                                                                                     |
| GitHub               | github                  | str                 |                      |                                                                                                     |
| 專業摘要             | professional_summary    | str                 |                      | 精簡的專業總結，需包含核心價值與推薦職缺的關鍵字                                                    |
| 工作經驗             | professional_experience | Optional[List[str]] | default_factory=list | 優化後的經歷列表。每筆包含 company, title, duration, 並以 STAR 原則重新撰寫的 description（條列式） |
| 技能專長             | core_skills             | List[str]           |                      | 從履歷中萃取與推薦職缺相關的技術或軟實力關鍵字6個                                                   |
| 專案作品集           | projects                | Optional[List[str]] | default_factory=list | 優化後的專案描述，強調技術棧與量化成果                                                              |
| 學歷                 | education               | List[str]           |                      | 最高及次高學歷資訊列表，包含學校、學系、學位與畢業時間                                              |
| 自傳                 | autobiography           | str                 |                      | 保留使用者原本風格、敘事順序與用詞習慣前提下的優化後完整自傳                                        |

* 灰底部分為個人資料，內容不應帶入，模型即不會有輸出
* 型別Optional代表若沒有相關資料，藉由default參數帶入預設值空陣列

## Agent(langchain框架才有用到，crewai框架沒有)

Class name：FinalAgentOutput

| 中文 | 英文(key) | 輸出內容型別(value) | 預設值

| (其他工具未被調用時) | 給AI的prompt        |                              |                      |                                                  |
| -------------------- | ------------------- | ---------------------------- | -------------------- | ------------------------------------------------ |
| 推薦職缺             | recommended_jobs    | List[JobItem]                | default_factory=list | 推薦的n個職缺列表                                |
| 履歷分析             | resume_analysis     | Optional[ResumeAnalysis]     | default=None         | 履歷分析的具體內容                               |
| 履歷優化             | resume_optimization | Optional[ResumeOptimization] | default=None         | 履歷優化的具體內容                               |
| 缺口分析             | skill_gap_analysis  |                              |                      |                                                  |
| 推薦 side project    | side_projects       | Optional[SideProject]        | default=None         | 推薦的1個 Side Projects                          |
| 推薦課程             | recommended_courses | List[CourseRecommendation]   | default_factory=list | 推薦的3個學習課程列表                            |
| 求職信生成           | cover_letter        | List[CoverLetter]            | default_factory=list | 依據推薦的不同職缺內容生成不同的客自化求職推薦信 |
