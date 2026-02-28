from pydantic import BaseModel, Field
from typing import List, Optional

class CourseItem(BaseModel):
    """
    單一課程推薦項目的資料模型
    """
    course_id: int               # 改為 int
    course_name: str
    url: str
    rating: float                # 新增
    review_count: int            # 新增
    level: str
    course_type: Optional[str] = None
    duration_suggested: Optional[str] = None # 新增
    course_level: int            # 新增
    priority_score: float
    quality_score: float

# class CourseRecommendationResponse(BaseModel):
#     """
#     課程推薦服務的整體回傳模型
#     """
#     user_id: str
#     user_level: int
#     match_score: int
#     recommendations: List[CourseItem]
