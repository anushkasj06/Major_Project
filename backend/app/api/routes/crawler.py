"""Crawler trigger routes."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import httpx
from app.core.security import get_current_admin
from app.core.config import settings
from app.core.database import get_collection
from datetime import datetime

router = APIRouter()

class CrawlRequest(BaseModel):
    url: str
    college_id: Optional[str] = None
    job_type: str = "full"
    max_depth: int = 3
    max_pages: int = 100

@router.post("/start")
async def start_crawl(req: CrawlRequest, current_user=Depends(get_current_admin)):
    col = get_collection("crawler_jobs")
    job = {
        "url": req.url, "college_id": req.college_id, "job_type": req.job_type,
        "status": "pending", "pages_crawled": 0, "pages_indexed": 0,
        "created_by": str(current_user["_id"]), "created_at": datetime.utcnow()
    }
    result = await col.insert_one(job)
    job_id = str(result.inserted_id)
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(
                f"{settings.CRAWLER_SERVICE_URL}/crawler/start",
                json={"job_id": job_id, **req.dict()}
            )
    except Exception as e:
        pass
    return {"job_id": job_id, "status": "pending"}

@router.get("/jobs")
async def list_jobs(current_user=Depends(get_current_admin)):
    col = get_collection("crawler_jobs")
    cursor = col.find({}).sort("created_at", -1).limit(30)
    jobs = []
    async for j in cursor:
        j["_id"] = str(j["_id"])
        jobs.append(j)
    return jobs
