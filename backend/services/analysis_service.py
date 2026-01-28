import re
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv  # 👈 新增這個：用來讀取 .env

# 1. 載入環境變數
load_dotenv()

# 2. 從環境變數讀取 Key (如果讀不到，會變成 None)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 設定 AI
try:
    if not GEMINI_API_KEY:
        raise ValueError("找不到 GEMINI_API_KEY，請檢查 .env 檔案")
        
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    print("✅ Gemini AI 模型載入成功！")
except Exception as e:
    print(f"⚠️ AI 設定失敗 (將切換至備用方案): {e}")
    model = None

# --- 備用方案：本地關鍵字比對邏輯 (Fallback) ---
COMMON_SKILLS_DB = {
    "react", "vue", "angular", "typescript", "javascript", "html", "css", "tailwind",
    "python", "django", "flask", "node.js", "express", "java", "spring", "go",
    "sql", "mysql", "postgresql", "mongodb", "redis",
    "docker", "kubernetes", "k8s", "aws", "gcp", "azure", "ci/cd", "git", "linux"
}

def extract_skills_regex(text):
    """備用的正則表達式提取法"""
    if not text: return set()
    text_lower = text.lower()
    found = set()
    for skill in COMMON_SKILLS_DB:
        pattern = r"(?:^|\s|[.,;(/])" + re.escape(skill) + r"(?:$|\s|[.,;)/])"
        if re.search(pattern, text_lower):
            found.add(skill)
    return found

def analyze_gap_fallback(resume_text, jd_text):
    """備用的分析函式"""
    print("⚠️ 執行本地關鍵字比對 (Fallback Mode)...")
    r_skills = extract_skills_regex(resume_text)
    j_skills = extract_skills_regex(jd_text)
    
    missing = list(j_skills - r_skills)
    matching = list(j_skills & r_skills)
    score = int((len(matching) / len(j_skills)) * 100) if j_skills else 0
    
    return {
        "missing_skills": missing,
        "matching_skills": matching,
        "score": score,
        "source": "Local Keyword Match (Fallback)"
    }

# --- 主要方案：AI 分析邏輯 ---

def analyze_gap(resume_text, jd_text):
    """
    優先使用 AI 分析，失敗則自動降級為關鍵字比對
    """
    # 如果沒設 Key 或內容太短，直接用舊方法
    if not model or not GEMINI_API_KEY or len(jd_text) < 10:
        return analyze_gap_fallback(resume_text, jd_text)

    prompt = f"""
    You are an expert ATS (Applicant Tracking System) scanner.
    
    Task: Compare the Candidate Resume with the Job Description (JD).
    
    Candidate Resume:
    {resume_text}
    
    Job Description:
    {jd_text}
    
    Output Format: JSON only. Do not output markdown code blocks.
    Structure:
    {{
        "missing_skills": ["skill1", "skill2"],
        "matching_skills": ["skill3", "skill4"],
        "score": 0-100 (integer, based on skill match percentage)
    }}
    
    Rules:
    1. Extract specific hard skills (tech stack, tools, languages).
    2. "missing_skills" are skills required in JD but NOT found in Resume.
    3. "matching_skills" are skills found in both.
    4. Be strict but understand synonyms (e.g. "k8s" == "Kubernetes").
    5. Translate output skills to English standard names (e.g. use "React" not "Reactjs").
    """

    try:
        # 呼叫 AI
        response = model.generate_content(prompt)
        response_text = response.text
        
        # 清理 AI 可能回傳的 Markdown 標記
        cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
        
        # 解析 JSON
        result = json.loads(cleaned_text)
        
        return {
            "missing_skills": result.get("missing_skills", []),
            "matching_skills": result.get("matching_skills", []),
            "score": result.get("score", 0),
            "source": "AI Analysis (Gemini)"
        }

    except Exception as e:
        print(f"❌ AI 分析出錯: {e}")
        # AI 掛掉時，自動切換回備用方案
        return analyze_gap_fallback(resume_text, jd_text)