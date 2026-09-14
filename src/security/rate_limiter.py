"""Security module: Rate Limiting & Anti-DoS Defense for scrapers."""
from __future__ import annotations

import asyncio
import logging
import random
import time
from typing import Optional

logger = logging.getLogger("job_radar.security.rate_limiter")


class AsyncPoliteRateLimiter:
    """Polite rate limiter implementing token bucket, jitter, and concurrency bounds.
    
    Guarantees our crawlers behave ethically and do not cause denial-of-service (DoS)
    on target recruiting portals.
    """

    def __init__(
        self,
        requests_per_second: float = 2.0,
        min_delay_seconds: float = 0.5,
        max_delay_seconds: float = 1.5,
        max_concurrent: int = 3,
    ) -> None:
        self.rps = requests_per_second
        self.min_delay = min_delay_seconds
        self.max_delay = max_delay_seconds
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self._last_request_time = 0.0
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Acquires a concurrency slot and applies random jitter backoff."""
        await self.semaphore.acquire()
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_request_time
            expected_interval = 1.0 / self.rps

            # Apply random jitter delay
            jitter = random.uniform(self.min_delay, self.max_delay)
            wait_time = max(0.0, expected_interval - elapsed) + jitter

            if wait_time > 0:
                logger.debug(f"RateLimiter applying polite delay: {wait_time:.2f}s")
                await asyncio.sleep(wait_time)

            self._last_request_time = time.monotonic()

    def release(self) -> None:
        """Releases a concurrency slot."""
        self.semaphore.release()

    async def __aenter__(self) -> AsyncPoliteRateLimiter:
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self.release()

    @staticmethod
    def parse_retry_after(header_value: Optional[str], default: float = 5.0) -> float:
        """Parses HTTP 429 Retry-After header cleanly."""
        if not header_value:
            return default
        try:
            return max(1.0, min(float(header_value), 60.0))
        except ValueError:
            return default
