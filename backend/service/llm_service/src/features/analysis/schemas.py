from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator

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
    role: Literal[
        "前端工程師", "後端工程師", "全端工程師", 
        "資料科學家/數據分析師", "AI 工程師", "DevOps/SRE 工程師"
    ] = Field(description=f"""
    使用者的目標職位名稱，必須與使用者[問卷資料] "q17_target_role" 一致，並正確轉換為{STANDARD_ROLES}清單中的字串。
    1. **標準化命名**：
        - [職位名稱] 必須嚴格從此清單選取：{STANDARD_ROLES}。
        - 不可以使用 "後端軟體工程師" (多了軟體二字) 或 "Backend Engineer" (英文)。
        - [CRITICAL] **注意：若職位名稱包含斜線 / (例如『資料科學家/數據分析師』)，請務必完整複製整個字串，絕對不可擅自拆分或縮寫。**
    """)
    match_score: str = Field(description="目標職位與目前能力的匹配百分比 (如 '75%')")
    gap_description: str = Field(description="""
        針對目標職位的深度落差分析，請務必使用以下結構輸出：
        【優勢 (Strengths)】：既有技術/軟實力中能直接對應目標職位的能力。
        【劣勢 (Weaknesses)】：技術斷層或相關經驗不足之處。
        【機會 (Opportunities)】：目標職位目前的市場缺口可以如何發揮使用者潛力。
        【威脅 (Threats)】：該職位的競爭情況或技術快速迭代帶來的外部風險。
        【核心落差 (Gap)】：具體指出缺漏的技術棧（如缺乏 K8s、高併發經驗）或需轉譯的舊經驗。
        """)
    
    @field_validator('role', mode='before')
    @classmethod
    def correct_role_name(cls, v: str) -> str:
        if not isinstance(v, str):
            return v
            
        # 移除前後空白
        v = v.strip()
        
        # 針對常見的縮寫進行防呆映射
        mapping = {
            "前端": "前端工程師",
            "後端": "後端工程師",
            "全端": "全端工程師",
            "資料科學家": "資料科學家/數據分析師",
            "數據分析師": "資料科學家/數據分析師",
            "AI工程師": "AI 工程師",
            "AI": "AI 工程師",
            "DevOps": "DevOps/SRE 工程師",
            "SRE": "DevOps/SRE 工程師",
            "SRE工程師": "DevOps/SRE 工程師",
            "DevOps工程師": "DevOps/SRE 工程師"
        }
        
        if v in mapping:
            return mapping[v]
            
        return v

class GapAnalysis(BaseModel):
    current_status: CurrentStatus
    target_position: TargetPosition
    # ★ 關鍵修改：新增 Optional 欄位給無經驗者

# ==========================================
# 行動計畫元件
# ==========================================

class ActionPlan(BaseModel):
    short_term: str = Field(description="短期計畫 (1-3個月)：針對最急迫的破口。必須包含具體的學習主題、推薦工具(如指定閱讀某技術文件或學習某特定語言)與預期達成的專案里程碑。")
    mid_term: str = Field(description="中期計畫 (3-6個月)：針對專案經驗與進階框架的補強。指出該如何累積作品集或工作上的實作方向。") 
    long_term: str = Field(description="長期計畫 (6個月以上)：針對架構思維、產業領域知識 (Domain Knowledge) 或跨領域整合的長遠職涯發展建議。")

class PreliminarySummary(BaseModel):
    core_insight: str = Field(description="""
        高階職涯顧問的深度洞察（總文字約 150-200 字）。
        請務必嚴格使用以下結構進行雙段落輸出，並且絕對要包含這兩個標籤：
        
        【產業洞察】：簡單描繪目標職位的市場趨勢與技術演進。
        【個人總結】：精闢點出使用者的核心潛力與潛在隱憂。
    """)

# 最終輸出的完整報告結構
class CareerReport(BaseModel):
    report_metadata: ReportMetadata = Field(description="報告的元數據")
    preliminary_summary: PreliminarySummary
    radar_chart: RadarChart
    gap_analysis: GapAnalysis
    action_plan: ActionPlan