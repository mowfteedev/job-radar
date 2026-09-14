"""Deduplication & State Management Processor."""
from __future__ import annotations

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple
from schemas.job import JobPost, JobStatus, compute_canonical_hash

logger = logging.getLogger(__name__)


class DeduplicationProcessor:
    """Manages deduplication and state synchronization against existing dataset."""

    def __init__(self, existing_jobs: List[JobPost], ttl_days: int = 30) -> None:
        self.ttl_days = ttl_days
        # Index existing jobs by canonical_hash
        self.jobs_by_hash: Dict[str, JobPost] = {job.canonical_hash: job for job in existing_jobs}

    def process_incoming(self, incoming_jobs: List[JobPost]) -> Tuple[List[JobPost], int, int]:
        """Merges incoming jobs with existing storage.
        
        Returns:
            Tuple of (merged_active_jobs, new_count, updated_count)
        """
        now = datetime.now(timezone.utc)
        new_count = 0
        updated_count = 0

        for inc in incoming_jobs:
            h = inc.canonical_hash
            if h in self.jobs_by_hash:
                # Update scraped_at and keep active
                existing = self.jobs_by_hash[h]
                existing.scraped_at = now
                existing.status = JobStatus.ACTIVE
                # Refresh description if incoming is richer
                if len(inc.description_summary) > len(existing.description_summary):
                    existing.description_summary = inc.description_summary
                updated_count += 1
            else:
                # Brand new job
                self.jobs_by_hash[h] = inc
                new_count += 1

        # Check TTL and purge expired jobs
        active_jobs = []
        for h, job in self.jobs_by_hash.items():
            age_days = (now - job.posted_at).total_seconds() / 86400.0
            if age_days > self.ttl_days:
                job.status = JobStatus.EXPIRED
            else:
                active_jobs.append(job)

        # Sort descending by posted_at
        active_jobs.sort(key=lambda j: j.posted_at, reverse=True)
        return active_jobs, new_count, updated_count
