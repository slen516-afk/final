"""
Supabase 前端寫入模組

提供「前端資料寫入資料庫」的函數，供後端 API 直接 import 使用。
與 supabase_connection 同風格：可傳入既有 client 或由本模組建立連線。

使用方式:
    from db_function.db_writes import insert_career_survey, upsert_user_profile, ...

    # 後端收到前端 payload 後
    result = insert_career_survey(user_id=1, payload=request_body)
"""

from datetime import datetime
from typing import Any, Optional

# 同 package 內連線模組
try:
    from .supabase_connection import connect_to_supabase
except ImportError:
    connect_to_supabase = None

# 表名（與 ERD / Supabase 一致）
TABLE_CAREER_SURVEY = "career_survey"
TABLE_USER_PROFILE = "user_profile"
TABLE_RESUME = "resume"
TABLE_RESUME_VERSION = "resume_version"
TABLE_UPLOAD_EVENT = "upload_event"
TABLE_USER_SKILL = "user_skill"
TABLE_COVER_LETTER = "cover_letter"


def _get_client(supabase=None):
    """若未傳入 supabase 則建立連線（不測試連線以加快速度）。"""
    if supabase is not None:
        return supabase
    if connect_to_supabase is None:
        raise RuntimeError("請安裝並設定 supabase_connection，或傳入 supabase 客戶端")
    return connect_to_supabase(test_connection=False)


# ---------------------------------------------------------------------------
# 1. 問卷（CAREER_SURVEY）
# ---------------------------------------------------------------------------


def insert_career_survey(
    user_id: int,
    payload: dict,
    *,
    supabase=None,
) -> dict:
    """
    寫入一筆職涯問卷（前端提交問卷後呼叫）。

    參數:
        user_id: 使用者 ID（由後端從 session/JWT 取得）。
        payload: 前端送來的問卷資料，建議含：
            - questionnaire_response (dict): 完整問卷 module_a/b/c/d
            - career_preference (dict, optional)
            - skill_self_assessment (dict, optional)
            - career_motivation (dict, optional)
            - salary_min, salary_max (int, optional)
            - location_preference, remote_preference (str, optional)
        supabase: 選填，Supabase 客戶端；未傳則自動連線。

    返回:
        dict: 寫入後的單筆記錄（含 survey_id 等）。

    異常:
        ValueError: 缺少必要欄位時。
    """
    client = _get_client(supabase)
    if not isinstance(user_id, int):
        raise ValueError("user_id 必須為整數")
    if not payload or not isinstance(payload, dict):
        raise ValueError("payload 必須為非空 dict")

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    row = {
        "user_id": user_id,
        "questionnaire_response": payload.get("questionnaire_response") or {},
        "completed_at": now,
        "updated_at": now,
    }
    if "career_preference" in payload and payload["career_preference"] is not None:
        row["career_preference"] = payload["career_preference"]
    if "skill_self_assessment" in payload and payload["skill_self_assessment"] is not None:
        row["skill_self_assessment"] = payload["skill_self_assessment"]
    if "career_motivation" in payload and payload["career_motivation"] is not None:
        row["career_motivation"] = payload["career_motivation"]
    if "salary_min" in payload and payload["salary_min"] is not None:
        row["salary_min"] = int(payload["salary_min"])
    if "salary_max" in payload and payload["salary_max"] is not None:
        row["salary_max"] = int(payload["salary_max"])
    if "location_preference" in payload and payload["location_preference"] is not None:
        row["location_preference"] = str(payload["location_preference"])[:100]
    if "remote_preference" in payload and payload["remote_preference"] is not None:
        row["remote_preference"] = str(payload["remote_preference"])[:50]

    result = client.table(TABLE_CAREER_SURVEY).insert(row).execute()
    if not result.data or len(result.data) == 0:
        raise RuntimeError("寫入問卷失敗，未回傳資料")
    return result.data[0]


# ---------------------------------------------------------------------------
# 2. 個人檔案（USER_PROFILE）
# ---------------------------------------------------------------------------


