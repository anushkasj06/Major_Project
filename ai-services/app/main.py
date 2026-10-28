"""Arambh AI Services — RAG + LangGraph Agents"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging, os

from app.rag.vector_store import init_vector_store
from app.embeddings.embedding_service import init_embeddings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🤖 Initializing AI Services...")
    await init_embeddings()
    await init_vector_store()
    logger.info("✅ AI Services ready")
    yield

app = FastAPI(title="Arambh AI Services", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

from app.api import chat_router, ingest_router
app.include_router(chat_router, prefix="/ai")
app.include_router(ingest_router, prefix="/ai")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "ai-services"}
