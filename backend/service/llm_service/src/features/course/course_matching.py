from typing import List, Dict, Any, Optional
import math
import os
from src.core.database.supabase_client import get_supabase_client

# =========================
# 基礎設定與權重表
# =========================
COURSE_LEVEL_MAP = {
    "Beginner": 1,
    "Intermediate": 2,
    "Advanced": 3
}

# 政策權重分佈 (Policy Distribution)
# 每一級的總和不需為1，這是「增益係數」
# 用途：決定「大方向」，例如 Level 2 主要看 Beginner/Intermediate，絕不看 Advanced
USER_TO_COURSE_DISTRIBUTION = {
    1: {1: 1.0, 2: 0.0, 3: 0.0},  # 新手：專注基礎
    2: {1: 0.9, 2: 0.6, 3: 0.0},  # 關鍵級別：開放 60% 的窗口給中階，讓 40分的人有機會
    3: {1: 0.5, 2: 1.0, 3: 0.4},  # 中階：向下複習，向上探索
    4: {1: 0.0, 2: 0.7, 3: 0.9},  # 中高階：強度提升
    5: {1: 0.0, 2: 0.0, 3: 1.0},  # 專家：只看難的
}

class CourseRecommendationService:
    """
    課程推薦服務，負責根據使用者的技能缺口分析結果提供課程建議。
    """
    def __init__(self, supabase_client=None):
        self.supabase = supabase_client or get_supabase_client()

    def fetch_user_gap(self, user_id: str) -> Dict:
        """
        從 Supabase 撈取該使用者的目標職類結果。
        """
        try:
            # 根據 Schema 結構，欄位名稱應為 role 與 match_score
            resp = (
                self.supabase
                .table("career_analysis_report") \
                .select("target_position") \
                .eq("user_id", user_id) \
                .order("generated_at", desc=True) \
                .limit(1) \
                .execute()
            )
            
            if not resp.data or len(resp.data) == 0:
                return None
            
            # 因為拿掉了 .single()，所以 resp.data 是一個 list，需取第一筆資料
            target_pos = resp.data[0]["target_position"]
            raw_role = target_pos["role"]
            raw_score = target_pos["match_score"]
            
            # 清理資料：移除 AI 產生的前綴與百分比符號
            # 1. 處理 Role (提取關鍵字)
            # 因 target_position 設定為必填，故沒有幫使用者判斷適合職類，但先保留
            clean_role = raw_role.replace("領航員分析您適合的職類為 - ", "").strip()
            
            # 2. 處理 Match Score (轉為整數)
            if isinstance(raw_score, str):
                clean_score = int(raw_score.replace("%", "").strip())
            else:
                clean_score = int(raw_score)
                
            return {
                "role": clean_role,
                "match_score": clean_score
            }
            
        except Exception as e:
            if "PGRST205" in str(e):
                print(f"ℹ️ 提示: 資料表尚未建立，將使用預設參數。")
            elif "42703" in str(e):
                print(f"⚠️ 欄位名稱不符，請檢查資料表表結構: {e}")
            else:
                print(f"⚠️ 獲取使用者缺口分析失敗: {e}")
            return None

    def fetch_candidate_courses(self, job_category: str) -> List[Dict]:
        """
        從 Supabase 撈取與職位類別相關的候選課程清單。
        """
        try:
            # 依 job_category 篩選
            resp = (
                self.supabase
                .table("course") \
                .select("course_id, course_name, url, rating, review_count, level, course_type, duration_suggested") \
                .eq("role_name", job_category) \
                .execute()
            )
            return resp.data
        except Exception as e:
            print(f"⚠️ 獲取候選課程失敗: {e}")
            return []

    @staticmethod
    def normalize_course_difficulty(courses: List[Dict]) -> List[Dict]:
        """
        將課程的中文字難易度轉換為數值，方便後續計算。
        """
        result = []

        for c in courses:
            level = COURSE_LEVEL_MAP.get(c.get("level"))
            if level is None:
                continue

            c["course_level"] = level
            result.append(c)

        return result

    @staticmethod
    def score_to_user_level(match_score: int) -> int:
        """
        將使用者的 0-100 的 match_score 映射到 1-5 等級。
        """
        if match_score <= 20: return 1
        elif match_score <= 40: return 2
        elif match_score <= 60: return 3
        elif match_score <= 80: return 4
        return 5

    @staticmethod
    def compute_user_ability_position(match_score: int) -> float:
        """
        將 0-100 的 match_score 映射到課程難度空間 (1.0-3.0)。
        """
        cursor = 1.0 + (match_score / 100) * 2.0
        return round(cursor, 3)
    
    @staticmethod
    def compute_priority_score(course_level: int, ability_position: float, user_level: int) -> float:
        """
        計算每一門課程的推薦分數。
        """
        # A. 距離分數 (Distance Score) - 連續性
        # 課程等級與使用者游標越近，分數越高
        # 使用高斯函數概念或簡單倒數： 1 / (1 + 距離平方) 讓接近的權重放大
        distance = abs(course_level - ability_position)
        distance_score = 1 / (1 + distance ** 2)

        # B. 政策權重 (Policy Weight) - 離散性
        # 查表確認該等級使用者是否適合此難度
        level_weight = USER_TO_COURSE_DISTRIBUTION[user_level].get(
            course_level, 0
        )
        return distance_score * level_weight

    def rank_courses(self, courses: List[Dict], match_score: int, user_level: int) -> List[Dict]:

        ability_position = self.compute_user_ability_position(match_score)

        ranked_list = [] # 建立新列表

        for c in courses:
            priority_score = self.compute_priority_score(
                c["course_level"],
                ability_position,
                user_level
            )
            # --- 重點：過濾掉課程難易度分數為 0 的課程 ---
            if priority_score <= 0.0:
              continue

            c["priority_score"] = priority_score

            # 次排序分數（品質）
            c["quality_score"] = (
                (c.get("rating", 0) / 5 * 0.7) +
                (min(c.get("review_count") or 0, 1000) / 1000 * 0.3)
            )

            ranked_list.append(c) # 只將合格的課程加入

        return sorted(
            ranked_list,
            key=lambda x: (
                x["priority_score"],     # 1.難度最重要
                x["quality_score"],      # 2.品質
            ),
            reverse=True
        )

    def get_recommendations(self, user_id: str, top_k: int = 5) -> Dict[str, Any]:
        """
        主推薦流程入口。
        """
        from src.core.agent_engine.manager import CareerAgentManager
        from src.core.agent_engine.task_types import TaskType

        # 1. 獲取使用者狀態 (從 Supabase 取得 match_score 與 job_category)
        user_gap = self.fetch_user_gap(user_id)
        if not user_gap:
            return {"status": "error", "message": "尚未找到您的職涯測驗報告，無法推薦課程。"}
        match_score = user_gap["match_score"]
        job_category = user_gap["role"]

        # 計算 User Level
        user_level = self.score_to_user_level(match_score)

        # 2. 獲取並處理課程
        courses = self.fetch_candidate_courses(job_category)
        if not courses:
            return {"status": "error", "message": f"目前資料庫中缺乏 {job_category} 的相關課程。"}
        scored_courses = self.normalize_course_difficulty(courses)

        # 3. 排序
        ranked = self.rank_courses(
            scored_courses,
            match_score,
            user_level
        )

        # 4. 取得 Top K 精華清單
        top_courses_raw = ranked[:top_k]
        
        # 5. 交接給 CrewAI Manager 進行認知分析與路線規劃
        # 先暫停丟給 Manager，為了測試將結果直接回傳
        user_input = {
            "user_id": user_id,
            "role": job_category,
            "match_score": match_score,
            "courses": top_courses_raw
        }
        
        manager = CareerAgentManager()
        result = manager.run_task(TaskType.COURSE_REC.value, user_input)

        return result
        
        # return {
        #     "user_id": user_id,
        #     "role": job_category,
        #     "match_score": match_score,
        #     "user_level": user_level,
        #     "recommended_courses": top_courses_raw
        # }
        
