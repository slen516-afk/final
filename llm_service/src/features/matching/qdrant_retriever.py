from qdrant_client import QdrantClient, models
from typing import List, Dict, Any

class JobMatchRetriever:
    """
    負責在 Qdrant 中執行硬篩選 (Payload Filtering) 與語意向量檢索。
    """
    def __init__(self, client: QdrantClient, collection_name: str):
        self.client = client
        self.collection_name = collection_name

    def _build_qdrant_filter(self, filters: Dict[str, Any]) -> models.Filter:
        """
        [逐行解析]
        將前端傳來的字典 (dict) 轉換成 Qdrant 的 Filter 物件。
        這是一個非常關鍵的轉換層，確保未來的擴充性。
        """
        must_conditions = []

        # 1. 處理地區 (Location) -> 使用 MatchAny 支援多選
        if "city" in filters and filters["city"]:
            must_conditions.append(
                models.FieldCondition(
                    key="city",  # 對應 Qdrant Payload 中的欄位名稱
                    match=models.MatchAny(any=filters["city"])
                )
            )

        # 2. 處理薪資 (邏輯：職缺的最大薪水，必須大於等於使用者要求的最小薪水)
        # 例如職缺是 40000~60000，使用者要求最低 50000，這樣算符合 (因為有交集)
        if "salary_min" in filters:
            must_conditions.append(
                models.FieldCondition(
                    key="salary_max", # 用職缺的天花板，去比對使用者的底線
                    range=models.Range(
                        gte=filters.get("salary_min")
                    )
                )
            )

        # 將所有條件打包成一個必須全部滿足 (must) 的 Filter
        return models.Filter(must=must_conditions)
    
    def filter_jobs_only(self, filters: Dict[str, Any], limit: int = 50) -> List[Dict]:
        """
        [逐行解析與意圖]
        只執行硬篩選 (Payload Filtering)，不計算任何向量相似度。
        用於測試過濾邏輯，或單純將 Qdrant 當作傳統 NoSQL 資料庫使用。
        """
        # 1. 組裝過濾條件
        qdrant_filter = self._build_qdrant_filter(filters)

        # 2. 使用 scroll 而不是 search
        # 為什麼用 scroll？因為 search 必須傳入 query_vector 來算分數，
        # 而 scroll 只是單純把符合條件的資料 "滾" 出來，不進行數學運算。
        records, next_page_offset = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=qdrant_filter,
            limit=limit,
            with_payload=True,
            with_vectors=False # 既然不比對向量，我們連向量資料都不用抓回來，節省頻寬
        )

        # 3. 整理回傳格式
        formatted_results = []
        for record in records:
            real_job_id = record.payload.get("job_id", record.id)
            formatted_results.append({
                "job_id": real_job_id,
                "score_text": None, # 因為沒有做向量檢索，所以相似度分數是 None
                "payload": record.payload
            })
            
        return formatted_results
    
    def search_hybrid_jobs(self, query_vector: List[float], filters: Dict[str, Any], limit: int = 50) -> List[Dict]:
        """
        [整體意圖]
        這就是我們系統的「第一階段召回 (Phase 1 Recall)」。
        它同時執行硬篩選 (過濾地區、薪資) 與語意向量相似度比對 (0.3 的分數來源)。
        """
        # 1. 組裝硬篩選條件 (複用我們之前寫好的黑盒邏輯)
        qdrant_filter = self._build_qdrant_filter(filters)

        # 2. 呼叫最新的 query_points API
        # ⚠️ 注意兩大修改：
        #    (1) 方法名稱改為 query_points
        #    (2) 參數名稱 query_vector 改為 query
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,          # 傳入陳浩宇的履歷向量
            query_filter=qdrant_filter,  # 傳入硬篩選條件
            limit=limit,                 
            with_payload=True            
        )

        # 3. 整理回傳格式
        formatted_results = []
        # ⚠️ 注意修改：最新的 API 會回傳一個 Response 物件，
        # 我們必須加上 .points 才能把裡面的職缺陣列拿出來迴圈
        for hit in response.points:
            # 優先從 Payload 拿取業務 ID
            real_job_id = hit.payload.get("job_id", hit.id)
            
            formatted_results.append({
                "job_id": real_job_id,
                "score_text": hit.score, # 這是 0.3 的文本相似度分數
                "payload": hit.payload   # D1~D6 分數在這裡面
            })
            
        return formatted_results

    # def search_jobs(self, query_vector: List[float], filters: Dict[str, Any], top_k: int = 50) -> List[Dict]:
    #     """
    #     [整體意圖]
    #     結合文本向量 (query_vector) 與硬篩選條件 (filters)，向 Qdrant 要資料。
    #     """
    #     # 1. 呼叫上方的方法，組裝過濾器 
    #     qdrant_filter = self._build_qdrant_filter(filters)

    #     # 2. 執行混合檢索
    #     search_results = self.client.search(
    #         collection_name=self.collection_name,
    #         query_vector=query_vector,
    #         query_filter=qdrant_filter, # 這裡把硬篩選條件塞進去！
    #         limit=top_k,
    #         with_payload=True # 務必設為 True，這樣才能把職缺的 D1~D6 分數一起拿回來
    #     )

    #     # 3. 整理回傳格式，方便下一個階段 (Python 計算 0.7 歐幾里得) 使用
    #     formatted_results = []
    #     for hit in search_results:
    #         formatted_results.append({
    #             "job_id": hit.id,
    #             "score_text": hit.score, # 這就是 Qdrant 算出的文本相似度 (佔 0.3)
    #             "payload": hit.payload   # 裡面包含 location, salary, d1_score 等資料
    #         })
            
    #     return formatted_results

class UserProfileRetriever:
    """
    負責從資料庫中提取使用者相關的向量與元數據。
    """
    def __init__(self, client: QdrantClient, resume_collection_name: str):
        self.client = client
        self.resume_collection_name = resume_collection_name

    def get_resume_vector(self, user_id: int) -> List[float]:
        """
        [逐行解析與意圖]
        透過 Payload 裡面的 user_id 欄位，撈取優化後的履歷向量。
        """
        # 1. 建立廣播條件：尋找 Payload 中 "user_id" 等於我們傳入的數字的資料
        # ⚠️ 【關鍵提示】：請確認您 Payload 裡面的鍵值真的是 "user_id"
        # 如果當初寫入時叫做 "id" 或 "userId"，請把下方的 key="user_id" 改掉
        user_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="user_id", 
                    match=models.MatchValue(value=user_id) # 精確比對這個數值
                )
            ]
        )

        # 2. 使用 scroll API 執行條件過濾
        # with_vectors=True 是為了把 1536 維的向量拿回來
        records, _ = self.client.scroll(
            collection_name=self.resume_collection_name,
            scroll_filter=user_filter,
            limit=1,              # 因為 user_id 應該是唯一的，拿 1 筆就夠了
            with_vectors=True,    
            with_payload=False    # 已經確定是這個人了，不需要把履歷文字抓回來佔頻寬
        )

        # 3. 錯誤處理：如果廣播了還是沒人理
        if not records:
            raise ValueError(f"❌ 找不到 Payload 中 user_id 為 [{user_id}] 的優化履歷向量！")
        
        # 4. 成功拿到！records[0] 是第一筆回傳資料，.vector 則是它的向量陣列
        return records[0].vector