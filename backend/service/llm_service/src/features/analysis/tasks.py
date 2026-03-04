from crewai import Task

# ==========================================
# Task 描述與規則常數
# ==========================================

STANDARD_ROLES_STR = "前端工程師, 後端工程師, 全端工程師, 資料科學家, AI 工程師, DevOps/SRE 工程師"

# --- 舊版指示 (保留以供切換) ---
# MAPPING_INSTRUCTION = """
# **[CRITICAL] Radar Chart Mapping & Data Integrity Rules (Strictly Follow)**:
# 你正在處理最後的 JSON 生成。雷達圖 `radar_chart.dimensions` 的分數，【必須 100% 精準抄寫】第一階段「技術評估備忘錄」中算出的 D1~D6 分數。
# 絕對不可以自己發明、猜測、或使用心理分析的百分比分數來替代！
# 請嚴格將 D1-D6 映射為以下中文名稱：
# - D1 -> "前端開發"
# - D2 -> "後端開發"
# - D3 -> "運維部署"
# - D4 -> "AI與數據"
# - D5 -> "工程品質"
# - D6 -> "軟實力"

# 注意：
# - 如果輸入資料是 Entry Level (無經驗)，Technical dimensions (前四項) 請直接使用 0.5。
# - 請確保 `radar_chart.dimensions` 陣列中剛好包含這 6 個項目，順序不拘。
# - 請務必去歷史訊息中尋找 `--- RAW_SCORES_START ---` 區塊，並把那六個數字精準地抄寫到 JSON 中。
# """
# --- 舊版邏輯結束 ---

# --- 新版指示 (區分有經驗與無經驗) ---
EXPERIENCED_MAPPING_INSTRUCTION = """
**[CRITICAL] Radar Chart Mapping & Data Integrity Rules (Strictly Follow)**:
你正在處理最後的 JSON 生成。雷達圖 `radar_chart.dimensions` 的分數，【必須 100% 精準抄寫】第一階段「技術評估備忘錄」中算出的 D1~D6 分數。
絕對不可以自己發明、猜測、或使用心理分析的百分比分數來替代！
請嚴格將 D1-D6 映射為以下中文名稱：
- D1 -> "前端開發"
- D2 -> "後端開發"
- D3 -> "運維部署"
- D4 -> "AI與數據"
- D5 -> "工程品質"
- D6 -> "軟實力"

注意：
- 請確保 `radar_chart.dimensions` 陣列中剛好包含這 6 個項目。
- 請務必去歷史訊息中尋找 `--- RAW_SCORES_START ---` 區塊，並把那六個數字精準地抄寫到 JSON 中。
"""

ENTRY_LEVEL_MAPPING_INSTRUCTION = """
**[CRITICAL] Radar Chart Mapping & Data Integrity Rules (Strictly Follow)**:
你正在處理最後的 JSON 生成。
請嚴格將雷達圖 `radar_chart.dimensions` 的項目映射為以下中文名稱：
- D1 -> "前端開發"
- D2 -> "後端開發"
- D3 -> "運維部署"
- D4 -> "AI與數據"
- D5 -> "工程品質"
- D6 -> "軟實力"

注意：
- 因為此用戶為無經驗/轉職者，請將雷達圖分數直接設定為: 前四項 (D1到D4) 為 0.5，D5 與 D6 為 1.0。
- 請嚴格遵守這個數值，不要去尋找歷史算分區塊。
- 請確保 `radar_chart.dimensions` 陣列中剛好包含這 6 個項目。
"""
# --- 新版邏輯結束 ---

CAREER_STAGE_MAPPING = """
**Career Stage Mapping Rules (Strictly Follow)**:
請將問卷的 q16_current_level 以及你評估的實際職級，嚴格轉譯為以下五種標準格式之一：
- entry_level -> "轉職中/學習中 (Entry Level)"
- junior -> "初階工程師 (Junior)"
- mid_level -> "中階工程師 (Mid Level)"
- senior -> "資深工程師 (Senior)"
- lead_architect -> "技術主管/架構師 (Lead Architect)"
"""

