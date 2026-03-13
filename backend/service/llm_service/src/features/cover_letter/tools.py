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
            # --- MOCK_MODE Fallback ---
            is_mock = os.environ.get("MOCK_MODE", "").lower() == "true"
            
            # 執行 SQL 查詢
            response = supabase.table("job_posting") \
                .select("job_id, job_title, job_description, requirements") \
                .eq("job_id", str(job_id)) \
                .single() \
                .execute()

            if not response.data:
                if is_mock:
                    logger.info(f"♻️ [Mock] 找不到職缺 {job_id}，回傳 Mock 職缺資料")
                    return {
                        "job_id": job_id,
                        "job_title": "【Mock】資深後端工程師 (Python)",
                        "job_description": "負責分散式系統開發、API 優化與架構設計。需熟悉 FastAPI, PostgreSQL, Redis。",
                        "requirements": "1. 3年以上 Python 開發經驗\n2. 熟悉微服務架構\n3. 具備 Cloud 平台使用經驗 (AWS/GCP)"
                    }
                return {"error": "找不到職缺資料"}

            return response.data

        except Exception as e:
            if os.environ.get("MOCK_MODE", "").lower() == "true":
                logger.info(f"♻️ [Mock Mode] 資料庫連線失敗，回傳 Mock 職缺資料 (job_id: {job_id})")
                return {
                    "job_id": job_id,
                    "job_title": "【Mock】資深後端工程師 (Python)",
                    "job_description": "負責分散式系統開發、API 優化與架駕設計。",
                    "requirements": "1. 3年以上 Python 開發經驗\n2. 熟悉微服務架構"
                }
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
            # --- MOCK_MODE Fallback ---
            is_mock = os.environ.get("MOCK_MODE", "").lower() == "true" or str(optimization_id).lower() == "mock"

            # 嘗試執行 SQL 查詢
            try:
                # 這裡對齊 optimization_id 欄位
                # 注意：如果傳入的是 "158_opt_1" 這種字串，資料庫可能會報錯，這裡加個防護
                query_id = optimization_id
                if "_opt_" in str(optimization_id):
                    query_id = str(optimization_id).split("_")[0]
                
                response = supabase.table("resume_optimization") \
                    .select("professional_summary, professional_experience, core_skills, projects, education, autobiography") \
                    .eq("resume_id", query_id) \
                    .limit(1) \
                    .execute() # 改用 execute() 不加 single() 以免噴錯

                if response.data and len(response.data) > 0:
                    return response.data[0]
            except Exception as db_e:
                logger.warning(f"⚠️ 資料庫查詢優化履歷失敗 (可能 ID 格式不對): {db_e}")

            # 如果資料庫找不到，且是 Mock 模式，嘗試讀取備份檔案
            if is_mock:
                logger.info(f"♻️ [Mock] 嘗試從本地備份讀取履歷資料...")
                try:
                    import pathlib
                    # 統一備份檔案路徑
                    project_root = pathlib.Path(__file__).resolve().parents[5] # tools.py -> cover_letter -> features -> src -> llm_service -> service -> backend (6層) -> final (5層)
                    # 修正: tools.py 在 backend/service/llm_service/src/features/cover_letter/
                    # parents[0]: cover_letter
                    # parents[1]: features
                    # parents[2]: src
                    # parents[3]: llm_service
                    # parents[4]: service
                    # parents[5]: backend
                    # parents[6]: project_root
                    project_root = pathlib.Path(__file__).resolve().parents[6]
                    backup_file = project_root / "frontend" / "src" / "test" / "optimized_resume_output.json"
                    
                    if backup_file.exists():
                        with open(backup_file, "r", encoding="utf-8") as f:
                            mock_data = json.load(f)
                        logger.info(f"✅ [Mock] 成功讀取本地備份履歷: {backup_file}")
                        return mock_data
                    else:
                        logger.warning(f"⚠️ [Mock] 找不到備份檔案: {backup_file}，回傳 Stub 資料")
                        return {
                            "professional_summary": "【Mock】資深後端開發者...",
                            "core_skills": ["Python", "Docker"],
                            "professional_experience": ["【Mock】經驗 A", "【Mock】經驗 B"]
                        }
                except Exception as file_e:
                    logger.error(f"❌ [Mock] 讀取檔案發生致命錯誤: {file_e}")

            return {"error": "找不到該用戶優化後履歷資料"}

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
            # --- MOCK_MODE Fallback ---
            is_mock = os.environ.get("MOCK_MODE", "").lower() == "true" or str(resume_id).lower() == "mock"

            # 執行 SQL 查詢
            response = supabase.table("resume") \
                .select("structured_data") \
                .eq("resume_id", str(resume_id)) \
                .execute()

            if not response.data or len(response.data) == 0:
                if is_mock:
                    logger.info(f"♻️ [Mock] 找不到原始履歷 {resume_id}，回傳 Mock 結構化資料")
                    return {
                        "structured_data": {
                            "name": "【Mock】王小明",
                            "email": "wang@example.com",
                            "experience": "3年後端開發經驗...",
                            "skills": "Python, Flask, Docker"
                        }
                    }
                return {"error": "找不到指定的用戶原始履歷資料"}

            return response.data[0]

        except Exception as e:
            if os.environ.get("MOCK_MODE", "").lower() == "true":
                logger.info(f"♻️ [Mock Mode] 資料庫連線失敗，回傳 Mock 履歷資料 (resume_id: {resume_id})")
                return {"structured_data": {"name": "【Mock】王小明", "skills": "Python, Flask"}}
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
