"""Health check routes."""
from fastapi import APIRouter
from app.core.database import get_database
from app.core.redis_client import get_redis
import httpx
from app.core.config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    status = {"status": "ok", "services": {}}
    try:
        db = get_database()
        await db.command("ping")
        status["services"]["mongodb"] = "ok"
    except Exception as e:
        status["services"]["mongodb"] = f"error: {e}"
        status["status"] = "degraded"
    try:
        r = get_redis()
        await r.ping()
        status["services"]["redis"] = "ok"
    except Exception as e:
        status["services"]["redis"] = f"error: {e}"
        status["status"] = "degraded"
    return status