TECH_VERIFICATION_DESCRIPTION = """計算技術分數與目標職位匹配度，並驗證履歷真實性。
[使用者 ID]: {user_id}
[問卷資料]: {survey_json}

請依序執行：
1. **獲取履歷**：使用 'Fetch Resume From Database' 工具並傳入 `user_id` 作為參數，獲取使用者最新的履歷資料。
2. **算分**：呼叫 'Calculate Technical Vectors' 工具並傳入 `user_id` 作為參數，計算 D1-D6 技術分數 (系統已自動將問卷資料綁定至工具內)。
3. **匹配**：根據算出的 D1-D6 分數與問卷中的目標職位 (target_role)，呼叫 'Calculate Job Match Score' 工具計算『匹配分數 (Match Score)』。
4. **驗證**：對比「獲取到的履歷資料」內容進行真實性驗證，若履歷證據與問卷分數不符，請註明落差。

**[輸出格式嚴格要求]**
在你的「技術評估備忘錄」最開頭，必須使用以下格式標明你從工具拿到的分數：
--- RAW_SCORES_START ---
D1={D1分}, D2={D2分}, D3={D3分}, D4={D4分}, D5={D5分}, D6={D6分}
--- RAW_SCORES_END ---
再繼續寫你後續的驗證評語。"""

TRAIT_ANALYSIS_DESCRIPTION = """分析人格特質。
資料: {trait_json}
根據使用者的分數，對照「認知分析理論」，評估其職位適配性。"""

# --- 舊版 ---
# FINAL_REPORT_DESCRIPTION = f"""綜合技術與心理分析，生成最終的 CareerReport JSON。
# {MAPPING_INSTRUCTION}
# {CAREER_STAGE_MAPPING}

# **寫作重點**:
# 1. 結合特質分析。
# 2. 針對「硬實力」落差提供補強建議。
# 3. Gap Analysis 中必須點出具體技術缺口 (如 K8s)。
# 4. 行動計畫應包含具體工具與實作建議。
# """

# --- 新版 ---
FINAL_REPORT_DESCRIPTION = f"""綜合技術與心理分析，生成最終的 CareerReport JSON。
{EXPERIENCED_MAPPING_INSTRUCTION}
{CAREER_STAGE_MAPPING}

**寫作重點**:
1. **Core Insight**: 以資深顧問口吻，給出具深度的職涯畫像與診斷。必須先講產業洞察，再論個人。
2. **Industry & SWOT**: 務必分析目標職位的產業趨勢，並採用 SWOT 模型嚴格劃分使用者的優勢、劣勢、機會與威脅。
3. **Gap Analysis**: 必須嚴格按照 SWOT 五大標題輸出，並提出「具體技術缺口」(如缺什麼框架與工具)，不可含糊帶過。
4. **Action Plan**: 短中長期計畫必須「極度具體可執行 (Actionable)」，例如推薦實作專案類型、特定技術框架。
"""

# --- 舊版 ---
# ENTRY_LEVEL_TRANSITION_DESCRIPTION = f"""分析履歷中的非技術經驗，進行『技能轉譯』。
# [使用者 ID]: {{user_id}}

# **核心任務**：
# 1. **獲取履歷**：必須先使用 'Fetch Resume From Database' 工具獲取使用者 {{user_id}} 的最新履歷資料。
# 2. **Skill Translation (技能轉譯)**: 針對獲取到的履歷內容，找出至少 3 個具體行為並對照程式概念。
# 3. **Role Recommendation (職位推薦)**: 從標準清單中推薦職位並說明理由。標準清單：[{STANDARD_ROLES_STR}]。
# """

