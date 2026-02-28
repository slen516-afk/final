from crewai.tools import BaseTool
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
            # 調用核心 Service (這裡拿到的 result 是一個 List[Dict])
            result_list = service.get_recommendations(user_id, top_k)
            
            # 如果陣列是空的
            if not result_list:
                return f"目前在資料庫中找不到適合使用者 {user_id} 的推薦課程。"
            
            output = f"### 為使用者 {user_id} 推薦的學習資源\n\n"
            
            # 正確使用迴圈讀取 Dictionary 裡面的資料
            for i, course in enumerate(result_list, 1):
                output += (
                    f"{i}. **{course.get('course_name')}**\n"
                    f"   - 難度分級: {course.get('level')}\n"
                    f"   - 課程連結: {course.get('url')}\n"
                    f"   - 推薦分數: {course.get('priority_score')}\n\n"
                )
            
            return output
            
        except Exception as e:
            return f"❌ 在檢索推薦課程時發生技術錯誤: {str(e)}"