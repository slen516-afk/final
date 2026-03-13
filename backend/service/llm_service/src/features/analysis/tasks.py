from crewai import Task
from src.common.logger import setup_logger
from src.common.crewai_callbacks import task_audit_callback
from .schemas import STANDARD_ROLES

logger = setup_logger()

# ==========================================
# Task 描述與規則常數
# ==========================================

STANDARD_ROLES_STR = ", ".join(STANDARD_ROLES)

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
- 前四項技術維度 (D1到D4) 請保持為基礎分 0.5。
- D5 與 D6 請務必去歷史訊息中尋找 `--- RAW_SCORES_START ---` 區塊，並把數字精準地抄寫到 JSON 中。
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

【任務執行步驟 (請務必嚴格依序執行並使用對應工具)】：
Step 1. 呼叫 'Calculate Technical Vectors' 工具 (傳入 user_id 作為參數)。
   - 記錄下工具回傳的 D1 到 D6 的確切分數。
   - **注意：無論工具回傳的英文維度為何，請將 D1~D6 視為以下固定維度進行後續驗證與評論：**
     D1: 前端開發、D2: 後端開發、D3: 運維部署、D4: AI與數據、D5: 工程品質、D6: 軟實力。
Step 2. 呼叫 'Calculate Job Match Score' 工具 (傳入 user_id 作為參數)。
   - 記錄下工具回傳的「匹配分數 (Match Score)」。
Step 3. 呼叫 'Fetch Resume From Database' 工具 (傳入 user_id 作為參數) 獲取最新履歷。
Step 4. 驗證 (Fact Check)：對比「履歷內容」與「問卷填寫的分數/經驗」，指出潛力被低估或過度誇大的部分。

**【最終輸出格式強制要求 (CRITICAL)】**
你的回覆「必須」是最終的技術評估備忘錄，且備忘錄的最開頭「必須、絕對」要包含以下精確格式，不可多加任何符號：

--- RAW_SCORES_START ---
D1=[你在Step1拿到的D1分數], D2=[你在Step1拿到的D2分數], D3=[你在Step1拿到的D3分數], D4=[你在Step1拿到的D4分數], D5=[你在Step1拿到的D5分數], D6=[你在Step1拿到的D6分數]
--- RAW_SCORES_END ---

接著在下方撰寫你詳細的技術診斷與職缺匹配分析結果。"""

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
1. **Core Insight**: 以資深顧問口吻，給出具深度、結構化的職涯畫像與診斷。必須嚴格按照【產業洞察】與【個人總結】兩大標題格式輸出，不可將其合併為單一段落散文。
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
4. **潛力維度評分 (Potential Scoring)**: 根據履歷中展現的做事嚴謹度/邏輯性，以及人格特質問卷的分數，評估使用者的【D5 工程品質】與【D6 軟實力】潛力，以 0.5 ~ 5.0 給分（建議轉職者最高不超過 3.5），並在備忘錄結尾獨立寫出：
--- RAW_SCORES_START ---
D1=0.5, D2=0.5, D3=0.5, D4=0.5, D5=[你評估的D5分數], D6=[你評估的D6分數]
--- RAW_SCORES_END ---
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
1. **Core Insight**: 150 字左右，結合特質與潛力。必須嚴格按照【產業洞察】與【個人總結】兩大標題格式輸出，不可省略標籤。
2. **Gap Analysis**: **必須完整擴寫『技能轉譯』內容**，且必須嚴格按照 SWOT 五大標題輸出。
3. **Action Plan**: 具體的工具 (Python, SQL) 與實作建議。短中長期計畫必須「極度具體可執行 (Actionable)」。
4. Target Role: 必須符合格式 "領航員分析您適合的職類為 - [職位名稱]"。
"""

def create_tech_verification_task(agent, tools: list = None) -> Task:
    """建立技術驗證任務"""
    logger.info("開始生成技術驗證任務 (Tech Verification Task)...")
    return Task(
        description=TECH_VERIFICATION_DESCRIPTION,
        expected_output="技術評估備忘錄 (包含 D1-D6 分數與驗證結果)",
        agent=agent,
        tools=tools or [],
        callback=task_audit_callback
    )

def create_trait_analysis_task(agent, tools: list = None) -> Task:
    """建立人格特質分析任務"""
    logger.info("開始生成人格特質分析任務 (Trait Analysis Task)...")
    return Task(
        description=TRAIT_ANALYSIS_DESCRIPTION,
        expected_output="一份關於使用者學習潛力與認知特質的分析報告。",
        agent=agent,
        tools=tools or [],
        callback=task_audit_callback
    )

def create_final_report_task(agent, tools: list = None) -> Task:
    """建立最終綜合報告任務 (Experienced 用)"""
    logger.info("開始生成最終綜合報告任務 (Final Report Task)...")
    return Task(
        description=FINAL_REPORT_DESCRIPTION,
        expected_output="CareerReport JSON",
        agent=agent,
        tools=tools or [],
        callback=task_audit_callback
    )

def create_discovery_mentor_task(agent, tools: list = None) -> Task:
    """建立技能轉譯任務 (Entry Level 用)"""
    logger.info("開始生成技能轉譯任務 (Discovery Mentor Task)...")
    return Task(
        description=ENTRY_LEVEL_TRANSITION_DESCRIPTION,
        expected_output="一份包含『技能轉譯對照表』與『職位推薦理由』的詳細備忘錄。",
        agent=agent,
        tools=tools or [],
        callback=task_audit_callback
    )

def create_entry_level_final_task(agent, tools: list = None) -> Task:
    """建立最終綜合報告任務 (Entry Level 用)"""
    logger.info("開始生成轉職最終綜合報告任務 (Entry Level Final Task)...")
    return Task(
        description=ENTRY_LEVEL_FINAL_DESCRIPTION,
        expected_output="轉職建議 CareerReport JSON",
        agent=agent,
        tools=tools or [],
        callback=task_audit_callback
    )
