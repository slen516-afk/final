import os
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path
import json

# ==========================================
# 🔧 強制載入 .env
# ==========================================
current_file_path = Path(__file__).resolve()
backend_dir = current_file_path.parent.parent
env_path = backend_dir / '.env'
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ [LLM Service] 嚴重錯誤：找不到 GEMINI_API_KEY，請檢查 .env 檔案")
else:
    genai.configure(api_key=api_key)

# ==========================================
# 1. 履歷分析功能 (上傳 PDF/圖片用)
# ==========================================
def generate_resume_advice(resume_text):
    """
    接收履歷文字，回傳結構化的 JSON 資料 (包含評分、職缺、專案推薦)。
    """
    print(f"[LLM Service] 收到履歷文字，正在進行 JSON 結構化分析...")

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')

        prompt = f"""
        你是一位專業的資深技術獵頭與職涯教練。
        以下是求職者的履歷內容（OCR 辨識結果）：
        ---
        {resume_text}
        ---
        
        請根據以上內容，提供全面的職涯分析。
        
        ⚠️ **非常重要：請務必只回傳純 JSON 格式字串，不要使用 Markdown (如 ```json)，也不要包含其他開場白或結尾文字。**
        
        JSON 資料結構必須嚴格遵守以下格式：
        {{
            "analysis": {{
                "score": (0-100的整數),
                "strengths": ["優點1", "優點2", "優點3"],
                "weaknesses": ["弱點1", "弱點2"],
                "overall_comment": "一句話的整體簡短評語"
            }},
            "job_recommendations": [
                {{ 
                    "title": "推薦職稱 (例如：後端工程師)", 
                    "reason": "為什麼適合這個職位的理由",
                    "missing_skills": ["缺少的關鍵技能1", "缺少的關鍵技能2"]
                }},
                {{ "title": "另一個推薦職稱", "reason": "...", "missing_skills": [] }}
            ],
            "project_recommendations": [
                {{
                    "name": "推薦的 Side Project 名稱 (例如：電商庫存系統)",
                    "difficulty": "易 / 中 / 難",
                    "tech_stack": "建議使用的技術 (例如：React + Firebase)",
                    "description": "這個專案能如何補強履歷弱點的簡短說明"
                }},
                {{ "name": "另一個專案...", "difficulty": "...", "tech_stack": "...", "description": "..." }}
            ],
            "learning_path": [
                {{ "topic": "建議學習主題", "resource": "推薦資源關鍵字 (例如：Docker 官方文件)", "priority": "高/中/低", "url": "#" }}
            ]
        }}
        """

        response = model.generate_content(prompt)
        raw_text = response.text

        # 🧹 清理資料
        cleaned_text = raw_text.replace("```json", "").replace("```", "").strip()

        # 🔄 嘗試解析 JSON
        try:
            advice_json = json.loads(cleaned_text)
            print("[LLM Service] 履歷分析 JSON 解析成功！")
            return advice_json
        except json.JSONDecodeError as e:
            print(f"⚠️ [LLM Service] JSON 解析失敗: {e}")
            return {
                "analysis": {
                    "score": 0,
                    "strengths": [],
                    "weaknesses": [],
                    "overall_comment": "AI 回傳格式錯誤，請稍後重試。"
                },
                "raw_text": raw_text
            }

    except Exception as e:
        print(f"[LLM Service] 發生錯誤: {e}")
        return {"error": str(e)}


# ==========================================
# 2. 專案推薦功能 (Postman 手動查詢用)
# ==========================================
def generate_project_suggestions_from_skills(skills, interests):
    """
    根據使用者的技能 (List) 和興趣 (String) 推薦 Side Project
    """
    print(f"[LLM Service] 收到技能查詢: {skills}, 興趣: {interests}")
    
    # 轉成字串方便塞入 Prompt
    skills_str = ", ".join(skills) if isinstance(skills, list) else str(skills)
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')

        prompt = f"""
        你是一位技術導師。使用者想做 Side Project 來練習技術。
        
        使用者的技能樹：{skills_str}
        使用者的興趣領域：{interests}
        
        請推薦 2 個適合他的 Side Project。
        
        ⚠️ **請務必只回傳純 JSON 格式，不要有 Markdown。**
        格式如下：
        {{
            "projects": [
                {{
                    "name": "專案名稱",
                    "difficulty": "易/中/難",
                    "tech_stack": "建議技術堆疊",
                    "description": "簡短說明為何適合他"
                }},
                {{
                     "name": "專案名稱2",
                     "difficulty": "...",
                     "tech_stack": "...",
                     "description": "..."
                }}
            ]
        }}
        """
        
        response = model.generate_content(prompt)
        cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
        
        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError:
            return {"projects": [], "error": "AI 回傳格式解析失敗"}
            
    except Exception as e:
        print(f"AI 生成專案失敗: {e}")
        return {"projects": [], "error": str(e)}