# =========================
# 測試專用區塊
# =========================
# if __name__ == "__main__":
#     import json
#     # 初始化推薦服務
#     service = CourseRecommendationService()
    
#     # 這裡請替換成您資料庫中實際存在的 user_id
#     # 也可以在終端機執行 `python -m src.features.course.course_matching` 時直接測
#     test_user_id = 3 # 假設的測試 ID
    
#     print(f"\n[測試開始] 正在為 user_id: {test_user_id} 產生課程推薦...")
    
#     # 執行主流程 (目前已暫停丟給 Agent)
#     result = service.get_recommendations(user_id=test_user_id, top_k=5)
    
#     if result.get("status") == "error":
#         print(f"\n❌ 錯誤: {result.get('message')}")
#     else:
#         print("\n✅ [推薦成功] 演算法計算結果如下：")
#         print("-" * 50)
#         print(f"🎯 目標職位 (Role): {result['role']}")
#         print(f"📊 媒合分數 (Match Score): {result['match_score']}")
#         print(f"⭐ 使用者等級 (User Level): {result['user_level']}")
#         print("\n📚 [Top 5 推薦課程清單]:")
#         for i, course in enumerate(result['recommended_courses'], 1):
#             print(f"  {i}. {course['course_name']} (難度: {course['level']})")
#             print(f"     -> 優先權分數: {course['priority_score']:.4f} | 品質分數: {course['quality_score']:.4f}")
#             print(f"     -> URL: {course['url']}")
#             print("  " + "-"*40)
        
#         print("\n(測試完畢。確認資料正確性後，請移除這段測試程式碼，並將交接給 CareerAgentManager 的註解打開。)")


