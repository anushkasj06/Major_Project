"""Input validation utilities."""
import re
from typing import Optional


def is_valid_url(url: str) -> bool:
    pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|localhost|\d{1,3}(?:\.\d{1,3}){3})'
        r'(?::\d+)?(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(pattern.match(url))


def sanitize_query(query: str) -> str:
    """Remove potential injection patterns from user queries."""
    query = re.sub(r'[<>{}|\\^`]', '', query)
    return query.strip()[:500]


def validate_language(lang: str) -> str:
    allowed = {"en", "hi", "mr"}
    return lang if lang in allowed else "en"
