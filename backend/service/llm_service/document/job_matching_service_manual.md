# `src/features/matching` 職缺推薦服務模組說明書

本模組為職缺推薦服務的核心，負責接收使用者的履歷、能力評估分數與篩選條件，透過 AI 語意檢索與硬實力算法，計算出最合適的推薦職缺，並附上專屬的微顧問分析報告。

## 一、 模組是怎麼運作的？ (核心流程)

`matching` 模組採用「四階段混合檢索漏斗」架構運作，由核心協調者 `service.py` 進行調用：

0. **Phase 0: 獲取最新六維能力報告 (Fetch Latest Profile)**
   系統首先根據 `user_id` 向 Supabase 的 `career_analysis_report` 資料表查詢，並依據 `report_version` (版本號) 降冪排序取得最新的一份雷達圖報告。將其中的中文維度標籤映射轉換為系統標準的 D1~D6 分數 (`user_6d_profile`)，確保後續比對使用最新鮮的資料。

1. **Phase 1: 混合召回 (Qdrant Semantic Recall & Filter)**
   系統透過前端傳來的 `source_type` (履歷來源：`RESUME` 或 `OPTIMIZATION`) 動態決定要查詢的 Qdrant 集合。接著以 `user_id` 與對應的 `document_id` 為精確過濾條件，安全地提取專屬的 1536 維履歷向量。
   結合使用者設定的職缺過濾條件 (`filters`：如地點、薪資) 以及**強制過濾條件 (`is_labeled: true`)**，到 Qdrant 進行混合檢索，初步撈取語意上最相近的 Top 50 個已貼標候選職缺 (語意分數佔 0.3 權重)。然後去 Supabase 補齊這些職缺的完整資訊 (公司、職缺敘述、要求等)。

2. **Phase 2: 精確重排序 (Re-ranking by JobMatcher)**
   取得初步候選名單後，系統利用 Phase 0 取得的「最新六維能力分數」，與「該職缺所需的六維能力要求」，計算歐幾里得距離 (Euclidean Distance)，歸一化為「硬實力契合度」。接著將： `(0.7 * 硬實力契合度) + (0.3 * Qdrant 語意分數)`，計算出最終加權分數，重新排序並取前 10 名 (Top 10)。

3. **Phase 3: AI 顧問分析與 JSON 格式化 (LLM Insight Analysis)**
   針對 Top 10 的職缺，系統開啟 10 個執行緒 (平行運算) 呼叫 `CareerLLMAdvisor`，將使用者能力、職缺要求與匹配分數丟給 OpenAI (gpt-4o-mini)，為每個職缺快速產生一份專屬的洞察報告 (包含推薦原因、優勢、劣勢、面試建議)，最後組合回前端。

---

## 二、 參數資料流：接收什麼？傳去哪？輸出什麼？

### 📥 1. 前端接收參數的結構
由 `schemas.py` 內的 `JobMatchRequest` 管控，系統會從前端接收以下 JSON 結構：
- `user_id` (Integer)：使用者資料庫 ID。
- `document_id` (Integer)：履歷 ID 或 優化履歷 ID (作為精確指定文件的依據)。
- `source_type` (Literal["RESUME", "OPTIMIZATION"])：履歷來源，決定要從原始履歷或優化後履歷進行比對。
- `filters` (Object)：職缺硬篩選條件，包含 `city` (地點)、`salary_min` (最低薪資)。

*(註：`user_6d_profile` 已從前端請求中移除，改由後端從資料庫直接獲取最新版本，確保資料的真實性)*

