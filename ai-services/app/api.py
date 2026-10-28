"""AI Services API routes."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json, logging, os
from datetime import datetime
from bson import ObjectId

logger = logging.getLogger(__name__)

chat_router = APIRouter()
ingest_router = APIRouter()


class ChatRequest(BaseModel):
    query: str
    session_id: str
    user_id: str
    language: str = "en"
    college_filter: Optional[str] = None
    conversation_history: List[Dict] = []


class IngestRequest(BaseModel):
    document_id: str
    file_path: str
    college_id: Optional[str] = None
    document_type: str = "general"


@chat_router.post("/chat")
async def chat(req: ChatRequest):
    from app.agents.rag_agent import run_rag_pipeline
    result = await run_rag_pipeline(
        query=req.query, session_id=req.session_id, user_id=req.user_id,
        language=req.language, college_filter=req.college_filter,
        conversation_history=req.conversation_history
    )
    return result


@chat_router.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    from app.agents.rag_agent import stream_rag_pipeline

    async def event_generator():
        async for chunk in stream_rag_pipeline(
            query=req.query, session_id=req.session_id, user_id=req.user_id,
            language=req.language, college_filter=req.college_filter,
            conversation_history=req.conversation_history
        ):
            yield f"data: {json.dumps(chunk)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@ingest_router.post("/ingest")
async def ingest_document(req: IngestRequest):
    """Ingest a document: extract text, chunk, embed, and index."""
    from app.rag.ingestion import ingest_file
    try:
        result = await ingest_file(
            document_id=req.document_id,
            file_path=req.file_path,
            college_id=req.college_id,
            document_type=req.document_type,
        )
        return result
    except Exception as e:
        logger.error(f"Ingestion failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@ingest_router.post("/reindex")
async def reindex(college_id: Optional[str] = None):
    """Reindex all documents for a college or all documents."""
    return {"message": "Reindex triggered", "college_id": college_id}


@ingest_router.post("/ingest/url")
async def ingest_url(url: str, college_id: Optional[str] = None, college_name: Optional[str] = None):
    """Ingest content from a URL directly."""
    from app.rag.ingestion import ingest_url as _ingest_url
    result = await _ingest_url(url=url, college_id=college_id, college_name=college_name)
    return result
