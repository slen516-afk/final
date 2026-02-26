import os
import time
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List
from dotenv import load_dotenv
import json

# Supabase & LangChain
from supabase import create_client, Client
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field, field_validator

# 定義六大職類
ROLE_NAME_MAPPING = {
    "A": "前端工程師",
    "B": "後端工程師",
    "C": "全端工程師",
    "D": "資料科學家/數據分析師",
    "E": "AI/演算法工程師",
    "F": "DevOps/SRE工程師"
}

# ==========================================
# 1. 初始化環境
# ==========================================
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") # 建議使用 service_role key 以確保寫入權限
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY]):
    raise ValueError("❌ 請檢查 .env 檔案，缺少必要的 API Key 或 URL")

# 初始化客戶端
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
llm = ChatOpenAI(model="o3-mini") 
TW_TZ = ZoneInfo("Asia/Taipei")

# ==========================================
# 2. 定義輸出 Schema (依照規格書定義)
# ==========================================
class JobCompetencyVector(BaseModel):
    role_type: str = Field(
        description="職缺所屬的角色代碼，必須是 A, B, C, D, E, F 其中之一"
    )
    role_name: str = Field(description="角色名稱，例如：後端工程師")
    
    # 定義六維能力分數 (Competency Vector)
    d1_frontend: float = Field(description="D1 前端工程能力要求 (1.0-5.0)")
    d2_backend: float = Field(description="D2 後端工程能力要求 (1.0-5.0)")
    d3_devops: float = Field(description="D3 雲端維運能力要求 (1.0-5.0)")
    d4_ai_data: float = Field(description="D4 AI與數據能力要求 (1.0-5.0)")
    d5_quality: float = Field(description="D5 品質與架構能力要求 (1.0-5.0)")
    d6_soft_skills: float = Field(description="D6 軟實力與商業思維要求 (1.0-5.0)")
    
    reasoning: str = Field(description="簡短說明為什麼給出這些分數的理由")

    @field_validator('role_type') # 欄位驗證：將下方的方法綁訂到指定的欄位
    @classmethod # field_validator 裝飾器需要搭配 classmethod 使用，驗證邏輯被類別本身綁定，而非特定實例。
    def validate_role_type(cls, v): # cls 代表這個類別本身，v 代表被驗證的值
        if v not in ['A', 'B', 'C', 'D', 'E', 'F']:
            raise ValueError("Role type must be one of A, B, C, D, E, F")
        return v

    # 驗證分數範圍
    @field_validator('d1_frontend', 'd2_backend', 'd3_devops', 'd4_ai_data', 'd5_quality', 'd6_soft_skills')
    @classmethod
    def check_score_range(cls, v):
        if not (1.0 <= v <= 5.0):
            # 容許一點誤差，強制修正
            return max(1.0, min(v, 5.0))
        return v

# 建立 Parser：將上面的規則掛載到 LangChain 的解析器上
parser = JsonOutputParser(pydantic_object=JobCompetencyVector)
# pydantic_object: LangChain 在定義解析器時的固定命名參數