### 🔄 2. 參數怎麼流動？
- **`user_id`**：進入 `service.py` 後，首先被用來去 Supabase 查詢最新的六維能力分析報告 (Phase 0)。
- **`user_id` + `document_id` + `source_type`**：被傳遞給 `UserProfileRetriever`，用來決定目標 Qdrant 集合 (例如 `resume_vectors` 或 `optimized_resume_vectors`)，並作為嚴格的 Payload 過濾條件，確保只會拿出屬於該使用者的那一份履歷的 1536 維向量。
- **履歷向量 + `filters` (+ `is_labeled`)**：傳遞給 `JobMatchRetriever.search_hybrid_jobs`，告訴 Qdrant 依照這個向量進行目標過濾的相似度比對，並強制排除未貼標的失效殘缺資料。
- **六維分數 (`user_6d_profile`)**：連同從 Supabase 拿回來的職缺六維詳細分數，被送到 `JobMatcher.calculate_dynamic_job_gap` 計算歐幾里得距離以評估能力契合度。
- **最後排序結果**：所有的分數、職缺敘述與使用者的六維分數會一併被送進 `CareerLLMAdvisor.generate_job_insights` 給 GPT 生成個人化點評。

### 📤 3. 輸出回前端的參數結構
由 `schemas.py` 內的 `JobMatchingResponse` 確保格式一致。系統回傳包含狀態與前 10 名推薦列表：
```json

  [
  {
    "job_id": "string",
    "job_title": "string",
    "company_name": "string",
    "industry": "string",
    "full_address": "string",
    "requirements": "string (以 | 分隔的條列式重點)",
    "final_score": "92.5%",
    "source_url": "string",
    "recommendation_reason": "推薦理由說明...",
    "strengths": "候選人優勢...",
    "weaknesses": "缺乏部分...",
    "interview_tips": "具體面試準備建議..."
  }
]

```

---

## 三、 各檔案的關聯與職責說明

此模組實作了關注點分離 (Separation of Concerns)，各個檔案各司其職：

1. **`service.py` (核心協調者)**
   - `CareerMatchingService`，身為服務主體，將其他的 Retriever、Matcher 和 Advisor 串聯起來。它負責處理 Phase 0 從 Supabase 拉取最新 6D 分數，接著用 Qdrant 第一階撈取、再用 Supabase 補職缺細節、接著呼叫 Matcher 算加權總分、最後以 concurrent 並行呼叫 LLM 顧問的整個大流程。

2. **`schemas.py` (資料驗證層)**
   - 包含了一系列基於 Pydantic 的資料模型，提供了前端傳入驗證與回傳型別提示。所有的輸入/輸出標準都在這個檔案被決定。

3. **`qdrant_retriever.py` (向量資料庫檢索層)**
   - 包含 `JobMatchRetriever` 與 `UserProfileRetriever`，主要負責實作向 Qdrant 的連線與查詢語法轉換。
   - `JobMatchRetriever`：將前端自定義的條件 (如薪水、城市) 轉換為 Qdrant 原生的 Filter，並強制加上 `is_labeled=True` 以確保演算法精準度，讀出相應的職缺向量與相似度分數。
   - `UserProfileRetriever`：實作了動態路由，根據 `source_type` 決定要去哪一個向量集合提取履歷向量，並加上嚴格的安全校驗 (同時驗證 `user_id` 與 文件 ID)。

4. **`matcher.py` (演算與排名層)**
   - 負責處理數學、邏輯運算以及原始資料轉換。
   - `CareerAnalyzer`：可將使用者做過的原始問卷選擇題轉換出 D1~D6 的分數。
   - `JobMatcher` / `JobRanker`：實作核心演算法，計算使用者雷達圖與職缺要求雷達圖的距離 (Euclidean Distance 計算法)，並產生 0.7 vs 0.3 的加權組合。

5. **`advisor.py` (AI 分析生成層)**
   - `CareerLLMAdvisor`，這是專屬的封裝工具，將候選人能力與目標職缺輸入至制定好的 GPT Prompt 當中，利用 LLM 自帶的洞察力產出 JSON 格式的 4 個面向建議，為死板的推薦數字增添人味。

6. **`fetch_filter_jobs.py` (測試指令碼)**
   - 獨立的除錯與測試程式 (`JobFilterTester`)，這個腳本被用來模擬前端下達 `filters` (地點與薪水)，直接針對關聯式資料庫 Supabase (PostgREST) 的搜尋準確度與語法做單元測試。此檔案並非運作流程上的一環。

---