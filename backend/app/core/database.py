"""
Arambh Backend — MongoDB async connection using Motor
"""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

client: Optional[AsyncIOMotorClient] = None


async def connect_db():
    global client
    logger.info(f"Connecting to MongoDB...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    # Verify connection
    await client.admin.command("ping")
    logger.info("✅ MongoDB connected")


async def disconnect_db():
    global client
    if client:
        client.close()
        logger.info("MongoDB disconnected")


def get_database():
    if client is None:
        raise RuntimeError("Database not initialized. Call connect_db() first.")
    return client[settings.MONGODB_DB_NAME]


def get_collection(collection_name: str):
    db = get_database()
    return db[collection_name]
