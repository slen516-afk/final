"""
課程貼標腳本：針對資料庫內課程，依「課程名稱」「課程資訊」「Skills」分析，
產出六大職類 (A-F) 標籤並可寫回 course 表與本地 JSON。

使用方式：
- 指定 ID：在 __main__ 的 test_ids 填入 course_id 後執行。
- 隨機批次：請使用 run_course_random_batch.py。
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from typing import List, Any
from dotenv import load_dotenv
import json

# 專案根目錄 = supabase_control
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

from supabase import create_client, Client
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field, field_validator

# 六大職類（與職缺貼標一致）
ROLE_NAME_MAPPING = {
    "A": "前端工程師",
    "B": "後端工程師",
    "C": "全端工程師",
    "D": "資料科學家/數據分析師",
    "E": "AI/演算法工程師",
    "F": "DevOps/SRE工程師",
}

# ==========================================
# 1. 初始化環境
# ==========================================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY]):
    raise ValueError("❌ 請檢查 .env 檔案，缺少必要的 API Key 或 URL")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
llm = ChatOpenAI(model="o3-mini")
TW_TZ = ZoneInfo("Asia/Taipei")

# ==========================================
# 2. 輸出 Schema：僅六大職類 (A-F)
# ==========================================
class CourseRoleLabel(BaseModel):
    role_type: str = Field(
        description="課程所屬的職類代碼，必須是 A, B, C, D, E, F 其中之一"
    )
    role_name: str = Field(description="職類名稱，對應六大職類之一")
    reasoning: str = Field(description="簡短說明為何將此課程歸類到該職類的理由")

    @field_validator("role_type")
    @classmethod
    def validate_role_type(cls, v: str) -> str:
        if v not in ("A", "B", "C", "D", "E", "F"):
            raise ValueError("role_type must be one of A, B, C, D, E, F")
        return v

parser = JsonOutputParser(pydantic_object=CourseRoleLabel)

# ==========================================
# 3. Prompt：依課程名稱、課程資訊、Skills 做六大職類貼標
# ==========================================
system_prompt_text = """
你是一位資深的「軟體職涯與教育內容分類專家」。你的任務是根據「課程名稱」「課程資訊」與「Skills」三個欄位，判斷該課程最適合歸類到以下六大職類中的哪一類。

# 六大職類定義 (僅能從中擇一)
- **A 前端工程師**：UI/UX、網頁前端、React/Vue/Angular、行動前端、前端效能等。
- **B 後端工程師**：API、資料庫、伺服器、高併發、後端語言（Java/C#/Go/Python 後端）等。
- **C 全端工程師**：課程**明確以同時涵蓋前後端**為目標，例如 Full-Stack、全端專案實作、或前後端技能在內容中**並重**。若僅以單一端（前端或後端）為主、另一端僅輕微提及，應歸類為該端（A 或 B），不選 C。
- **D 資料科學家/數據分析師**：資料分析、統計、視覺化、ETL、商業分析、報表等（偏分析而非 ML 模型）。
- **E AI/演算法工程師**：機器學習、深度學習、NLP、電腦視覺、LLM/RAG、演算法、模型訓練與部署。
- **F DevOps/SRE工程師**：雲端、Docker/K8s、CI/CD、維運、監控、基礎設施、SRE 等。

# 判斷原則
1. **優先依據「Skills」**：若技能列表明確（如 Python, React, Kubernetes），依技能對應到上述職類。
2. **課程資訊與課程名稱**：用來輔助判斷主題與深度，當 Skills 不明確時，以課程名稱與課程資訊內容為準。
3. **單一職類**：每門課程只輸出一個最符合的職類代碼 (A/B/C/D/E/F) 與對應名稱。
4. **主次原則（內容橫跨多類時）**：若課程**以單一職類技能為主**，僅在 Skills 或描述中**輕微提及**另一職類，應歸類為**主要職類**。例如：以 Angular／前端為主，Skills 僅列出少數後端相關標籤、且課程名稱與課程資訊未強調全端或並重 → 歸類為 **A 前端工程師**。僅當課程**明確以「前後端並重」或「全端專案」為主要目標**時，才選擇 **C 全端工程師**。
5. **A 與 C 的取捨**：若 Skills 中**前端相關技能明顯多於後端**（或課程名稱／課程資訊明顯偏向前端主題），則選 **A 前端工程師**。僅當 Skills 或課程內容中前後端技能**數量與權重相當**，或課程名稱／描述**明確出現 Full-Stack、全端、前後端並重**時，才選 **C 全端工程師**。

