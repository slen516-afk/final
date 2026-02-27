from crewai.tools import BaseTool
import os
from src.core.database.supabase_client import get_supabase_client
from dotenv import load_dotenv

load_dotenv()

class DatabaseTools:

    @staticmethod
    def get_job_recommendation_profile(job_id: str):
        """
        到 Supabase 抓取推薦職缺資料，進行推薦信生成。
        """
        supabase = get_supabase_client()

        try:
            # 執行 SQL 查詢
            response = supabase.table("job_posting") \
                .select("job_id, job_title, job_description, requirements") \
                .eq("job_id", job_id) \
                .single() \
                .execute()

            if not response.data:
                return {"error": "找不到職缺資料"}

            return response.data

        except Exception as e:
            return {"error": f"資料庫抓取失敗: {str(e)}"}

    @staticmethod
    def get_optimize_resume(optimization_id: str):
        """
        根據 optimization_id 到 Supabase 抓取用戶的優化後履歷。
        """
        supabase = get_supabase_client()

        try:
            # 執行 SQL 查詢
            response = supabase.table("resume_optimization") \
                .select("professional_summary, professional_experience, core_skills, projects, education, autobiography") \
                .eq("optimization_id", optimization_id) \
                .single() \
                .execute()

            if not response.data:
                return {"error": "找不到該用戶優化後履歷資料"}

            return response.data

        except Exception as e:
            return {"error": f"資料庫抓取失敗: {str(e)}"}


class RecommendJobSearchTool(BaseTool):
    name: str = "SearchRecommendJob"
    description: str = "搜尋推薦職缺。Input: job_id"
    def _run(self, job_id: str) -> str:
        return DatabaseTools.get_job_recommendation_profile(job_id)

class FetchOptimizeResumeTool(BaseTool):
    name: str = "FetchUserOptimizeResume"
    description: str = "獲取使用者個人優化後的履歷。Input: optimization_id"
    def _run(self, optimization_id: str) -> str:
        return DatabaseTools.get_optimize_resume(optimization_id)