# --- 新版 ---
ENTRY_LEVEL_TRANSITION_DESCRIPTION = f"""分析履歷中的非技術經驗，進行『技能轉譯』。
[使用者 ID]: {{user_id}}
[問卷資料]: {{survey_json}}

**核心任務**：
1. **獲取履歷**：必須先使用 'Fetch Resume From Database' 工具獲取使用者 {{user_id}} 的最新履歷資料。
2. **Skill Translation (技能轉譯)**: 針對獲取到的履歷內容，找出至少 3 個具體行為並對照程式概念。
3. **Role Alignment (職位對齊)**: 請依照 [問卷資料] 中的目標職位 (target_role)，將上述的技能轉譯結果與該目標職位進行連結與說明。若使用者未指定，請從標準清單 [{STANDARD_ROLES_STR}] 中推薦一個最適合的並說明理由。
"""

# --- 舊版 ---
# ENTRY_LEVEL_FINAL_DESCRIPTION = f"""根據轉譯結果與特質，推薦職位並規劃學習路徑。
# {MAPPING_INSTRUCTION}
# {CAREER_STAGE_MAPPING}

# **寫作風格**:
# 1. Preliminary Summary: 100 字左右，結合特質與潛力。
# 2. Gap Analysis: **必須完整擴寫『技能轉譯』內容**。
# 3. Action Plan: 具體的工具 (Python, SQL) 與實作建議。
# 4. Target Role: 必須符合格式 "領航員分析您適合的職類為 - [職位名稱]"。
# """

# --- 新版 ---
ENTRY_LEVEL_FINAL_DESCRIPTION = f"""根據轉譯結果與特質，推薦職位並規劃學習路徑。
{ENTRY_LEVEL_MAPPING_INSTRUCTION}
{CAREER_STAGE_MAPPING}

**寫作風格**:
1. **Core Insight**: 150 字左右，結合特質與潛力。必須先講產業洞察，再論個人。
2. **Gap Analysis**: **必須完整擴寫『技能轉譯』內容**，且必須嚴格按照 SWOT 五大標題輸出。
3. **Action Plan**: 具體的工具 (Python, SQL) 與實作建議。短中長期計畫必須「極度具體可執行 (Actionable)」。
4. Target Role: 必須符合格式 "領航員分析您適合的職類為 - [職位名稱]"。
"""

def create_tech_verification_task(agent, tools: list = None) -> Task:
    """建立技術驗證任務"""
    return Task(
        description=TECH_VERIFICATION_DESCRIPTION,
        expected_output="技術評估備忘錄 (包含 D1-D6 分數與驗證結果)",
        agent=agent,
        tools=tools or []
    )

def create_trait_analysis_task(agent, tools: list = None) -> Task:
    """建立人格特質分析任務"""
    return Task(
        description=TRAIT_ANALYSIS_DESCRIPTION,
        expected_output="一份關於使用者學習潛力與認知特質的分析報告。",
        agent=agent,
        tools=tools or []
    )

def create_final_report_task(agent, tools: list = None) -> Task:
    """建立最終綜合報告任務 (Experienced 用)"""
    return Task(
        description=FINAL_REPORT_DESCRIPTION,
        expected_output="CareerReport JSON",
        agent=agent,
        tools=tools or []
    )

def create_discovery_mentor_task(agent, tools: list = None) -> Task:
    """建立技能轉譯任務 (Entry Level 用)"""
    return Task(
        description=ENTRY_LEVEL_TRANSITION_DESCRIPTION,
        expected_output="一份包含『技能轉譯對照表』與『職位推薦理由』的詳細備忘錄。",
        agent=agent,
        tools=tools or []
    )

def create_entry_level_final_task(agent, tools: list = None) -> Task:
    """建立最終綜合報告任務 (Entry Level 用)"""
    return Task(
        description=ENTRY_LEVEL_FINAL_DESCRIPTION,
        expected_output="轉職建議 CareerReport JSON",
        agent=agent,
        tools=tools or []
    )
