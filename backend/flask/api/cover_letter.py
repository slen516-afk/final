from flask import Blueprint, request, jsonify
from crewai import Crew, LLM
import json

# 引入 agents, tasks, tools
from service.llm_service.src.features.cover_letter.agents import get_cover_letter_strategist_agent
from service.llm_service.src.features.cover_letter.tasks import get_cover_letter_task
from service.llm_service.src.features.cover_letter.tools import RecommendJobSearchTool, FetchOptimizeResumeTool

cover_letter_bp = Blueprint('cover_letter', __name__)

@cover_letter_bp.route('/generate', methods=['POST'])
def generate_cover_letter():
    """
    第一支 API: 生成 Cover Letter。
    前端傳入 : job_id, optimization_id 以及 LLM 模型參數 (如 model, temperature)
    回傳輸出結果給前端
    """
    try:
        data = request.get_json() or {}
        job_id = data.get("job_id")
        optimization_id = data.get("optimization_id")
        
        # 接收模型參數 (前端可傳入，預設給定 gpt-4o 與 temperature 0.7)
        model_name = data.get("model", "gpt-4o")
        temperature = data.get("temperature", 0.7)

        if not job_id or not optimization_id:
            return jsonify({"status": "error", "message": "缺少 job_id 或 optimization_id"}), 400

        # 初始化 Tools
        job_tool = RecommendJobSearchTool()
        resume_tool = FetchOptimizeResumeTool()
        tools = [job_tool, resume_tool]

        # 初始化 Agent，並傳入模型參數
        agent = get_cover_letter_strategist_agent()
        agent.llm = LLM(model=model_name, temperature=temperature)
        
        # 將工具傳遞給 Task
        task = get_cover_letter_task(agent, tools)
        
        # 替換提示詞內變數 (因為 tasks.py 內格式為 '{job_id}')
        task.description = task.description.replace('{job_id}', str(job_id)).replace('{optimization_id}', str(optimization_id))

        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True
        )

        print(f"開始執行 Cover Letter 生成任務...")
        result = crew.kickoff()
        raw_output = str(result.raw).strip()

        # 解析若是包裝成 JSON 格式或純文字回傳
        return jsonify({
            "status": "success",
            "data": raw_output
        }), 200

    except Exception as e:
        print(f"生成 Cover Letter 發生錯誤: {str(e)}")
        return jsonify({"status": "error", "message": "伺服器內部錯誤", "details": str(e)}), 500


@cover_letter_bp.route('/preview_data', methods=['POST'])
def preview_cover_letter_data():
    """
    第二支 API: 提供抓取預覽資料 (Preview)。
    回傳工具抓取的推薦職缺與優化履歷結果給前端，不進入 LLM 生成，便於驗證與檢視。
    """
    try:
        data = request.get_json() or {}
        job_id = data.get("job_id")
        optimization_id = data.get("optimization_id")

        if not job_id or not optimization_id:
            return jsonify({"status": "error", "message": "缺少 job_id 或 optimization_id"}), 400

        # 直接呼叫 Tool 的 run 來抓取資料
        job_info = RecommendJobSearchTool()._run(job_id=str(job_id))
        resume_info = FetchOptimizeResumeTool()._run(optimization_id=str(optimization_id))

        return jsonify({
            "status": "success",
            "job_data": job_info,
            "resume_data": resume_info
        }), 200

    except Exception as e:
        print(f"預覽發生錯誤: {str(e)}")
        return jsonify({"status": "error", "message": "伺服器內部錯誤", "details": str(e)}), 500
