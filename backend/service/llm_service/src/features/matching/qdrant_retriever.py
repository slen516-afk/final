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
        將前端傳來的字典轉換成 Qdrant 的 Filter 物件。
        """
        must_conditions = []

        # 1. 處理地區 (City) -> 支援多選
        if "city" in filters and filters["city"]:
            must_conditions.append(
                models.FieldCondition(
                    key="city", 
                    match=models.MatchAny(any=filters["city"])
                )
            )

        # 2. 處理薪資 (邏輯：職缺上限 >= 使用者下限)
        if "salary_min" in filters:
            must_conditions.append(
                models.FieldCondition(
                    key="salary_max", 
                    range=models.Range(
                        gte=filters.get("salary_min")
                    )
                )
            )

        return models.Filter(must=must_conditions)
    
    def filter_jobs_only(self, filters: Dict[str, Any], limit: int = 50) -> List[Dict]:
        """
        純硬篩選 (Scroll API)，不計算語意分數。
        """
        qdrant_filter = self._build_qdrant_filter(filters)

        records, _ = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=qdrant_filter,
            limit=limit,
            with_payload=True,
            with_vectors=False 
        )

        formatted_results = []
        for record in records:
            real_job_id = record.payload.get("job_id", record.id)
            formatted_results.append({
                "job_id": real_job_id,
                "score_text": None, 
                "payload": record.payload
            })
            
        return formatted_results
    
    def search_hybrid_jobs(self, query_vector: List[float], filters: Dict[str, Any], limit: int = 50) -> List[Dict]:
        """
        第一階段召回 (Phase 1 Recall)：語意搜尋 + 硬篩選。
        回傳 score_text 為語意相似度。
        """
        qdrant_filter = self._build_qdrant_filter(filters)

        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=qdrant_filter,
            limit=limit,
            with_payload=True            
        )

        formatted_results = []
        for hit in response.points:
            real_job_id = hit.payload.get("job_id", hit.id)
            formatted_results.append({
                "job_id": real_job_id,
                "score_text": hit.score, # 這是 0.3 的來源
                "payload": hit.payload
            })
            
        return formatted_results

class UserProfileRetriever:
    """
    負責從 Qdrant 提取使用者的優化履歷向量。
    """
    def __init__(self, client: QdrantClient, resume_collection_name: str):
        self.client = client
        self.resume_collection_name = resume_collection_name

    def get_resume_vector(self, user_id: int) -> List[float]:
        """
        透過 user_id 撈取 1536 維的向量。
        """
        user_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="user_id", 
                    match=models.MatchValue(value=user_id)
                )
            ]
        )

        records, _ = self.client.scroll(
            collection_name=self.resume_collection_name,
            scroll_filter=user_filter,
            limit=1,
            with_vectors=True,    
            with_payload=False    
        )

        if not records:
            raise ValueError(f"❌ 找不到 user_id 為 [{user_id}] 的履歷向量！")
        
        return records[0].vector
