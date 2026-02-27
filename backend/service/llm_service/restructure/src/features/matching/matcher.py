# src/features/matching/matcher.py
import math
import statistics
import logging
import numpy as np
from typing import List, Dict, Any

# 設定日誌記錄器
logger = logging.getLogger(__name__)

# ==========================================
# Part 1: 資料轉換層 (ETL) - 負責處理問卷原始資料
# ==========================================
# 1. 分數對照表
class ScoreMapper:
    """
    負責將問卷的 String 選項映射為 1-5 分的數值 (Based on PDF Spec)
    """
    MAPPING = {
        # Q2 前端
        "unfamiliar": 1, "basic_html_css": 2, "framework_spa": 3, 
        "optimization_ssr": 4, "system_design": 5,
        # Q3 後端
        "unfamiliar": 1, "crud_api": 2, "db_auth_testing": 3, 
        "high_concurrency": 4, "distributed_system": 5,
        # Q5 DevOps
        "paas_only": 1, "docker_basic": 2, "cloud_manual": 3, 
        "k8s_cicd": 4, "iac_monitoring": 5,
        # Q6 AI/Data
        "api_consumer": 1, "pandas_numpy": 2, "model_training": 3, 
        "rag_langchain": 4, "mlops": 5,
        # Q7 Security
        "framework_default": 1, "owasp_basic": 2, "auth_rbac": 3, 
        "audit_devsecops": 4,
        # Module B (情境題)
        "restart": 1, "log_search": 2, "rollback": 4, "incident_analysis": 5, # Q9
        "newest_tech": 1, "popularity": 2, "team_familiarity": 4, "tradeoff_analysis": 5, # Q10
        "comply": 1, "reject": 2, "alternative_solution": 4, "value_driven": 5, # Q11
        "formality": 2, "style_check": 3, "logic_safety": 4, "architecture_solid": 5, # Q12
        "just_in_time": 1, "hoarding": 2, "consistent_input": 3, "deep_dive_sharing": 5, # Q13
        "waterfall_none": 1, "agile_scrum": 2, "kanban": 3, "process_optimization": 5, # Q14
        "translation_tool": 1, "slow_reading": 2, "fluent_reading": 3, "global_comm": 5 # Q15
    }

    @staticmethod  # 靜態方法裝飾器：不需要存取 class 內部屬性，工具人
    def get_score(key: str) -> float:  # 將選項 str 轉換成 1-5 分的 float
        return float(ScoreMapper.MAPPING.get(key, 0.0)) 
        # .get(欲查詢的鍵, 找不到的預設值)
        ### 找不到預設值會回 0.0，完全無經驗的使用者

