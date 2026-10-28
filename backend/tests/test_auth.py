"""Tests for authentication endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_register_success():
    from app.main import app
    with patch("app.repositories.user_repository.UserRepository.get_by_email", return_value=None), \
         patch("app.repositories.user_repository.UserRepository.create", return_value="fake_id_123"):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/auth/register", json={
                "name": "Test User", "email": "test@example.com", "password": "password123"
            })
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_register_duplicate_email():
    from app.main import app
    with patch("app.repositories.user_repository.UserRepository.get_by_email",
               return_value={"email": "test@example.com"}):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/auth/register", json={
                "name": "Test", "email": "test@example.com", "password": "password123"
            })
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_health_check():
    from app.main import app
    with patch("app.core.database.get_database") as mock_db, \
         patch("app.core.redis_client.get_redis") as mock_redis:
        mock_db.return_value.command = AsyncMock(return_value=True)
        mock_redis.return_value.ping = AsyncMock(return_value=True)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] in ["ok", "degraded"]
