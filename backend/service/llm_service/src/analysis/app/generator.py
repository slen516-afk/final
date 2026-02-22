import json
import os
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from dotenv import load_dotenv
from .schemas import CareerReport

# 載入環境變數
load_dotenv()

class CareerReportGenerator:
    def __init__(self, model_name="o3-mini"):
        # 判斷模型名稱，如果是推理模型 (o1, o3)，就不能傳入 temperature
        if "o1" in model_name or "o3" in model_name:
            # 推理模型專用設定
            # o3-mini 支援 reasoning_effort 參數 (low, medium, high)
            # 預設 medium，如果你希望它思考深一點，可以設為 high
            self.llm = ChatOpenAI(
                model=model_name, 
                reasoning_effort="medium" 
            )
        else:
            # 一般模型 (gpt-4o, gpt-4o-mini) 需要設定 temperature
            self.llm = ChatOpenAI(
                model=model_name, 
                temperature=0.1
            )
            
        self.parser = PydanticOutputParser(pydantic_object=CareerReport)

    def generate_report(self, processed_data: dict, match_score: str, resume_content: str = "") -> dict:
        """
        接收 Python 計算好的向量資料與原始問卷，生成質性分析報告
        """
        # 定義 Few-Shot 範例：給 mini 模型看「標準答案」長什麼樣子
        # 這能大幅提升輸出的穩定性與專業度
        example_input = """
        [範例輸入]
        Target Role: Backend Engineer (Role B)
        Calculated Vectors: D1(2.0), D2(4.5), D3(1.0)
        Resume: "曾使用 Python Flask 開發電商 API，熟悉 MySQL。"
        """

        example_output = """
        [範例輸出邏輯]
        Current Status:
          self_assessment: "入門/轉職中 (Entry Level)"
          actual_level: "中階 (Mid-Level)"
        Target Position:
          role: "後端工程師 (Backend Engineer)"
          gap_description: "您的後端開發能力 (D2) 已達標，但嚴重缺乏雲端維運能力 (D3)，這在現代 DevOps 流程中是致命傷。"
        Action Plan:
          short_term: "學習 Docker 基礎指令，並嘗試將 Python 專案容器化。"
          mid_term: "學習 GitHub Actions，建立自動化 CI/CD 流程。"
          long_term: "深入研究 Kubernetes (K8s) 架構，並參與開源專案。"
        """

        # 1. 準備 Prompt
        # 我們將 PDF 中的「角色矩陣」與「分析原則」注入到 System Prompt 中
        system_template = """
        你是一位擁有 20 年經驗且極度嚴謹、數據導向的軟體工程職涯顧問與技術專家。
        你的任務是根據使用者的「量化能力向量 (Calculated Vectors)」與「原始問卷回答 (Raw Input)」，
        生成一份專業、具體且以繁體中文 (Traditional Chinese, Taiwan) 撰寫的職涯分析報告。

         ### 分析原則：
        1. **數據導向**：你的分析必須基於輸入的 D1-D6 分數。若分數與使用者的自評 (Q16) 不符，請直言不諱地指出「認知落差 (Cognitive Bias)」。
        2. **數據與經歷互證**：
           - 請將「問卷分數 (D1-D6)」與「履歷內容 (Resume)」進行交叉比對。
           - 例如：若 D2 後端分數低，但履歷上有後端專案，可能代表使用者缺乏自信（Cognitive Bias），請予以鼓勵並修正評價。
           - 若目標是 Data Scientist，請檢查履歷中是否有具體的數據分析專案或論文。
        3. **具體建議**：不要只說「加強後端」，要根據使用者填寫的 Q1 語言 (如 Python) 建議具體的生態系工具 (如 FastAPI, Celery)；或是根據履歷中提到的技術堆疊（如已會 Python/Django），推薦互補的技術（如建議學 Docker/K8s）等。
        4. **目標對齊**：Gap Analysis 必須針對使用者選擇的「目標職位 (Q17)」進行比較。
           - 若目標是 Data Scientist (Role D)，重點看 D4(數據) 與 D1(程式)。
           - 若目標是 Architect (Role E)，重點看 D5(品質) 與 D6(軟實力)。

        ### 格式規則 :
        1. **術語人性化 (Human-Readable Terms)**:
           - **嚴格禁止** 在描述中單獨使用 "D1", "D2" 等代號。
           - 必須結合或替換為中文名稱，例如：寫成 **"前端開發能力 (D1)"** 或直接寫 **"前端能力"**。
           - 參照表：
             D1: 前端開發 / D2: 後端開發 / D3: 雲端維運 / D4: AI與數據 / D5: 工程品質 / D6: 軟實力

        2. **中文轉譯規則 (Localization)**:
           - **self_assessment (自評職級)** 必須依據以下對照表轉譯：
             * entry_level -> "入門/轉職中 (Entry Level)"
             * junior -> "初階工程師 (Junior)"
             * mid_level -> "中階工程師 (Mid-Level)"
             * senior -> "資深工程師 (Senior)"
             * lead_architect -> "技術主管/架構師 (Lead)"
           - **role (目標職位)** 必須依據以下對照表轉譯：
             * frontend -> "前端工程師"
             * backend -> "後端工程師"
             * fullstack -> "全端工程師"
             * data_scientist -> "資料科學家"
             * ai_engineer -> "AI 工程師"
             * devops_sre -> "DevOps/SRE 工程師"

        3. **格式標準化 (Standardization)**:
           - **actual_level (實際職級)** 只能從以下 **四種** 格式中擇一輸出，不可創造新詞：
             * "入門 (Entry Level)"
             * "初階 (Junior)"
             * "中階 (Mid-Level)"
             * "資深 (Senior)"

        4. **行動計畫三部曲**:
           - **Short-term**: 針對技術債或基礎工具 (Tooling)。
           - **Mid-term**: 針對專案實作或進階框架 (Framework/Project)。
           - **Long-term**: 針對架構思維、軟實力或理論深化 (Architecture/Soft Skills)。

        ### 角色權重參考 (Role Matrix Standards):
        請參考以下六大標準職涯路徑的權重矩陣，用於計算與解釋 Gap：
        
        * **Role A - 前端工程師 (Frontend):**
          - D1(5.0), D2(1.5), D3(2.0), D4(1.0), D5(4.0), D6(3.5)
        
        * **Role B - 後端工程師 (Backend):**
          - D1(1.5), D2(5.0), D3(3.0), D4(1.5), D5(4.5), D6(3.5)
        
        * **Role C - 全端工程師 (Full Stack):**
          - D1(4.0), D2(4.0), D3(3.0), D4(2.0), D5(4.0), D6(4.0)
        
        * **Role D - 資料科學家 (Data Scientist):**
          - D1(1.0), D2(2.5), D3(2.0), D4(5.0), D5(3.0), D6(4.0)
        
        * **Role E - AI/演算法工程師 (AI Engineer):**
          - D1(1.0), D2(3.0), D3(2.5), D4(5.0), D5(4.0), D6(3.5)
        
        * **Role F - DevOps/SRE 工程師:**
          - D1(1.0), D2(3.5), D3(5.0), D4(2.0), D5(4.5), D6(4.0)

        請依據使用者選擇的目標職位（Target Role），對照上述標準分數。
        若使用者的某項分數低於標準分數 1.0 分以上，視為「顯著落差 (Significant Gap)」，需在建議中重點加強。

        ### 輸出格式：
        必須嚴格遵守 JSON 格式輸出。

        ### 嚴格規範 (Guardrails):
        - **禁止幻覺**：絕對不要自己重新計算分數或匹配度百分比，必須直接使用輸入的數值。
        - **格式要求**：輸出 **必須** 是純粹的 JSON 格式，不要包含 Markdown 標記 (如 ```json ... ```)。

        ### 學習範例 (Few-Shot Example):
        為了讓你了解語氣與深度，請參考以下範例邏輯：
        {example_input}
        {example_output}

        """

        human_template = """
        請分析以下使用者資料：

        ### 1. 數學模型計算結果 (Calculated Vectors)
        {vectors_json}

        ### 2. 真實匹配度計算 (Mathematical Match Score)
        目標職位: {target_role}
        匹配度: {match_score}

        ### 3. 使用者履歷 (Resume Context)
        {resume_content}

        ### 4. 使用者原始問卷 (Raw Input)
        {raw_input_json}

        請生成完整的 JSON 報告。
        \n{format_instructions}
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_template),
            ("human", human_template),
        ])

        chain = prompt | self.llm | self.parser

        vectors = processed_data.get("calculated_vectors", {})
        raw_input = processed_data.get("user_raw_input", {})
        
        # [修改點 2]: 從 raw_input 抓取目標職位名稱
        target_role = raw_input.get("module_c", {}).get("q17_target_role", "unknown")

        try:
            result = chain.invoke({
                "vectors_json": json.dumps(vectors, indent=2),
                "match_score": match_score,    # [修改點 3]: 傳入分數
                "target_role": target_role,
                "resume_content": resume_content,
                "raw_input_json": json.dumps(raw_input, indent=2, ensure_ascii=False),
                "format_instructions": self.parser.get_format_instructions(),
                "example_input": example_input,
                "example_output": example_output,
            })
            
            # Pydantic 物件轉回 Dict
            report_dict = result.dict()
            
            # --- 重要後處理 ---
            # LLM 有時會產生幻覺數字，我們強制用「數學計算好的分數」覆蓋回去
            # 確保前端雷達圖顯示的是精確計算值
            dimensions = [
                {"axis": "前端工程 (Frontend)", "score": vectors.get("D1", 0)},
                {"axis": "後端工程 (Backend)", "score": vectors.get("D2", 0)},
                {"axis": "雲端維運 (DevOps)", "score": vectors.get("D3", 0)},
                {"axis": "AI與數據 (AI/Data)", "score": vectors.get("D4", 0)},
                {"axis": "品質與架構 (Quality)", "score": vectors.get("D5", 0)},
                {"axis": "軟實力 (Soft Skills)", "score": vectors.get("D6", 0)},
            ]
            report_dict['radar_chart']['dimensions'] = dimensions
            
            # 補上 Metadata
            report_dict['report_metadata'] = {
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat(),
                "user_id": raw_input.get("user_id", "unknown")
            }

            return result.dict() # 記得這裡要包含你的 radar_chart 覆蓋邏輯

        except Exception as e:
            print(f"Error generating report: {e}")
            return {"error": str(e)}