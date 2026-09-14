"""Base Scraper Adapter Definition with Security Hardening."""
from abc import ABC, abstractmethod
import logging
from typing import List, Optional
import httpx

from schemas.job import JobPost
from src.security.rate_limiter import AsyncPoliteRateLimiter
from src.security.sanitizer import sanitize_text, validate_and_sanitize_url
from src.security.user_agents import UserAgentRotator

logger = logging.getLogger("job_radar.scraper.base")


class BaseScraper(ABC):
    """Abstract base class for all job source scrapers (Adapter Pattern).
    
    Equipped with randomized User-Agent headers, polite rate limiting, and input sanitization.
    """

    def __init__(
        self,
        platform_name: str,
        base_url: str,
        request_timeout: float = 15.0,
        rate_limiter: Optional[AsyncPoliteRateLimiter] = None,
    ) -> None:
        self.platform_name = platform_name
        self.base_url = base_url
        self.request_timeout = request_timeout
        self.ua_rotator = UserAgentRotator()
        self.rate_limiter = rate_limiter or AsyncPoliteRateLimiter(
            requests_per_second=2.0,
            min_delay_seconds=0.3,
            max_delay_seconds=1.0,
            max_concurrent=3,
        )

    @abstractmethod
    async def scrape(self, client: Optional[httpx.AsyncClient] = None) -> List[JobPost]:
        """Fetch and parse raw job postings into validated JobPost instances."""
        pass

    def get_client(self) -> httpx.AsyncClient:
        """Returns a configured asynchronous HTTP client with rotating browser headers."""
        headers = self.ua_rotator.get_headers()
        return httpx.AsyncClient(
            headers=headers,
            timeout=self.request_timeout,
            follow_redirects=True,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )

    def sanitize_job_url(self, raw_url: str) -> Optional[str]:
        """Validates and cleans external URL to prevent SSRF or XSS."""
        return validate_and_sanitize_url(raw_url)

    def sanitize_description(self, raw_desc: str) -> str:
        """Strips HTML tags and escapes malicious scripts."""
        return sanitize_text(raw_desc, max_length=400)
