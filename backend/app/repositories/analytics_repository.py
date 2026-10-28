"""Analytics repository."""
from datetime import datetime
from typing import Dict, Any, List
from bson import ObjectId
from app.core.database import get_collection


class AnalyticsRepository:
    COLLECTION = "query_analytics"

    @classmethod
    def _col(cls):
        return get_collection(cls.COLLECTION)

    @classmethod
    async def log_query(cls, data: Dict[str, Any]) -> str:
        data["created_at"] = datetime.utcnow()
        result = await cls._col().insert_one(data)
        return str(result.inserted_id)

    @classmethod
    async def update_feedback(cls, session_id: str, message_index: int, was_helpful: bool, text: str = None):
        await cls._col().update_one(
            {"session_id": session_id},
            {"$set": {"was_helpful": was_helpful, "feedback_text": text}}
        )

    @classmethod
    async def get_top_queries(cls, limit=20) -> List[Dict]:
        pipeline = [
            {"$group": {"_id": "$query", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        results = []
        async for doc in cls._col().aggregate(pipeline):
            results.append(doc)
        return results

    @classmethod
    async def get_stats(cls) -> Dict:
        total = await cls._col().count_documents({})
        helpful = await cls._col().count_documents({"was_helpful": True})
        return {"total_queries": total, "helpful_responses": helpful}
