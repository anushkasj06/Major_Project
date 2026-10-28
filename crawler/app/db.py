"""Crawler DB helpers."""
import os
from typing import Optional, Dict
async def get_job_status(job_id: str) -> Optional[Dict]:
    import motor.motor_asyncio
    from bson import ObjectId
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGODB_URL", ""))
        db = client[os.getenv("MONGODB_DB_NAME", "arambh")]
        job = await db.crawler_jobs.find_one({"_id": ObjectId(job_id)})
        client.close()
        if job:
            job["_id"] = str(job["_id"])
        return job
    except Exception:
        return None
