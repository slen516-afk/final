import sys
import os
import json
from pydantic import BaseModel

# 確保能正確載入 src 模組（將專案根目錄加到 sys.path）
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.features.course.course_matching import CourseRecommendationService

def main():
    # 使用者可以傳入自訂的 user_id 或使用預設值
    test_user_id = sys.argv[1] if len(sys.argv) > 1 else "3" 
    
    print("=" * 70)
    print(f"🚀 開始測試課程推薦模組 (Course Recommendation Module)")
    print(f"👤 目標 User ID: {test_user_id}")
    print("=" * 70)
    
    try:
        service = CourseRecommendationService()
        
        print("\n⏳ 正在執行演算法撈取課程與 CrewAI 分析...")
        print("   (因為會呼叫 LLM 進行 API 請求，這可能會需要 1~3 分鐘的時間，請稍候。)")
        print("-" * 70)
        
        # 呼叫主流程入口
        result = service.get_recommendations(user_id=test_user_id, top_k=5)
        
        print("\n✅ [測試完成] 以下為 CrewAI 最終生成的資料結果：\n")
        
        # 如果發生自定義錯誤，處理字典結果
        if isinstance(result, dict) and result.get("status") == "error":
            print(f"❌ 模組回報錯誤: {result.get('message')}")
            return
            
        # 為了保留原始輸出格式，判斷回傳是否為 Pydantic Model 或是 dict，還是 raw CrewOutput
        output_dict = None
        
        if hasattr(result, "pydantic") and result.pydantic:
            # 如果是 CrewOutput 物件且帶有 pydantic 模型
            output_dict = result.pydantic.model_dump()
        elif hasattr(result, "json_dict") and result.json_dict:
            output_dict = result.json_dict
        elif isinstance(result, BaseModel):
            output_dict = result.model_dump()
        elif hasattr(result, "dict"):
            output_dict = result.dict()
        elif isinstance(result, dict):
            output_dict = result
        else:
            # 原生字串或不預期的格式
            print(result)
            return

        print(json.dumps(output_dict, indent=4, ensure_ascii=False))
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"\n❌ 測試過程中發生技術錯誤:\n{e}")

if __name__ == "__main__":
    main()
