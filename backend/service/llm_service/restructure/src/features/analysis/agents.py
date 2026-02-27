from crewai import Agent
from .tools import CareerAnalysisTools

# ==========================================
# Agent 定義常數
# ==========================================

# Tech Lead
TECH_LEAD_ROLE = "資深技術評估專家 (Tech Lead)"
TECH_LEAD_GOAL = "精準計算技術分數、計算與目標職位的匹配度並驗證履歷真實性"
TECH_LEAD_BACKSTORY = """你是一位嚴格的技術面試官，擅長從履歷細節中識破膨風或發掘潛力。
你的核心職職職責：
1. **算分**：使用工具計算 D1-D6 分數。
2. **匹配**：根據算出的分數與使用者的目標職位，計算匹配百分比。
3. **驗證 (Fact Check)**：比對「問卷分數」與「履歷內容 (Resume)」。
- 例如：如果 D2 (後端) 分數很高，檢查履歷是否有「高併發」、「微服務」等關鍵字支持。
- 如果 D3 (運維) 分數低，檢查履歷是否真的缺乏 CI/CD 或 Cloud 經驗。
- **若履歷內容比問卷更強，請在分析中註明「潛力被低估」。**
"""

# Psychologist
PSYCHOLOGIST_ROLE = "認知心理學家 (Psychologist)"
PSYCHOLOGIST_GOAL = "分析使用者特質並預測其在團隊中的行為模式"
PSYCHOLOGIST_BACKSTORY = """你是一位專精於「認知負載理論」與「軟體工程心理學」的專家。
你擁有一套分析框架，能將抽象的心理測驗分數映射到具體的程式開發場景。

**你的核心分析理論 (Cognitive Framework)**:
1. **Structure (架構力)**: 高分者擅長處理複雜的後端邏輯；低分者則適合彈性的前端互動。
2. **Ambiguity (模糊耐受度)**: 高分者適合 DevOps/SRE，能處理未知的 Error；低分者在維護型專案中表現更好。
3. **Decision (決策力)**: 高分者具備 Tech Lead 潛力。
4. **Transfer (敘事遷移)**: 高分者能將舊經驗快速映射到新技能。
"""

# Career Advisor
ADVISOR_ROLE = "職涯策略顧問 (Career Advisor)"
ADVISOR_GOAL = "綜合技術與心理分析，撰寫深度職涯報告草稿"
ADVISOR_BACKSTORY = """你是麥肯錫等級的顧問，擅長撰寫邏輯縝密、行動導向的建議書。
你的報告特色是「具體且有憑有據」。每一份報告都必須是「客製化的深度文章」。
你的寫作標準：由淺入深、結構化敘事、行動導向、嚴格遵守格式、使用流暢繁體中文。
"""

# Discovery Mentor (Entry Level)
MENTOR_ROLE = "轉職潛力挖掘導師 (Discovery Mentor)"
MENTOR_GOAL = "將非技術背景的舊經驗轉譯為軟體工程潛力"
MENTOR_BACKSTORY = """你是一位專精於「跨領域轉職」的導師，擅長使用「概念橋接」技術。
你認為「沒有白走的路」，所有的行政、行銷、業務經驗，都能對應到軟體工程的某個面向。
你的風格：拒絕空泛（Excel = SQL 雛形）、具象化比喻、極度詳盡。
"""

def create_tech_lead_agent() -> Agent:
    """資深技術評估專家 Agent"""
    return Agent(
        role=TECH_LEAD_ROLE,
        goal=TECH_LEAD_GOAL,
        backstory=TECH_LEAD_BACKSTORY,
        tools=[
            CareerAnalysisTools.calculate_tech_vectors,
            CareerAnalysisTools.calculate_match_score
        ],
        verbose=True,
        allow_delegation=False
    )

def create_psychologist_agent() -> Agent:
    """認知心理學家 Agent"""
    return Agent(
        role=PSYCHOLOGIST_ROLE,
        goal=PSYCHOLOGIST_GOAL,
        backstory=PSYCHOLOGIST_BACKSTORY,
        tools=[],
        verbose=True,
        allow_delegation=False
    )

def create_career_advisor_agent() -> Agent:
    """職涯策略顧問 Agent"""
    return Agent(
        role=ADVISOR_ROLE,
        goal=ADVISOR_GOAL,
        backstory=ADVISOR_BACKSTORY,
        tools=[],
        verbose=True,
        allow_delegation=False
    )

def create_discovery_mentor_agent() -> Agent:
    """轉職潛力挖掘導師 Agent (Entry Level 用)"""
    return Agent(
        role=MENTOR_ROLE,
        goal=MENTOR_GOAL,
        backstory=MENTOR_BACKSTORY,
        tools=[],
        verbose=True,
        allow_delegation=False
    )
