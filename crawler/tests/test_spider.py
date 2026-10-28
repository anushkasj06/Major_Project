"""Tests for crawler spider."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def test_normalize_url():
    from app.spider import ArambhSpider
    spider = ArambhSpider("https://coep.org.in", max_depth=2, max_pages=10)

    # Should normalize relative URLs
    result = spider.normalize_url("/admissions", "https://coep.org.in/page")
    assert result == "https://coep.org.in/admissions"

    # Should reject external URLs
    result = spider.normalize_url("https://google.com/page", "https://coep.org.in/")
    assert result is None

    # Should reject image files
    result = spider.normalize_url("/logo.png", "https://coep.org.in/")
    assert result is None


def test_url_hash():
    from app.spider import ArambhSpider
    spider = ArambhSpider("https://coep.org.in", max_depth=2, max_pages=10)
    h1 = spider.url_hash("https://coep.org.in/fees")
    h2 = spider.url_hash("https://coep.org.in/fees")
    assert h1 == h2
    h3 = spider.url_hash("https://coep.org.in/placements")
    assert h1 != h3


def test_html_extractor_tables():
    from app.extractors.html_extractor import extract_tables_as_text
    html = """
    <table>
        <tr><th>Branch</th><th>Fees</th></tr>
        <tr><td>CSE</td><td>95000</td></tr>
        <tr><td>ME</td><td>92000</td></tr>
    </table>
    """
    tables = extract_tables_as_text(html)
    assert len(tables) == 1
    assert "CSE" in tables[0]
    assert "95000" in tables[0]