# ==========================================
# 3. 定義 Prompt (核心腦袋)
# ==========================================
system_prompt_text = """
你是一位擁有 15 年經驗的「軟體工程架構師」與「資深技術評量專家」。你精通 IEEE SWEBOK (軟體工程知識體系)、SFIA (全球資訊技能標準) 以及 Dreyfus 技能習得模型。

你的核心任務是穿透職缺表象，識別出該職位的真實技術深度，並將其量化為「六維能力向量」。

請分析提供給你的「職缺名稱 (Job Title)」、「職缺描述 (Job Description)」、「技能需求 (Requirements)」，並將其轉化為 IEEE SWEBOK 標準下的「六維能力向量 (D1-D6)」。

# Conflict Resolution Protocol (衝突處理協議 - 關鍵！)
# 評分權重指引
1. **D1-D4 (硬實力)**：請**優先依據「技能需求 (Requirements)」**評分。若需求中明確列出 "Kubernetes" 或 "High Concurrency"，則 D3/D2 應給高分；若僅在描述中帶過，信心度較低。
2. **D5-D6 (軟實力/架構)**：請**優先依據「職缺描述 (Job Description)」**評分。從日常職責中判斷是否需要帶人 (Lead)、Code Review 或跨部門溝通。
3. **事實基準 (Ground Truth)**：當職缺名稱與描述內容存在落差時（例如：標題為「資深/架構師」，但內容僅要求基礎 CRUD），**請絕對以「職缺描述 (JD)」中的具體技術要求為準**。
4. **標題校正**：職缺名稱僅作為「預期薪資等級」或「團隊定位」的參考。不要因為標題有 "Senior" 就自動給高分，必須要在 JD 中看到對應的「架構設計」、「效能優化」或「指導他人」的具體職責才可給分。
5. **模糊推論**：若 JD 寫得非常簡略（例如只寫「熟悉 Java」），請參考標題來進行保守推估，但必須將信心分數 (Confidence Score) 調低。

# Dimensions Definitions (維度定義)
請依據以下標準評分 (1.0: 基礎認知 ~ 5.0: 專家/架構師)：
1. **D1 前端工程 (Frontend)**: 涵蓋 UI 實作、瀏覽器渲染原理、UX。若 JD 出現未列出的現代框架，請依據其生態系地位自行歸類。
2. **D2 後端工程 (Backend)**: 涵蓋 API 設計、資料庫設計、高併發處理。
3. **D3 雲端維運 (DevOps/SRE)**: 涵蓋 Docker/K8s、CI/CD、雲端架構 (AWS/GCP)。
4. **D4 AI與數據 (AI & Data)**: 涵蓋 ETL、Python 數據分析、RAG/LLM 應用、機器學習模型。
5. **D5 品質與架構 (Quality)**: 涵蓋單元測試、設計模式 (Design Patterns)、SOLID 原則、資安意識。
   * 注意：這是區分 Senior 的關鍵。若 JD 強調 "Clean Code" 或 "Refactoring"，此項應高分。
6. **D6 軟實力 (Soft Skills)**: 涵蓋溝通協作、Agile/Scrum 流程、商業思維。

同時，請判斷該職缺最接近哪一個角色分類 (A-F)：
- **A**: 前端工程師
- **B**: 後端工程師
- **C**: 全端工程師
- **D**: 資料科學家/數據分析師
- **E**: AI/演算法工程師
- **F**: DevOps/SRE

**評分原則**：
- 請嚴格基於 JD 內容進行推斷。
- 若 JD **未提及**某項技能，請給予該職位類型的「預設基礎分」(通常是 1.0，若是全端則可能是 1.5)。
- 若 JD 提到「加分項目 (Nice to have)」，可酌量加 0.5 分。

{format_instructions}
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt_text),
    ("user", """
    職缺標題：{job_title}
    
    【職缺描述 (Responsibilities)】：
    {job_description}
    
    【技能需求 (Requirements)】：
    {requirements}
    """)
])

chain = prompt | llm | parser

# ==========================================
# 4. 執行函數 (指定 ID)
# ==========================================
def process_specific_jobs(target_ids: List[str], table_name="job_posting"):
    print(f"🎯 準備處理指定的 {len(target_ids)} 筆職缺...")
    
    # 關鍵步驟：使用 .in_() 只撈取指定的 ID
    response = supabase.table(table_name)\
        .select("*")\
        .in_("job_id", target_ids)\
        .is_("d1_frontend", "null")\
        .execute()
    
    jobs = response.data
    
    if not jobs:
        print("❌ 找不到任何對應的 ID，請檢查 ID 是否正確。")
        return

    print(f"✅ 成功撈取 {len(jobs)} 筆資料，開始分析...\n" + "="*50)

    # 用於儲存要寫入本地 JSON 的完整紀錄
    local_records = []

    for job in jobs:
        current_id = job.get('job_id')
        title = job.get('job_title', job.get('title', 'Unknown')) # 容錯
        desc = job.get('job_description', job.get('description', ''))
        req = job.get('requirements', job.get('requirements', ''))
        
        print(f"正在分析 ID: {current_id} | {title} ...", end="", flush=True)

        start_t = time.time()
        
        try:
            # 1. AI 分析
            result = chain.invoke({
                "job_title": title,
                "job_description": desc,
                "requirements": req,
                "format_instructions": parser.get_format_instructions()
            })

            detected_type = result["role_type"]
            standardized_name = ROLE_NAME_MAPPING.get(detected_type, "未定義角色")

            # 計算耗時與當下時間
            end_t = time.time()
            duration_sec = round(end_t - start_t, 2) # 執行花費時間 (秒)
            processed_time = datetime.now(TW_TZ).isoformat()
            
            # -------------------------------------------------------
            # 軌道 A: 寫入 Supabase (只取 DB 有的欄位)
            # -------------------------------------------------------
            db_payload = {
                "role_type": result["role_type"],
                "role_name": standardized_name,
                "d1_frontend": result["d1_frontend"],
                "d2_backend": result["d2_backend"],
                "d3_devops": result["d3_devops"],
                "d4_ai_data": result["d4_ai_data"],
                "d5_quality": result["d5_quality"],
                "d6_soft_skills": result["d6_soft_skills"]
                # 注意：這裡不包含 reasoning 與 processed_at
            }
            
            supabase.table(table_name).update(db_payload).eq("job_id", current_id).execute()
            
            # -------------------------------------------------------
            # 軌道 B: 儲存至本地 List (包含完整資料)
            # -------------------------------------------------------
            full_record = {
                "job_id": current_id,
                "job_title": title,
                **result,  # 這包含 reasoning, d1-d6, role...
                "processed_at": processed_time,
                "execution_duration_seconds": duration_sec # 跑了多久 (3.5s)
            }
            local_records.append(full_record)

            print(f" [完成] 耗時 {duration_sec}s -> {standardized_name}")
            
            duration = round(time.time() - start_t, 2)
            print(f" [完成] 耗時 {duration}s -> {standardized_name}")

        except Exception as e:
            print(f"\n❌ 失敗: {e}")

    # -------------------------------------------------------
    # 最終步驟: 將完整紀錄寫入本地 JSON 檔案
    # -------------------------------------------------------
    if local_records:
        # 1. 取得目前這支程式 (.py) 所在的資料夾絕對路徑
        current_script_dir = os.path.dirname(os.path.abspath(__file__))
        # 檔名範例: labeling_result_20231027_153001.json
        current_time_str = datetime.now(TW_TZ).strftime("%Y%m%d_%H%M%S")
        output_filename = f"labeling_result_{current_time_str}.json"
        
        # 3. 組合完整的路徑 (資料夾 + 檔名)
        output_filepath = os.path.join(current_script_dir, output_filename)

        with open(output_filepath, "w", encoding="utf-8") as f:
            json.dump(local_records, f, ensure_ascii=False, indent=4)
            
        print(f"\n🎉 全部完成！")
        print(f"1. 資料庫更新完畢 (IDs: {target_ids})")
        print(f"2. 本地完整報告已存為獨立檔案: {output_filepath}") # 確保不會覆蓋舊檔
    else:
        print("\n⚠️ 本次沒有產生任何結果，未儲存檔案。")

# ==========================================
# 5. 主程式入口
# ==========================================
if __name__ == "__main__":
    # 【請在這裡填入你想測試的 10 筆 ID】
    # 你可以去 Supabase Table Editor 複製 10 個 ID 過來
    test_ids = [
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20
    ]
    
    # 防呆機制：如果忘記填 ID，提醒使用者
    if "貼上你的ID_1" in test_ids:
        print("⚠️ 請先在程式碼最下方的 'test_ids' 列表中填入真實的 Job ID！")
    else:
        process_specific_jobs(test_ids)