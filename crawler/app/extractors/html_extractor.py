"""HTML content extraction — tables, metadata, structured data."""
from bs4 import BeautifulSoup
from typing import Dict, Any, List
import re


def extract_metadata(html: str, url: str) -> Dict[str, Any]:
    """Extract page metadata from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    meta = {"url": url}

    # Title
    title_tag = soup.find("title")
    meta["title"] = title_tag.get_text(strip=True) if title_tag else ""

    # Meta description
    desc_tag = soup.find("meta", attrs={"name": "description"})
    meta["description"] = desc_tag.get("content", "") if desc_tag else ""

    # OpenGraph
    og_title = soup.find("meta", attrs={"property": "og:title"})
    if og_title:
        meta["og_title"] = og_title.get("content", "")

    # Keywords
    kw_tag = soup.find("meta", attrs={"name": "keywords"})
    meta["keywords"] = kw_tag.get("content", "") if kw_tag else ""

    return meta


def extract_tables_as_text(html: str) -> List[str]:
    """Extract HTML tables and convert to readable text."""
    soup = BeautifulSoup(html, "html.parser")
    tables_text = []

    for table in soup.find_all("table"):
        rows = []
        # Headers
        headers = [th.get_text(strip=True) for th in table.find_all("th")]
        if headers:
            rows.append(" | ".join(headers))
            rows.append("-" * len(" | ".join(headers)))

        # Data rows
        for tr in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            if cells and any(c for c in cells):
                rows.append(" | ".join(cells))

        if rows:
            tables_text.append("\n".join(rows))

    return tables_text


def extract_fee_info(html: str) -> List[str]:
    """Heuristically extract fee information from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    fee_keywords = ["fee", "fees", "tuition", "cost", "charges", "scholarship", "hostel fee"]
    fee_sections = []

    for elem in soup.find_all(["p", "div", "li", "td", "h3", "h4"]):
        text = elem.get_text(strip=True).lower()
        if any(kw in text for kw in fee_keywords):
            full_text = elem.get_text(strip=True)
            if 20 < len(full_text) < 500:
                fee_sections.append(full_text)

    return fee_sections[:10]
