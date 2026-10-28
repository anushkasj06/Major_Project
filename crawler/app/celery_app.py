"""Celery app for async crawl tasks."""
from celery import Celery
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

celery_app = Celery(
    "arambh_crawler",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.celery_app"],
)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    beat_schedule={
        "crawl-all-colleges-daily": {
            "task": "app.celery_app.scheduled_crawl",
            "schedule": 86400.0,  # 24 hours
        },
    },
)

@celery_app.task(name="app.celery_app.crawl_task", bind=True, max_retries=3)
def crawl_task(self, job_id: str, url: str, college_id=None, max_depth=3, max_pages=100):
    """Celery task wrapping the async crawl_site function."""
    import asyncio
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        from app.spider import crawl_site
        result = loop.run_until_complete(
            crawl_site(job_id=job_id, url=url, college_id=college_id, max_depth=max_depth, max_pages=max_pages)
        )
        loop.close()
        return result
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(name="app.celery_app.scheduled_crawl")
def scheduled_crawl():
    """Scheduled task to re-crawl all registered college URLs."""
    import asyncio, motor.motor_asyncio, os
    async def _run():
        client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGODB_URL", ""))
        db = client[os.getenv("MONGODB_DB_NAME", "arambh")]
        colleges = await db.colleges.find({"website": {"$exists": True}}).to_list(100)
        client.close()
        for college in colleges:
            if college.get("website"):
                crawl_task.delay(
                    job_id=str(college["_id"]) + "_sched",
                    url=college["website"],
                    college_id=str(college["_id"]),
                )
    asyncio.run(_run())
