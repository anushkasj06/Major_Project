"""Admin dashboard routes."""
from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_admin
from app.repositories.user_repository import UserRepository
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.college_repository import CollegeRepository
from app.core.config import settings
import httpx

router = APIRouter()

@router.get("/users")
async def list_users(skip: int = 0, limit: int = 50, current_user=Depends(get_current_admin)):
    return await UserRepository.list_users(skip, limit)

@router.put("/users/{user_id}/role")
async def update_user_role(user_id: str, role: str, current_user=Depends(get_current_admin)):
    if role not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    await UserRepository.update_role(user_id, role)
    return {"message": f"Role updated to {role}"}

@router.delete("/users/{user_id}")
async def deactivate_user(user_id: str, current_user=Depends(get_current_admin)):
    await UserRepository.deactivate(user_id)
    return {"message": "User deactivated"}

@router.post("/reindex")
async def trigger_reindex(college_id: str = None, current_user=Depends(get_current_admin)):
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            f"{settings.AI_SERVICE_URL}/ai/reindex",
            json={"college_id": college_id}
        )
    return resp.json()

@router.get("/crawler/jobs")
async def get_crawler_jobs(current_user=Depends(get_current_admin)):
    from app.core.database import get_collection
    col = get_collection("crawler_jobs")
    cursor = col.find({}).sort("created_at", -1).limit(20)
    jobs = []
    async for j in cursor:
        j["_id"] = str(j["_id"])
        jobs.append(j)
    return jobs
