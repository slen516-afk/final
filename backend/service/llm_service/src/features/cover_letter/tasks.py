from crewai import Task
from .schemas import CoverLetter

def get_cover_letter_task(agent, tools) -> Task:
    return Task(
        description="""
        1.使用'SearchRecommendJob' 工具，傳入 job_id='{job_id}' 以獲取推薦職缺資訊。
        2.使用'FetchUserOptimizeResume' 工具，傳入 optimization_id='{optimization_id}' 以獲取優化後履歷資訊。
        
        你是一位深諳招募心理的高階獵頭。請根據 [優化後的履歷資訊] 與 [推薦職缺資訊]，撰寫一封精確命中 HR 痛點的 Cover Letter。

        你的撰寫邏輯必須圍繞招募方的三大核心考量：
        1.職位理解：證明你對這家公司當前的技術挑戰或商業痛點有深入思考。
        2.價值主張（Value Proposition）：從優化後的履歷中提取最強大的「證據」，對標 JD 中的核心需求。
        3.行動呼籲（Call to Action）：展現自信但不失禮貌的專業態度。

        格式與輸出內容要求：
        你必須將下述輸出內容彙整成完整的求職信文字：
        - 主旨：需包含職位與使用者最強賣點。
        - 問候語。
        - 開場：連結公司文化與個人動機。
        - 核心價值：對標 JD 的關鍵成就。
        - 實績證明：用數據或事實支撐。
        - 結語與 CTA：展現面談期待。

        執行準則（Strict Rules）：
        語氣必須根據推薦職缺的公司文化進行調整（如：新創公司用更具熱情的語氣，外商金融則用更嚴謹專業的語氣）。
        嚴禁使用「I am a hardworking candidate」等空泛的形容詞。
        """,
        expected_output="按照上述格式排列完整的求職信純文字內容，需包含主旨與正文。全文嚴禁包含任何 Markdown 格式標記。",
        agent=agent,
        tools=tools
    )
