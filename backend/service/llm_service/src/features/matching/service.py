# src/features/matching/service.py
import concurrent.futures
from qdrant_client import QdrantClient
from typing import List, Dict, Any

# 匯入本模組的其他組件
from src.features.matching.qdrant_retriever import JobMatchRetriever, UserProfileRetriever
from src.features.matching.matcher import JobMatcher
from src.features.matching.advisor import CareerLLMAdvisor

class CareerMatchingService:
    """
    職缺匹配模組的核心入口。
    負責協調 Qdrant、Supabase 與 AI 顧問，執行混合計分流程並產出前端 JSON。
    """
    def __init__(self, qdrant_client: QdrantClient, supabase_client: Any, openai_api_key: str):
        self.qdrant_client = qdrant_client
        self.supabase_client = supabase_client

        # 初始化檢索器
        self.resume_retriever = UserProfileRetriever(qdrant_client, "resume_vectors")
        self.job_retriever = JobMatchRetriever(qdrant_client, "job_vectors")
        
        # 初始化 AI 顧問
        self.llm_advisor = CareerLLMAdvisor(api_key=openai_api_key)

    def find_best_jobs(self, user_id: int, filters: dict, user_6d_profile: dict) -> List[dict]:
        """
        執行完整的三階段匹配流程。
        """
        try:
            # ==========================================
            # Phase 1: Qdrant 混合召回 (撈取 Top 50 候選名單)
            # ==========================================
            print(f"正在提取 User {user_id} 的履歷向量...")
            resume_vector = self.resume_retriever.get_resume_vector(user_id)

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
                        "ai_analysis": ai_insights
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
