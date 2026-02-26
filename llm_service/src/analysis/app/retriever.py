# app/retriever.py

# 在真實專案中，這裡會使用 SQL 資料庫
# 這裡模擬一個簡單的資料庫查詢類別

class ResumeRetriever:
    def __init__(self, db_connection=None):
        self.db = db_connection # 假設這是你的資料庫連線物件

    def get_resume_text_by_user(self, user_id: str) -> str:
        """
        從關聯式資料庫 (RDBMS) 撈取使用者的完整履歷文字
        """
        print(f"[系統日誌] 正在從 SQL 資料庫查詢 User: {user_id} 的履歷...")

        # --- 模擬 SQL 查詢 ---
        # sql = "SELECT content FROM user_resumes WHERE user_id = %s"
        # cursor.execute(sql, (user_id,))
        # result = cursor.fetchone()
        
        # 為了測試，我們還是回傳之前的假資料，但在邏輯上這是從 DB 來的
        if user_id == "test_user_bio_001":
            return """
【個人簡介】
國立陽明交通大學 生物醫學工程碩士畢業。擁有 2 年生醫資料分析經驗，熟悉 Python 與 R 語言。
目前正積極尋求 Data Scientist 職位，希望能將領域知識結合機器學習技術，解決醫療產業問題。

【工作經歷】
1. 生醫數據研究助理 | 台北榮總實驗室 (2023/06 - 至今)
   - 負責分析次世代定序 (NGS) 數據，使用 R 語言進行資料清洗與統計檢定。
   - 使用 Python (Pandas, Matplotlib) 建立自動化報表。

【技能清單】
- 程式語言：Python (熟練), R (中等)
"""
        else:
            return "" # 查無資料