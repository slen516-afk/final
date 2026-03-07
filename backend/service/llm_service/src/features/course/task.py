from crewai import Task
from crewai import Agent

def get_diagnostic_analysis_task(agent: Agent) -> Task:
    """
    診斷痛點與給予戰略大方向的任務
    """
    return Task(
        description="""
        針對目標職位：【{role}】，以及目前的媒合度：【{match_score}%】進行深度分析：
        1. 識別核心痛點：在這個媒合分數下，使用者最可能缺乏的關鍵硬實力或架構觀念是什麼？
        2. 定義戰略大方向：給予一個 500 字以內的晉升戰略，說明應優先鞏固地基還是直接衝擊高階技術。
        3. 設定期望：描述完成這套學習後，使用者在職場上的競爭地位將會如何改變。
        """,
        expected_output="一份包含技能缺口診斷、戰略方向建議與競爭力提升預測的戰略報告。",
        agent=agent
    )

def get_roadmap_design_task(agent: Agent, context_tasks: list) -> Task:
    """
    路徑設計任務
    """
    return Task(
        description="""
        參考『戰略分析師』的診斷報告，針對從演算法精準挑選出來的以下課程清單進行專業編排：{courses}。
        你的目標是產出最終的學習路線圖，必須包含:
        1. 邏輯排序：根據知識依賴性 (Pre-requisites) 決定修課順序，分配課程 priority_order。
        2. 承接原因：設定 strategic_reason，詳細解釋為什麼 A 課程必須在 B 課程之前。
        3. 能力里程碑：定義明確的技術階段點，讓使用者知道自己學到什麼程度時已達成階段性突破。
        """,
        expected_output="完整的學習路線圖，需包含大方向建議、排序後的課程詳情與里程碑。",
        agent=agent,
        context=context_tasks
    )
