"""Job Radar Ingestion & Deduplication Pipeline Orchestrator."""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from schemas.job import (
    JobPost,
    JobStatus,
    RadarMetrics,
    SkillFrequency,
)
from src.processors.dedupe import DeduplicationProcessor
from src.scrapers.base import BaseScraper
from src.scrapers.community_tech import CommunityTechScraper
from src.scrapers.fpt_telecom import FPTTelecomScraper
from src.scrapers.viettel_careers import ViettelCareersScraper

logger = logging.getLogger("job_radar.pipeline")


class PipelineTelemetry(BaseModel):
    """Execution telemetry of a pipeline ingestion run."""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    total_harvested_raw: int = 0
    valid_jobs_processed: int = 0
    new_jobs_added: int = 0
    existing_jobs_updated: int = 0
    total_active_jobs: int = 0
    scrapers_executed: int = 0
    scrapers_failed: int = 0
    failed_sources: List[str] = Field(default_factory=list)
    duration_seconds: float = 0.0


class JobRadarPipeline:
    """Orchestrates asynchronous scraping, deduplication, schema validation, and storage."""

    def __init__(
        self,
        data_dir: str | Path = "data",
        ttl_days: int = 30,
        scrapers: Optional[List[BaseScraper]] = None,
    ) -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_days = ttl_days
        self.jobs_file = self.data_dir / "jobs.json"
        self.metrics_file = self.data_dir / "metrics.json"

        # Default registered scraper suite
        self.scrapers = scrapers or [
            FPTTelecomScraper(),
            ViettelCareersScraper(),
            CommunityTechScraper(),
        ]

    def load_existing_jobs(self) -> List[JobPost]:
        """Loads and validates existing active jobs from the JSON storage."""
        if not self.jobs_file.exists():
            logger.info(f"No existing {self.jobs_file} found. Initializing empty collection.")
            return []

        try:
            with open(self.jobs_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            validated_jobs = []
            for item in data:
                try:
                    job = JobPost.model_validate(item)
                    validated_jobs.append(job)
                except Exception as ve:
                    logger.warning(f"Corrupted job entry skipped: {ve}")
            logger.info(f"Loaded {len(validated_jobs)} existing jobs from {self.jobs_file}.")
            return validated_jobs
        except Exception as e:
            logger.error(f"Error reading {self.jobs_file}: {e}. Starting fresh.")
            return []

    async def run(self) -> PipelineTelemetry:
        """Executes the full end-to-end ingestion pipeline."""
        start_time = datetime.now(timezone.utc)
        telemetry = PipelineTelemetry()
        telemetry.scrapers_executed = len(self.scrapers)

        existing_jobs = self.load_existing_jobs()
        dedup_processor = DeduplicationProcessor(existing_jobs, ttl_days=self.ttl_days)

        logger.info(f"Starting asynchronous execution across {len(self.scrapers)} scrapers...")
        
        # Concurrently trigger all scrapers with error isolation
        tasks = [scraper.scrape() for scraper in self.scrapers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        harvested_jobs: List[JobPost] = []
        for scraper, res in zip(self.scrapers, results):
            if isinstance(res, Exception):
                telemetry.scrapers_failed += 1
                telemetry.failed_sources.append(scraper.platform_name)
                logger.error(
                    f"Scraper [{scraper.platform_name}] crashed: {res}", exc_info=res
                )
            elif isinstance(res, list):
                telemetry.total_harvested_raw += len(res)
                harvested_jobs.extend(res)

        telemetry.valid_jobs_processed = len(harvested_jobs)

        # Deduplication, state reconciliation, and TTL cleanup
        active_jobs, new_count, updated_count = dedup_processor.process_incoming(harvested_jobs)
        telemetry.new_jobs_added = new_count
        telemetry.existing_jobs_updated = updated_count
        telemetry.total_active_jobs = len(active_jobs)

        # Atomic persistence of active jobs
        self._save_jobs(active_jobs)

        # Compute & persist updated Radar Metrics
        self._compute_and_save_metrics(active_jobs)

        duration = (datetime.now(timezone.utc) - start_time).total_seconds()
        telemetry.duration_seconds = round(duration, 2)
        logger.info(
            f"Pipeline completed in {telemetry.duration_seconds}s. "
            f"New: {new_count}, Updated: {updated_count}, Total Active: {len(active_jobs)}."
        )
        return telemetry

    def _save_jobs(self, jobs: List[JobPost]) -> None:
        """Atomically serializes jobs to jobs.json."""
        temp_file = self.jobs_file.with_suffix(".tmp")
        payload = [j.model_dump(mode="json") for j in jobs]
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        temp_file.replace(self.jobs_file)
        logger.info(f"Persisted {len(jobs)} jobs to {self.jobs_file}.")

    def _compute_and_save_metrics(self, jobs: List[JobPost]) -> None:
        """Calculates aggregation frequencies and writes metrics.json."""
        now = datetime.now(timezone.utc)
        roles_count: Dict[str, int] = {}
        locs_count: Dict[str, int] = {}
        skills_count: Dict[str, int] = {}
        fresh_24h = 0

        for j in jobs:
            r = j.role_category.value
            roles_count[r] = roles_count.get(r, 0) + 1

            for loc in j.locations:
                l = loc.value
                locs_count[l] = locs_count.get(l, 0) + 1

            for s in j.skills:
                skills_count[s] = skills_count.get(s, 0) + 1

            if (now - j.posted_at).total_seconds() <= 86400:
                fresh_24h += 1

        total_jobs = len(jobs)
        top_skills = [
            SkillFrequency(
                skill=k,
                count=v,
                percentage=round((v / total_jobs) * 100, 1) if total_jobs > 0 else 0.0,
                category="tech",
            )
            for k, v in sorted(skills_count.items(), key=lambda x: x[1], reverse=True)
        ]

        metrics = RadarMetrics(
            last_updated=now,
            total_active_jobs=total_jobs,
            fresh_jobs_24h=fresh_24h,
            jobs_by_role=roles_count,
            jobs_by_location=locs_count,
            top_skills=top_skills,
        )

        temp_metrics = self.metrics_file.with_suffix(".tmp")
        with open(temp_metrics, "w", encoding="utf-8") as f:
            json.dump(metrics.model_dump(mode="json"), f, indent=2, ensure_ascii=False)
        temp_metrics.replace(self.metrics_file)
        logger.info(f"Updated Radar Metrics saved to {self.metrics_file}.")
