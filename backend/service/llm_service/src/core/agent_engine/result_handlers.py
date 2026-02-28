from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from .task_types import TaskType

class BaseResultHandler(ABC):
    """所有 Agent 結果處理器的基底類別"""
    def __init__(self, supabase_client):
        self.supabase = supabase_client

    @abstractmethod
    def process(self, pydantic_result: Any, **kwargs) -> Any:
        """
        處理並儲存結果的抽象方法
        :param pydantic_result: CrewAI 產出的 Pydantic 模型或 Dict
        :param kwargs: 包含 user_id, survey_id 等 metadata
        """
        pass

class GapAnalysisHandler(BaseResultHandler):
    """
    職涯缺口分析報告 (Gap Analysis) 儲存處理器
    對應資料表: career_analysis_report
    """
    def process(self, pydantic_result: Any, **kwargs) -> Any:
        # 1. 確保格式為字典 (相容 Pydantic v1/v2)
        if hasattr(pydantic_result, "model_dump"):
            data = pydantic_result.model_dump()
        elif hasattr(pydantic_result, "dict"):
            data = pydantic_result.dict()
        else:
            data = pydantic_result

        # 2. 身份識別：優先從 kwargs 拿，若無則從 metadata 提取
        user_id = kwargs.get("user_id") or data.get("report_metadata", {}).get("user_id")
        
        target_resume_id = kwargs.get("resume_id")
        if not target_resume_id and user_id:
            try:
                resume_info = self.supabase.table("resume") \
                    .select("resume_id") \
                    .eq("user_id", user_id) \
                    .order("created_at", desc=True) \
                    .limit(1) \
                    .single() \
                    .execute()
                
                if resume_info.data:
                    target_resume_id = resume_info.data.get('resume_id')
            except Exception as e:
                print(f"⚠️ [GapAnalysisHandler] 無法自動獲取 resume_id: {e}")

        # 3. 欄位精準映射 (Mapping)
        # 根據資料表結構，將巢狀的 Pydantic 數據扁平化或存入 JSONB 欄位
        payload = {
            "user_id": user_id,
            "report_version": data.get("report_metadata", {}).get("version", "1.0"),
            "generated_at": data.get("report_metadata", {}).get("timestamp"),
            
            # JSONB 區塊
            "preliminary_summary": data.get("preliminary_summary"),
            "radar_chart": data.get("radar_chart"),
            "gap_analysis": data.get("gap_analysis", {}).get("current_status"),
            "target_position": data.get("gap_analysis", {}).get("target_position"),
            "action_plan": data.get("action_plan"),
            
            # 關聯鍵
            # "survey_id": kwargs.get("survey_id"),
            "resume_id": target_resume_id
        }

        # 4. 資料清洗：剔除 None 值
        payload = {k: v for k, v in payload.items() if v is not None}

        # 5. 執行寫入
        try:
            return self.supabase.table("career_analysis_report").insert(payload).execute()
        except Exception as e:
            print(f"❌ [GapAnalysisHandler] 寫入資料庫失敗: {e}")
            raise

# ======================================================
# 範例 1：履歷優化處理器 (Resume Optimization) - 新增式存檔(需要撈 resume_id & 算版本)
# ======================================================
class ResumeOptHandler(BaseResultHandler):
    def process(self, pydantic_result: any, **kwargs):
        user_id = kwargs.get("user_id")

        # 1. 從 resume 表撈出該用戶最原始的 resume_id
        resume_info = self.supabase.table("resume") \
            .select("resume_id") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(1) \
            .single() \
            .execute()

        if not resume_info.data:
            raise ValueError(f"找不到用戶 {user_id} 的原始履歷，無法存儲優化結果")

        target_resume_id = resume_info.data['resume_id']

        # 2. 計算版本號 (取目前最大版本 + 1)
        res = self.supabase.table("resume_optimization") \
            .select("optimization_version") \
            .eq("user_id", user_id) \
            .order("optimization_version", desc=True) \
            .limit(1) \
            .execute()

        max_version = res.data[0]['optimization_version'] if res.data else 0
        new_version = int(max_version) + 1

        # 3. 組裝並寫入資料庫 (拆分欄位)
        payload = {
            "user_id": user_id,
            "resume_id": target_resume_id, # 這是額外撈出的值
            "optimization_version": new_version, # 這是計算出的值
            **pydantic_result, # AI 生成的欄位
            # "created_at": "now()"
        }

        return self.supabase.table("resume_optimization").insert(payload).execute()

