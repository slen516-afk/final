# src/features/matching/service.py
import concurrent.futures
from qdrant_client import QdrantClient
from typing import List, Dict, Any

# 匯入本模組的其他組件
from src.features.matching.qdrant_retriever import JobMatchRetriever, UserProfileRetriever
from src.features.matching.matcher import JobMatcher
from src.features.matching.advisor import CareerLLMAdvisor
from src.features.matching.schemas import JobMatchRequest, JobMatchingResponse

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
            print(f"正在從 Supabase 取得 User {user_id} 的最新六維能力報告...")
            
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
                print("⚠️ 警告：報告版本號無法轉換為浮點數，將使用字串排序。")
                latest_report = max(
                    report_response.data, 
                    key=lambda x: str(x.get('report_version') or '0.0')
                )
            
            print(f"✅ 成功鎖定最新版本報告 (版本號: {latest_report.get('report_version')})")

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
                    
            print(f"✅ 成功載入六維能力分數: {user_6d_profile}")

            # ==========================================
            # Phase 1: Qdrant 混合召回 (撈取 Top 50 候選名單)
            # ==========================================
            print(f"正在提取 User {user_id} 的 {source_type} 履歷向量 (文件ID: {document_id})...")
            # 修改點 3：將路由參數傳遞給 Retriever
            resume_vector = self.resume_retriever.get_user_resume_vector(
                user_id=user_id,
                document_id=document_id,
                source_type=source_type
            )

            print("正在進行第一階段：Qdrant 語意與硬條件檢索...")
            primary_candidates = self.job_retriever.search_hybrid_jobs(
                query_vector=resume_vector,
                filters=filters,
                limit=50
            )

            if not primary_candidates:
                print("⚠️ 找不到任何符合篩選條件的職缺。")
                return []

            # ==========================================
            # Phase 1.5: Supabase 批量查詢 (Batch Query)
            # ==========================================
            print("正在向 Supabase 提取職缺細節與能力要求...")
            job_ids = [job['job_id'] for job in primary_candidates]

            # 1. 查詢職缺內容
            response_jobs = (
                self.supabase_client.table('job_posting')
                .select('job_id, job_title, job_description, requirements, full_address, source_url, company_id, d1_frontend, d2_backend, d3_devops, d4_ai_data, d5_quality, d6_soft_skills')
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
            print("正在進行第二階段：硬實力差距精算與重新計分...")
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
            print("正在產出 Top 10 AI 分析報告 (10 股平行運算)...")
            
            def format_and_analyze(job):
                try:
                    details = job['job_details']
                    f_final_pct = f"{job['final_score']:.1%}"

                    # 清理 Requirements 換行符號
                    raw_req = str(details.get('requirements', ''))
                    req_lines = [line.strip() for line in raw_req.split('\n') if line.strip()]
                    req_lines = list(dict.fromkeys(req_lines)) # 去重
                    clean_requirements = " | ".join(req_lines)
                    
                    # 生成 AI 洞察
                    ai_insights = self.llm_advisor.generate_job_insights(
                        job_title=details.get('job_title', '未知職缺'),
                        user_6d=user_6d_profile,
                        job_6d=details,
                        match_score=f_final_pct
                    )
                    
                    return {
                        "job_id": str(details.get('job_id', '')),
                        "job_title": str(details.get('job_title', '')),
                        "job_description": str(details.get('job_description', '')),
                        "requirements": clean_requirements,
                        "company_name": str(details.get('company_name', '')),
                        "industry": str(details.get('industry', '')),
                        "full_address": str(details.get('full_address', '')),
                        "source_url": str(details.get('source_url', '')),
                        "final_score": f_final_pct,
                        "recommendation_reason": ai_insights.get("recommendation_reason", ""),
                        "strengths": ai_insights.get("strengths", ""),
                        "weaknesses": ai_insights.get("weaknesses", ""),
                        "interview_tips": ai_insights.get("interview_tips", "")
                    }
                except Exception as e:
                    print(f"⚠️ 單筆職缺分析失敗: {e}")
                    return None

            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                final_json_list = list(executor.map(format_and_analyze, top_10_candidates))
                
            return [j for j in final_json_list if j is not None]

        except Exception as e:
            print(f"❌ CareerMatchingService 發生錯誤: {e}")
            raise e
