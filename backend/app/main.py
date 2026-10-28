"""
Arambh Backend API — FastAPI Application
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings
from app.core.database import connect_db, disconnect_db
from app.core.redis_client import init_redis, close_redis
from app.api.middleware.rate_limiter import RateLimitMiddleware
from app.api.middleware.logging_middleware import LoggingMiddleware
from app.api.routes import (
    auth, chat, colleges, admin, crawler, health, documents, analytics
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("🚀 Starting Arambh API...")
    await connect_db()
    await init_redis()
    logger.info("✅ Arambh API ready")
    yield
    logger.info("🛑 Shutting down Arambh API...")
    await disconnect_db()
    await close_redis()


app = FastAPI(
    title="Arambh API",
    description="Scalable Multi-Agent RAG-Powered Admission Assistance",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# ─── Middleware ────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# ─── Routes ───────────────────────────────────
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(colleges.router, prefix="/api/colleges", tags=["Colleges"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(crawler.router, prefix="/api/crawler", tags=["Crawler"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__}
    )
