from typing import List, Optional
from pydantic import BaseModel, Field

# ==========================================
# 差距分析報告基礎元件
# ==========================================

# 定義標準的六大維度名稱
ALLOWED_AXES = [
    "前端開發", "後端開發", "運維部署", 
    "AI與數據", "工程品質", "軟實力"
]

# 定義標準職涯階段清單 (與 Q16 選項一致)
STANDARD_CAREER_STAGES = [
    "轉職中/學習中 (Entry Level)",
    "初階工程師 (Junior)",
    "中階工程師 (Mid Level)",
    "資深工程師 (Senior)",
    "技術主管/架構師 (Lead architect)"
]

# 定義標準職稱清單 (讓 LLM 參考)
STANDARD_ROLES = [
    "前端工程師", "後端工程師", "全端工程師", 
    "資料科學家/數據分析師", "AI 工程師", "DevOps/SRE 工程師"
]

# ★ 新增：定義 Metadata 的嚴格結構
class ReportMetadata(BaseModel):
    user_id: str = Field(description="使用者 ID (需與輸入資料一致)")
    timestamp: str = Field(description="報告生成當下的 ISO 8601 時間戳記 (包含毫秒與時區 Z)")
    version: str = Field(description="動態生成的報告版本號，反映該使用者的報告計數 (例如: 1.0, 2.0)")

class RadarDimension(BaseModel):
    axis: str = Field(description=f"維度名稱，必須嚴格從此清單選取: {ALLOWED_AXES}")
    score: float = Field(description="分數 (0.5 - 5.0)。無經驗者技術維度預設為 0.5。")

class RadarChart(BaseModel):
    dimensions: List[RadarDimension] = Field(description="雷達圖的六個維度數據")

# ==========================================
# 狀態分析元件
# ==========================================
class CurrentStatus(BaseModel):
    self_assessment: str = Field(description= f"使用者問卷自評的職涯階段。必須嚴格從此清單完全複製：{STANDARD_CAREER_STAGES}，不可簡寫")
    actual_level: str = Field(description= f"系統根據 D1-D6 分數評估的實際職級 必須嚴格從此清單完全複製：{STANDARD_CAREER_STAGES}，不可簡寫")
    cognitive_bias: str = Field(description="針對『硬實力』的認知落差分析與補強建議。請具體對比使用者的『自評職級』與『實際 D1-D6 技術分數』。指出落差在哪裡(例如：自評 Senior 但缺乏雲端維運經驗)，並提供具體該學什麼框架或工具的補強建議。字數約 100 字。")

class TargetPosition(BaseModel):
    role: str = Field(description=f"""
    使用者的目標職位名稱。
    1. **格式強制 (MANDATORY)**：
        - 若使用者有指定目標：直接填寫職位名稱 (如 '後端工程師')。
        - 若使用者未指定目標 (系統推薦)：**必須**使用格式 "領航員分析您適合的職類為 - [職位名稱]"。
        - **嚴禁** 只輸出職位名稱 (如 "後端工程師")，否則會被視為錯誤。

    2. **標準化命名**：
        - [職位名稱] 必須嚴格從此清單選取：{STANDARD_ROLES}。
        - 不可以使用 "後端軟體工程師" (多了軟體二字) 或 "Backend Engineer" (英文)。
    """)
    match_score: str = Field(description="目標職位與目前能力的匹配百分比 (如 '75%')")
    gap_description: str = Field(description="""
        針對目標職位的落差分析。
        - 有經驗者：具體說明技術缺口 (如缺 K8s)。
        - 無經驗者：**必須在此處整合『技能轉譯』**。解釋使用者的舊經驗 (如 Excel) 如何對應到新職位 (如 SQL)，並說明雖然目前技術分低 (0.5)，但具備哪些遷移潛力。
        """)

class GapAnalysis(BaseModel):
    current_status: CurrentStatus
    target_position: TargetPosition
    # ★ 關鍵修改：新增 Optional 欄位給無經驗者

# ==========================================
# 行動計畫元件
# ==========================================

class ActionPlan(BaseModel):
    short_term: str = Field(description="短期計畫 (1-3個月)：針對最急迫的 Gap，提及具體工具或語法")
    mid_term: str = Field(description="中期計畫 (3-6個月)：針對專案經驗與進階框架的補強") # [新增]
    long_term: str = Field(description="長期計畫 (6個月以上)：針對架構思維、軟實力或跨領域整合")

class PreliminarySummary(BaseModel):
    core_insight: str = Field(description="一句話精闢總結使用者的職涯畫像，包含強項與隱憂")

# 最終輸出的完整報告結構
class CareerReport(BaseModel):
    report_metadata: ReportMetadata = Field(description="報告的元數據")
    preliminary_summary: PreliminarySummary
    radar_chart: RadarChart
    gap_analysis: GapAnalysis
    action_plan: ActionPlan