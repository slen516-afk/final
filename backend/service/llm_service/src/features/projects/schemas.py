from typing import List
from pydantic import BaseModel, Field

class ProjectPhase(BaseModel):
    phase_name: str = Field(description="階段名稱，例如：'Phase 1: 核心 API 與資料庫設計 (MVP Backend)'")
    phase_goal: str = Field(description="此階段的核心目標，說明為何要做這個階段")
    tasks: List[str] = Field(description="此階段需完成的具體任務清單（可直接作為 checklist 使用）")
    resume_value: str = Field(description="此階段完成後，可直接寫進履歷的一段敘述（偏向職缺導向關鍵字）")

class SideProject(BaseModel):
    project_name: str = Field(description="專案名稱。需具專業感，能清楚體現應用核心價值")
    capability_gaps_addressed: List[str] = Field(description="此專案主要補強的能力缺口清單（對應求職弱項）")
    tech_stack: List[str] = Field(description="完整技術棧清單，包含後端、資料庫、部署、容器化等")
    project_phases: List[ProjectPhase] = Field(description="專案分階段實作規劃，每一階段需包含目標、任務與履歷價值")
    overall_resume_impact: str = Field(description="整個專案完成後，對履歷競爭力的整體提升說明")
    difficulty: str = Field(description="專案整體難度與時程評估，格式為：'難度等級 (低/中/高) | 預估開發週期'，並簡述主要挑戰點。")
