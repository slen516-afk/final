from crewai.tools import BaseTool
from pydantic import Field

class DatabaseTools:
    """
    未來與資料庫實際介接的類別占位符。
    """
    @staticmethod
    def get_user_resume(user_id: str) -> str:
        # TODO: 實作從資料庫獲取使用者履歷的邏輯
        # 目前暫時回傳範例文字
        return f"User {user_id}'s resume content from database..."

class FetchResumeTool(BaseTool):
    """
    獲取使用者個人履歷的工具。
    """
    name: str = "FetchUserResume"
    description: str = "獲取使用者個人履歷。Input: user_id"
    
    def _run(self, user_id: str) -> str:
        """
        執行獲取履歷的動作。
        """
        return DatabaseTools.get_user_resume(user_id)
