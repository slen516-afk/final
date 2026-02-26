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
        }

        try:
            # 處理可能的多個 JSON 物件
            try:
                user_data = json.loads(user_json_str)
            except json.JSONDecodeError as jde:
                # 如果發生 Extra data (說明有兩個 JSON 物件)，嘗試解析第一個
                if "Extra data" in str(jde):
                    import re
                    # 簡單的正則表達式提取第一個 JSON 對象 {...}
                    match = re.search(r'\{.*\}', user_json_str, re.DOTALL)
                    if match:
                        # 嘗試解析第一個匹配到的 {}，但 JSONDecodeError 可能發生在物件之間
                        # 所以我們用 json.JSONDecoder().raw_decode(user_json_str) 更專業
                        user_data, _ = json.JSONDecoder().raw_decode(user_json_str)
                    else:
                        raise jde
                else:
                    raise jde

            # 檢查是否為無經驗者 (如果沒有 module_a 或是 q1_languages 為空)
            ma = user_data.get("module_a", {})
            if not ma or not ma.get("q1_languages"):
                return str(default_scores)

            # 正常計算流程
            if CareerAnalyzer:
                analyzer = CareerAnalyzer(user_data)
                analyzer.calculate_vectors()
                return str(analyzer.scores) 
            else:
                return str(default_scores)

        except Exception as e:
            # 發生任何錯誤都回傳預設值
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