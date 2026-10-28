"""User repository — MongoDB CRUD for users."""
from datetime import datetime
from typing import Optional, Dict, Any
from bson import ObjectId
from app.core.database import get_collection


class UserRepository:
    COLLECTION = "users"

    @classmethod
    def _col(cls):
        return get_collection(cls.COLLECTION)

    @classmethod
    async def create(cls, user_doc: Dict[str, Any]) -> str:
        result = await cls._col().insert_one(user_doc)
        return str(result.inserted_id)

    @classmethod
    async def get_by_email(cls, email: str) -> Optional[Dict]:
        return await cls._col().find_one({"email": email})

    @classmethod
    async def get_by_id(cls, user_id: str) -> Optional[Dict]:
        try:
            return await cls._col().find_one({"_id": ObjectId(user_id)})
        except Exception:
            return None

    @classmethod
    async def update_last_login(cls, user_id: str):
        await cls._col().update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"last_login": datetime.utcnow()}}
        )

    @classmethod
    async def update_language(cls, user_id: str, language: str):
        await cls._col().update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"preferred_language": language}}
        )

    @classmethod
    async def list_users(cls, skip=0, limit=50) -> list:
        cursor = cls._col().find({}, {"hashed_password": 0}).skip(skip).limit(limit)
        users = []
        async for u in cursor:
            u["_id"] = str(u["_id"])
            users.append(u)
        return users

    @classmethod
    async def count(cls) -> int:
        return await cls._col().count_documents({})

    @classmethod
    async def update_role(cls, user_id: str, role: str):
        await cls._col().update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"role": role}}
        )

    @classmethod
    async def deactivate(cls, user_id: str):
        await cls._col().update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_active": False}}
        )
