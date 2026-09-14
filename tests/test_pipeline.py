"""Integration and Adversarial tests for JobRadarPipeline."""
import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock
import pytest

from schemas.job import (
    CompanyInfo,
    ExperienceLevel,
    JobPost,
    JobStatus,
    LocationCategory,
    RoleCategory,
    SalaryInfo,
    compute_canonical_hash,
)
from src.pipeline import JobRadarPipeline
from src.scrapers.base import BaseScraper


class MockSuccessScraper(BaseScraper):
    def __init__(self, platform: str, titles: list):
        super().__init__(platform_name=platform, base_url="https://mock.com")
        self.titles = titles

    async def scrape(self, client=None):
        jobs = []
        for t in self.titles:
            h = compute_canonical_hash("MockCorp", t, "ha_noi")
            jobs.append(
                JobPost(
                    id=f"mock-{h[:8]}",
                    canonical_hash=h,
                    title=t,
                    company=CompanyInfo.create(name="MockCorp"),
                    role_category=RoleCategory.NETWORK,
                    experience_level=ExperienceLevel.FRESHER,
                    skills=["CCNA", "Linux"],
                    locations=[LocationCategory.HA_NOI],
                    salary=SalaryInfo(),
                    source_url=f"https://mock.com/{h}",
                    source_platform=self.platform_name,
                    description_summary="Mock job description",
                    posted_at=datetime.now(timezone.utc),
                )
            )
        return jobs


class MockCrashingScraper(BaseScraper):
    def __init__(self):
        super().__init__(platform_name="CrashedPlatform", base_url="https://crash.com")

    async def scrape(self, client=None):
        raise RuntimeError("Catastrophic WAF block or DOM mutation error!")


@pytest.mark.asyncio
async def test_pipeline_end_to_end_and_idempotency(tmp_path: Path):
    scraper1 = MockSuccessScraper("SourceA", ["Fresher Network Engineer 1", "Fresher Network Engineer 2"])
    scraper2 = MockSuccessScraper("SourceB", ["Fresher NOC Operator"])

    pipeline = JobRadarPipeline(
        data_dir=tmp_path,
        ttl_days=30,
        scrapers=[scraper1, scraper2],
    )

    # First Run
    telemetry1 = await pipeline.run()
    assert telemetry1.scrapers_executed == 2
    assert telemetry1.scrapers_failed == 0
    assert telemetry1.total_harvested_raw == 3
    assert telemetry1.new_jobs_added == 3
    assert telemetry1.existing_jobs_updated == 0
    assert telemetry1.total_active_jobs == 3

    # Check that data files exist and are valid JSON
    jobs_file = tmp_path / "jobs.json"
    metrics_file = tmp_path / "metrics.json"
    assert jobs_file.exists()
    assert metrics_file.exists()

    with open(jobs_file, "r", encoding="utf-8") as f:
        jobs_data = json.load(f)
    assert len(jobs_data) == 3

    with open(metrics_file, "r", encoding="utf-8") as f:
        metrics_data = json.load(f)
    assert metrics_data["total_active_jobs"] == 3
    assert "network" in metrics_data["jobs_by_role"]

    # Second Run (Idempotency check: exact same jobs incoming)
    telemetry2 = await pipeline.run()
    assert telemetry2.new_jobs_added == 0
    assert telemetry2.existing_jobs_updated == 3
    assert telemetry2.total_active_jobs == 3


@pytest.mark.asyncio
async def test_pipeline_crash_isolation(tmp_path: Path):
    """Ensures a catastrophic failure in 1 scraper does NOT bring down the entire pipeline."""
    good_scraper = MockSuccessScraper("ResilientSource", ["Fresher Cloud Engineer"])
    crash_scraper = MockCrashingScraper()

    pipeline = JobRadarPipeline(
        data_dir=tmp_path,
        ttl_days=30,
        scrapers=[good_scraper, crash_scraper],
    )

    telemetry = await pipeline.run()
    assert telemetry.scrapers_executed == 2
    assert telemetry.scrapers_failed == 1
    assert "CrashedPlatform" in telemetry.failed_sources
    assert telemetry.total_active_jobs == 1

    # Data from good scraper must still be saved
    with open(tmp_path / "jobs.json", "r", encoding="utf-8") as f:
        jobs = json.load(f)
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Fresher Cloud Engineer"


@pytest.mark.asyncio
async def test_pipeline_handles_corrupt_existing_file(tmp_path: Path):
    """Corrupt entries in jobs.json should be skipped without throwing unhandled exceptions."""
    jobs_file = tmp_path / "jobs.json"
    corrupt_data = [
        {"title": "Valid Job but missing required fields"},
        "totally invalid string entry",
    ]
    with open(jobs_file, "w", encoding="utf-8") as f:
        json.dump(corrupt_data, f)

    pipeline = JobRadarPipeline(data_dir=tmp_path, scrapers=[])
    existing = pipeline.load_existing_jobs()
    assert existing == []
