"""Base Scraper Adapter Definition."""
from abc import ABC, abstractmethod
import logging
from typing import List, Optional
import httpx
from schemas.job import JobPost

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract base class for all job source scrapers (Adapter Pattern)."""

    def __init__(self, platform_name: str, base_url: str, request_timeout: float = 15.0) -> None:
        self.platform_name = platform_name
        self.base_url = base_url
        self.request_timeout = request_timeout
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    @abstractmethod
    async def scrape(self, client: Optional[httpx.AsyncClient] = None) -> List[JobPost]:
        """Fetch and parse raw job postings into validated JobPost instances.
        
        Must handle its own specific pagination, DOM / JSON parsing, and map
        fields directly to the JobPost contract.
        """
        pass

    def get_client(self) -> httpx.AsyncClient:
        """Returns a configured asynchronous HTTP client."""
        return httpx.AsyncClient(
            headers=self.headers,
            timeout=self.request_timeout,
            follow_redirects=True
        )
