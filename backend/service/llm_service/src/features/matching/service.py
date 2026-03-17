# src/features/matching/service.py
import concurrent.futures
from qdrant_client import QdrantClient
from typing import List, Dict, Any

# 匯入本模組的其他組件
from src.common.logger import setup_logger
logger = setup_logger()
from .qdrant_retriever import JobMatchRetriever, UserProfileRetriever
from .matcher import JobMatcher
from .advisor import CareerLLMAdvisor
from .schemas import JobMatchRequest, JobMatchingResponse

class CareerMatchingService:
    """
    職缺匹配模組的核心入口。
    負責協調 Qdrant、Supabase 與 AI 顧問，執行混合計分流程並產出前端 JSON。
    """
    def __init__(self, qdrant_client: QdrantClient, supabase_client: Any, openai_api_key: str):
        self.qdrant_client = qdrant_client
        self.supabase_client = supabase_client

        # 修改點 1：初始化檢索器
        # 移除原本寫死的 "resume_vectors"，因為現在 UserProfileRetriever 會根據 source_type 自己決定
        self.resume_retriever = UserProfileRetriever(qdrant_client)
        self.job_retriever = JobMatchRetriever(qdrant_client, "job_vectors")
        
        # 初始化 AI 顧問
        self.llm_advisor = CareerLLMAdvisor(api_key=openai_api_key)

    # 修改點 2：函數入口新增 document_id 與 source_type 參數
    # (註：如果前端是傳 Pydantic DTO 物件進來，這裡可以直接改成接收 request: JobMatchRequest)
    def find_best_jobs(self, user_id: int, document_id: int, source_type: str, filters: dict) -> List[dict]:
        """
        執行完整的三階段匹配流程。
        """
        try:
            # ==========================================
            # 🚀 Phase 0: 從 Supabase 提取最新六維分析報告
            # ==========================================
            logger.info(f"正在從 Supabase 取得 User {user_id} 的最新六維能力報告...")
            
            # 依據 generated_at 降冪排序，加上 limit(1) 取得最新的一份報告
            report_response = (
                self.supabase_client.table('career_analysis_report')
                .select('radar_chart, report_version')
                .eq('user_id', user_id)
                .execute()
            )
            
            # 2. 在 Python 端進行安全排序與篩選 (避開 SQL 字串排序陷阱)
            # 將 report_version 轉為 float 比較 (例如 "2.0" -> 2.0, "10.0" -> 10.0)
            # 若某些舊資料沒有 report_version，預設給 "0.0"
            try:
                latest_report = max(
                    report_response.data, 
                    key=lambda x: float(x.get('report_version') or '0.0')
                )
            except ValueError:
                # 防呆：如果版本號出現 "v1.0" 這種無法直接轉 float 的字串，退回安全的字串比對
                logger.warning("警告：報告版本號無法轉換為浮點數，將使用字串排序。")
                latest_report = max(
                    report_response.data, 
                    key=lambda x: str(x.get('report_version') or '0.0')
                )
            
            logger.info(f"✅ 成功鎖定最新版本報告 (版本號: {latest_report.get('report_version')})")

            if not report_response.data:
                raise ValueError(f"❌ 找不到 User {user_id} 的職涯分析報告！請使用者先完成問卷與報告生成。")

            # 萃取 radar_chart 並進行欄位映射 (Mapping)
            radar_chart = report_response.data[0].get('radar_chart', {})
            dimensions = radar_chart.get('dimensions', [])
            
            # 定義從中文標籤到系統 D1~D6 的對應表
            # (架構師註：這樣做可以保護 matcher.py 完全不需修改)
            axis_mapping = {
                "前端開發": "D1",
                "後端開發": "D2",
                "運維部署": "D3",
                "AI與數據": "D4",
                "工程品質": "D5",
                "軟實力": "D6"
            }
            
            user_6d_profile = {}
            for dim in dimensions:
                axis_name = dim.get("axis")
                score = dim.get("score", 0)
                mapped_key = axis_mapping.get(axis_name)
                if mapped_key:
                    user_6d_profile[mapped_key] = score
                    
            logger.info(f"✅ 成功載入六維能力分數: {user_6d_profile}")

            # ==========================================
            # Phase 0.5: 從 Supabase 取得使用者履歷文字摘要 (RAG Context)
            # ==========================================
            logger.info(f"正在取得 User {user_id} 的履歷文字內容 (source_type: {source_type})...")
            resume_summary = ""
            try:
                if source_type == "RESUME":
                    # 從 resume 資料表取得 structured_data 欄位
                    # 使用 maybe_single() 而非 single()：
                    #   - single()       → 0 筆時拋出 PGRST116 錯誤
                    #   - maybe_single() → 0 筆時回傳 data=None，安全降級
                    resume_text_response = (
                        self.supabase_client.table('resume')
                        .select('structured_data')
                        .eq('resume_id', document_id)
                        .maybe_single()
                        .execute()
                    )
                    if resume_text_response.data is None:
                        logger.warning(f"⚠️ resume 表找不到 resume_id={document_id} 的資料，跳過履歷文字注入。")
                    else:
                        structured_data = resume_text_response.data.get('structured_data') or {}
                        # 將 structured_data dict 轉成可讀文字塊（取各節標題與內容）
                        if isinstance(structured_data, dict):
                            parts = []
                            for section_key, section_val in structured_data.items():
                                if section_val:
                                    parts.append(f"[{section_key}] {str(section_val)[:300]}")
                            resume_summary = "\n".join(parts)[:1200]  # 避免 token 超出
                        elif isinstance(structured_data, str):
                            resume_summary = structured_data[:1200]

                elif source_type == "OPTIMIZATION":
                    # 從 resume_optimization 資料表取得多個欄位
                    opt_text_response = (
                        self.supabase_client.table('resume_optimization')
                        .select('professional_summary, professional_experience, core_skills, projects, education, autobiography')
                        .eq('optimization_id', document_id)
                        .maybe_single()
                        .execute()
                    )
                    if opt_text_response.data is None:
                        logger.warning(f"⚠️ resume_optimization 表找不到 optimization_id={document_id} 的資料，跳過履歷文字注入。")
                    else:
                        opt_data = opt_text_response.data or {}
                        # 拼接各欄位，形成完整的履歷摘要文字
                        opt_parts = []
                        field_labels = {
                            'professional_summary':    '個人摘要',
                            'core_skills':             '核心技能',
                            'professional_experience': '工作經歷',
                            'projects':                '專案經歷',
                            'education':               '學歷',
                            'autobiography':           '自傳',
                        }
                        for field, label in field_labels.items():
                            val = opt_data.get(field)
                            if val:
                                opt_parts.append(f"[{label}] {str(val)[:250]}")
                        resume_summary = "\n".join(opt_parts)[:1200]  # 避免 token 超出

                if resume_summary:
                    logger.info(f"✅ 成功取得履歷文字摘要 (字元數: {len(resume_summary)})")
                else:
                    logger.warning("⚠️ 查無履歷文字內容，AI 建議將退回純數字模式。")

            except Exception as e:
                # 查詢失敗不中斷主流程，降級為純數字模式
                logger.warning(f"⚠️ 取得履歷文字失敗（降級為純分數模式）: {e}")
                resume_summary = ""

            # ==========================================
            # Phase 1: Qdrant 混合召回 (撈取 Top 50 候選名單)
            # ==========================================
            logger.info(f"正在提取 User {user_id} 的 {source_type} 履歷向量 (文件ID: {document_id})...")
            # 修改點 3：將路由參數傳遞給 Retriever
            resume_vector = self.resume_retriever.get_user_resume_vector(
                user_id=user_id,
                document_id=document_id,
                source_type=source_type
            )

            logger.info("正在進行第一階段：Qdrant 語意與硬條件檢索...")
            primary_candidates = self.job_retriever.search_hybrid_jobs(
                query_vector=resume_vector,
                filters=filters,
                limit=50
            )

            if not primary_candidates:
                logger.warning("找不到任何符合篩選條件的職缺。")
                return []

            # ==========================================
            # Phase 1.5: Supabase 批量查詢 (Batch Query)
            # ==========================================
            logger.info("正在向 Supabase 提取職缺細節與能力要求...")
            job_ids = [job['job_id'] for job in primary_candidates]

            # 1. 查詢職缺內容 (🌟 這裡補上了 city, salary_min, salary_max)
            response_jobs = (
                self.supabase_client.table('job_posting')
                .select('job_id, job_title, job_description, requirements, full_address, city, salary_min, salary_max, source_url, company_id, d1_frontend, d2_backend, d3_devops, d4_ai_data, d5_quality, d6_soft_skills')
                .in_('job_id', job_ids)
                .execute()
            )
            job_data_list = response_jobs.data

            # 2. 批量查詢關聯公司資訊
            company_ids = list(set([job['company_id'] for job in job_data_list if job.get('company_id')]))
            response_companies = (
                self.supabase_client.table('company_info')
                .select('company_id, company_name, industry')
                .in_('company_id', company_ids)
                .execute()
            )
            company_lookup = {row['company_id']: row for row in response_companies.data}

            # 3. 合併職缺與公司資訊
            job_full_lookup = {}
            for job_row in job_data_list:
                comp_info = company_lookup.get(job_row.get('company_id'), {})
                job_full_lookup[job_row['job_id']] = {
                    **job_row, 
                    'company_name': comp_info.get('company_name', '未提供'),
                    'industry': comp_info.get('industry', '未提供')
                }

            # ==========================================
            # Phase 2: 精確重排序 (Re-ranking)
            # ==========================================
            logger.info("正在進行第二階段：硬實力差距精算與重新計分...")
            final_candidates = []
            
            for job in primary_candidates:
                job_id = job['job_id']
                job_details = job_full_lookup.get(job_id, {})
                if not job_details: continue

                # 取得語意相似度分數 (0.3)
                score_text = max(0.0, job.get('score_text', 0.0))
                # 計算硬實力契合度 (0.7)
                score_6d = JobMatcher.calculate_dynamic_job_gap(user_6d_profile, job_details)
                
                # 執行加權總分計算 (0.7 Hard-skill + 0.3 Semantic)
                final_score = (0.7 * score_6d) + (0.3 * score_text)
                
                job['score_6d'] = score_6d
                job['final_score'] = final_score
                job['job_details'] = job_details
                final_candidates.append(job)

            # 排序並取 Top 10
            final_candidates.sort(key=lambda x: x['final_score'], reverse=True)
            top_10_candidates = final_candidates[:10]

            # ==========================================
            # Phase 3: AI 分析與 JSON 格式化 (平行處理)
            # ==========================================
            logger.info("正在產出 Top 10 AI 分析報告 (10 股平行運算)...")
            
            def format_and_analyze(job):
                try:
                    details = job['job_details']
                    f_final_pct = f"{job['final_score']:.1%}"

                    # 清理 Requirements 換行符號
                    raw_req = str(details.get('requirements', ''))
                    req_lines = [line.strip() for line in raw_req.split('\n') if line.strip()]
                    req_lines = list(dict.fromkeys(req_lines)) # 去重
                    clean_requirements = " | ".join(req_lines)
                    
                    # 生成 AI 洞察（4.1 傳入職缺文字 + 4.2 傳入履歷摘要）
                    ai_insights = self.llm_advisor.generate_job_insights(
                        job_title=details.get('job_title', '未知職缺'),
                        user_6d=user_6d_profile,
                        job_6d=details,
                        match_score=f_final_pct,
                        # [4.1] 傳入已查出的職缺文字（限制長度避免 token 超出）
                        job_description=str(details.get('job_description', ''))[:500],
                        job_requirements=clean_requirements[:300],
                        # [4.2] 傳入 Phase 0.5 查出的履歷文字摘要
                        resume_summary=resume_summary,
                    )
                    
                    # 🌟 新增：把薪水的數學邏輯搬過來，轉成前端愛看的字串
                    s_min = details.get('salary_min') or 0
                    s_max = details.get('salary_max') or 0
                    if s_min > 100000: s_min = int(s_min / 12)
                    if s_max > 100000: s_max = int(s_max / 12)
                    
                    if s_min == s_max or s_max == 0:
                        salary_str = f"{int(s_min/1000)}k"
                    else:
                        salary_str = f"{int(s_min/1000)}k - {int(s_max/1000)}k"

                    # 🌟 替換：直接輸出前端 React 認識的 Key！
                    return {
                        "id": str(details.get('job_id', '')),                   # 換成 id
                        "title": str(details.get('job_title', '')),             # 換成 title
                        "description": str(details.get('job_description', '')),
                        "requirements": clean_requirements,
                        "company": str(details.get('company_name', '')),        # 換成 company
                        "industry": str(details.get('industry', '')),
                        "location": str(details.get('city', '')),               # 用 city 填入 location
                        "salary_range": salary_str,                             # 補上薪水！
                        "externalUrl": str(details.get('source_url', '')),      # 換成 externalUrl
                        
                        # 底下是 AI 算出來的新玩具，我們先保留著，等前端來接！
                        "match_score": f_final_pct,
                        "recommendation_reason": ai_insights.get("recommendation_reason", ""),
                        "strengths": ai_insights.get("strengths", ""),
                        "weaknesses": ai_insights.get("weaknesses", ""),
                        "interview_tips": ai_insights.get("interview_tips", "")
                    }
                except Exception as e:
                    logger.warning(f"單筆職缺分析失敗: {e}")
                    return None

            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                final_json_list = list(executor.map(format_and_analyze, top_10_candidates))
                
            return [j for j in final_json_list if j is not None]

        except Exception as e:
            logger.error(f"CareerMatchingService 發生錯誤: {e}", exc_info=True)
            raise e
