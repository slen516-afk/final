import os
import json
from dotenv import load_dotenv
from src.features.course.course_matching import CourseRecommendationService

# 載入環境變數 (確保能連到 Supabase)
load_dotenv()

def test_course_recommendation():
    print("====== 正在測試課程推薦服務 (CourseRecommendationService) ======")
    
    # 1. 初始化服務
    service = CourseRecommendationService()
    
    # 2. 測試獲取推薦 (假設使用一個測試 ID，若無則會使用默認值)
    # 你可以嘗試把 '1' 換成資料庫中真實存在的 user_id
    test_user_id = "1" 
    
    print(f"測試使用者 ID: {test_user_id}")
    
    try:
        result = service.get_recommendations(test_user_id, top_k=3)
        
        print("✅ 推薦結果獲取成功！")
        print(f"使用者等級: {result['user_level']} (匹配分數: {result['match_score']})")
        print(f"獲取推薦課程數量: {len(result['recommendations'])}")
        
        for i, course in enumerate(result['recommendations'], 1):
            print(f"[{i}] {course['course_name']}")
            print(f"    - 難度: {course['level']}")
            print(f"    - 優先分數 (Priority): {course['priority_score']:.4f}")
            print(f"    - 品質分數 (Quality): {course['quality_score']:.2f}")
            print(f"    - 連結: {course['url']}")

    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")

if __name__ == "__main__":
    test_course_recommendation()
