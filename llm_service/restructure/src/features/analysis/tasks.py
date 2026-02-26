from crewai import Task

# ==========================================
# Task 描述與規則常數
# ==========================================

STANDARD_ROLES_STR = "前端工程師, 後端工程師, 全端工程師, 資料科學家, AI 工程師, DevOps/SRE 工程師"

MAPPING_INSTRUCTION = """
**Radar Chart Mapping Rules (Strictly Follow)**:
請將工具計算出的 D1-D6 分數映射為以下中文名稱：
- D1 -> "前端開發"
- D2 -> "後端開發"
- D3 -> "運維部署"
- D4 -> "AI與數據"
- D5 -> "工程品質"
- D6 -> "軟實力"

注意：
- 如果輸入資料是 Entry Level (無經驗)，Technical dimensions (前四項) 請直接使用 0.5。
- 請確保 `radar_chart.dimensions` 陣列中剛好包含這 6 個項目，順序不拘。
"""

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
[問卷資料]: {survey_json}
[履歷資料]: {resume_json}
請依序執行：
1. 使用「問卷資料」呼叫工具計算 D1-D6 技術分數。
2. 根據算出的 D1-D6 分數與問卷中的目標職位 (target_role)，呼叫工具計算『匹配分數 (Match Score)』。
3. 對比「履歷資料」內容進行真實性驗證，若履歷證據與問卷分數不符，請註明落差。"""

TRAIT_ANALYSIS_DESCRIPTION = """分析人格特質。
資料: {trait_json}
根據使用者的分數，對照「認知分析理論」，評估其職位適配性。"""

FINAL_REPORT_DESCRIPTION = f"""綜合技術與心理分析，生成最終的 CareerReport JSON。
{MAPPING_INSTRUCTION}
{CAREER_STAGE_MAPPING}

**寫作重點**:
1. 結合特質分析。
2. 針對「硬實力」落差提供補強建議。
3. Gap Analysis 中必須點出具體技術缺口 (如 K8s)。
4. 行動計畫應包含具體工具與實作建議。
"""

ENTRY_LEVEL_TRANSITION_DESCRIPTION = f"""分析履歷中的非技術經驗，進行『技能轉譯』。
資料: {{resume_json}}

**核心任務**：
1. **Skill Translation (技能轉譯)**: 找出至少 3 個具體行為並對照程式概念。
2. **Role Recommendation (職位推薦)**: 從標準清單中推薦職位並說明理由。標準清單：[{STANDARD_ROLES_STR}]。
"""

ENTRY_LEVEL_FINAL_DESCRIPTION = f"""根據轉譯結果與特質，推薦職位並規劃學習路徑。
{MAPPING_INSTRUCTION}
{CAREER_STAGE_MAPPING}

**寫作風格**:
1. Preliminary Summary: 100 字左右，結合特質與潛力。
2. Gap Analysis: **必須完整擴寫『技能轉譯』內容**。
3. Action Plan: 具體的工具 (Python, SQL) 與實作建議。
4. Target Role: 必須符合格式 "領航員分析您適合的職類為 - [職位名稱]"。
"""

def create_tech_verification_task(agent) -> Task:
    """建立技術驗證任務"""
    return Task(
        description=TECH_VERIFICATION_DESCRIPTION,
        expected_output="技術評估備忘錄 (包含 D1-D6 分數與驗證結果)",
        agent=agent
    )

def create_trait_analysis_task(agent) -> Task:
    """建立人格特質分析任務"""
    return Task(
        description=TRAIT_ANALYSIS_DESCRIPTION,
        expected_output="一份關於使用者學習潛力與認知特質的分析報告。",
        agent=agent
    )

def create_final_report_task(agent) -> Task:
    """建立最終綜合報告任務 (Experienced 用)"""
    return Task(
        description=FINAL_REPORT_DESCRIPTION,
        expected_output="CareerReport JSON",
        agent=agent
    )

def create_discovery_mentor_task(agent) -> Task:
    """建立技能轉譯任務 (Entry Level 用)"""
    return Task(
        description=ENTRY_LEVEL_TRANSITION_DESCRIPTION,
        expected_output="一份包含『技能轉譯對照表』與『職位推薦理由』的詳細備忘錄。",
        agent=agent
    )

def create_entry_level_final_task(agent) -> Task:
    """建立最終綜合報告任務 (Entry Level 用)"""
    return Task(
        description=ENTRY_LEVEL_FINAL_DESCRIPTION,
        expected_output="轉職建議 CareerReport JSON",
        agent=agent
    )
