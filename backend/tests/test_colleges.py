"""Tests for college endpoints."""
import pytest
from unittest.mock import AsyncMock, patch


MOCK_COLLEGE = {
    "_id": "64f1a2b3c4d5e6f7a8b9c0d1",
    "name": "COEP Pune",
    "college_type": "engineering",
    "location": {"city": "Pune", "state": "Maharashtra"},
    "fees": {"annual_tuition": 95000},
    "placements": {"avg_package_lpa": 8.5},
    "branches": [{"name": "Computer Engineering", "seats": 120}],
}


@pytest.mark.asyncio
async def test_list_colleges():
    from app.main import app
    from httpx import AsyncClient, ASGITransport
    with patch("app.repositories.college_repository.CollegeRepository.search",
               AsyncMock(return_value=[MOCK_COLLEGE])):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/colleges/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_college_not_found():
    from app.main import app
    from httpx import AsyncClient, ASGITransport
    with patch("app.repositories.college_repository.CollegeRepository.get_by_id",
               AsyncMock(return_value=None)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/colleges/nonexistent_id")
        assert response.status_code == 404
