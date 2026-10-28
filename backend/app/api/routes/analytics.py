"""Analytics routes."""
from fastapi import APIRouter, Depends
from app.core.security import get_current_admin
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.user_repository import UserRepository
from app.repositories.college_repository import CollegeRepository

router = APIRouter()

@router.get("/stats", dependencies=[Depends(get_current_admin)])
async def get_stats():
    query_stats = await AnalyticsRepository.get_stats()
    user_count = await UserRepository.count()
    college_count = await CollegeRepository.count()
    top_queries = await AnalyticsRepository.get_top_queries(10)
    return {
        **query_stats,
        "total_users": user_count,
        "total_colleges": college_count,
        "top_queries": top_queries,
    }
