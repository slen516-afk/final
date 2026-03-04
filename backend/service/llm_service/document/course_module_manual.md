# 課程推薦模組 (Course Module) 說明書

## 1. 模組簡介
本模組位於 `src/features/course`，主要功能為**課程推薦服務**。其核心目標是作為一個**純粹的獨立微服務**，根據使用者近期的職涯分析報告 (Career Analysis Report) 所產出的技術匹配度，找出資料庫中最適合該使用者的學習課程。

本模組**不依賴任何 LLM 或 Multi-Agent 框架**，全憑自建的權重演算法進行分數計算與排序，並輸出標準化的字典結構，可供前端 API 或其他後端服務（包含 Agent 的工具層）無縫調用。

## 2. 模組運作流程

當模組的 `CourseRecommendationService.get_recommendations()` 被呼叫時，會經歷以下 5 個階段的標準化流程：

### 1. 獲取使用者狀態 (Fetch User Gap)
透過傳入的 `user_id`，查詢 Supabase 的 `career_analysis_report` 資料表，取得最新一筆職涯分析紀錄。
*   系統會清理並提取出使用者的「目標職類 (job_category)」與「技術匹配度分數 (match_score)」。

### 2. 能力定位與映射轉換 (Score Mapping)
將使用者 0-100 的 `match_score` 轉換為兩種數值：
*   **使用者等級 (`user_level`)**：映射到 1 到 5 級 (從新手到專家)，用以對應政策權重表。
*   **課程難度座標 (`ability_position`)**：將分數換算為 1.0 到 3.0 的空間座標，精確定位使用者當前的實力落點。

### 3. 獲取候選課程 (Fetch Candidate Courses)
從 Supabase 的 `course` 資料表撈取候選課程清單。此階段會直接利用 SQL 的 `eq("role_name", job_category)` 過濾出與使用者目標職類完全相符的課程。

### 4. 計算推薦與品質分數 (Calculate Scores)
針對剛剛撈取到的每一門候選課程，系統會進行雙重評分：
*   **優先權分數 (Priority Score)**: 根據使用者的能力座標與課程難度層級，計算兩者之間的「距離空間」。距離越近分數越高，並乘上模組內建的「政策權重表 (Policy Distribution)」。這能確保新手不會被推薦極難的課程，而專家則專注於進階挑戰。
*   **品質分數 (Quality Score)**: 根據課程的總評分 (Rating, 佔70%) 與評論數量 (Review Count, 佔30%) 計算出課程的客觀品質。

### 5. 排序與導出 (Ranking & Export)
將所有課程優先依照 **Priority Score** 降冪排序，如果遇到同分的狀況則依照 **Quality Score** 降冪排序。依此選出前 `top_k` (預設為 5) 門最符合且最優質的課程。

## 3. 參數流轉與結構

### 📥 接收的參數 (Input)
模組主要接收兩個參數：
*   **`user_id`** (字串, `str`): 必填，使用者的唯一識別碼。
*   **`top_k`** (整數, `int`): 選填，期望輸出的推薦課程數量，預設值為 `5`。

### 📤 輸出的結構 (Output)
輸出的參數為一個由純字典 (Dictionary) 組成的陣列 (`List[Dict]`)。這完美還原了資料庫的原始樣貌，並新增了演算法計算後的分數評級。

**結構範例**：
```json
[
  {
    "course_id": 50,
    "course_name": "C Programming with Linux",
    "url": "https://www.coursera.org/... ",
    "rating": 4.6,
    "review_count": 436,
    "level": "Beginner",
    "course_type": "Specialization",
    "duration_suggested": "2 months",
    "course_level": 1,
    "priority_score": 0.85,
    "quality_score": 0.7748
  }
]
```

### 🔀 參數被傳去哪裡？
這份乾淨的 `List[Dict]` 結構，具備極高的泛用性：
1.  **FastAPI 回傳**：可直接透過 FastAPI 轉譯為 JSON 格式，回傳給前端渲染出精美的課程推薦卡片。
2.  **Agent 架構轉接**：可以被 `src/agents/tools/` 裡面的 Agent 工具層接手，由他們加工翻譯成 Markdown 後餵給 LLM 閱讀。

## 4. 目錄內的檔案與其關聯

目前 `course` 目錄內的結構非常純粹乾淨，主要由以下兩個檔案組成：

### 1. `course_matching.py` (核心邏輯與服務層)
這是整個模組的心臟。裡面實作了 `CourseRecommendationService` 類別以及各項靜態計算方法（如 `@staticmethod` 的 `score_to_user_level`）。
它負責所有的**資料庫連線、查詢邏輯、權重表定義、以及各種數學演算**，是整個推薦行為的真正執行者。

### 2. `schemas.py` (資料定型與合約層)
實作基於 Pydantic 的資料模型類別（如 `CourseItem`）。
雖然目前的輸出邏輯為了效能與保留所有欄位，選擇直接輸出 `List[Dict]`。但 `schemas.py` 依然是一個非常重要的**型別定型檔 (Contract)**。它向其他開發者或前端團隊明確宣告了這項服務輸出清單中每一包欄位的名稱與型別 (例如 `course_id` 必定是 `int`，`rating` 必定是 `float`)，完美具備現代 API 微服務的架構精神。

*(備註：原本破壞模組獨立性的 `tools.py` 或 `course_tools.py` 已被正式移除並移至外部應用層，所以目前本模組已達到 100% 的隔離度與獨立性。)*
