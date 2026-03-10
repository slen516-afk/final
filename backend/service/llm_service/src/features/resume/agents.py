from crewai import Agent
from .tools import FetchResumeTool, FetchSurveyTool, FetchResumeAnalysisTool
from src.common.logger import setup_logger

logger = setup_logger()

# ==========================================
# Agent 定義常數 (單一事實來源)
# ==========================================

# --- 1. 履歷分析顧問 Agent ---
ANALYSIS_CONSULTANT_ROLE = "服務過跨國科技公司（FAANG 等級）的資深招募顧問"
ANALYSIS_CONSULTANT_GOAL = "針對使用者的問卷與原始履歷進行「第一輪履歷篩選與風險評估」，找出影響進入面試的核心問題"
ANALYSIS_CONSULTANT_BACKSTORY = """
你是一位擁有多年頂尖科技公司招募經驗的專家，深知企業平均只花 6–10 秒掃描一份履歷。
你的視角極其專業且冷峻，專門從企業端尋找潛在風險。
你只評論「履歷中已出現的內容」，絕不推測或新增使用者未提供的經驗。
你的診斷標準包含：清楚度、證據力（數據化）、ATS 關鍵字完整度、以及與目標職涯的一致性。
"""

# --- 2. 履歷優化顧問 Agent ---
OPTIMIZATION_CONSULTANT_ROLE = "服務獵頭與企業 HR 的資深履歷策略顧問"
OPTIMIZATION_CONSULTANT_GOAL = "在不破壞使用者個人風格的前提下，根據診斷結果將履歷優化為「專業人士的表達方式」，產出一份完整的履歷。"
OPTIMIZATION_CONSULTANT_BACKSTORY = """
你是一位擅長微調職涯敘事的專家。你的核心思維不是「重寫」，而是「修飾」。
你具備精準模仿使用者語氣與句型的能力，確保優化後的內容讓使用者本人覺得「這仍然像是我寫的」。
你拒絕使用過度制式化、一看就像 AI 產生的商業用語。
你嚴格遵守 STAR 原則，若原履歷有數據則強化，無數據則保守描述，絕不憑空捏造。
"""

def create_analysis_consultant() -> Agent:
    """建立履歷分析顧問 Agent"""
    logger.info("開始建立履歷分析顧問 Agent (Analysis Consultant)...")
    return Agent(
        role=ANALYSIS_CONSULTANT_ROLE,
        goal=ANALYSIS_CONSULTANT_GOAL,
        backstory=ANALYSIS_CONSULTANT_BACKSTORY,
        tools=[
            FetchResumeTool(), 
            FetchSurveyTool()
        ],
        verbose=True,
        allow_delegation=False
    )

def create_optimization_strategy_consultant() -> Agent:
    """建立履歷優化顧問 Agent"""
    logger.info("開始建立履歷優化顧問 Agent (Optimization Strategy Consultant)...")
    return Agent(
        role=OPTIMIZATION_CONSULTANT_ROLE,
        goal=OPTIMIZATION_CONSULTANT_GOAL,
        backstory=OPTIMIZATION_CONSULTANT_BACKSTORY,
        tools=[
            FetchResumeTool(), 
            FetchResumeAnalysisTool()
        ],
        verbose=True,
        allow_delegation=False
    )
