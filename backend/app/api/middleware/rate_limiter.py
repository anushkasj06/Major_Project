"""Rate limiting middleware using Redis."""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import time

RATE_LIMIT = 100  # requests per minute
WINDOW = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api/docs") or request.url.path == "/api/health":
            return await call_next(request)
        try:
            from app.core.redis_client import get_redis
            r = get_redis()
            ip = request.client.host if request.client else "unknown"
            key = f"rl:{ip}"
            count = await r.incr(key)
            if count == 1:
                await r.expire(key, WINDOW)
            if count > RATE_LIMIT:
                return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
        except Exception:
            pass
        return await call_next(request)