{format_instructions}
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt_text),
    (
        "user",
        """
課程名稱：{course_name}

【課程資訊】：
{course_information}

【Skills】：
{skills_text}
""",
    ),
])

chain = prompt | llm | parser

# ==========================================
# 4. 將課程的 skills 轉成字串供 LLM 使用
# ==========================================
def _skills_to_text(skills: Any) -> str:
    if skills is None:
        return "（無）"
    if isinstance(skills, list):
        return ", ".join(str(s).strip() for s in skills if s) or "（無）"
    if isinstance(skills, str):
        try:
            parsed = json.loads(skills)
            if isinstance(parsed, list):
                return ", ".join(str(s).strip() for s in parsed if s) or "（無）"
        except (json.JSONDecodeError, TypeError):
            pass
        return skills.strip() or "（無）"
    return str(skills) if skills else "（無）"

# ==========================================
# 5. 執行函數：對指定 course_id 列表貼標
# ==========================================
def process_specific_courses(
    target_ids: List[int],
    table_name: str = "course",
) -> None:
    print(f"🎯 準備處理指定的 {len(target_ids)} 筆課程...")

    response = (
        supabase.table(table_name)
        .select("*")
        .in_("course_id", target_ids)
        .is_("role_type", "null")
        .execute()
    )

    courses = response.data

    if not courses:
        print("❌ 找不到任何未貼標的對應課程，請檢查 course_id 或是否已貼標。")
        return

    print(f"✅ 成功撈取 {len(courses)} 筆課程，開始分析...\n" + "=" * 50)

    local_records: List[dict] = []
    total = len(courses)

    for course in courses:
        course_id = course.get("course_id")
        course_name = course.get("course_name", course.get("title", "Unknown"))
        course_info = course.get("course_information", course.get("description", "")) or ""
        skills = course.get("skills")

        skills_text = _skills_to_text(skills)

        print(f"正在分析 course_id: {course_id} | {course_name[:50]}...", end="", flush=True)
        start_t = time.time()

        try:
            result = chain.invoke({
                "course_name": course_name,
                "course_information": course_info,
                "skills_text": skills_text,
                "format_instructions": parser.get_format_instructions(),
            })

            detected_type = result["role_type"]
            standardized_name = ROLE_NAME_MAPPING.get(detected_type, result.get("role_name", "未定義"))

            end_t = time.time()
            duration_sec = round(end_t - start_t, 2)
            processed_time = datetime.now(TW_TZ).isoformat()

            # 寫回 Supabase（僅 role_type, role_name；若表無此欄位需先 ALTER TABLE 新增）
            db_payload = {
                "role_type": result["role_type"],
                "role_name": standardized_name,
            }
            try:
                supabase.table(table_name).update(db_payload).eq("course_id", course_id).execute()
            except Exception as db_err:
                print(f" [DB 更新略過: {db_err}]", end="", flush=True)

            full_record = {
                "course_id": course_id,
                "course_name": course_name,
                **result,
                "role_name": standardized_name,
                "processed_at": processed_time,
                "execution_duration_seconds": duration_sec,
            }
            local_records.append(full_record)

            print(f" [完成] 耗時 {duration_sec}s -> {standardized_name}")
            if len(local_records) % 10 == 0 or len(local_records) == total:
                print(f"📊 進度: {len(local_records)}/{total}")

        except Exception as e:
            print(f"\n❌ 失敗: {e}")

    if local_records:
        script_dir = Path(__file__).resolve().parent
        current_time_str = datetime.now(TW_TZ).strftime("%Y%m%d_%H%M%S")
        output_filename = f"course_labeling_result_{current_time_str}.json"
        output_filepath = script_dir / output_filename

        with open(output_filepath, "w", encoding="utf-8") as f:
            json.dump(local_records, f, ensure_ascii=False, indent=4)

        print("\n🎉 全部完成！")
        print(f"1. 資料庫 course 已更新 (course_id: {target_ids})")
        print(f"2. 本地報告: {output_filepath}")
    else:
        print("\n⚠️ 本次沒有產生任何結果，未儲存檔案。")

# ==========================================
# 6. 主程式入口
# ==========================================
if __name__ == "__main__":
    # 在此填入要貼標的 course_id
    test_ids = [
        141,
    ]

    if not test_ids:
        print("⚠️ 請在 test_ids 中填入要測試的 course_id，或改用 run_course_random_batch.py 隨機批次。")
    else:
        process_specific_courses(test_ids)
