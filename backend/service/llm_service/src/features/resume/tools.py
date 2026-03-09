from typing import Any, Dict
from crewai.tools import BaseTool
from src.core.database.supabase_client import get_supabase_client
from src.common.logger import setup_logger

logger = setup_logger()

class DatabaseTools:
    """
    提供與 Supabase 資料庫直接互動的靜態方法。
    """
    
    @staticmethod
    def get_user_resume(user_id: str) -> Dict[str, Any]:
        """
        根據 user_id 到 Supabase 抓取用戶最新的履歷內容。
        """
        logger.info(f"開始抓取最新的履歷內容 (user_id: {user_id})")
        supabase = get_supabase_client()
        try:
            response = supabase.table("resume") \
                .select("structured_data") \
                .eq("user_id", user_id) \
                .order("created_at", desc=True) \
                .limit(1) \
                .single() \
                .execute()

            if not response.data:
                return {"error": "找不到該用戶履歷資料"}
            return response.data

        except Exception as e:
            logger.error(f"抓取用戶最新履歷內容失敗: {str(e)}", exc_info=True)
            return {"error": f"資料庫抓取失敗: {str(e)}"}

    @staticmethod
    def get_user_survey(user_id: str) -> str:
        """
        根據 user_id 到 Supabase 抓取用戶問卷中 questionnaire_response 不為空的最新結果。
        (已針對 CrewAI 強化防呆：發生任何錯誤皆回傳自然語言提示，確保 Agent 不會崩潰)
        """
        logger.info(f"開始抓取最新的問卷結果 (user_id: {user_id})")
        from src.core.database.supabase_client import get_supabase_client # 確保你有引入
        
        supabase = get_supabase_client()
        try:
            response = supabase.table("career_survey") \
                .select("questionnaire_response") \
                .eq("user_id", user_id) \
                .not_.is_("questionnaire_response", "null") \
                .order("completed_at", desc=True) \
                .limit(1) \
                .maybe_single() \
                .execute()

            # 🌟 終極防呆 1：確保 response 存在且具有 data 屬性，且 data 不是 None 或空字典
            if not response or not hasattr(response, 'data') or not response.data:
                return "【系統提示】：該用戶尚未填寫職涯問卷，請忽略目標職位的比對，直接依據「履歷原文」進行客觀的分析與優化。"

            # 🌟 安全處理 JSON 嵌套結構
            resp = response.data.get("questionnaire_response") or {}
            module_c = resp.get("module_c") or {}
            target_role = module_c.get("q17_target_role")

            # 🌟 終極防呆 2：如果問卷有填，但目標職位沒填
            if not target_role or target_role == "未指定目標職位":
                return "【系統提示】：該用戶未在問卷中明確指定目標職位，請直接依據現有經歷推測適合的發展方向，並進行履歷優化。"

            return f"使用者的目標職位為：{target_role}"

        except Exception as e:
            logger.error(f"抓取用戶問卷結果失敗: {str(e)}", exc_info=True)
            # 🌟 終極防呆 3：發生任何未知錯誤時，絕對不回傳 dict，而是用文字安撫 AI 繼續工作！
            return f"【系統提示】：讀取問卷時發生異常（{str(e)}），請忽略問卷目標，直接對現有履歷進行深度評估與全文重寫優化。"
    
    @staticmethod
    def get_resume_analysis(user_id: str) -> Dict[str, Any]:
        """
        根據 user_id 到 Supabase 抓取用戶最新的履歷分析報告。
        """
        logger.info(f"開始抓取最新的履歷分析報告 (user_id: {user_id})")
        supabase = get_supabase_client()
        try:
            fields = (
                "candidate_positioning, target_role_gap_summary, "
                "overall_strengths, overall_weaknesses, ats_risk_level, "
                "screening_outcome_prediction, recommended_next_actions, critical_issues"
            )
            response = supabase.table("resume_analysis") \
                .select(fields) \
                .eq("user_id", user_id) \
                .order("generated_at", desc=True) \
                .limit(1) \
                .single() \
                .execute()

            if not response.data:
                return {"error": "找不到該用戶履歷分析報告資料"}

            return response.data

        except Exception as e:
            logger.error(f"抓取用戶履歷分析報告失敗: {str(e)}", exc_info=True)
            return {"error": f"資料庫抓取失敗: {str(e)}"}


# ==========================================
# CrewAI 工具封裝 (Tools)
# ==========================================

class FetchResumeTool(BaseTool):
    """
    獲取使用者個人履歷的工具。
    """
    name: str = "FetchUserResume"
    description: str = "獲取使用者個人原始履歷。輸入參數為 user_id。"
    
    def _run(self, user_id: str) -> str:
        return str(DatabaseTools.get_user_resume(user_id))


class FetchSurveyTool(BaseTool):
    """
    獲取使用者問卷結果的工具。
    """
    name: str = "FetchUserSurvey"
    description: str = "獲取使用者個人問卷結果中的目標職位。輸入參數為 user_id。"
    
    def _run(self, user_id: str) -> str:
        return str(DatabaseTools.get_user_survey(user_id))


class FetchResumeAnalysisTool(BaseTool):
    """
    獲取使用者個人履歷分析結果的工具。
    """
    name: str = "FetchUserResumeAnalysis"
    description: str = "獲取使用者個人履歷分析結果。輸入參數為 user_id。"
    
    def _run(self, user_id: str) -> str:
        return str(DatabaseTools.get_resume_analysis(user_id))
