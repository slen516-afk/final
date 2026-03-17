import json
from openai import OpenAI
from typing import Dict, Any
from src.common.logger import setup_logger

logger = setup_logger()

class CareerLLMAdvisor:
    """
    負責生成職缺推薦理由、優劣勢分析與面試建議。
    """
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def generate_job_insights(
        self,
        job_title: str,
        user_6d: dict,
        job_6d: dict,
        match_score: str,
        job_description: str = "",
        job_requirements: str = "",
        resume_summary: str = "",
    ) -> Dict[str, Any]:
        """
        職缺落差分析並產出 JSON。

        Args:
            job_title:        目標職缺名稱
            user_6d:          候選人六維能力分數 dict
            job_6d:           職缺六維能力要求 dict
            match_score:      系統計算的百分比契合度字串
            job_description:  職缺描述原文（RAG 上下文）
            job_requirements: 職缺條件原文（RAG 上下文）
            resume_summary:   候選人履歷摘要原文（RAG 上下文）
        """
        system_prompt = """
        你是一位頂級的科技業獵頭與職涯顧問。
        請根據候選人的履歷內容、職缺描述，以及雙方的六維能力對比，進行個人化的差距分析。
        你的建議必須具體、有針對性，不能使用空洞的泛化語言。
        請務必以 JSON 格式回傳，必須包含以下四個 key (皆為字串)：
        1. "recommendation_reason": 推薦此職缺的核心理由，需結合候選人的具體背景 (約 60 字)
        2. "strengths": 候選人應徵此職缺的最大優勢，需引用履歷中的具體技能或經驗 (約 60 字)
        3. "weaknesses": 候選人較缺乏、需要補足的部分，需對應職缺的具體要求 (約 60 字)
        4. "interview_tips": 針對落差給予一項具體的面試準備建議，需提到具體技術或技能名稱 (約 60 字)
        """

        # --- 動態組裝 RAG 上下文區塊（有值才顯示）---
        resume_block = f"""\n        【候選人履歷摘要】:\n        {resume_summary}""".rstrip() if resume_summary else ""
        jd_block = f"""\n        【職缺描述摘要】:\n        {job_description}""".rstrip() if job_description else ""
        req_block = f"""\n        【職缺要求條件】:\n        {job_requirements}""".rstrip() if job_requirements else ""

        user_prompt = f"""
        【目標職缺】: {job_title}
        【系統演算契合度】: {match_score}
        {resume_block}
        {jd_block}
        {req_block}

        【候選人六維能力分數 (滿分 5 分)】:
        {json.dumps(user_6d, ensure_ascii=False)}

        【職缺六維能力要求 (滿分 5 分)】:
        {json.dumps(job_6d, ensure_ascii=False)}

        請根據候選人的履歷內容與職缺描述，給出個人化的差距分析與具體建議。
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                response_format={ "type": "json_object" },
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5
            )
            
            result_json = response.choices[0].message.content

             # === [新增獨立的 JSON 稽核紀錄] ===
            audit_folder = "logs/crewai_outputs"
            import os
            from datetime import datetime
            if not os.path.exists(audit_folder):
                os.makedirs(audit_folder)
            
            audit_data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "agent_name": "CareerLLMAdvisor (OpenAI API)",
                "task_description": f"產出職缺匹配洞察與建議 (目標職缺: {job_title})",
                "final_output": result_json
            }
            with open(os.path.join(audit_folder, "task_audit_trail.log"), "a", encoding="utf-8") as f:
                f.write(json.dumps(audit_data, ensure_ascii=False, indent=4) + "\n" + "="*50 + "\n")
            # =================================

            return json.loads(result_json)
            
        except Exception as e:
            print(f"⚠️ LLM 生成洞察失敗: {e}")
            return {
                "recommendation_reason": "系統分析中...",
                "strengths": "無",
                "weaknesses": "無",
                "interview_tips": "無"
            }
