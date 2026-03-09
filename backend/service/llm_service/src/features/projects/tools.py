from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import os
from src.core.database.supabase_client import get_supabase_client
from dotenv import load_dotenv
from src.common.logger import setup_logger

load_dotenv()

logger = setup_logger()

class DatabaseTools:

    @staticmethod
    def get_gap_analysis(user_id: str):
        """
        根據 user_id 到 Supabase 抓取用戶與目標職位的缺口分析資料。
        """
        logger.info(f"開始從資料庫獲取使用者缺口分析資料 (user_id: {user_id})")
        supabase = get_supabase_client()

        try:
            # 執行 SQL 查詢
            response = supabase.table("career_analysis_report") \
                .select("target_position") \
                .eq("user_id", user_id) \
                .order("generated_at", desc=True) \
                .limit(1) \
                .single() \
                .execute()

            if not response.data:
                return {"error": "找不到該用戶缺口分析報告中的目標職位資料"}

            # target_role = response.data["gap_analysis"]["target_position"]
            # 這裡我們應該回傳整個缺口分析，讓模型有足夠上下文，而不只有 title
            return str(response.data["target_position"])

        except Exception as e:
            logger.error(f"獲取使用者缺口分析資料失敗: {str(e)}", exc_info=True)
            return {"error": f"資料庫抓取失敗: {str(e)}"}


class FetchGapAnalysisInput(BaseModel):
    user_id: str = Field(description="目標使用者的唯一識別碼，必須為純文字字串")

class FetchGapAnalysisTool(BaseTool):
    name: str = "FetchUserGapAnalysis"
    description: str = "獲取使用者個人與目標職位的缺口分析結果。Input: user_id"
    args_schema: type[BaseModel] = FetchGapAnalysisInput
    
    def _run(self, user_id: str) -> str:
        clean_id = str(user_id).strip().strip("'").strip('"')
        return str(DatabaseTools.get_gap_analysis(clean_id))

