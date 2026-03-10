import json

from crewai.tools import BaseTool
import os
from src.core.database.supabase_client import get_supabase_client
from dotenv import load_dotenv
from src.common.logger import setup_logger

load_dotenv()
logger = setup_logger()

class DatabaseTools:

    @staticmethod
    def get_job_recommendation_profile(job_id: str):
        """
        到 Supabase 抓取推薦職缺資料，進行推薦信生成。
        """
        supabase = get_supabase_client()
        logger.info(f"開始抓取推薦職缺資料 (job_id: {job_id})")

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
            logger.error(f"抓取推薦職缺資料失敗: {str(e)}", exc_info=True)
            return {"error": f"資料庫抓取失敗: {str(e)}"}

    @staticmethod
    def get_optimize_resume(optimization_id: str):
        """
        根據 optimization_id 到 Supabase 抓取用戶的優化後履歷。
        """
        supabase = get_supabase_client()
        logger.info(f"開始抓取用戶優化後履歷資料 (optimization_id: {optimization_id})")

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
            logger.error(f"抓取用戶優化後履歷資料失敗: {str(e)}", exc_info=True)
            return {"error": f"資料庫抓取失敗: {str(e)}"}
        
    @staticmethod
    def get_user_designated_resume(resume_id: str):
        """
        根據 resume_id 到 Supabase 抓取指定的用戶原始履歷。
        """
        supabase = get_supabase_client()
        logger.info(f"開始抓取用戶原始履歷資料 (resume_id: {resume_id})")

        try:
            # 執行 SQL 查詢
            response = supabase.table("resume") \
                .select("structured_data") \
                .eq("resume_id", resume_id) \
                .single() \
                .execute()

            if not response.data:
                return {"error": "找不到指定的用戶原始履歷資料"}

            return response.data

        except Exception as e:
            logger.error(f"抓取用戶原始履歷資料失敗: {str(e)}", exc_info=True)
            return {"error": f"資料庫抓取失敗: {str(e)}"}


class RecommendJobSearchTool(BaseTool):
    name: str = "SearchRecommendJob"
    description: str = "搜尋推薦職缺。Input: job_id"
    def _run(self, job_id: str) -> str:
        return DatabaseTools.get_job_recommendation_profile(job_id)

class FetchOptimizeResumeTool(BaseTool):
    name: str = "FetchUserOptimizeResume"
    description: str = "獲取使用者指定的優化後履歷。Input: optimization_id"
    def _run(self, optimization_id: str) -> str:
        return DatabaseTools.get_optimize_resume(optimization_id)
    
class FetchDesignatedResumeTool(BaseTool):
    name: str = "FetchUserDesignatedResume"
    description: str = "獲取使用者指定的原始履歷。Input: resume_id"
    def _run(self, resume_id: str) -> str:
        return DatabaseTools.get_user_designated_resume(resume_id)
