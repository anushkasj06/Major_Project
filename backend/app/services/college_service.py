"""College service — business logic layer."""
from typing import List, Optional, Dict, Any
from app.repositories.college_repository import CollegeRepository
from app.core.redis_client import cache_get, cache_set


class CollegeService:

    @staticmethod
    async def search_colleges(
        query: str = "",
        college_type: Optional[str] = None,
        city: Optional[str] = None,
        min_placement: Optional[float] = None,
        max_fees: Optional[int] = None,
        branch: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Dict]:
        cache_key = f"college_search:{query}:{college_type}:{city}:{skip}:{limit}"
        cached = await cache_get(cache_key)
        if cached:
            return cached

        filters: Dict[str, Any] = {}
        if college_type:
            filters["college_type"] = college_type
        if city:
            filters["location.city"] = {"$regex": city, "$options": "i"}
        if max_fees:
            filters["fees.annual_tuition"] = {"$lte": max_fees}
        if min_placement:
            filters["placements.avg_package_lpa"] = {"$gte": min_placement}
        if branch:
            filters["branches.name"] = {"$regex": branch, "$options": "i"}

        results = await CollegeRepository.search(query=query, filters=filters, skip=skip, limit=limit)
        await cache_set(cache_key, results, ttl=300)
        return results

    @staticmethod
    async def get_college_summary(college_id: str) -> Optional[Dict]:
        cache_key = f"college:{college_id}"
        cached = await cache_get(cache_key)
        if cached:
            return cached
        college = await CollegeRepository.get_by_id(college_id)
        if college:
            await cache_set(cache_key, college, ttl=600)
        return college

    @staticmethod
    async def compare_colleges(college_ids: List[str]) -> List[Dict]:
        results = []
        for cid in college_ids[:5]:
            c = await CollegeRepository.get_by_id(cid)
            if c:
                results.append({
                    "id": c["_id"],
                    "name": c["name"],
                    "location": c.get("location", {}),
                    "fees": c.get("fees", {}),
                    "placements": c.get("placements", {}),
                    "ranking": c.get("ranking", {}),
                    "branches": c.get("branches", []),
                })
        return results
