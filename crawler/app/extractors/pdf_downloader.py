"""Downloads and extracts PDFs found during crawling."""
import os, asyncio, logging, uuid
import httpx
from typing import Optional

logger = logging.getLogger(__name__)
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")


async def download_pdf(url: str, timeout: int = 60) -> Optional[str]:
    """Download a PDF from a URL and save locally. Returns local file path."""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(
                url,
                headers={"User-Agent": os.getenv("USER_AGENT", "ArambhBot/1.0")},
                follow_redirects=True,
            )
            if response.status_code != 200:
                return None
            content_type = response.headers.get("content-type", "")
            if "pdf" not in content_type and not url.lower().endswith(".pdf"):
                return None

            os.makedirs(UPLOAD_DIR, exist_ok=True)
            filename = f"{uuid.uuid4()}.pdf"
            file_path = os.path.join(UPLOAD_DIR, filename)

            with open(file_path, "wb") as f:
                f.write(response.content)

            logger.info(f"Downloaded PDF: {url} -> {file_path}")
            return file_path
    except Exception as e:
        logger.warning(f"Failed to download PDF {url}: {e}")
        return None


async def find_pdf_links(html: str, base_url: str) -> list:
    """Find all PDF links in an HTML page."""
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin, urlparse

    soup = BeautifulSoup(html, "html.parser")
    pdf_links = []
    domain = urlparse(base_url).netloc

    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        if href.lower().endswith(".pdf"):
            full_url = urljoin(base_url, href)
            if urlparse(full_url).netloc == domain:
                pdf_links.append(full_url)

    return list(set(pdf_links))
