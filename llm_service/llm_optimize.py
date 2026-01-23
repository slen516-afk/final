import time
import os
# from openai import OpenAI # 如果你之後要接 OpenAI，就把這行解開

def generate_resume_advice(resume_text):
    """
    這個函式負責接收履歷文字，丟給 AI，並回傳優化建議。
    """
    print(f"[LLM Service] 收到文字，長度：{len(resume_text)} 字")

    # -----------------------------------------------------
    # TODO (未來): 在這裡貼上你原本呼叫 LLM 的程式碼
    # client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    # response = client.chat.completions.create(...)
    # advice = response.choices[0].message.content
    # -----------------------------------------------------

    # --- 模擬運算過程 (假裝 AI 在思考) ---
    time.sleep(2)

    # --- 暫時回傳的假建議 ---
    advice = f"""
    【AI 優化建議】
    針對您上傳的內容：
    "{resume_text[:20]}..."
    
    1. 建議將「技能」部分條列式呈現，會更清晰。
    2. 專案經驗可以多增加量化數據（例如：提升了 30% 效率）。
    3. 這是一個很棒的開始！
    """

    print("[LLM Service] 建議生成完成！")
    return advice