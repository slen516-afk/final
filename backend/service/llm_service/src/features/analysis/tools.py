# tools.py
import json
import ast
import re
from typing import Any, Union, Dict
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

from src.features.analysis.calculator import CareerAnalyzer
from src.features.matching.matcher import JobMatcher
from src.core.database.supabase_client import get_latest_resume

def safe_parse_json(input_data: Union[str, Dict, Any]) -> Dict:
    """Safely parse input string or dict into dict"""
    if isinstance(input_data, dict):
        return input_data
    if not isinstance(input_data, str):
        return {}
        
    clean_str = input_data.strip().replace("```json", "").replace("```", "").strip()
    try:
        # 1. 嘗試標準 JSON
        return json.loads(clean_str)
    except Exception:
        try:
            # 2. 嘗試 Python literal_eval (處理單引號的情況)
            return ast.literal_eval(clean_str)
        except Exception:
            return {}

# 1. Fetch Resume Tool
class FetchResumeInput(BaseModel):
    user_id: str = Field(description="目標使用者的唯一識別碼，必須為純文字字串")

class FetchResumeFromDBTool(BaseTool):
    name: str = "Fetch Resume From Database"
    description: str = "根據 user_id 從資料庫中獲取該使用者最新的履歷內容 (JSON 格式字串)。"
    args_schema: type[BaseModel] = FetchResumeInput
    
    def _run(self, user_id: str) -> str:
        try:
            # 確保提取出乾淨的字串 ID
            clean_id = str(user_id).strip().strip("'").strip('"')
            print(f"DEBUG: fetch_resume_from_db 提取 user_id: {clean_id}")
            return str(get_latest_resume(clean_id))
        except Exception as e:
            return f"Error fetching resume: {str(e)}"

# 2. Calculate Technical Vectors Tool
class CalculateTechVectorsInput(BaseModel):
    user_json_str: str = Field(description="使用者職涯問卷的完整 JSON 字串")

class CalculateTechVectorsTool(BaseTool):
    name: str = "Calculate Technical Vectors"
    description: str = "接收使用者職涯問卷查核結果的 JSON 字串，計算 D1-D6 六維能力分數。"
    args_schema: type[BaseModel] = CalculateTechVectorsInput
    
    def _run(self, user_json_str: str) -> str:
        default_scores = {"D1": 0.5, "D2": 0.5, "D3": 0.5, "D4": 0.5, "D5": 1.0, "D6": 1.0}
        try:
            user_data = safe_parse_json(user_json_str)
            if not user_data:
                return str(default_scores)

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

# 3. Calculate match score tool
class CalculateMatchScoreInput(BaseModel):
    vectors_str: str = Field(description="使用者能力向量 (D1-D6) 的 JSON 字串")
    target_role: str = Field(description="目標職位名稱")

class CalculateMatchScoreTool(BaseTool):
    name: str = "Calculate Job Match Score"
    description: str = "計算使用者能力向量與目標職位的匹配分數 (0-100)。"
    args_schema: type[BaseModel] = CalculateMatchScoreInput
    
    def _run(self, vectors_str: str, target_role: str) -> str:
        try:
            vectors = safe_parse_json(vectors_str)
            if not vectors:
                vectors = {"D1": 0.5, "D2": 0.5, "D3": 0.5, "D4": 0.5, "D5": 1.0, "D6": 1.0}
            
            score = JobMatcher.calculate_match_score(vectors, target_role)
            return str(score)
        except Exception as e:
            return f"Error calculating match score: {str(e)}"
