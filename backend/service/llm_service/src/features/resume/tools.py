from typing import Any, Dict
from crewai.tools import BaseTool
from src.core.database.supabase_client import get_supabase_client

class DatabaseTools:
    """
    提供與 Supabase 資料庫直接互動的靜態方法。
    """
    
    @staticmethod
    def get_user_resume(user_id: str) -> Dict[str, Any]:
        """
        根據 user_id 到 Supabase 抓取用戶最新的履歷內容。
        """
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
            return {"error": f"資料庫抓取失敗: {str(e)}"}

    @staticmethod
    def get_user_survey(user_id: str) -> Any:
        """
        根據 user_id 到 Supabase 抓取用戶問卷中的目標職位。
        """
        supabase = get_supabase_client()
        try:
            response = supabase.table("career_survey") \
                .select("career_preference") \
                .eq("user_id", user_id) \
                .order("completed_at", desc=True) \
                .limit(1) \
                .single() \
                .execute()

            if not response.data:
                return {"error": "找不到該用戶問卷資料"}

            # 提取 career_preference 中的 target_role
            pref = response.data.get("career_preference", {})
            return pref.get("target_role", "未指定目標職位")

        except Exception as e:
            return {"error": f"資料庫抓取失敗: {str(e)}"}
    
    @staticmethod
    def get_resume_analysis(user_id: str) -> Dict[str, Any]:
        """
        根據 user_id 到 Supabase 抓取用戶最新的履歷分析報告。
        """
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
