"""Unit tests for JobSearchIndexer and Static Indexes."""
from datetime import datetime, timezone
import json
from pathlib import Path
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
from src.processors.indexer import JobSearchIndexer


@pytest.fixture
def sample_indexed_jobs():
    now = datetime.now(timezone.utc)
    return [
        JobPost(
            id="job-fpt-01",
            canonical_hash=compute_canonical_hash("FPT Telecom", "Kỹ sư mạng CCNA", "ha_noi"),
            title="Kỹ sư mạng CCNA",
            company=CompanyInfo.create(name="FPT Telecom"),
            role_category=RoleCategory.NETWORK,
            experience_level=ExperienceLevel.FRESHER,
            skills=["CCNA", "Cisco", "Routing"],
            locations=[LocationCategory.HA_NOI],
            salary=SalaryInfo(),
            source_url="https://fpt.vn/job/1",
            source_platform="FPT",
            description_summary="Vận hành hệ thống Switch Router",
            posted_at=now,
        ),
        JobPost(
            id="job-vng-02",
            canonical_hash=compute_canonical_hash("VNG Corp", "Fresher DevOps Kubernetes", "ho_chi_minh"),
            title="Fresher DevOps Kubernetes",
            company=CompanyInfo.create(name="VNG Corp"),
            role_category=RoleCategory.DEVOPS,
            experience_level=ExperienceLevel.FRESHER,
            skills=["Docker", "Kubernetes", "Linux"],
            locations=[LocationCategory.HO_CHI_MINH],
            salary=SalaryInfo(),
            source_url="https://vng.com/job/2",
            source_platform="VNG",
            description_summary="Triển khai cụm microservices",
            posted_at=now,
        ),
    ]


def test_indexer_builds_inverted_indexes(sample_indexed_jobs):
    indexer = JobSearchIndexer(sample_indexed_jobs)
    index_data = indexer.build_indexes()

    assert index_data["total_records"] == 2
    indexes = index_data["indexes"]

    # Role Index
    assert "network" in indexes["by_role"]
    assert "job-fpt-01" in indexes["by_role"]["network"]
    assert "devops" in indexes["by_role"]
    assert "job-vng-02" in indexes["by_role"]["devops"]

    # Location Index
    assert "ha_noi" in indexes["by_location"]
    assert "job-fpt-01" in indexes["by_location"]["ha_noi"]
    assert "ho_chi_minh" in indexes["by_location"]
    assert "job-vng-02" in indexes["by_location"]["ho_chi_minh"]

    # Skill Index (normalized lowercase)
    assert "docker" in indexes["by_skill"]
    assert "ccna" in indexes["by_skill"]
    assert "job-vng-02" in indexes["by_skill"]["docker"]

    # Keyword Index
    assert "kubernetes" in indexes["by_keyword"]
    assert "cisco" in indexes["by_keyword"]


def test_indexer_saves_atomically(sample_indexed_jobs, tmp_path: Path):
    indexer = JobSearchIndexer(sample_indexed_jobs)
    out_file = tmp_path / "test_search_index.json"
    indexer.save_index(out_file)

    assert out_file.exists()
    with open(out_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["total_records"] == 2
    assert "records" in data
    assert "job-fpt-01" in data["records"]
    assert data["records"]["job-fpt-01"]["salary"] == "Thỏa thuận"
