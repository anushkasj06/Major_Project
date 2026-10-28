"""Query Understanding Agent — intent detection, entity extraction."""
import json, logging, re
from typing import Dict, Any
from app.agents.llm_provider import generate_response
from app.prompts.templates import QUERY_UNDERSTANDING_PROMPT

logger = logging.getLogger(__name__)

DEFAULT_ANALYSIS = {
    "intent": "general",
    "entities": {"college_name": None, "branch": None, "year": None, "category": None, "location": None},
    "requires_comparison": False,
    "language": "en",
    "cleaned_query": ""
}


async def analyze_query(query: str) -> Dict[str, Any]:
    """Detect intent and extract entities from user query."""
    prompt = QUERY_UNDERSTANDING_PROMPT.format(query=query)
    try:
        response = await generate_response(prompt)
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            result["cleaned_query"] = result.get("cleaned_query") or query
            return result
    except Exception as e:
        logger.warning(f"Query analysis failed: {e}")

    result = DEFAULT_ANALYSIS.copy()
    result["cleaned_query"] = query
    result["language"] = detect_language(query)
    return result


def detect_language(text: str) -> str:
    """Simple language detection based on Unicode ranges."""
    devanagari = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    if devanagari > len(text) * 0.2:
        # Could be Hindi or Marathi — check for Marathi-specific words
        marathi_words = ["आहे", "मला", "कुठे", "महाराष्ट्र", "कसे"]
        if any(w in text for w in marathi_words):
            return "mr"
        return "hi"
    return "en"
