from pydantic import BaseModel, Field
from typing import Literal, List, Optional, Dict, Any


# class User6DProfile(BaseModel):
#     """
#     使用者六維職能評分 (1.0 - 5.0)
#     對應 PDF 規格書中的 D1~D6 維度
#     """
#     d1_frontend: float = Field(..., ge=0, le=5, description="D1: 前端開發能力")
#     d2_backend: float = Field(..., ge=0, le=5, description="D2: 後端開發能力")
#     d3_devops: float = Field(..., ge=0, le=5, description="D3: 雲端維運能力")
#     d4_ai_data: float = Field(..., ge=0, le=5, description="D4: AI與數據能力")
#     d5_quality: float = Field(..., ge=0, le=5, description="D5: 品質與架構能力")
#     d6_soft_skills: float = Field(..., ge=0, le=5, description="D6: 軟實力/溝通能力")

#     class Config:
#         # 允許使用 D1, D2 這種別名，增加相容性
#         populate_by_name = True

class JobMatchFilters(BaseModel):
    """職缺搜尋過濾條件"""
    city: Optional[str] = Field(None, description="工作地點 (例如: 台北市)")
    industry: Optional[str] = Field(None, description="產業類型")
    salary_min: Optional[int] = Field(None, description="最低薪資月薪 (預留欄位)")

class JobMatchRequest(BaseModel):
    """
    職缺匹配請求格式
    API 負責人應依照此格式傳入 JSON
    """
    user_id: int = Field(..., description="使用者資料庫 ID")
    document_id: int = Field(..., description="履歷 ID 或 優化履歷 ID")
    source_type: Literal["RESUME", "OPTIMIZATION"] = Field(..., description="履歷來源：原始或優化")

    filters: Optional[JobMatchFilters] = Field(default_factory=JobMatchFilters)
    # user_6d_profile: User6DProfile = Field(..., description="使用者的六維職能分數")

class JobMatchResult(BaseModel):
    """
    單筆職缺匹配結果格式
    """
    job_id: str = Field(..., description="職缺唯一識別碼")
    job_title: str = Field(..., description="職缺名稱")
    company_name: str = Field(..., description="公司名稱")
    industry: str = Field(..., description="產業類別")
    full_address: str = Field(..., description="完整地址")
    requirements: str = Field(..., description="職缺要求 (清理後的字串)")
    final_score: str = Field(..., description="最終匹配百分比 (例如: '92.5%')")
    recommendation_reason: Optional[str] = Field(None, description="AI 推薦理由說明")
    strengths: Optional[str] = Field(None, description="AI 候選人優勢")
    weaknesses: Optional[str] = Field(None, description="AI 缺乏部分")
    interview_tips: Optional[str] = Field(None, description="AI 面試準備建議")
    source_url: Optional[str] = Field(None, description="原始職缺連結")

#======
# 這兩個 key (status 與 results) 在 API 設計中被稱為 「回應包裝 (Response Envelope / Wrapper)」。通常如果 API 要回傳一個陣列 (例如 Top 10 的職缺列表)，開發者會習慣把它包在一個帶有 status 的物件裡面，這個結構原本被定義在 schemas.py的 JobMatchingResponse 類別中。
#======
class JobMatchingResponse(BaseModel):
    """
    職缺匹配完整回應格式
    """
    results: List[JobMatchResult] = Field(default_factory=list, description="推薦的職缺列表 (Top 10)")
    status: str = Field("success", description="執行狀態")
