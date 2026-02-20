import json
from datetime import datetime
from typing import List, Dict, Any
import statistics

# ==========================================
# 1. 核心邏輯類別 (與之前設計一致)
# ==========================================

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

    @staticmethod
    def get_score(key: str) -> float:
        # 如果 key 不存在或為 null，預設給 0
        return float(ScoreMapper.MAPPING.get(key, 0))

class CareerAnalyzer:
    def __init__(self, user_data: Dict[str, Any]):
        self.data = user_data
        self.scores = {} # 儲存計算出的 D1-D6

    def _get_lang_score(self, category_langs: List[str]) -> float:
        """
        計算 Q1 語言分數：從使用者填寫的語言中，找出屬於該類別(ex: backend)的最高分
        """
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
            if any(c_lang in lang_name for c_lang in normalized_category):
                if lang_score > max_score:
                    max_score = lang_score
                    
        return max_score

    def _get_checkbox_score(self, target_values: List[str], user_choices: List[str]) -> float:
        """複選題邏輯：有選中目標選項給 5.0，否則 1.0"""
        if not user_choices:
            return 1.0
        for choice in user_choices:
            if choice in target_values:
                return 5.0
        return 1.0

    def calculate_vectors(self):
        """執行向量化公式"""
        ma = self.data['module_a']
        mb = self.data['module_b']

        # 定義語言分類
        frontend_langs = ['javascript', 'typescript', 'html', 'css']
        backend_langs = ['java', 'go', 'python', 'c#', 'rust', 'php']
        data_langs = ['python', 'r', 'sql', 'julia']

        # D1: 前端 (Q2 + Q1_FE)
        s_q2 = ScoreMapper.get_score(ma.get('q2_frontend'))
        s_q1_fe = self._get_lang_score(frontend_langs)
        self.scores['D1'] = statistics.mean([s_q2, s_q1_fe])

        # D2: 後端 (Q3 + Q1_BE + Q4_Relational)
        s_q3 = ScoreMapper.get_score(ma.get('q3_backend'))
        s_q1_be = self._get_lang_score(backend_langs)
        s_q4_rel = self._get_checkbox_score(['rdbms_sql'], ma.get('q4_database', []))
        self.scores['D2'] = statistics.mean([s_q3, s_q1_be, s_q4_rel])

        # D3: 維運 (Q5 + Q9)
        s_q5 = ScoreMapper.get_score(ma.get('q5_devops'))
        s_q9 = ScoreMapper.get_score(mb.get('q9_troubleshoot'))
        self.scores['D3'] = statistics.mean([s_q5, s_q9])

        # D4: 數據 (Q6 + Q4_Vector + Q4_NoSQL)
        s_q6 = ScoreMapper.get_score(ma.get('q6_ai_data'))
        s_q4_vec = self._get_checkbox_score(['vector_db'], ma.get('q4_database', []))
        s_q4_nosql = self._get_checkbox_score(['nosql_document'], ma.get('q4_database', []))
        self.scores['D4'] = statistics.mean([s_q6, s_q4_vec, s_q4_nosql])

        # D5: 品質 (Q7 + Q10 + Q12)
        s_q7 = ScoreMapper.get_score(ma.get('q7_security'))
        s_q10 = ScoreMapper.get_score(mb.get('q10_tech_choice'))
        s_q12 = ScoreMapper.get_score(mb.get('q12_code_review'))
        self.scores['D5'] = statistics.mean([s_q7, s_q10, s_q12])

        # D6: 軟實力 (Q11 + Q13 + Q14 + Q15)
        s_q11 = ScoreMapper.get_score(mb.get('q11_communication'))
        s_q13 = ScoreMapper.get_score(mb.get('q13_learning'))
        s_q14 = ScoreMapper.get_score(mb.get('q14_process'))
        s_q15 = ScoreMapper.get_score(mb.get('q15_english'))
        self.scores['D6'] = statistics.mean([s_q11, s_q13, s_q14, s_q15])

        # 四捨五入到小數點第一位
        for k, v in self.scores.items():
            self.scores[k] = round(v, 1)

    def generate_prompt_payload(self) -> str:
        """準備送給 LLM 的資料"""
        context = {
            "calculated_vectors": self.scores,
            "user_raw_input": self.data
        }
        return json.dumps(context, indent=2, ensure_ascii=False)


# ==========================================
# 2. 命令列執行區
# ==========================================
import sys
import argparse
from pathlib import Path

