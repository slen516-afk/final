from pydantic import BaseModel, Field
from typing import List, Optional

class CourseRecommendation(BaseModel):
    """
    單一課程推薦項目的資料模型
    """
    course_id: int = Field(description="課程ID")
    course_name: str = Field(description="課程名稱")
    rating: float = Field(description="課程評分")
    review_count: int = Field(description="課程評論數")
    level: str = Field(description="課程難度")
    course_type: Optional[str] = Field(None, description="課程類型")
    duration_suggested: Optional[str] = Field(None, description="建議的課程時長")
    url: str = Field(description="課程連結")
    priority_order: int = Field(description="建議的修課序號 (1-5)")
    strategic_reason: str = Field(description="選擇此課程與排序順序的戰略原因")

class CareerRoadmap(BaseModel):
    """
    課程推薦服務的整體回傳模型 (路線圖)
    """
    overall_strategy: str = Field(description="針對使用者當前媒合度與目標職位的學習大方向建議")
    learning_pathway: List[CourseRecommendation] = Field(description="按建議順序排列的課程清單")
    key_milestones: List[str] = Field(description="完成這些課程後，使用者應達成的核心能力里程碑")

