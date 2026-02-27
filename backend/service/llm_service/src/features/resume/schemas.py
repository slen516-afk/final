from pydantic import BaseModel, Field
from typing import List, Optional

# --- 履歷分析相關模型 ---

class ResumeIssue(BaseModel):
    section: str = Field(description="履歷區塊名稱，如: 簡介、技能專長、專案、經歷、自傳")
    original_text: str = Field(description="使用者履歷中的原始文字內容，僅作為分析依據，不做任何評論說明，禁止修改")
    issue_type: List[str] = Field(description="問題類型分類（如：描述模糊、缺乏量化證據、ATS 關鍵字缺失、與目標職位不一致）,並詳加說明")
    severity: List[str] = Field(description="從企業篩選視角評估的嚴重程度(如：可優化、明顯扣分、直接刷掉、不修基本不用投),並詳加說明")
    diagnosis_dimension: str = Field(description="此問題主要影響的企業診斷面向")
    issue_reason: str = Field(description="站在企業 / HR / ATS 角度，說明為何此問題會降低錄取率")
    improvement_direction: List[str] = Field(description="可執行的改善方向，列點式說明（只說『該補什麼證據或結構』，不代寫內容）")

class ResumeAnalysis(BaseModel):
    candidate_positioning: str = Field(description="說明企業視角下，這份履歷目前『看起來像什麼角色』")
    target_role_gap_summary: str = Field(description="與目標職位（如後端工程師）之間的整體落差說明")
    overall_strengths: List[str] = Field(description="履歷中目前最具說服力、可保留的優勢點")
    overall_weaknesses: List[str] = Field(description="整體最影響錄取率的核心弱點")
    critical_issues: List[ResumeIssue] = Field(description="需要優先修正的關鍵問題清單（依嚴重度排序）")
    ats_risk_level: str = Field(description="從 ATS 與第一輪篩選角度評估的整體風險等級(如:低/中/高)")
    screening_outcome_prediction: str = Field(description="模擬企業 6–10 秒快速掃描後，最可能的篩選結果與原因")
    recommended_next_actions: List[str] = Field(description="不涉及代寫的前提下，給候選人的下一步行動建議，列點式說明")

# --- 履歷優化相關模型 ---

class ResumeOptimization(BaseModel):
    professional_summary: str = Field(description="精簡的專業總結，需包含核心價值與推薦職缺的關鍵字")
    professional_experience: Optional[List[str]] = Field(default_factory=list, description="優化後的經歷列表。每筆包含 company, title, duration, 並以 STAR 原則重新撰寫的 description（條列式）")
    core_skills: List[str] = Field(description="從履歷中萃取與推薦職缺相關的技術或軟實力關鍵字6個")
    projects: Optional[List[str]] = Field(default_factory=list, description="優化後的專案描述，強調技術棧與量化成果")
    education: List[str] = Field(description="最高及次高學歷資訊列表，包含學校、學系、學位與畢業時間")
    autobiography: str = Field(description="保留使用者原本風格、敘事順序與用詞習慣前提下的優化後完整自傳")
