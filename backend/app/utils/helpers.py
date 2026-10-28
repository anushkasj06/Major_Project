"""General utility helpers."""
import re, hashlib
from typing import Any, Dict


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text


def hash_content(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


def sanitize_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    """Remove None values from dict."""
    return {k: v for k, v in d.items() if v is not None}


def paginate_response(items: list, total: int, skip: int, limit: int) -> Dict:
    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": skip + limit < total,
    }
