from crewai_tools import BaseTool
from typing import Type, List, Optional
from pydantic import BaseModel, Field
from .course_matching import CourseRecommendationService

class CourseRecommendationToolInput(BaseModel):
    """
    課程推薦工具的輸入參數
    """
    user_id: str = Field(..., description="使用者的唯一識別碼，用於查詢其技能分析與目標職位。")
    top_k: int = Field(5, description="最終需要輸出的推薦課程數量，預設為 5。")

class CourseRecommendationTool(BaseTool):
    """
    專門用於獲取推薦課程的工具。
    該工具會根據使用者的技能缺口 (Skill Gap) 與其當前的技術等級，
    計算推薦優先權分數 (Priority Score) 並回傳最適合的課程清單。
    """
    name: str = "Course Recommendation Tool"
    description: str = (
        "輸入 user_id 後，自動查詢該使用者的最新技能分析結果，"
        "並計算符合其難度與需求的推薦課程列表，包含課程名稱、連結與推薦評分。"
    )
    args_schema: Type[BaseModel] = CourseRecommendationToolInput

    def _run(self, user_id: str, top_k: int = 5) -> str:
        """
        工具執行邏輯：將 Service 的結構化結果轉換為 Agent 可讀的文本。
        """
        service = CourseRecommendationService()
        try:
            # 調用核心 Service
            result = service.get_recommendations(user_id, top_k)
            
            # 格式化輸出，方便 Agent 閱讀與整合進最終回覆
            if not result.recommendations:
                return f"目前在資料庫中找不到適合使用者 {user_id} 的推薦課程。"
            
            output = f"### 為使用者 {user_id} 推薦的學習資源\n"
            output += f"**當前技術匹配度**: {result.match_score}/100 (等級: {result.user_level})\n\n"
            
            for i, course in enumerate(result.recommendations, 1):
                output += (
                    f"{i}. **{course.course_name}**\n"
                    f"   - 難度分級: {course.level}\n"
                    f"   - 課程連結: {course.url}\n"
                    f"   - 推薦理由: 該課程難度與您的當前水平精確匹配，是提升技能的最佳切入點。\n\n"
                )
            
            return output
            
        except Exception as e:
            return f"❌ 在檢索推薦課程時發生技術錯誤: {str(e)}"