def upsert_user_profile(
    user_id: int,
    payload: dict,
    *,
    supabase=None,
) -> dict:
    """
    新增或更新使用者個人檔案（前端編輯個人資料後呼叫）。

    參數:
        user_id: 使用者 ID。
        payload: 前端送來的欄位，可含：
            full_name, location, github_repo, years_of_experience,
            current_position, education_background, privacy_settings (dict)。
        supabase: 選填。

    返回:
        dict: 寫入/更新後的單筆記錄（含 profile_id）。
    """
    client = _get_client(supabase)
    if not isinstance(user_id, int):
        raise ValueError("user_id 必須為整數")
    if not isinstance(payload, dict):
        raise ValueError("payload 必須為 dict")

    allowed = {
        "full_name", "location", "github_repo", "years_of_experience",
        "current_position", "education_background", "privacy_settings",
    }
    row = {"user_id": user_id, "updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}
    for key in allowed:
        if key in payload and payload[key] is not None:
            if key == "github_repo":
                row[key] = str(payload[key])[:100]
            elif key in ("full_name", "location", "current_position"):
                row[key] = str(payload[key])[:100]
            elif key == "years_of_experience":
                row[key] = int(payload[key])
            elif key == "education_background":
                row[key] = str(payload[key])
            elif key == "privacy_settings":
                row[key] = payload[key] if isinstance(payload[key], dict) else {}

    existing = client.table(TABLE_USER_PROFILE).select("profile_id").eq("user_id", user_id).execute()
    if existing.data and len(existing.data) > 0:
        profile_id = existing.data[0]["profile_id"]
        client.table(TABLE_USER_PROFILE).update(row).eq("profile_id", profile_id).execute()
        return {**row, "profile_id": profile_id}
    result = client.table(TABLE_USER_PROFILE).insert(row).execute()
    if not result.data or len(result.data) == 0:
        raise RuntimeError("寫入 user_profile 失敗")
    return result.data[0]


# ---------------------------------------------------------------------------
# 3. 履歷（RESUME）與履歷版本（RESUME_VERSION）
# ---------------------------------------------------------------------------


def create_resume(
    user_id: int,
    payload: dict,
    *,
    supabase=None,
) -> dict:
    """
    建立一筆履歷主檔（使用者建立/上傳履歷後呼叫）。

    參數:
        user_id: 使用者 ID。
        payload: 建議含 template_id (int), resume_type (str, 如 'uploaded'/'generated'),
            structured_data (dict), normalized_data (dict, optional), is_primary (bool, optional)。
        supabase: 選填。

    返回:
        dict: 寫入後的履歷記錄（含 resume_id）。
    """
    client = _get_client(supabase)
    if not isinstance(user_id, int):
        raise ValueError("user_id 必須為整數")
    if not isinstance(payload, dict):
        raise ValueError("payload 必須為 dict")

    template_id = payload.get("template_id")
    if template_id is None:
        raise ValueError("template_id 為必填")
    resume_type = payload.get("resume_type") or "uploaded"
    if resume_type not in ("uploaded", "generated"):
        resume_type = "uploaded"

    row = {
        "user_id": user_id,
        "template_id": int(template_id),
        "resume_type": resume_type[:50],
        "structured_data": payload.get("structured_data") or {},
        "is_embedded": False,
        "is_primary": bool(payload.get("is_primary", False)),
    }
    if payload.get("normalized_data") is not None:
        row["normalized_data"] = payload["normalized_data"]

    result = client.table(TABLE_RESUME).insert(row).execute()
    if not result.data or len(result.data) == 0:
        raise RuntimeError("寫入 resume 失敗")
    return result.data[0]


def create_resume_version(
    resume_id: int,
    payload: dict,
    *,
    supabase=None,
) -> dict:
    """
    建立一筆履歷版本（使用者儲存新版本或匯出後呼叫）。

    參數:
        resume_id: 履歷 ID。
        payload: 建議含 version_number (int), file_path (str, optional),
            content (dict), optimization_target (str, optional)。
        supabase: 選填。

    返回:
        dict: 寫入後的版本記錄（含 version_id）。
    """
    client = _get_client(supabase)
    if not isinstance(resume_id, int):
        raise ValueError("resume_id 必須為整數")
    if not isinstance(payload, dict):
        raise ValueError("payload 必須為 dict")

    version_number = payload.get("version_number")
    if version_number is None:
        raise ValueError("version_number 為必填")

    row = {
        "resume_id": resume_id,
        "version_number": int(version_number),
        "content": payload.get("content") or {},
    }
    if payload.get("file_path") is not None:
        row["file_path"] = str(payload["file_path"])[:255]
    if payload.get("optimization_target") is not None:
        row["optimization_target"] = str(payload["optimization_target"])[:100]

    result = client.table(TABLE_RESUME_VERSION).insert(row).execute()
    if not result.data or len(result.data) == 0:
        raise RuntimeError("寫入 resume_version 失敗")
    return result.data[0]


# ---------------------------------------------------------------------------
# 4. 上傳記錄（UPLOAD_EVENT）
# ---------------------------------------------------------------------------


def create_upload_event(
    user_id: int,
    file_name: str,
    file_path: str,
    upload_type: str = "resume",
    *,
    metadata: Optional[dict] = None,
    status: str = "pending",
    supabase=None,
) -> dict:
    """
    記錄一筆上傳事件（前端上傳檔案後，後端寫入 storage 再呼叫）。

    參數:
        user_id: 使用者 ID。
        file_name: 檔案名稱。
        file_path: 儲存路徑（例如 Supabase Storage 的 path）。
        upload_type: 上傳類型，如 'resume' / 'portfolio'。
        metadata: 選填，JSON 中繼資料。
        status: 初始狀態，預設 'pending'。
        supabase: 選填。

    返回:
        dict: 寫入後的記錄（含 event_id）。
    """
    client = _get_client(supabase)
    if not isinstance(user_id, int):
        raise ValueError("user_id 必須為整數")

    row = {
        "user_id": user_id,
        "file_name": str(file_name)[:255],
        "file_path": str(file_path)[:500],
        "upload_type": str(upload_type)[:50],
        "status": str(status)[:50],
        "uploaded_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
    }
    if metadata is not None:
        row["metadata"] = metadata

    result = client.table(TABLE_UPLOAD_EVENT).insert(row).execute()
    if not result.data or len(result.data) == 0:
        raise RuntimeError("寫入 upload_event 失敗")
    return result.data[0]


# ---------------------------------------------------------------------------
# 5. 使用者技能（USER_SKILL）
# ---------------------------------------------------------------------------


def add_user_skill(
    user_id: int,
    skill_id: int,
    payload: dict,
    *,
    supabase=None,
) -> dict:
    """
    新增一筆使用者技能（前端「新增技能」後呼叫）。

    參數:
        user_id: 使用者 ID。
        skill_id: 技能 ID（對應 skill_master）。
        payload: 可含 proficiency_level (int), years_of_experience (float), verified (bool)。
        supabase: 選填。

    返回:
        dict: 寫入後的記錄（含 user_skill_id）。
    """
    client = _get_client(supabase)
    if not isinstance(user_id, int) or not isinstance(skill_id, int):
        raise ValueError("user_id 與 skill_id 必須為整數")

    row = {
        "user_id": user_id,
        "skill_id": skill_id,
        "proficiency_level": int(payload.get("proficiency_level", 1)),
        "years_of_experience": float(payload.get("years_of_experience", 0)),
        "verified": bool(payload.get("verified", False)),
    }
    result = client.table(TABLE_USER_SKILL).insert(row).execute()
    if not result.data or len(result.data) == 0:
        raise RuntimeError("寫入 user_skill 失敗")
    return result.data[0]


def update_user_skill(
    user_skill_id: int,
    payload: dict,
    *,
    supabase=None,
) -> dict:
    """
    更新一筆使用者技能（前端「編輯技能」後呼叫）。

    參數:
        user_skill_id: 使用者技能記錄 ID。
        payload: 可含 proficiency_level, years_of_experience, verified。
        supabase: 選填。

    返回:
        dict: 更新後的記錄（由 select 取回）。
    """
    client = _get_client(supabase)
    if not isinstance(user_skill_id, int):
        raise ValueError("user_skill_id 必須為整數")
    if not isinstance(payload, dict):
        raise ValueError("payload 必須為 dict")

    row = {}
    if "proficiency_level" in payload and payload["proficiency_level"] is not None:
        row["proficiency_level"] = int(payload["proficiency_level"])
    if "years_of_experience" in payload and payload["years_of_experience"] is not None:
        row["years_of_experience"] = float(payload["years_of_experience"])
    if "verified" in payload and payload["verified"] is not None:
        row["verified"] = bool(payload["verified"])
    if not row:
        # 只回傳現有資料
        result = client.table(TABLE_USER_SKILL).select("*").eq("user_skill_id", user_skill_id).execute()
        if not result.data or len(result.data) == 0:
            raise ValueError(f"找不到 user_skill_id={user_skill_id}")
        return result.data[0]

    client.table(TABLE_USER_SKILL).update(row).eq("user_skill_id", user_skill_id).execute()
    result = client.table(TABLE_USER_SKILL).select("*").eq("user_skill_id", user_skill_id).execute()
    if not result.data or len(result.data) == 0:
        raise RuntimeError("更新 user_skill 後查詢失敗")
    return result.data[0]


# ---------------------------------------------------------------------------
# 6. 求職信（COVER_LETTER）
# ---------------------------------------------------------------------------


def save_cover_letter(
    user_id: int,
    job_id: int,
    subject: str,
    content: str,
    *,
    resume_id: Optional[int] = None,
    optimization_id: Optional[int] = None,
    llm_model_used: Optional[str] = None,
    is_sent: bool = False,
    supabase=None,
) -> dict:
    """
    儲存一筆求職信（前端產生/編輯求職信後呼叫，或標記已寄出時更新）。

    參數:
        user_id: 使用者 ID。
        job_id: 職缺 ID。
        subject: 郵件主旨。
        content: 求職信正文。
        resume_id: 選填，使用的履歷 ID。
        optimization_id: 選填，使用的履歷優化 ID。
        llm_model_used: 選填，產生時使用的模型。
        is_sent: 是否已發送，預設 False。
        supabase: 選填。

    返回:
        dict: 寫入後的記錄（含 cover_letter_id）。
    """
    client = _get_client(supabase)
    if not isinstance(user_id, int) or not isinstance(job_id, int):
        raise ValueError("user_id 與 job_id 必須為整數")
    if not subject or not content:
        raise ValueError("subject 與 content 為必填")

    row = {
        "user_id": user_id,
        "job_id": job_id,
        "subject": str(subject),
        "content": str(content),
        "is_sent": bool(is_sent),
    }
    if resume_id is not None:
        row["resume_id"] = int(resume_id)
    if optimization_id is not None:
        row["optimization_id"] = int(optimization_id)
    if llm_model_used is not None:
        row["llm_model_used"] = str(llm_model_used)[:100]
    if is_sent:
        row["sent_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    result = client.table(TABLE_COVER_LETTER).insert(row).execute()
    if not result.data or len(result.data) == 0:
        raise RuntimeError("寫入 cover_letter 失敗")
    return result.data[0]


def mark_cover_letter_sent(cover_letter_id: int, *, supabase=None) -> dict:
    """
    將求職信標記為已發送（前端「標記已寄出」時呼叫）。

    參數:
        cover_letter_id: 求職信 ID。
        supabase: 選填。

    返回:
        dict: 更新後的該筆記錄。
    """
    client = _get_client(supabase)
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    client.table(TABLE_COVER_LETTER).update({
        "is_sent": True,
        "sent_at": now,
    }).eq("cover_letter_id", cover_letter_id).execute()
    result = client.table(TABLE_COVER_LETTER).select("*").eq("cover_letter_id", cover_letter_id).execute()
    if not result.data or len(result.data) == 0:
        raise ValueError(f"找不到 cover_letter_id={cover_letter_id}")
    return result.data[0]


# ---------------------------------------------------------------------------
# 匯出
# ---------------------------------------------------------------------------

__all__ = [
    "insert_career_survey",
    "upsert_user_profile",
    "create_resume",
    "create_resume_version",
    "create_upload_event",
    "add_user_skill",
    "update_user_skill",
    "save_cover_letter",
    "mark_cover_letter_sent",
]
