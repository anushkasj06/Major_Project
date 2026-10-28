"""Recommendation Agent — recommends colleges based on student preferences."""
import logging
from typing import Dict, Any, List, Optional
from app.agents.llm_provider import generate_response
from app.prompts.templates import RECOMMENDATION_PROMPT
from app.rag.retriever import retrieve

logger = logging.getLogger(__name__)


async def recommend_colleges(
    budget: Optional[int] = None,
    location: Optional[str] = None,
    branches: Optional[List[str]] = None,
    rank: Optional[float] = None,
    needs_hostel: bool = False,
    other_requirements: str = "",
) -> Dict[str, Any]:
    """Generate personalized college recommendations."""

    # Build retrieval query from preferences
    query_parts = []
    if location:
        query_parts.append(f"engineering colleges in {location}")
    if branches:
        query_parts.append(f"{' '.join(branches)} engineering colleges")
    if budget:
        query_parts.append(f"colleges with fees under {budget}")
    if needs_hostel:
        query_parts.append("colleges with hostel facility")

    search_query = " ".join(query_parts) if query_parts else "top engineering colleges Maharashtra"
    docs = await retrieve(search_query, top_k=8)

    context = "\n\n".join(
        f"[{d.get('college_name', 'Unknown')}]\n{d['text']}" for d in docs
    ) if docs else "No specific college data available."

    prompt = RECOMMENDATION_PROMPT.format(
        budget=f"₹{budget:,}/year" if budget else "Not specified",
        location=location or "Maharashtra",
        branches=", ".join(branches) if branches else "Any",
        rank=str(rank) if rank else "Not specified",
        other=other_requirements or needs_hostel and "Hostel required" or "None",
        context=context,
    )

    response = await generate_response(prompt)
    return {
        "recommendations": response,
        "based_on_docs": len(docs),
        "preferences": {
            "budget": budget,
            "location": location,
            "branches": branches,
            "rank": rank,
            "needs_hostel": needs_hostel,
        }
    }
