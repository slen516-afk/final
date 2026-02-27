# 專案全功能模組說明手冊 (Project Modules Specification)

本文件整理了專案中所有功能模組的細節，包含 Multi-Agent 系統內的任務以及獨立運行的後端服務。

---

## 1. Multi-Agent 系統功能模組

所有 Multi-Agent 任務均由 `CareerAgentManager` 統一調度，並固定由 **QA Lead Agent** 進行最終格式把關。

### A. 職涯分析模組 (Career Analysis)
*   **任務標籤 (TaskType)**：
    *   `career_analysis_experienced` (有經驗者)
    *   `career_analysis_entry_level` (轉職/新手)
*   **接收參數**：
    *   `survey_json` (str): 職涯問卷 JSON。
    *   `resume_json` (str): 履歷解析後的內容。
    *   `trait_json` (str): 心理測驗結果。
*   **功能描述**：計算 D1-D6 六維技術向量，對比自評與實測的認知落差，並提供轉職技能轉譯建議。
*   **輸出內容**：`CareerReport` JSON（含雷達圖數據、職級評估、行動計畫）。
*   **關鍵 Agent**：Tech Lead (技術驗證), Psychologist (特質分析), Advisor/Mentor (綜合建議)。

### B. 履歷診斷與優化模組 (Resume Module)
*   **任務標籤 (TaskType)**：
    *   `resume_critique`: 履歷深度診斷（找缺點）。
    *   `resume_generation`: 針對目標職位生成優化後的履歷。
*   **接收參數**：
    *   `resume_json` (str): 原始履歷。
    *   `target_job_description` (str): 目標職位的內容（選填）。
*   **功能描述**：找出履歷中描述模糊、缺乏量化數據的缺點，並根據目標職位進行關鍵字補強。
*   **輸出內容**：結構化診斷報告或優化後的 Markdown/JSON 履歷。

### C. 專案推薦模組 (Project Recommendation)
*   **任務標籤 (TaskType)**：`project_rec`
*   **接收參數**：
    *   `career_report_json` (str): 職涯分析報告。
    *   `user_interest` (str): 使用者感興趣的領域。
*   **功能描述**：針對使用者的技術缺口 (Gap)，設計專屬的 Side Project 實作建議，以補足實戰經驗。
*   **輸出內容**：專案計畫書（含技術堆棧、實作時程、預期成果）。

### D. 求職信生成模組 (Cover Letter)
*   **任務標籤 (TaskType)**：`cover_letter`
*   **接收參數**：
    *   `resume_json` (str): 履歷內容。
    *   `job_description` (str): 應徵職位的描述。
*   **功能描述**：結合履歷強項與職位需求，生成具備個人特色且高說服力的求職信。
*   **輸出內容**：多個版本的 Cover Letter（專業版、熱情版等）。

---

## 2. 獨立後端功能模組 (Non-Agent)

這些功能主要由傳統程式邏輯實作，強調精準度與檢索效率。

### E. 職缺匹配與檢索 (Job Matching Service)
*   **接收參數**：`user_id`, `filters` (地點、薪資等)。
*   **功能描述**：
    1.  從資料庫讀取使用者的 D1-D6 分數。
    2.  利用 **Qdrant 向量資料庫** 進行語義檢索。
    3.  使用「混合距離算法」計算使用者與職缺的契合度。
*   **輸出內容**：前 N 個最適合的職缺清單（含匹配百分比）。

### F. 課程推薦系統 (Course Recommendation) - 尚未實裝
*   **接收參數**：`user_id`, `top_k`。
*   **功能描述**：
    1.  計算使用者能力位置 (Ability Position)。
    2.  對應課程難度等級 (Beginner/Intermediate/Advanced)。
    3.  根據「政策權重」過濾不合適的難度，並依品質分數排序。
*   **輸出內容**：推薦學習路徑與課程清單。

---

## 3. 核心 Agent 角色說明

### Manager Agent (總調度員)
*   **角色**：CareerAgentManager。
*   **職責**：
    *   接收 API 傳入的原始資料。
    *   注入 Metadata（時間戳記、版本號）。
    *   根據任務標籤，像「工頭」一樣組裝正確的 Agent 團隊與 Task 鏈結。

### QA Lead Agent (品質監控官)
*   **角色**：固定出現在每個任務的最後一環。
*   **職責**：
    *   **格式檢查**：確保輸出 100% 符合 Pydantic Schemas 定義。
    *   **內容審核**：檢查 Worker Agents 是否產生幻覺或邏輯矛盾。
    *   **語氣校正**：將回覆調整為溫暖、專業的繁體中文。

---

## 4. 模組關聯與資料流 (Summary)

1.  **資料源**：問卷 + 履歷 -> **分析模組** (產出 D1-D6)。
2.  **核心依賴**：分析模組的結果是 **課程推薦**、**職缺匹配** 與 **專案推薦** 的關鍵輸入。
3.  **輔助工具**：**履歷優化** 與 **求職信生成** 則在使用者準備應徵時被調用。
