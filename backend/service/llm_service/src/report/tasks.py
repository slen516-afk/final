# tasks.py
import json
import datetime
from crewai import Task
from src.features.analysis.schemas import CareerReport

class CareerTaskFactory:

    # 定義共用的 Mapping 指令 (避免重複寫)
    MAPPING_INSTRUCTION = """
    **Radar Chart Mapping Rules (Strictly Follow)**:
    請將工具計算出的 D1-D6 分數映射為以下中文名稱：
    - D1 -> "前端開發"
    - D2 -> "後端開發"
    - D3 -> "運維部署"
    - D4 -> "AI與數據"
    - D5 -> "工程品質"
    - D6 -> "軟實力"
    
    注意：
    - 如果輸入資料是 Entry Level (無經驗)，Technical dimensions (前四項) 請直接使用 0.5 或 1.0。
    - 請確保 `radar_chart.dimensions` 陣列中剛好包含這 6 個項目，順序不拘。
    """

    # ★ 新增：標準職稱定義 (與 Schema 一致)
    STANDARD_ROLES_STR = "前端工程師, 後端工程師, 全端工程師, 資料科學家, AI 工程師, DevOps/SRE 工程師"

    # ★ 輔助函式：產生 ISO 時間字串
    @staticmethod
    def get_current_iso_time():
        # 產生類似 '2026-02-06T13:36:07.158Z' 的格式
        return datetime.datetime.utcnow().isoformat(timespec='milliseconds') + "Z"

    # ★ 輔助函式：嘗試從字串中解析 user_id
    @staticmethod
    def extract_user_id(inputs):
        try:
            # 嘗試從 survey_json 或 trait_json 解析 user_id
            if 'survey_json' in inputs:
                data = json.loads(inputs['survey_json'])
                return data.get('user_id', 'unknown_user')
            elif 'trait_json' in inputs:
                data = json.loads(inputs['trait_json'])
                return data.get('user_id', 'unknown_user')
        except:
            return "unknown_user"
        return "unknown_user"
    
    # --- Group A: 有經驗者的任務 ---
    @staticmethod
    def tech_analysis(agent, inputs):
        return Task(
            description=f"""
            1. 計算問卷分數: {inputs['survey_json']}
            2. 計算與目標 '{inputs['target_role']}' 的匹配度。
            3. 履歷驗證: {inputs['resume_json']}
            產出技術備忘錄。
            """,
            expected_output="技術評估報告",
            agent=agent
        )

    @staticmethod
    def psych_analysis(agent, inputs):
        return Task(
            description=f"""
            分析特質數據: {inputs['trait_json']}
            
            **核心任務**:
            1. 根據使用者的分數 (Structure, Ambiguity...)，對照你的「核心分析理論」。
            2. **情境模擬**: 
               - 如果是 High Structure，他在寫 Code 時會有什麼優勢？(例如：變數命名規範、模組化設計)
               - 如果是 Low Ambiguity，他在 Debug 時會遇到什麼困難？
            3. **職位適配性**: 根據特質分數，驗證他與目標職位 (或推薦職位) 的匹配程度。
            """,
            expected_output="一份關於使用者學習潛力與認知特質的分析報告。",
            agent=agent
        )

    @staticmethod
    def final_report_experienced(agent, context_tasks, inputs=None):
        # 註：需要在 main.py 呼叫時傳入 inputs，如果沒傳就用預設值
        current_time = CareerTaskFactory.get_current_iso_time()
        user_id = CareerTaskFactory.extract_user_id(inputs) if inputs else "unknown"

        return Task(
            description=f"""
            綜合技術與心理分析，生成 CareerReport JSON。
            
            {CareerTaskFactory.MAPPING_INSTRUCTION}

            **Metadata Instructions (MANDATORY)**:
            請務必在 `report_metadata` 欄位填入以下精確數值：
            - `user_id`: "{user_id}"
            - `timestamp`: "{current_time}"
            - `version`: "1.0"
            
            **寫作重點**:
            1. 根據 D1-D6 的真實高分項，強調技術優勢。
            2. Action Plan 需包含進階技術關鍵字 (如 K8s, Microservices)。
            3. **Preliminary Summary**: 必須結合特質分析。例如：「陳先生具備極高的架構力 (Structure 95)，這使他是天生的後端架構師人選...」
            4. **Gap Analysis**: 
               - 在 `gap_description` 欄位中，引用 Psychologist 的理論。例如：「雖然您技術力強，但模糊耐受度較低 (Ambiguity 28)，建議避開需求變動劇烈的新創公司，選擇制度完善的企業。」
            5. **Radar Chart**: 確保軟實力分數反映了特質分析的結果。
            """,
            expected_output="CareerReport JSON",
            agent=agent,
            context=context_tasks,
            output_pydantic=CareerReport
        )

    # --- Group B: 無經驗者的 Mentor 任務 --- 專注於「挖掘」而非「寫報告
    @staticmethod
    def discovery_analysis(agent, inputs):
        # 判斷有無目標職位，調整 Prompt
        target_instruction = ""
        if inputs.get('target_role'):
             target_instruction = f"使用者已選定目標：{inputs['target_role']}。請驗證其適配性。"
        else:
             target_instruction = "使用者未定目標。請從六大職類中推薦一個最適合的。"

        return Task(
            description=f"""
            分析使用者資料：
            1. Resume: {inputs['resume_json']} (重點關注非技術經驗)
            2. Survey: {inputs['survey_json']}
            
            {target_instruction}
            
            **核心任務**：
            1. **Skill Translation (技能轉譯)**: 
               - 請找出履歷中至少 3 個具體的非技術行為（如：建立 SOP、處理 Excel 報表、跨部門溝通）。
               - 為每一個行為建立「程式設計概念」的對照。
               - **範例邏輯**：
                 * "制定請款流程 SOP" -> "演算法設計 (Algorithm Design) 與 邊界案例處理 (Edge Cases)"
                 * "Excel VLOOKUP/樞紐分析" -> "關聯式資料庫 (RDBMS) 與 聚合查詢 (Aggregation)"
                 * "Notion/Trello 專案管理" -> "模組化思維 (Modularity) 與 敏捷開發 (Agile)"
            
            2. **Role Recommendation (職位推薦)**:
               - 推薦職位必須是標準清單中的一個。
               - 說明理由時，請引用上述的轉譯分析，證明他為什麼適合。
               - **注意**：職位名稱必須嚴格遵守此清單：[{CareerTaskFactory.STANDARD_ROLES_STR}]。
               - 不要創造新名詞 (如 "後端軟體工程師" 是錯的，請用 "後端工程師")。
            """,
            expected_output="一份包含『技能轉譯對照表』與『職位推薦理由』的詳細備忘錄 (Memo)。",
            agent=agent,
        )
    
    # 新增無經驗者的最終報告任務 (給 Advisor)
    @staticmethod
    def final_report_entry_level(agent, context_tasks, inputs=None):
        return Task(
            description=f"""
            你是總編輯。請綜合 Mentor 的「技能轉譯」與 Psychologist 的「潛力分析」，生成最終的 CareerReport。
            
            {CareerTaskFactory.MAPPING_INSTRUCTION}

            **Metadata Instructions (MANDATORY)**:
            請務必在 `report_metadata` 欄位填入以下精確數值：
            - `user_id`: "{user_id}"
            - `timestamp`: "{current_time}"
            - `version`: "1.0"

            **寫作風格指南 (WRITING STYLE GUIDE - STRICT)**:
            為了讓報告豐厚且有溫度，請嚴格遵守以下寫作要求：
            1. **Preliminary Summary (豐厚化)**:
               - 不要只寫一句話。請寫一段約 80-100 字的完整段落。
               - 結構：[使用者核心特質] + [具體履歷亮點] + [對應的軟體潛力]。
               - 範例：「Alex 在行政管理中展現極高的結構化思維...這正好對應到後端工程對邏輯的嚴謹要求...」
            
            2. **Gap Analysis (敘事化)**:
               - **Target Role**: 必須格式化為 "領航員分析您適合的職類為 - [標準職位名稱]"。
               - **Gap Description**: 這是報告的靈魂。**請將 Mentor 的「技能轉譯」完整擴寫進來。**
               - **寫作模板**：「雖然您目前缺乏 [程式語言] 經驗，但您在 [舊工作] 中的 [具體行為]，實際上就是在執行 [軟體概念]。例如，您曾 [引用履歷細節]...這顯示您具備 [某種潛力]。」
               - 字數要求：至少 150 字。
            
            3. **Action Plan (具體化)**:
               - **Short-term**: 針對非本科系，建議從具體工具入手 (如: Python 基礎語法, SQL Select 查詢)。
               - **Mid-term**: 建議小型實作專案 (如: 將行政 Excel 流程改寫為 Python Script)。
               - **Long-term**: 建議系統性思維 (如: 資料庫設計, API 串接)。
               - 每一項都必須包含「為什麼要做這個」的理由。
            
            4. **Current Status**:
               - **Cognitive Bias**: 請 Psychologist 分析使用者是否因為非本科系而低估自己。
            

            **重要輸出格式**:
            1. **Target Role Formatting (FORMAT CHECK)**:
               - 檢查 Mentor 推薦的職位是否在標準清單內：[{CareerTaskFactory.STANDARD_ROLES_STR}]。如果不符，請修正為最接近的標準名稱。
               - **輸出格式**: 若使用者未指定目標，你 **必須** 將 `target_position.role` 欄位填寫為：
                 "領航員分析您適合的職類為 - [標準職位名稱]"
               - **範例**:
                 (O) Correct: "領航員分析您適合的職類為 - 後端工程師"
                 (X) Wrong: "後端工程師"
                 (X) Wrong: "領航員分析您適合的職類為 - 後端軟體工程師"
            
            2. **Radar Chart**: 
                - 技術維度 (前端/後端/運維/AI) 設定為 **0.5** (Entry Level Baseline)。
                - 軟實力與工程品質可根據特質給予 **1.0 ~ 2.0** 的潛力分。
            """,
            expected_output="一份內容豐厚、語氣詳實且符合 Schema 的 CareerReport JSON。",
            agent=agent,
            context=context_tasks, # 接收上面兩個任務的結果
            output_pydantic=CareerReport
        )