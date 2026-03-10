from crewai import Task
from .schemas import SideProject
from src.common.logger import setup_logger
from src.common.crewai_callbacks import task_audit_callback

logger = setup_logger()

def get_project_design_task(agent, tools: list = None) -> Task:
    logger.info("開始生成專案設計任務 (Project Design Task)...")
    return Task(
        description="""
        身為職涯專案架構師，請先使用 FetchUserGapAnalysis 工具，傳入使用者 ID：{user_id} 以獲取缺口分析資料。
        接著根據取得之 [能力缺口分析結果]，設計一個具備「職場可解釋性」的實戰專案。
        
        這個專案不是為了學習，而是為了**「在履歷上證明能力」**。設計邏輯必須符合以下規則：
        1. **MVP（最小可行性）起步**：從最核心、最能證明該缺口能力的基礎功能開始。
        2. **多階段擴充（Phase-based）**：專案必須拆解為 4 個階段。每個階段必須明確定義：
           a. 階段目標：要向面試官證明哪項特定能力？
           b. 實作任務：具體要做哪些開發或分析動作？
           c. 履歷價值（Resume Value）：此階段完成後，如何用專業語言將其寫入履歷中。
        3. **技術棧對齊**：使用的技術必須是該職位主流且使用者可上手的。
        4. **語言限制**：所有產出的文字內容都必須使用「台灣繁體中文 (Traditional Chinese)」撰寫。
        
        執行準則（Strict Rules）：
        1. 避開所有「教學型、練習型」的常見專案（如：To-do List, Weather App 等）。
        2. 專案必須具備真實世界的商業邏輯，讓面試官有興趣追問細節。
        """,
        expected_output="一份包含專案名稱、技術棧與階段劃分的詳細專案計畫書草案，且必須為台灣繁體中文。",
        agent=agent,
        tools=tools or [],
        callback=task_audit_callback
    )

def get_project_refinement_task(agent, context_tasks, tools: list = None) -> Task:
    logger.info("開始生成專案審核與優化任務 (Project Refinement Task)...")
    return Task(
        description="""
        審核上一個任務產出的專案計畫書。
        你的目標是：
        1. **強化履歷價值**：確保每一 Phase 的 Resume Value 描述都足夠具備競爭力，使用 STAR 原則與專業術語。
        2. **難度校準**：檢查專案整體難度是否適中，技術棧是否齊全。
        3. **格式化輸出**：確保最終產出符合 SideProject 的 Pydantic 模型。
        4. **語言限制**：所有生成的內容（包含專案名稱、目標、任務與履歷價值）都必須使用「台灣繁體中文 (Traditional Chinese)」撰寫。
        """,
        expected_output="最終審核通過的 Side Project 計畫 JSON 報告，且必須為台灣繁體中文。",
        agent=agent,
        context=context_tasks,
        tools=tools or [],
        callback=task_audit_callback
    )
