import json
from openai import OpenAI
from typing import Dict, Any

class CareerLLMAdvisor:
    """
    負責生成職缺推薦理由、優劣勢分析與面試建議。
    """
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def generate_job_insights(self, job_title: str, user_6d: dict, job_6d: dict, match_score: str) -> Dict[str, Any]:
        """
        職缺落差分析並產出 JSON。
        """
        system_prompt = """
        你是一位頂級的科技業獵頭與職涯顧問。
        請根據候選人的六維能力分數，以及職缺的六維能力要求，進行客觀的差距分析。
        請務必以 JSON 格式回傳，必須包含以下四個 key (皆為字串)：
        1. "recommendation_reason": 推薦此職缺的核心理由 (約 50 字)
        2. "strengths": 候選人應徵此職缺的最大優勢 (約 50 字)
        3. "weaknesses": 候選人較缺乏，需要補足的劣勢 (約 50 字)
        4. "interview_tips": 針對此落差，給予一項具體的面試準備建議 (約 50 字)
        """

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
                model="gpt-4o-mini",
                response_format={ "type": "json_object" },
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7
            )
            
            result_json = response.choices[0].message.content
            return json.loads(result_json)
            
        except Exception as e:
            print(f"⚠️ LLM 生成洞察失敗: {e}")
            return {
                "recommendation_reason": "系統分析中...",
                "strengths": "無",
                "weaknesses": "無",
                "interview_tips": "無"
            }
