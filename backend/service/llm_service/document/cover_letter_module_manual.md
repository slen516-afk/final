# AIPE02_01_Project_re 專案 - 求職信模組 (Cover Letter Module) 說明書

## 1. 模組架構概要
本專案的 `cover_letter` 模組依附於 `CrewAI` 的架構之上，並統一由 `CareerAgentManager` (Facade) 接收外部命令。主要提供一項核心服務：
1. **客製化求職信生成 (Cover Letter Generation)**
   
其邏輯為：使用者選擇用「原始履歷」或 「優化過的履歷」，與系統推薦的「目標職缺 (Job Posting)」進行深度對標，並自動撰寫出一封高點擊率、符合招募方痛點的求職信。

---

## 2. 模組觸發與入口點 (Entry Point)
該模組並無獨立的執行腳本或 API Router，統一由 `src/core/agent_engine/manager.py` 處理。

- **核心入口**：`CareerAgentManager.run_task()`
- **觸發方式**：在需要生成求職信時，呼叫上述 Manager 方法。內部引擎會尋找 `src/core/agent_engine/config.py` 中的配置，並最終導向 `src/features/cover_letter/prompts.py` 來獲取 Agent 執行藍圖。

---

## 3. 輸入參數 (Input Parameters)
當外部 API 或前台需要觸發此服務時，需要往 `manager.run_task` 傳遞以下兩個參數 (task_type_str、user_input)：

```python
manager.run_task(
    task_type_str="cover_letter",                     
    user_input={
        "user_id": "1",      # 目標使用者的 ID
        "job_id": "60",      # 關聯的職缺 UUID 
        "optimization_id": "", # 指定要使用的原始或優化後履歷版本，另一個則為空字串
        "resume_id": "1"       
    }
)
```

### 參數結構與型別剖析
1. **`task_type_str`** (`str`): 固定輸入 `"cover_letter"`，以此來通知引擎載入對應的任務。
2. **`user_input`** (`Dict[str, Any]`): CrewAI 運行時的 Context Variables 字典，必須包含：
   - `user_id`** (`str`): 用戶的唯一識別碼，主要用於最終產出儲存回資料庫時的表單關聯 (Foreign Key)。
   - `job_id` (`str`): 目標職缺的 ID，讓內部工具去資料庫撈職缺說明。
   - `optimization_id` (`str`) 或 `resume_id` (`str`): 傳入優化後履歷的 ID (`optimization_id`) 或是原始履歷的 ID (`resume_id`)，系統會根據傳入的參數決定使用哪一版履歷作為生成依據。兩者均需包含在 user_input 內，即是其中一者沒有使用，也必須帶入空字串""。
   - *(其餘自動注入)*: Manager 執行時依然會自動混入 `current_timestamp` 等防呆資訊。

---

## 4. 資料庫撈取與資料流延展 (Data Fetching & Flow)
Agent 本身不依賴前端傳入動輒幾千字的文本字串，而是利用 Tools 向 Supabase 提取資料。

### 所需資料與獲取工具：
1. **目標職缺資訊** 
   - **工具**: `SearchRecommendJob` (`RecommendJobSearchTool`)
   - **參數**: 透過字典裡的 `{job_id}` 解析。
   - **來源表單**: `job_posting`，從中擷取 `job_id`, `job_title`, `job_description`, `requirements`。
   
2. **使用者履歷資訊 (優化後或原始)**
   - **工具**: `FetchUserOptimizeResume` (`FetchOptimizeResumeTool`) 或 `FetchUserDesignatedResume` (`FetchDesignatedResumeTool`)
   - **參數**: 透過字典裡的 `{optimization_id}` 或 `{resume_id}` 解析。
   - **來源表單**: 若為優化後履歷則抓取 `resume_optimization`，從中擷取 `professional_summary`, `professional_experience`, `core_skills`, `projects`, 基本學歷與自傳；若為原始履歷則抓取 `resume` 表單中的 `structured_data`。

**資料流向**：這幾個 Tools 將 DB 抓出的 JSON 型態轉換為字串 (String) 回傳給 Agent，Agent 隨後會在內部理解職位需求，再從指定的履歷中挑選合適的「證據 (Evidence)」放入生成的信件中。

---

## 5. Agent 與工具運作機制 (Agents & Tools Operations)
此模組建置了 **1 個專屬的 Worker Agent** 與 **1 個全域的 QA Agent** (定義在 Manager 內)。

### 專屬執行者 (Worker Agent)
- **資深獵頭顧問 (Cover Letter Strategist)**
  - 對應 `src/features/cover_letter/agents.py`。
  - **角色定位**：服務外商與大型科技公司的資深獵頭，深知 HR 只關心「你是否理解職位」與「價值對標」。
  - **配備工具**：上述提及的三個 Tools (`SearchRecommendJob`, `FetchUserOptimizeResume`, `FetchUserDesignatedResume`)。
  - **執行邏輯**：
    1. 呼叫工具拿取該 `job_id` 的痛點需求。
    2. 依據傳入的參數，呼叫工具拿取該 `optimization_id` 或 `resume_id` 中最合適的專業經歷。
    3. 找出關聯，生成一封具備「**主旨、問候語、開場動機、對標價值、實績數據、結語與 CTA**」的完整信件。
    4. 嚴格規定：會判斷公司屬性（新創或外商金融）來微調語氣，且嚴禁輸出包含 Markdown 標示的排版。

### QA 把關機制
- 由 Manager 底層的 QA Agent 接手，確認信件是否流暢、沒有出現 AI 幻覺，最後強制按照 Pydantic 模型格式化輸出。

---

## 6. 輸出架構、型別與結果保存 (Outputs & DB Persistence)
### 輸出結構與型別
輸出會嚴格遵守 `src/features/cover_letter/schemas.py` 定義的 Pydantic 模型 (`CoverLetter`)，並由 Manager 回傳為 Dictionary (`Dict[str, Any]`) 給呼叫端：

```json
{
  "subject": "【應徵 後端工程師】具備 5 年微服務架構經驗 - 王大明",
  "content": "親愛的招募團隊您好：...\n\n(這是一封不帶任何 markdown 排版的純文字信件)...\n\n期待有機會與您面談。"
}
```
- `subject` (`str`): 吸睛求職信主旨。
- `content` (`str`): 完整的求職信內文。

### 存入資料庫處理流程 (Automatic Logging to DB)
此模組支援結果**自動儲存**。當 QA 打包好 JSON 之後，Manager 會呼叫 `src/core/agent_engine/result_handlers.py`。

- 由 **`CoverLetterHandler` (推薦信撰寫處理器)** 接手：
  - 取出存在 `user_input` 內的 `user_id` 與 `job_id`。
  - 結合模型生成的 `subject` 與 `content` 組合成 Payload。
  - **動態關聯 ID**：系統會動態檢查 `user_input` 傳入的 `optimization_id` 與 `resume_id` 兩個參數，只有當參數具有實質數值（非空字串或 None）時，才會將其加入 Payload 進行關聯儲存；此舉是為避免將空字串 `""` 送入關聯的欄位，導致資料庫引發型別轉換錯誤（如：`invalid input syntax for type bigint: ""`）。
  - 對 Supabase 的 `cover_letter` 資料表執行 **Insert 操作**。
  - _備註：以此機制，使用者每一次請求不同 `job_id` 的求職信，系統都會以 `user_id` + `job_id` 綁定的形式保留一份備份在資料庫中。_