# ======================================================
# 範例 2：履歷分析處理器 (Resume Analysis) - 新增式存檔
# ======================================================
class ResumeAnalysisHandler(BaseResultHandler):
    def process(self, pydantic_result: any, **kwargs):
        user_id = kwargs.get("user_id")

        # 1. 從 resume 表撈出該用戶最原始的 resume_id
        resume_info = self.supabase.table("resume") \
            .select("resume_id") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(1) \
            .single() \
            .execute()

        if not resume_info.data:
            raise ValueError(f"找不到用戶 {user_id} 的原始履歷，無法存儲優化結果")

        target_resume_id = resume_info.data['resume_id']

        payload = {
            "user_id": user_id,
            "resume_id": target_resume_id,
            **pydantic_result,
            # "created_at": "now()"
        }
        # 使用 upsert，衝突時更新
        return self.supabase.table("resume_analysis").insert(payload).execute()

# ... 你可以依此類推，為其他 5 個功能建立專屬 Handler ...
# ======================================================
# 3. 職缺推薦處理器 (Job Recommendation) - 新增式存檔
# ======================================================
# class JobRecHandler(BaseResultHandler):
#     def process(self, pydantic_result: any, **kwargs):
#         user_id = kwargs.get("user_id")

#         # 假設職缺推薦是一個包含多個職缺的 List
#         payload = {
#             "user_id": user_id,
#             **pydantic_result,
#             # "created_at": "now()"
#         }
#         return self.supabase.table("job_recommendations").insert(payload).execute()

# ======================================================
# 4. 課程推薦處理器 (Course Recommendation) - 新增式存檔
# ======================================================
# class CourseRecHandler(BaseResultHandler):
#     def process(self, pydantic_result: any, **kwargs):
#         user_id = kwargs.get("user_id")

#         payload = {
#             "user_id": user_id,
#             **pydantic_result,
#             # "created_at": "now()"
#         }
#         return self.supabase.table("course_recommendations").insert(payload).execute()

# ======================================================
# 5. Side Project 推薦處理器 (Project Recommendation) - 新增式存檔
# ======================================================
class ProjectRecHandler(BaseResultHandler):
    def process(self, pydantic_result: any, **kwargs):
        user_id = kwargs.get("user_id")

        payload = {
            "user_id": user_id,
            **pydantic_result,
            # "created_at": "now()"
        }
        return self.supabase.table("side_project_recommendation").insert(payload).execute()

# ======================================================
# 6. 推薦信撰寫處理器 (Cover Letter) - 新增式存檔
# ======================================================
class CoverLetterHandler(BaseResultHandler):
    def process(self, pydantic_result: any, **kwargs):
        # 從 kwargs 拿取從前端或 Task 傳進來的 job_id
        job_id = kwargs.get("job_id")
        user_id = kwargs.get("user_id")

        payload = {
            "user_id": user_id,
            "job_id": job_id,
            **pydantic_result,
            # "created_at": "now()"
        }
        # 這裡建議用 user_id + job_id 作為 Unique Key，如果不希望同職缺存兩封
        return self.supabase.table("cover_letter").insert(payload).execute()



class HandlerRegistry:
    """任務類型與處理器的註冊對照表"""
    def __init__(self, supabase_client):
        self._handlers = {
            # 這裡註冊不同 TaskType 對應的 Handler
            TaskType.CAREER_ANALYSIS_EXPERIENCED: GapAnalysisHandler(supabase_client),
            TaskType.CAREER_ANALYSIS_ENTRY_LEVEL: GapAnalysisHandler(supabase_client),
            TaskType.CAREER_ANALYSIS: GapAnalysisHandler(supabase_client),
            TaskType.RESUME_OPT: ResumeOptHandler(supabase_client),
            TaskType.RESUME_ANALYSIS: ResumeAnalysisHandler(supabase_client),
            TaskType.PROJECT_REC: ProjectRecHandler(supabase_client),
            TaskType.COVER_LETTER: CoverLetterHandler(supabase_client)
            # 未來可在這裡擴充其他模組的 Handler
        }

    def get_handler(self, task_type: TaskType) -> Optional[BaseResultHandler]:
        return self._handlers.get(task_type)
