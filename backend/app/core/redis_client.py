"""
Arambh Backend — Redis client for caching and sessions
"""
import redis.asyncio as redis
from typing import Optional, Any
import json
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

redis_client: Optional[redis.Redis] = None


async def init_redis():
    global redis_client
    logger.info("Connecting to Redis...")
    redis_client = redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )
    await redis_client.ping()
    logger.info("✅ Redis connected")


async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()


def get_redis() -> redis.Redis:
    if redis_client is None:
        raise RuntimeError("Redis not initialized")
    return redis_client


async def cache_set(key: str, value: Any, ttl: int = None) -> bool:
    r = get_redis()
    ttl = ttl or settings.REDIS_TTL
    serialized = json.dumps(value) if not isinstance(value, str) else value
    return await r.setex(key, ttl, serialized)


async def cache_get(key: str) -> Optional[Any]:
    r = get_redis()
    val = await r.get(key)
    if val is None:
        return None
    try:
        return json.loads(val)
    except (json.JSONDecodeError, TypeError):
        return val


async def cache_delete(key: str) -> bool:
    r = get_redis()
    return bool(await r.delete(key))


async def cache_delete_pattern(pattern: str) -> int:
    r = get_redis()
    keys = await r.keys(pattern)
    if keys:
        return await r.delete(*keys)
    return 0
