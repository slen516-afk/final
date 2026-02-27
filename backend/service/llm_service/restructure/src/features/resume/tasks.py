from crewai import Task

# ==========================================
# Task 定義與邏輯規則 (單一事實來源)
# ==========================================

# --- 1. 履歷分析任務 ---
ANALYSIS_TASK_DESCRIPTION = """
身為 FAANG 等級的資深招募顧問，你的任務是執行極其嚴苛的「第一輪履歷篩選與風險評估」。
請對輸入的 [使用者問卷]: {survey_json} 與 [使用者履歷]: {resume_json} 進行交叉比對。

你必須模擬企業 HR 僅有 6–10 秒的掃描行為，針對以下維度進行深度診斷：
1. 清楚度（Clarity）：排版邏輯是否讓關鍵資訊（職稱、公司、年資）一眼可見？敘述是否過於冗長？
2. 證據力（Evidence & Metrics）：檢視每一項工作經歷，判斷其是否具備數據支撐。
3. ATS 關鍵字完整度：判斷履歷中的硬實力關鍵字是否能通過自動化篩選系統。
4. 目標一致性：評估目前的經歷敘述，是否足以支撐使用者在問卷中所表達的職涯目標。

執行準則（Strict Rules）：
1. 零推測原則：你只能分析履歷中「白紙黑字」寫出的內容，嚴禁腦補。
2. 風險標註：若有空白期或職涯跨度過大等可能被挑戰的點，必須明確指出。
3. 可執行建議：每一項診斷出的缺點，都必須配對一個具體的「修改動作」。
"""

# --- 2. 履歷優化任務 ---
OPTIMIZATION_TASK_DESCRIPTION = """
你現在是一位資深履歷策略顧問。
你的目標是將 [原始履歷內容]: {resume_json} 根據 [履歷診斷分析結果]: {analysis_result} 進行優化。

執行步驟如下：
1. 風格建模：首先分析原履歷的語氣，定義其寫作風格輪廓。
2. 微調優化：在不改變原本敘事順序與語氣的前提下，進行「補清楚、補具體、補專業」的微調。
3. STAR 化處理：將工作經歷轉化為自然且不生硬的 STAR 原則敘述。
4. 專業轉化：將口語化的描述轉化為符合科技業文化的專業術語，但避免 AI 產出的制式模板（Cliché）。

執行準則（Strict Rules）：
1. 嚴格維持原有的句型結構（偏敘事則維持敘事，偏條列則維持條列）。
2. 嚴禁新增任何原履歷中不存在的技能、證照或專案經驗。
"""

def create_analysis_task(agent) -> Task:
    """建立履歷分析任務"""
    return Task(
        description=ANALYSIS_TASK_DESCRIPTION,
        expected_output="一份純文字的診斷分析報告備忘錄，包含【清楚度、證據力、關鍵字、一致性】分析與風險警示。",
        agent=agent
    )

def create_optimization_task(agent) -> Task:
    """建立履歷優化任務"""
    return Task(
        description=OPTIMIZATION_TASK_DESCRIPTION,
        expected_output="優化後的完整履歷全文與風格定義。",
        agent=agent
    )
