import os
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

# ==========================================
# 🔧 強制載入 .env (解決找不到 Key 的問題)
# ==========================================
# 1. 抓出目前檔案的位置
current_file_path = Path(__file__).resolve()

# 2. 往上一層找到 backend 資料夾 (因為 .env 在 backend 底下)
backend_dir = current_file_path.parent.parent

# 3. 指定 .env 的完整路徑
env_path = backend_dir / '.env'

# 4. 載入！
load_dotenv(dotenv_path=env_path)

# 5. 檢查 Key 是否存在
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ [LLM Service] 嚴重錯誤：找不到 GEMINI_API_KEY，請檢查 .env 檔案")
else:
    # 設定 API Key
    genai.configure(api_key=api_key)
# ==========================================

def generate_resume_advice(resume_text):
    """
    接收履歷文字，使用 Google Gemini 進行深度分析並提供建議。
    """
    print(f"[LLM Service] 收到文字，長度：{len(resume_text)} 字")

    try:
        # 使用你帳號支援的最新模型 (解決 404 錯誤)
        model = genai.GenerativeModel('gemini-2.0-flash')

        prompt = f"""
        你是一位資深的職涯顧問與履歷優化專家。請針對使用者的履歷內容進行分析。
        你的回應必須包含以下三個部分，並使用 Markdown 格式：
        
        1. **【優點分析】**：找出這份履歷做得好的地方 (2-3 點)。
        2. **【關鍵問題】**：指出履歷中致命的缺點或不夠好的地方 (例如：缺乏量化數據、排版混亂、技能描述模糊)。
        3. **【具體修改建議】**：提供 3-5 條具體的修改建議，告訴使用者該怎麼改寫會更吸引 HR。
        
        語氣要專業、鼓勵人心但針針見血。
        
        以下是使用者的履歷內容：
        {resume_text}
        """

        response = model.generate_content(prompt)

        advice = response.text
        print("[LLM Service] 建議生成完成！")
        return advice

    except Exception as e:
        print(f"[LLM Service] 發生錯誤: {e}")
        return f"AI 分析失敗: {str(e)}"