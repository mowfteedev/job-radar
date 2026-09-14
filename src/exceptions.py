"""Centralized Custom Exception Hierarchy for Job Radar System.

Follows clean code principles with clear domain separation and diagnostic context.
"""
from __future__ import annotations
from typing import Optional


class JobRadarError(Exception):
    """Base exception for all domain errors within Job Radar."""

    def __init__(self, message: str, context: Optional[dict] = None) -> None:
        super().__init__(message)
        self.message = message
        self.context = context or {}

    def __str__(self) -> str:
        if self.context:
            return f"{self.message} | Context: {self.context}"
        return self.message


class ScraperError(JobRadarError):
    """Raised when an error occurs during scraping."""
    pass


class ScraperNetworkError(ScraperError):
    """Raised when network connectivity or DNS resolution fails during scraping."""
    pass


class ScraperRateLimitError(ScraperError):
    """Raised when the target platform throttles requests (e.g. HTTP 429)."""
    pass


class ScraperParsingError(ScraperError):
    """Raised when the scraper encounters corrupt or unrecognizable HTML structure."""
    pass


class SecurityViolationError(JobRadarError):
    """Raised when a security boundary is breached (e.g., SSRF, XSS, Secret leak)."""
    pass


class IndexingError(JobRadarError):
    """Raised when search indexing or payload compression fails."""
    pass


class DeduplicationError(JobRadarError):
    """Raised when deduplication processor fails to reconcile state."""
    pass