class CareerAnalyzer:
    """
    負責將使用者的問卷答案轉換為「六維職能向量」。
    這是產生 User Profile 的核心。
    """
    def __init__(self, user_data: Dict[str, Any]):
        self.data = user_data
        self.scores = {}

    def _get_lang_score(self, category_langs: List[str]) -> float:
        """計算語言分數 (取該類別中最高分)"""
        user_langs = self.data['module_a'].get('q1_languages', [])
        max_score = 1.0
        normalized_category = [l.lower() for l in category_langs]
        for item in user_langs:
            lang_name = item['name'].lower().strip()
            try:
                lang_score = float(item['score'])
            except:
                lang_score = 1.0
            # 模糊比對: 例如使用者填 "Python 3.9" 也能對應到 "python"
            # 不符合實際狀況，可以修改
            if any(c_lang in lang_name for c_lang in normalized_category):
                if lang_score > max_score:
                    max_score = lang_score
        return max_score

    def _get_checkbox_score(self, target_values: List[str], user_choices: List[str]) -> float:
        """
        累計得分制 (符合 PDF Q4 規格)
        每命中一個目標選項給 0.5 分，最高給予固定上限。
        """
        if not user_choices: return 0.0
    
        # 計算命中數量
        match_count = len(set(user_choices) & set(target_values))
    
        # 依照規格書：每項 0.5，上限 2.0 (或自定義上限)
        score = match_count * 0.5
        return min(score, 2.0) # 確保不超過 2.0

    def calculate_vectors(self):
        """
        執行 PDF 4.1 節的向量化公式
        """
        ma = self.data['module_a']
        mb = self.data['module_b']
        user_db_choices = ma.get('q4_database', []) # 使用者在 Q4 的所有勾選

        # 定義語言分類 (PDF Source 63-65)
        frontend_langs = ['javascript', 'typescript', 'html', 'css']
        backend_langs = ['java', 'go', 'python', 'c#', 'rust', 'php']
        data_langs = ['python', 'r', 'sql', 'julia']

        # --- 計算 D1: 前端工程 ---
        # Formula: Avg(Q2, Q1 if JS)
        s_q2 = ScoreMapper.get_score(ma['q2_frontend'])
        s_q1_fe = self._get_lang_score(frontend_langs)
        self.scores['D1'] = statistics.mean([s_q2, s_q1_fe])

        # --- 計算 D2: 後端工程 ---
        # Formula: Avg(Q3, Q4_relational, Q1 if Backend)
        s_q3 = ScoreMapper.get_score(ma['q3_backend'])
        s_q1_be = self._get_lang_score(backend_langs)
        # 根據 PDF ，D2 關注 RDBMS, NoSQL, Cache (A/B/C 選項)
        d2_db_targets = ['rdbms_sql', 'nosql_document', 'key_value_cache']
        s_q4_backend_breadth = self._get_checkbox_score(d2_db_targets, user_db_choices)
        self.scores['D2'] = statistics.mean([s_q3, s_q1_be, s_q4_backend_breadth])

        # --- 計算 D3: 雲端維運 ---
        # Formula: Avg(Q5, Q9)
        s_q5 = ScoreMapper.get_score(ma['q5_devops'])
        s_q9 = ScoreMapper.get_score(mb['q9_troubleshoot'])
        self.scores['D3'] = statistics.mean([s_q5, s_q9])

        # --- 計算 D4: AI 與數據 ---
        # Formula: Avg(Q6, Q4_vector, Q4_nosql)
        s_q6 = ScoreMapper.get_score(ma['q6_ai_data'])
        # 根據 PDF ，D4 關注 Search, Vector, Warehouse (D/E/G 選項)
        d4_db_targets = ['search_engine', 'vector_db', 'data_warehouse']
        s_q4_data_breadth = self._get_checkbox_score(d4_db_targets, user_db_choices)
        self.scores['D4'] = statistics.mean([s_q6, s_q4_data_breadth])

        # --- 計算 D5: 品質與架構 ---
        # Formula: Avg(Q7, Q10, Q12)
        s_q7 = ScoreMapper.get_score(ma['q7_security'])
        s_q10 = ScoreMapper.get_score(mb['q10_tech_choice'])
        s_q12 = ScoreMapper.get_score(mb['q12_code_review'])
        self.scores['D5'] = statistics.mean([s_q7, s_q10, s_q12])

        # --- 計算 D6: 軟實力 ---
        # Formula: Avg(Q11, Q13, Q14, Q15)
        s_q11 = ScoreMapper.get_score(mb['q11_communication'])
        s_q13 = ScoreMapper.get_score(mb['q13_learning'])
        s_q14 = ScoreMapper.get_score(mb['q14_process'])
        s_q15 = ScoreMapper.get_score(mb['q15_english'])
        self.scores['D6'] = statistics.mean([s_q11, s_q13, s_q14, s_q15])

        # Round all scores to 1 decimal
        for k, v in self.scores.items():
            self.scores[k] = round(v, 1)

# ==========================================
# Part 2: 靜態診斷層 (Diagnostic) - 負責產出雷達圖報告
# ==========================================

