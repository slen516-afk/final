# tools.py
import json
from crewai.tools import tool
# 假設這是你的原始模組
from src.features.analysis.calculator import CareerAnalyzer
from src.features.matching.matcher import JobMatcher

class CareerAnalysisTools:
    
    @tool("Calculate Technical Vectors")
    def calculate_tech_vectors(user_json_str: str):
        """
        接收使用者職涯問卷的 JSON 字串，計算 D1-D6 六維能力分數。
        """
        # 定義預設分數 (Entry Level Baseline)
        default_scores = {
            "D1": 0.5, "D2": 0.5, "D3": 0.5, 
            "D4": 0.5, "D5": 1.0, "D6": 1.0 
            # D5(品質)與D6(軟實力)給 1.0 是假設即使無技術經驗，成年人也有基礎的工作品質與溝通能力，這比純技術(0.5)稍高一點較合理。
        }

        try:
            user_data = json.loads(user_json_str)

        # 檢查是否為無經驗者
        # 這裡假設如果沒有 module_a (硬實力)，就是無經驗
            if not user_data.get("module_a") or not user_data.get("module_a", {}).get("q1_languages"):
                return str(default_scores)

            # 正常計算流程
            if CareerAnalyzer:
                analyzer = CareerAnalyzer(user_data)
                analyzer.calculate_vectors()
                return str(analyzer.scores) # 預期回傳 {'D1': 3.5, ...}
            else:
                # 測試環境若無 Analyzer，回傳模擬數據
                return str(default_scores)

        except Exception as e:
            # 發生任何錯誤都回傳預設值，保證流程不中斷
            return f"Error (using defaults): {str(default_scores)}. Details: {str(e)}"

    @tool("Calculate Job Match Score")
    def calculate_match_score(vectors_str: str, target_role: str):
        """
        計算使用者能力向量與目標職位的匹配分數 (0-100)。
        """
        try:
            # 安全起見實際專案可用 json.loads
            vectors = eval(vectors_str) 
            score = JobMatcher.calculate_match_score(vectors, target_role)
            return str(score)
        except Exception as e:
            return f"Error calculating match score: {str(e)}"