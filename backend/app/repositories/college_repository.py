"""College repository."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from bson import ObjectId
from app.core.database import get_collection


class CollegeRepository:
    COLLECTION = "colleges"

    @classmethod
    def _col(cls):
        return get_collection(cls.COLLECTION)

    @classmethod
    async def create(cls, data: Dict) -> str:
        data["created_at"] = datetime.utcnow()
        data["updated_at"] = datetime.utcnow()
        result = await cls._col().insert_one(data)
        return str(result.inserted_id)

    @classmethod
    async def get_by_id(cls, college_id: str) -> Optional[Dict]:
        try:
            doc = await cls._col().find_one({"_id": ObjectId(college_id)})
            if doc: doc["_id"] = str(doc["_id"])
            return doc
        except: return None

    @classmethod
    async def search(cls, query: str = "", filters: Dict = {}, skip=0, limit=20) -> List[Dict]:
        match = {}
        if query:
            match["$text"] = {"$search": query}
        match.update(filters)
        cursor = cls._col().find(match).skip(skip).limit(limit)
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        return results

    @classmethod
    async def list_all(cls, skip=0, limit=50) -> List[Dict]:
        cursor = cls._col().find({}).skip(skip).limit(limit)
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        return results

    @classmethod
    async def update(cls, college_id: str, data: Dict) -> bool:
        data["updated_at"] = datetime.utcnow()
        result = await cls._col().update_one(
            {"_id": ObjectId(college_id)},
            {"$set": data}
        )
        return result.modified_count > 0

    @classmethod
    async def delete(cls, college_id: str) -> bool:
        result = await cls._col().delete_one({"_id": ObjectId(college_id)})
        return result.deleted_count > 0

    @classmethod
    async def count(cls) -> int:
        return await cls._col().count_documents({})
