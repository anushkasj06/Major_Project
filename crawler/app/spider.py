"""
Async web spider with robots.txt handling, rate limiting, and deduplication.
"""
import asyncio, logging, re, hashlib, os
from typing import Set, List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import httpx
import trafilatura
from bs4 import BeautifulSoup
from datetime import datetime

logger = logging.getLogger(__name__)

RATE_LIMIT = float(os.getenv("CRAWLER_RATE_LIMIT_DELAY", "2.0"))
CONCURRENT = int(os.getenv("CRAWLER_CONCURRENT_REQUESTS", "5"))
TIMEOUT = int(os.getenv("CRAWLER_TIMEOUT", "30"))
USER_AGENT = os.getenv("USER_AGENT", "ArambhBot/1.0")


class ArambhSpider:
    def __init__(self, base_url: str, max_depth: int = 3, max_pages: int = 100):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.visited: Set[str] = set()
        self.url_hashes: Set[str] = set()
        self.semaphore = asyncio.Semaphore(CONCURRENT)
        self.robots = RobotFileParser()
        self.pages: List[Dict] = []

    async def init_robots(self, client: httpx.AsyncClient):
        robots_url = f"{urlparse(self.base_url).scheme}://{self.domain}/robots.txt"
        try:
            resp = await client.get(robots_url, timeout=10.0)
            self.robots.parse(resp.text.splitlines())
        except Exception:
            pass  # No robots.txt — proceed

    def can_fetch(self, url: str) -> bool:
        return self.robots.can_fetch(USER_AGENT, url)

    def normalize_url(self, url: str, base: str) -> Optional[str]:
        try:
            full = urljoin(base, url)
            parsed = urlparse(full)
            if parsed.netloc != self.domain:
                return None
            if any(ext in parsed.path.lower() for ext in [".jpg", ".png", ".gif", ".css", ".js", ".ico", ".svg"]):
                return None
            # Remove fragment
            clean = parsed._replace(fragment="").geturl()
            return clean
        except Exception:
            return None

    def url_hash(self, url: str) -> str:
        return hashlib.md5(url.encode()).hexdigest()

    async def fetch_page(self, client: httpx.AsyncClient, url: str) -> Optional[Dict]:
        async with self.semaphore:
            await asyncio.sleep(RATE_LIMIT)
            try:
                response = await client.get(
                    url, timeout=TIMEOUT,
                    headers={"User-Agent": USER_AGENT},
                    follow_redirects=True,
                )
                if response.status_code != 200:
                    return None
                content_type = response.headers.get("content-type", "")
                if "text/html" not in content_type and "application/pdf" not in content_type:
                    return None

                if "application/pdf" in content_type:
                    return {"url": url, "type": "pdf", "content": response.content, "html": None}

                html = response.text
                # Check for duplicate content
                content_hash = hashlib.md5(html.encode()).hexdigest()
                if content_hash in self.url_hashes:
                    return None
                self.url_hashes.add(content_hash)

                text = trafilatura.extract(html, include_tables=True) or ""
                soup = BeautifulSoup(html, "html.parser")
                title = soup.find("title")
                title_text = title.get_text(strip=True) if title else url

                return {
                    "url": url,
                    "type": "html",
                    "title": title_text,
                    "text": text,
                    "html": html[:50000],  # Store first 50k chars
                    "fetched_at": datetime.utcnow().isoformat(),
                }
            except Exception as e:
                logger.debug(f"Failed to fetch {url}: {e}")
                return None

    def extract_links(self, html: str, base_url: str) -> List[str]:
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for tag in soup.find_all("a", href=True):
            normalized = self.normalize_url(tag["href"], base_url)
            if normalized and normalized not in self.visited:
                links.append(normalized)
        return links

    async def crawl(self, job_id: str, college_id: Optional[str] = None) -> List[Dict]:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            await self.init_robots(client)
            await self._crawl_recursive(client, self.base_url, 0, job_id, college_id)
        logger.info(f"Crawl complete: {len(self.pages)} pages collected from {self.base_url}")
        return self.pages

    async def _crawl_recursive(
        self, client: httpx.AsyncClient, url: str, depth: int,
        job_id: str, college_id: Optional[str]
    ):
        if depth > self.max_depth or len(self.pages) >= self.max_pages:
            return
        if url in self.visited:
            return
        if not self.can_fetch(url):
            logger.debug(f"robots.txt disallows: {url}")
            return

        self.visited.add(url)
        page = await self.fetch_page(client, url)
        if not page:
            return

        page["college_id"] = college_id
        page["depth"] = depth
        self.pages.append(page)

        # Update job progress in MongoDB
        await _update_job_progress(job_id, len(self.pages))

        # Recurse into links
        if page.get("html") and depth < self.max_depth:
            links = self.extract_links(page["html"], url)
            tasks = [
                self._crawl_recursive(client, link, depth + 1, job_id, college_id)
                for link in links[:20]  # Limit branching
            ]
            await asyncio.gather(*tasks, return_exceptions=True)


async def _update_job_progress(job_id: str, pages_crawled: int):
    try:
        import motor.motor_asyncio
        from bson import ObjectId
        client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGODB_URL", ""))
        db = client[os.getenv("MONGODB_DB_NAME", "arambh")]
        await db.crawler_jobs.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": {"pages_crawled": pages_crawled, "status": "running", "started_at": datetime.utcnow()}}
        )
        client.close()
    except Exception:
        pass


async def crawl_site(
    job_id: str, url: str,
    college_id: Optional[str] = None,
    max_depth: int = 3,
    max_pages: int = 100,
):
    """Main crawl entry point — crawl site and ingest results."""
    spider = ArambhSpider(url, max_depth=max_depth, max_pages=max_pages)
    pages = await spider.crawl(job_id=job_id, college_id=college_id)

    # Send pages to AI service for indexing
    indexed = 0
    async with httpx.AsyncClient(timeout=60.0) as client:
        for page in pages:
            if page.get("type") == "pdf":
                continue  # Handle PDFs separately
            if not page.get("text"):
                continue
            try:
                resp = await client.post(
                    f"{os.getenv('AI_SERVICE_URL', 'http://ai-services:8001')}/ai/ingest/url",
                    params={"url": page["url"], "college_id": college_id},
                )
                if resp.status_code == 200:
                    indexed += 1
            except Exception as e:
                logger.warning(f"Failed to index {page['url']}: {e}")

    # Mark job complete
    try:
        import motor.motor_asyncio
        from bson import ObjectId
        mongo_client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGODB_URL", ""))
        db = mongo_client[os.getenv("MONGODB_DB_NAME", "arambh")]
        await db.crawler_jobs.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": {
                "status": "completed",
                "pages_crawled": len(pages),
                "pages_indexed": indexed,
                "completed_at": datetime.utcnow(),
            }}
        )
        mongo_client.close()
    except Exception:
        pass
    return {"pages_crawled": len(pages), "pages_indexed": indexed}