# 3. [NEW] 職位匹配器
class JobMatcher:
    ROLE_PROFILES = {
        "frontend":       np.array([5.0, 1.5, 2.0, 1.0, 4.0, 3.5]),
        "backend":        np.array([1.5, 5.0, 3.0, 1.5, 4.5, 3.5]),
        "fullstack":      np.array([4.0, 4.0, 3.0, 2.0, 4.0, 4.0]),
        "data_scientist": np.array([1.0, 2.5, 2.0, 5.0, 3.0, 4.0]),
        "ai_engineer":    np.array([1.0, 3.0, 2.5, 5.0, 4.0, 3.5]),
        "devops_sre":     np.array([1.0, 3.5, 5.0, 2.0, 4.5, 4.0])
    }

    @classmethod
    def _get_safe_score(cls, data: dict, *keys) -> float:
        """
        安全獲取數值分數，處理缺失值與格式異常，並記錄日誌。
        """
        for k in keys:
            val = data.get(k)
            if val is not None:
                try:
                    return float(val)
                except (ValueError, TypeError):
                    logger.error(f"❌ 資料格式異常: Key '{k}' 的值為 '{val}' (型別: {type(val)})，無法轉換為數字。")
                    return 0.0
        
        # 遍歷所有 Key 都沒找到有效值
        main_key = keys[0] if keys else "Unknown"
        logger.warning(f"⚠️ 資料缺失: 找不到維度 '{main_key}' (嘗試過: {keys})，預設為 0.0。")
        return 0.0

    @classmethod
    def calculate_match_score(cls, user_vectors: dict, target_role_key: str) -> str:
        """
        實作 PDF 4.3 節：混合距離算法
        """
        # 1. 準備向量
        u_vec = np.array([
            cls._get_safe_score(user_vectors, 'D1', 'd1_frontend'),
            cls._get_safe_score(user_vectors, 'D2', 'd2_backend'),
            cls._get_safe_score(user_vectors, 'D3', 'd3_devops'),
            cls._get_safe_score(user_vectors, 'D4', 'd4_ai_data', 'd4_data'),
            cls._get_safe_score(user_vectors, 'D5', 'd5_quality'),
            cls._get_safe_score(user_vectors, 'D6', 'd6_soft_skills', 'd6_soft')
        ])
        
        # 取得目標職位的標準向量
        t_vec = cls.ROLE_PROFILES.get(target_role_key)
        if t_vec is None: return "N/A"

        # 2. 計算歐幾里得距離 (Euclidean Distance)
        dist = np.linalg.norm(t_vec - u_vec)
        
        # 正規化距離 (假設最大可能距離約為 12)
        max_dist = 12.0
        norm_dist = min(dist / max_dist, 1.0)

        # 3. 計算相似度 (Similarity)
        dot_product = np.dot(u_vec, t_vec)
        norm_u = np.linalg.norm(u_vec)
        norm_t = np.linalg.norm(t_vec)
        
        if norm_u == 0 or norm_t == 0: similarity = 0
        else: similarity = dot_product / (norm_u * norm_t)

        final_score = (0.7 * (1 - norm_dist)) + (0.3 * similarity)
        return f"{int(final_score * 100)}%"

    @classmethod
    def calculate_dynamic_job_gap(cls, user_6d: dict, job_payload: dict) -> float:
        """
        [職缺匹配專用]：針對真實職缺計算「硬實力契合度」。
        邏輯：計算六維能力的歐幾里得距離，並轉化為 0-1 分數。
        """
        # 使用者向量 (D1~D6)
        u_vec = np.array([
            cls._get_safe_score(user_6d, 'D1', 'd1_frontend'),
            cls._get_safe_score(user_6d, 'D2', 'd2_backend'),
            cls._get_safe_score(user_6d, 'D3', 'd3_devops'),
            cls._get_safe_score(user_6d, 'D4', 'd4_ai_data', 'd4_data'),
            cls._get_safe_score(user_6d, 'D5', 'd5_quality'),
            cls._get_safe_score(user_6d, 'D6', 'd6_soft_skills', 'd6_soft')
        ])
        
        # 職缺向量 (對應資料庫欄位)
        j_vec = np.array([
            cls._get_safe_score(job_payload, 'd1_frontend'),
            cls._get_safe_score(job_payload, 'd2_backend'),
            cls._get_safe_score(job_payload, 'd3_devops'),
            cls._get_safe_score(job_payload, 'd4_ai_data'),
            cls._get_safe_score(job_payload, 'd5_quality'),
            cls._get_safe_score(job_payload, 'd6_soft_skills')
        ])

        dist = np.linalg.norm(j_vec - u_vec)
        max_dist = math.sqrt(6 * (5 ** 2)) 
        
        match_score = max(0.0, 1.0 - (dist / max_dist))
        return float(match_score)

# ==========================================
# Part 3: [NEW] 職缺推薦層 (Recommendation) - 混合檢索漏斗
# ==========================================

class JobRanker:
    """
    (新增的類別)
    實作「混合檢索漏斗」的第三層 (Math Layer)。
    負責接收 Searcher 找出的「候選職缺列表」，進行精確的數學排序。
    """
    
    @staticmethod
    def _dict_to_array(vec_dict: Dict[str, float]) -> np.ndarray:
        """輔助函式：將 Dict 轉為標準順序的 Numpy Array"""
        return np.array([
            vec_dict.get('d1_frontend', 0.0),
            vec_dict.get('d2_backend', 0.0),
            vec_dict.get('d3_devops', 0.0),
            vec_dict.get('d4_data', 0.0),
            vec_dict.get('d5_quality', 0.0),
            vec_dict.get('d6_soft', 0.0)
        ])

    def rank_jobs(self, user_vectors: Dict[str, float], candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        核心排序入口：接收候選人列表 -> 計算差距 -> 排序回傳
        """
        ranked_results = []
        u_arr = self._dict_to_array(user_vectors)
        
        # 理論最大距離 (用於正規化)
        MAX_DIST = 12.0 
        
        for job in candidates:
            # 1. 準備職缺向量
            j_arr = self._dict_to_array(job.get("required_vectors", {}))
            
            # 2. 計算硬實力幾何距離 (Euclidean Distance)
            # 使用 numpy 加速運算
            dist = np.linalg.norm(j_arr - u_arr)
            
            # 正規化 (距離越小，分數越高)
            comp_score = max(0.0, min(1.0, 1 - (dist / MAX_DIST)))
            
            # 3. 取得語意分數 (來自 Searcher)
            sem_score = job.get("temp_semantic_score", 0.0)
            
            # 4. 計算最終加權分數 (PDF Spec: 0.7 vs 0.3)
            final_score = (0.7 * comp_score) + (0.3 * sem_score)
            
            # 5. 格式化結果
            ranked_results.append({
                "id": job.get("id"),
                "title": job.get("title"),
                "company": job.get("company"),
                "location": job.get("location"),
                "final_score": round(final_score * 100, 1),
                "details": {
                    "competency_match": round(comp_score * 100, 1),
                    "semantic_match": round(sem_score * 100, 1),
                    "vector_distance": round(dist, 2)
                }
            })
            
        # 依照最終分數降序排列
        return sorted(ranked_results, key=lambda x: x["final_score"], reverse=True)