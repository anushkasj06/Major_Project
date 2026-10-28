"""Periodic crawl scheduler using Celery Beat."""
import logging, os
from datetime import datetime

logger = logging.getLogger(__name__)


async def get_colleges_to_crawl() -> list:
    """Get list of colleges with websites that need re-crawling."""
    import motor.motor_asyncio
    from datetime import timedelta

    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017/arambh")
    client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
    db = client[os.getenv("MONGODB_DB_NAME", "arambh")]

    # Colleges not crawled in last 7 days
    cutoff = datetime.utcnow() - timedelta(days=7)
    cursor = db.colleges.find({
        "website": {"$exists": True, "$ne": ""},
        "$or": [
            {"last_crawled": {"$lt": cutoff}},
            {"last_crawled": {"$exists": False}},
        ]
    }).limit(10)

    colleges = await cursor.to_list(10)
    client.close()
    return colleges


async def mark_college_crawled(college_id: str):
    """Update last_crawled timestamp for a college."""
    import motor.motor_asyncio
    from bson import ObjectId

    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017/arambh")
    client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
    db = client[os.getenv("MONGODB_DB_NAME", "arambh")]

    await db.colleges.update_one(
        {"_id": ObjectId(college_id)},
        {"$set": {"last_crawled": datetime.utcnow()}}
    )
    client.close()
