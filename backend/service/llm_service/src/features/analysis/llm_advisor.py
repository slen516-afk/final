# llm_advisor.py
import json
from openai import OpenAI
from typing import Dict, Any

class CareerLLMAdvisor:
    """
    負責生成職缺推薦理由、優劣勢分析與面試建議的 AI 顧問模組。
    """
    def __init__(self, api_key: str):
        # 初始化 OpenAI Client
        self.client = OpenAI(api_key=api_key)

    def generate_job_insights(self, job_title: str, user_6d: dict, job_6d: dict, match_score: str) -> Dict[str, Any]:
        """
        傳入職缺名稱、雙方 6 維分數與總分，請 LLM 進行深度 Gap Analysis。
        """
        # 建立給 LLM 的系統人設與強迫 JSON 輸出的指令
        system_prompt = """
        你是一位頂級的科技業獵頭與職涯顧問。
        請根據候選人的六維能力分數，以及職缺的六維能力要求，進行客觀的差距分析。
        請務必以 JSON 格式回傳，必須包含以下四個 key (皆為字串)：
        1. "recommendation_reason": 推薦此職缺的核心理由 (約 50 字)
        2. "strengths": 候選人應徵此職缺的最大優勢 (約 50 字)
        3. "weaknesses": 候選人較缺乏，需要補足的劣勢 (約 50 字)
        4. "interview_tips": 針對此落差，給予一項具體的面試準備建議 (約 50 字)
        """

        # 組合使用者的具體狀況
        user_prompt = f"""
        【目標職缺】: {job_title}
        【系統演算契合度】: {match_score}

        【候選人現有能力 (滿分 5 分)】:
        {json.dumps(user_6d, ensure_ascii=False)}

        【職缺要求能力 (滿分 5 分)】:
        {json.dumps(job_6d, ensure_ascii=False)}

        請分析上述落差並給出客觀建議。
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini", # 使用 4o-mini 速度最快且便宜，適合做這類結構化分析
                response_format={ "type": "json_object" },
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7
            )
            
            # 將 LLM 回傳的 JSON 字串轉為 Python 字典
            result_json = response.choices[0].message.content
            return json.loads(result_json)
            
        except Exception as e:
            print(f"⚠️ LLM 生成洞察時發生錯誤: {e}")
            # 防呆機制：如果 API 失敗，回傳預設的空字串，不要讓整個系統崩潰
            return {
                "recommendation_reason": "系統分析中...",
                "strengths": "無",
                "weaknesses": "無",
                "interview_tips": "無"
            }