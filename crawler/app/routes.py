"""Crawler routes."""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import logging
from app.spider import crawl_site
from app.celery_app import crawl_task

router = APIRouter()
logger = logging.getLogger(__name__)


class CrawlRequest(BaseModel):
    job_id: str
    url: str
    college_id: Optional[str] = None
    job_type: str = "full"
    max_depth: int = 3
    max_pages: int = 100


@router.post("/start")
async def start_crawl(req: CrawlRequest, background_tasks: BackgroundTasks):
    """Start a crawl job."""
    try:
        task = crawl_task.delay(
            job_id=req.job_id,
            url=req.url,
            college_id=req.college_id,
            max_depth=req.max_depth,
            max_pages=req.max_pages,
        )
        return {"job_id": req.job_id, "celery_task_id": task.id, "status": "started"}
    except Exception as e:
        logger.error(f"Failed to start crawl: {e}")
        background_tasks.add_task(crawl_site, req.job_id, req.url, req.college_id, req.max_depth, req.max_pages)
        return {"job_id": req.job_id, "status": "started_background"}


@router.get("/status/{job_id}")
async def get_status(job_id: str):
    from app.db import get_job_status
    status = await get_job_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    return status
