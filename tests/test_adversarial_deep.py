"""Extreme Adversarial, Stress, and Chaos Pipeline Test Suite.

Author: @tester (Reality Checker & Adversarial Testing Specialist)
Validates system resilience against extreme edge cases, chaos network conditions,
payload fuzzing, and boundary violations.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
import pytest
from pydantic import ValidationError

from schemas.job import (
    CompanyInfo,
    ExperienceLevel,
    JobPost,
    JobStatus,
    LocationCategory,
    RoleCategory,
    SalaryInfo,
    WorkType,
    compute_canonical_hash,
)
from src.exceptions import (
    JobRadarError,
    ScraperNetworkError,
    ScraperParsingError,
    ScraperRateLimitError,
)
from src.pipeline import JobRadarPipeline
from src.processors.classifier import (
    classify_role,
    detect_locations,
    determine_experience_level,
)
from src.scrapers.base import BaseScraper
from tests.fixtures.mock_responses import (
    CORRUPTED_HTML_SAMPLES,
    INVALID_SALARY_TEST_CASES,
    TRICKY_SENIORITY_CASES,
)


def test_salary_bounds_rejection():
    """Adversarial Test: Rejects negative salaries and inverted min > max."""
    for case in INVALID_SALARY_TEST_CASES:
        with pytest.raises(ValidationError) as exc_info:
            SalaryInfo(
                min_amount=case["min_amount"],
                max_amount=case["max_amount"],
                is_negotiable=False,
            )
        assert case["expected_error"] in str(exc_info.value)


def test_location_word_boundary_precision():
    """Adversarial Test: Verifies substring matches don't falsely trigger locations.
    
    Example: 'John' should NOT trigger 'ha_noi' (from 'hn'),
             'dnase' should NOT trigger 'da_nang' (from 'dn').
    """
    # Substrings that contain letters of location codes but are NOT the locations
    false_positives = [
        "Lập trình viên John tham gia dự án",
        "Nghiên cứu về dnase và protein",
        "Chuyển đổi giao diện lightning speed",
    ]
    for text in false_positives:
        locs = detect_locations(text)
        assert LocationCategory.HA_NOI not in locs, f"'hn' falsely detected in: {text}"
        assert LocationCategory.DA_NANG not in locs, f"'dn' falsely detected in: {text}"

    # True positives must be cleanly recognized
    true_cases = [
        ("Kỹ sư mạng làm việc tại HN", LocationCategory.HA_NOI),
        ("Tuyển IT Support tại Hà Nội", LocationCategory.HA_NOI),
        ("DevOps Engineer văn phòng HCM", LocationCategory.HO_CHI_MINH),
        ("Quản trị hệ thống tại TP.HCM", LocationCategory.HO_CHI_MINH),
        ("Network NOC tại ĐN", LocationCategory.DA_NANG),
        ("Thực tập sinh Đà Nẵng", LocationCategory.DA_NANG),
        ("Làm việc từ xa hoàn toàn (Remote)", LocationCategory.REMOTE),
    ]
    for text, expected_loc in true_cases:
        detected = detect_locations(text)
        assert expected_loc in detected, f"Failed to detect {expected_loc} in: {text}"


def test_tricky_seniority_detection_adversarial():
    """Adversarial Test: Ensures executive, principal, and senior roles are strictly filtered."""
    for title, desc, expected_level in TRICKY_SENIORITY_CASES:
        detected = determine_experience_level(title, desc)
        if expected_level is None:
            assert detected is None, f"Senior role was not filtered: {title}"
        else:
            assert detected.value == expected_level, f"Expected {expected_level}, got {detected} for {title}"


def test_unicode_and_rtl_hash_consistency():
    """Adversarial Test: Fuzzes hashing engine with zero-width spaces, emojis and RTL text."""
    title_raw = "Fresher\u200b Network \u202eEngineer 👨‍👩‍👧‍👦"
    hash1 = compute_canonical_hash("FPT Telecom", title_raw, "ha_noi")
    hash2 = compute_canonical_hash("FPT Telecom", "Fresher Network Engineer", "ha_noi")
    
    # Non-alphanumerics stripped, ensuring consistent canonical identity
    assert len(hash1) == 16
    assert hash1 == hash2


class FlakyScraper(BaseScraper):
    """Mock scraper designed to fail violently."""

    def __init__(self, name: str, fail_mode: str) -> None:
        super().__init__(platform_name=name, base_url="https://mock.example.com")
        self.fail_mode = fail_mode

    async def scrape(self, client=None) -> List[JobPost]:
        if self.fail_mode == "network_error":
            raise ScraperNetworkError(f"DNS lookup failed for {self.platform_name}")
        elif self.fail_mode == "rate_limit":
            raise ScraperRateLimitError(f"HTTP 429 Too Many Requests on {self.platform_name}")
        elif self.fail_mode == "unhandled_crash":
            raise RuntimeError("Fatal unhandled memory corruption simulation!")
        elif self.fail_mode == "empty_corrupt":
            return []
        
        # Healthy mock response
        now = datetime.now(timezone.utc)
        return [
            JobPost(
                id=f"{self.platform_name.lower()}-test-1",
                canonical_hash=compute_canonical_hash(self.platform_name, "Fresher NOC", "ha_noi"),
                title="Fresher NOC Engineer",
                company=CompanyInfo.create(name=self.platform_name, location=LocationCategory.HA_NOI),
                role_category=RoleCategory.NETWORK,
                experience_level=ExperienceLevel.FRESHER,
                skills=["CCNA", "Cisco"],
                locations=[LocationCategory.HA_NOI],
                source_url="https://example.com/job/noc",
                source_platform=self.platform_name,
                description_summary="Healthy job posting",
                posted_at=now,
            )
        ]


@pytest.mark.asyncio
async def test_chaos_pipeline_resilience(tmp_path: Path):
    """Adversarial Test: Pipeline survives when 75% of scrapers crash violently."""
    scrapers = [
        FlakyScraper("Scraper-A", "network_error"),
        FlakyScraper("Scraper-B", "rate_limit"),
        FlakyScraper("Scraper-C", "unhandled_crash"),
        FlakyScraper("Scraper-Healthy", "success"),
    ]

    pipeline = JobRadarPipeline(data_dir=tmp_path, scrapers=scrapers)
    telemetry = await pipeline.run()

    # Assert that pipeline completed without raising an exception
    assert telemetry.scrapers_executed == 4
    assert telemetry.scrapers_failed == 3
    assert "Scraper-A" in telemetry.failed_sources
    assert "Scraper-B" in telemetry.failed_sources
    assert "Scraper-C" in telemetry.failed_sources
    assert telemetry.valid_jobs_processed == 1
    assert telemetry.total_active_jobs == 1

    # Verify atomic files were safely produced
    assert (tmp_path / "jobs.json").exists()
    assert (tmp_path / "metrics.json").exists()
    assert (tmp_path / "search_index.json").exists()


@pytest.mark.asyncio
async def test_idempotency_multi_cycle_stress(tmp_path: Path):
    """Adversarial Test: 10 consecutive pipeline runs must yield identical job counts."""
    scrapers = [FlakyScraper("HealthyProvider", "success")]
    pipeline = JobRadarPipeline(data_dir=tmp_path, scrapers=scrapers)

    # Run 10 cycles in rapid succession
    for cycle in range(10):
        telemetry = await pipeline.run()
        assert telemetry.total_active_jobs == 1
        if cycle == 0:
            assert telemetry.new_jobs_added == 1
            assert telemetry.existing_jobs_updated == 0
        else:
            assert telemetry.new_jobs_added == 0
            assert telemetry.existing_jobs_updated == 1
