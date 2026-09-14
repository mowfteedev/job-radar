"""Unit tests for Classifier and Deduplication Processor."""
from datetime import datetime, timezone, timedelta
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
from src.processors.classifier import (
    classify_role,
    detect_locations,
    determine_experience_level,
    extract_skills,
)
from src.processors.dedupe import DeduplicationProcessor


def test_classify_network_role():
    role = classify_role("Kỹ sư mạng Cisco NOC", "Yêu cầu CCNA và hiểu biết switch routing")
    assert role == RoleCategory.NETWORK


def test_classify_devops_role():
    role = classify_role("Thực tập sinh DevOps", "Triển khai Docker container và CI/CD pipeline")
    assert role == RoleCategory.DEVOPS


def test_determine_experience_level():
    lvl_intern = determine_experience_level("Thực tập sinh Network", "Dành cho sinh viên năm cuối")
    assert lvl_intern == ExperienceLevel.INTERN

    lvl_senior = determine_experience_level("Senior DevOps Engineer", "Yêu cầu 5+ năm kinh nghiệm quản trị")
    assert lvl_senior is None


def test_extract_skills():
    skills = extract_skills("Cần nắm vững kiến thức Linux, Docker, CCNA và giao thức TCP/IP")
    assert "Linux" in skills
    assert "Docker" in skills
    assert "CCNA" in skills
    assert "TCP/IP" in skills


def test_deduplication_processor():
    now = datetime.now(timezone.utc)
    job1 = JobPost(
        id="job-1",
        canonical_hash="hash_same",
        title="Fresher SysAdmin",
        company=CompanyInfo.create(name="Tech Corp"),
        role_category=RoleCategory.SYSADMIN,
        experience_level=ExperienceLevel.FRESHER,
        skills=["Linux"],
        locations=[LocationCategory.HA_NOI],
        salary=SalaryInfo(),
        source_url="https://site1.com/job/1",
        source_platform="Platform1",
        description_summary="Short desc",
        posted_at=now - timedelta(days=1),
    )

    processor = DeduplicationProcessor(existing_jobs=[job1])

    # Incoming duplicate with updated description
    job1_duplicate = JobPost(
        id="job-2",
        canonical_hash="hash_same",
        title="Fresher SysAdmin",
        company=CompanyInfo.create(name="Tech Corp"),
        role_category=RoleCategory.SYSADMIN,
        experience_level=ExperienceLevel.FRESHER,
        skills=["Linux"],
        locations=[LocationCategory.HA_NOI],
        salary=SalaryInfo(),
        source_url="https://site2.com/job/1",
        source_platform="Platform2",
        description_summary="Much longer description summary with more details",
        posted_at=now,
    )

    merged, new_count, updated_count = processor.process_incoming([job1_duplicate])
    assert len(merged) == 1
    assert new_count == 0
    assert updated_count == 1
    assert merged[0].description_summary == "Much longer description summary with more details"
