"""Arambh Crawler Service."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🕷️ Crawler service starting...")
    yield

app = FastAPI(title="Arambh Crawler", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

from app.routes import router
app.include_router(router, prefix="/crawler")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "crawler"}
