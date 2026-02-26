from crewai.tools import BaseTool
import os
from src.core.database.supabase_client import get_supabase_client
from dotenv import load_dotenv

load_dotenv()

class SearchRecommendJobTool(BaseTool):
    name: str = "SearchRecommendJob"
    description: str = "獲取推薦職缺的詳細資訊 (JD)，包含 job_title, job_description, requirements。Input: job_id"
    
    def _run(self, job_id: str) -> str:
        """
        到 Supabase 抓取職缺資料，進行推薦信生成。
        """
        try:
            supabase = get_supabase_client()
            
            # 採用括號包裹的方式進行鏈式呼叫，避免縮進與反斜線問題
            response = (
                supabase.table("job_posting")
                .select("job_id, job_title, job_description, requirements")
                .eq("job_id", job_id)
                .single()
                .execute()
            )

            if not response.data:
                return f"錯誤: 找不到 ID 為 {job_id} 的職缺資料。"

            return str(response.data)

        except Exception as e:
            return f"資料庫抓取失敗: {str(e)}"
