"""Tests for chat endpoints."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_chat_requires_auth():
    from app.main import app
    from httpx import AsyncClient, ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/chat/message", json={
            "message": "What are COEP fees?",
            "session_id": "test_session",
            "stream": False,
        })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_sessions_requires_auth():
    from app.main import app
    from httpx import AsyncClient, ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/chat/sessions")
    assert response.status_code == 401
