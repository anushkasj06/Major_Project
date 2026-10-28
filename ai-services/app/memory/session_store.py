"""
Session-based conversation memory backed by Redis.
Stores last N messages per session for context injection.
"""
import json, os, logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)
MAX_HISTORY = 20


async def get_redis():
    import redis.asyncio as aioredis
    return aioredis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"), decode_responses=True)


async def save_message(session_id: str, role: str, content: str, metadata: dict = {}):
    """Save a message to session history in Redis."""
    try:
        r = await get_redis()
        key = f"session:{session_id}:history"
        message = json.dumps({"role": role, "content": content, **metadata})
        await r.rpush(key, message)
        await r.ltrim(key, -MAX_HISTORY, -1)
        await r.expire(key, 86400)  # 24h TTL
        await r.aclose()
    except Exception as e:
        logger.warning(f"Could not save message to Redis: {e}")


async def get_history(session_id: str, last_n: int = 10) -> List[Dict[str, Any]]:
    """Get last N messages for a session."""
    try:
        r = await get_redis()
        key = f"session:{session_id}:history"
        raw = await r.lrange(key, -last_n * 2, -1)
        await r.aclose()
        messages = []
        for item in raw:
            try:
                messages.append(json.loads(item))
            except Exception:
                pass
        return messages
    except Exception as e:
        logger.warning(f"Could not read session history: {e}")
        return []


async def clear_session(session_id: str):
    """Clear all history for a session."""
    try:
        r = await get_redis()
        await r.delete(f"session:{session_id}:history")
        await r.aclose()
    except Exception:
        pass
