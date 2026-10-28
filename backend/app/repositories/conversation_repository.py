"""Conversation repository — MongoDB CRUD for chat sessions."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from bson import ObjectId
import uuid
from app.core.database import get_collection


class ConversationRepository:
    COLLECTION = "conversations"

    @classmethod
    def _col(cls):
        return get_collection(cls.COLLECTION)

    @classmethod
    async def get_or_create(cls, user_id: str, session_id: str) -> Dict:
        existing = await cls._col().find_one({"session_id": session_id, "user_id": user_id})
        if existing:
            existing["_id"] = str(existing["_id"])
            return existing
        doc = {
            "user_id": user_id,
            "session_id": session_id,
            "messages": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = await cls._col().insert_one(doc)
        doc["_id"] = str(result.inserted_id)
        return doc

    @classmethod
    async def add_message(cls, session_id: str, message: Dict):
        await cls._col().update_one(
            {"session_id": session_id},
            {
                "$push": {"messages": message},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

    @classmethod
    async def get_by_session(cls, session_id: str, user_id: str) -> Optional[Dict]:
        doc = await cls._col().find_one({"session_id": session_id, "user_id": user_id})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    @classmethod
    async def get_user_sessions(cls, user_id: str) -> List[Dict]:
        cursor = cls._col().find(
            {"user_id": user_id},
            {"messages": {"$slice": -1}, "session_id": 1, "created_at": 1, "updated_at": 1, "title": 1}
        ).sort("updated_at", -1).limit(20)
        sessions = []
        async for s in cursor:
            s["_id"] = str(s["_id"])
            sessions.append(s)
        return sessions

    @classmethod
    async def delete_session(cls, session_id: str, user_id: str) -> bool:
        result = await cls._col().delete_one({"session_id": session_id, "user_id": user_id})
        return result.deleted_count > 0

    @classmethod
    async def update_title(cls, session_id: str, title: str):
        await cls._col().update_one(
            {"session_id": session_id},
            {"$set": {"title": title}}
        )