def load_json_from_file(file_path: str):
    """從檔案讀取 JSON 資料（支援單一物件或陣列）"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        print(f"錯誤：找不到檔案 {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"錯誤：JSON 格式錯誤 - {e}")
        sys.exit(1)

def is_array_format(data) -> bool:
    """判斷輸入資料是否為陣列格式"""
    return isinstance(data, list)

def process_single_user(user_data: Dict[str, Any], show_output: bool = True) -> Dict[str, Any]:
    """處理單一使用者的資料並返回結果"""
    analyzer = CareerAnalyzer(user_data)
    analyzer.calculate_vectors()
    
    if show_output:
        user_id = user_data.get('user_id', 'unknown')
        print(f"\n👤 使用者: {user_id}")
        print("-" * 50)
        for key, value in analyzer.scores.items():
            print(f"  {key}: {value}")
        print("-" * 50)
    
    return {
        "radar_scores": analyzer.scores,
        "llm_payload": json.loads(analyzer.generate_prompt_payload())
    }

def save_results_to_file(output_path: str, results, is_batch: bool = False):
    """將結果儲存到檔案（支援單一結果或結果陣列）"""
    if is_batch:
        # 批量處理：輸出為陣列
        output_data = results
    else:
        # 單一使用者：輸出為單一物件
        output_data = results
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    count = len(results) if is_batch else 1
    print(f"\n✓ 結果已儲存至: {output_path} (共 {count} 筆資料)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='職涯分析問卷計算器 - 計算 D1-D6 向量分數',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  # 從 JSON 檔案讀取資料
  python test_logic.py -i input.json
  
  # 從 JSON 檔案讀取並儲存結果到檔案
  python test_logic.py -i input.json -o output.json
  
  # 只顯示分數，不顯示完整 payload
  python test_logic.py -i input.json --scores-only
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        type=str,
        help='輸入的 JSON 檔案路徑（包含問卷資料）'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='輸出的 JSON 檔案路徑（選填，不指定則只顯示在終端機）'
    )
    
    parser.add_argument(
        '--scores-only',
        action='store_true',
        help='只顯示雷達圖分數，不顯示完整 LLM payload'
    )
    
    args = parser.parse_args()
    
    # 讀取輸入資料
    if args.input:
        print(f"正在讀取檔案: {args.input}")
        input_data = load_json_from_file(args.input)
    else:
        # 如果沒有指定輸入檔案，使用預設測試資料
        print("⚠ 未指定輸入檔案，使用預設測試資料")
        print("提示：使用 -i 參數指定 JSON 檔案路徑\n")
        input_data = {
            "user_id": "test_user_4075",
            "timestamp": "2026-02-06T13:36:07.158Z",
            "module_a": {
                "q1_languages": [
                    {"name": "Python", "score": 2},
                    {"name": "SQL", "score": 2},
                    {"name": "JS", "score": 2}
                ],
                "q2_frontend": "basic_html_css",
                "q3_backend": "crud_api",
                "q4_database": ["rdbms_sql", "vector_db"],
                "q5_devops": "docker_basic",
                "q6_ai_data": "pandas_numpy",
                "q7_security": "framework_default",
                "q8_domain": "生命科學"
            },
            "module_b": {
                "q9_troubleshoot": "log_search",
                "q10_tech_choice": "team_familiarity",
                "q11_communication": "alternative_solution",
                "q12_code_review": "style_check",
                "q13_learning": "hoarding",
                "q14_process": "process_optimization",
                "q15_english": "slow_reading"
            },
            "module_c": {
                "q16_current_level": "entry_level",
                "q17_target_role": "data_scientist",
                "q18_industry": "traditional_digital",
                "q19_search_status": "active_urgent"
            },
            "module_d": {
                "q20_values_top3": ["financial_reward", "technical_growth", "work_life_balance"],
                "q21_pressure": "consider_short_term",
                "q22_career_type": "generalist",
                "q23_learning_style": ["hands_on_projects"]
            }
        }
    
    # 判斷輸入格式：單一物件或陣列
    is_batch = is_array_format(input_data)
    
    if is_batch:
        # 批量處理模式
        print("\n" + "="*50)
        print(f"批量處理模式：偵測到 {len(input_data)} 個使用者")
        print("="*50)
        
        results = []
        for idx, user_data in enumerate(input_data, 1):
            print(f"\n[{idx}/{len(input_data)}] 處理中...")
            try:
                result = process_single_user(user_data, show_output=not args.scores_only)
                results.append(result)
            except Exception as e:
                user_id = user_data.get('user_id', f'user_{idx}')
                print(f"❌ 處理使用者 {user_id} 時發生錯誤: {e}")
                # 即使錯誤也加入一個錯誤標記的結果
                results.append({
                    "error": str(e),
                    "user_id": user_id,
                    "radar_scores": {},
                    "llm_payload": None
                })
        
        # 顯示摘要
        print("\n" + "="*50)
        print("📊 處理完成摘要")
        print("="*50)
        print(f"總共處理: {len(results)} 個使用者")
        successful = sum(1 for r in results if 'error' not in r)
        print(f"成功: {successful} 個")
        if successful < len(results):
            print(f"失敗: {len(results) - successful} 個")
        
        # 顯示完整 payload（除非指定只顯示分數）
        if not args.scores_only and len(results) > 0:
            print("\n📤 準備送給 LLM 的完整 Payload (第一個使用者):")
            print("="*50)
            if 'error' not in results[0]:
                print(json.dumps(results[0]['llm_payload'], indent=2, ensure_ascii=False))
            else:
                print("第一個使用者處理失敗，無法顯示 payload")
            print("="*50)
        
        # 儲存結果到檔案（如果指定）
        if args.output:
            save_results_to_file(args.output, results, is_batch=True)
    else:
        # 單一使用者處理模式（原有邏輯）
        print("\n" + "="*50)
        print("單一使用者處理模式")
        print("="*50)
        
        result = process_single_user(input_data, show_output=True)
        
        # 顯示完整 payload（除非指定只顯示分數）
        if not args.scores_only:
            print("\n📤 準備送給 LLM 的完整 Payload:")
            print("="*50)
            print(json.dumps(result['llm_payload'], indent=2, ensure_ascii=False))
            print("="*50)
        
        # 儲存結果到檔案（如果指定）
        if args.output:
            save_results_to_file(args.output, result, is_batch=False) 