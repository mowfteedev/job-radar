"""Unit tests for JobPost schema and canonical hashing."""
from datetime import datetime, timezone
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


def test_canonical_hash_consistency():
    hash1 = compute_canonical_hash("FPT Telecom", "Network Engineer Intern", "ha_noi")
    hash2 = compute_canonical_hash("fpt telecom", "Network Engineer Intern", "HA_NOI")
    assert hash1 == hash2
    assert len(hash1) == 16


def test_job_post_validation():
    now = datetime.now(timezone.utc)
    job = JobPost(
        id="test-001",
        canonical_hash="hash123",
        title="  DevOps Intern  ",
        company=CompanyInfo.create(name="Acme Corp"),
        role_category=RoleCategory.DEVOPS,
        experience_level=ExperienceLevel.INTERN,
        skills=["Docker", "Linux"],
        locations=[LocationCategory.HA_NOI],
        salary=SalaryInfo(display_text="5M"),
        source_url="https://example.com/jobs/1",
        source_platform="Manual",
        description_summary="Test job description",
        posted_at=now,
    )
    assert job.title == "DevOps Intern"
    assert job.status == JobStatus.ACTIVE
    assert job.company.normalized_name == "acme corp"
