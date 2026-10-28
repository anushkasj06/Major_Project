"""
Arambh Backend — Chat Routes with SSE streaming
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import httpx
import json
import logging
import uuid
from datetime import datetime

from app.core.security import get_current_user
from app.core.config import settings
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.analytics_repository import AnalyticsRepository

router = APIRouter()
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    language: Optional[str] = "en"
    college_filter: Optional[str] = None
    stream: bool = True


class FeedbackRequest(BaseModel):
    session_id: str
    message_index: int
    was_helpful: bool
    feedback_text: Optional[str] = None


@router.post("/message")
async def chat_message(
    request: ChatRequest,
    current_user=Depends(get_current_user)
):
    """Send a chat message — returns streaming or non-streaming response."""
    user_id = str(current_user["_id"])
    session_id = request.session_id or str(uuid.uuid4())

    # Get conversation history
    conversation = await ConversationRepository.get_or_create(user_id, session_id)
    history = conversation.get("messages", [])[-10:]  # last 10 messages

    # Prepare request for AI service
    ai_request = {
        "query": request.message,
        "session_id": session_id,
        "user_id": user_id,
        "language": request.language or current_user.get("preferred_language", "en"),
        "college_filter": request.college_filter,
        "conversation_history": history,
    }

    # Save user message
    await ConversationRepository.add_message(session_id, {
        "role": "user",
        "content": request.message,
        "timestamp": datetime.utcnow(),
        "language": request.language,
    })

    if request.stream:
        return StreamingResponse(
            _stream_ai_response(ai_request, session_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Access-Control-Allow-Origin": "*",
            }
        )
    else:
        return await _get_ai_response(ai_request, session_id)


async def _stream_ai_response(ai_request: dict, session_id: str):
    """Stream response from AI service via SSE."""
    full_response = ""
    sources = []

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{settings.AI_SERVICE_URL}/ai/chat/stream",
                json=ai_request,
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    yield f"data: {json.dumps({'error': 'AI service error', 'detail': error_text.decode()})}\n\n"
                    return

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            if data.get("type") == "token":
                                full_response += data.get("content", "")
                                yield f"data: {json.dumps(data)}\n\n"
                            elif data.get("type") == "sources":
                                sources = data.get("sources", [])
                                yield f"data: {json.dumps(data)}\n\n"
                            elif data.get("type") == "metadata":
                                yield f"data: {json.dumps(data)}\n\n"
                        except json.JSONDecodeError:
                            pass

        # Save assistant message
        await ConversationRepository.add_message(session_id, {
            "role": "assistant",
            "content": full_response,
            "timestamp": datetime.utcnow(),
            "sources": sources,
        })

        # Log analytics
        await AnalyticsRepository.log_query({
            "session_id": session_id,
            "query": ai_request["query"],
            "response_length": len(full_response),
            "sources_count": len(sources),
        })

        yield f"data: [DONE]\n\n"

    except httpx.ConnectError:
        yield f"data: {json.dumps({'error': 'AI service unavailable'})}\n\n"
    except Exception as e:
        logger.error(f"Streaming error: {e}", exc_info=True)
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


async def _get_ai_response(ai_request: dict, session_id: str):
    """Non-streaming response from AI service."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{settings.AI_SERVICE_URL}/ai/chat",
            json=ai_request,
        )
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail="AI service error")

        result = response.json()

        # Save assistant message
        await ConversationRepository.add_message(session_id, {
            "role": "assistant",
            "content": result.get("response", ""),
            "timestamp": datetime.utcnow(),
            "sources": result.get("sources", []),
            "confidence": result.get("confidence", 0.0),
        })

        return result


@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    current_user=Depends(get_current_user)
):
    """Get conversation history for a session."""
    user_id = str(current_user["_id"])
    conversation = await ConversationRepository.get_by_session(session_id, user_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.get("/sessions")
async def get_sessions(current_user=Depends(get_current_user)):
    """Get all conversation sessions for the user."""
    user_id = str(current_user["_id"])
    sessions = await ConversationRepository.get_user_sessions(user_id)
    return sessions


@router.delete("/session/{session_id}")
async def delete_session(
    session_id: str,
    current_user=Depends(get_current_user)
):
    """Delete a conversation session."""
    user_id = str(current_user["_id"])
    deleted = await ConversationRepository.delete_session(session_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted"}


@router.post("/feedback")
async def submit_feedback(
    feedback: FeedbackRequest,
    current_user=Depends(get_current_user)
):
    """Submit feedback on a response."""
    user_id = str(current_user["_id"])
    await AnalyticsRepository.update_feedback(
        feedback.session_id,
        feedback.message_index,
        feedback.was_helpful,
        feedback.feedback_text
    )
    return {"message": "Feedback recorded"}
