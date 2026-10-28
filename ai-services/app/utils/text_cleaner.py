"""Text cleaning utilities for scraped content."""
import re


def clean_html_text(text: str) -> str:
    """Clean text extracted from HTML pages."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special chars keeping Indian language chars
    text = re.sub(r'[^\w\s\.,!?\-\(\)\[\]:\;\'\"\n।॥\u0900-\u097F\u0A00-\u0A7F]', '', text)
    # Remove very short lines (nav items, breadcrumbs)
    lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 20]
    return '\n'.join(lines).strip()


def extract_fees_pattern(text: str) -> list:
    """Extract fee patterns from text."""
    patterns = [
        r'₹\s*[\d,]+(?:\s*(?:per year|annually|per annum|p\.a\.))?',
        r'Rs\.?\s*[\d,]+(?:\s*(?:per year|annually))?',
        r'[\d,]+\s*(?:lakh|lakhs|L)\s*(?:per year|annually)?',
    ]
    fees = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        fees.extend(matches)
    return fees


def extract_placement_pattern(text: str) -> dict:
    """Extract placement statistics from text."""
    result = {}
    avg_match = re.search(r'average\s+(?:package|ctc|salary)[^\d]*(\d+(?:\.\d+)?)\s*(?:lpa|lakh)', text, re.IGNORECASE)
    if avg_match:
        result['avg_lpa'] = float(avg_match.group(1))
    high_match = re.search(r'highest\s+(?:package|ctc|salary)[^\d]*(\d+(?:\.\d+)?)\s*(?:lpa|lakh)', text, re.IGNORECASE)
    if high_match:
        result['highest_lpa'] = float(high_match.group(1))
    pct_match = re.search(r'(\d+(?:\.\d+)?)\s*%\s*(?:placement|placed|students placed)', text, re.IGNORECASE)
    if pct_match:
        result['placement_pct'] = float(pct_match.group(1))
    return result
