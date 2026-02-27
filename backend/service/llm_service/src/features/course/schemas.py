from pydantic import BaseModel, Field
from typing import List, Optional

class CourseItem(BaseModel):
    """
    單一課程推薦項目的資料模型
    """
    course_id: str
    course_name: str
    url: str
    level: str
    course_type: Optional[str] = None
    priority_score: float = Field(..., description="推薦優先權分數 (基於能力距離與政策權重)")
    quality_score: float = Field(..., description="課程品質分數 (基於評價與評論數)")
    recommendation_reason: Optional[str] = Field(None, description="推薦原因說明")

class CourseRecommendationResponse(BaseModel):
    """
    課程推薦服務的整體回傳模型
    """
    user_id: str
    user_level: int
    match_score: int
    recommendations: List[CourseItem]
