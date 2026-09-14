"""Adversarial and Edge Case Tests for VN Tech Job Radar."""
from datetime import datetime, timezone
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
    compute_canonical_hash,
)
from src.processors.classifier import (
    classify_role,
    detect_locations,
    determine_experience_level,
    extract_skills,
)
from src.processors.dedupe import DeduplicationProcessor


def test_fuzzing_massive_strings_and_injection():
    """Verify that huge strings, SQL/XSS payloads and emojis do not crash parsing."""
    huge_title = "Fresher DevOps Engineer " + "A" * 10000
    xss_payload = "<script>alert('pwned');</script> ' OR 1=1 -- 👨‍👩‍👧‍👦"
    
    role = classify_role(huge_title, xss_payload)
    assert role == RoleCategory.DEVOPS

    skills = extract_skills(f"Kỹ năng: Docker, Linux, {xss_payload}")
    assert "Docker" in skills
    assert "Linux" in skills

    locations = detect_locations(f"Văn phòng tại Hà Nội, Hồ Chí Minh {xss_payload}")
    assert LocationCategory.HA_NOI in locations
    assert LocationCategory.HO_CHI_MINH in locations


def test_canonical_hash_special_characters():
    """Canonical hash must be deterministic even with punctuation and emojis."""
    h1 = compute_canonical_hash("FPT Telecom!", "Kỹ Sư Mạng (NOC) 🔥", "ha_noi")
    h2 = compute_canonical_hash("FPT Telecom", "Kỹ sư mạng NOC", "ha_noi")
    assert h1 == h2
    assert len(h1) == 16


def test_validation_rejects_empty_locations():
    """JobPost schema must reject a job post with empty locations list."""
    now = datetime.now(timezone.utc)
    with pytest.raises(ValidationError):
        JobPost(
            id="bad-job-001",
            canonical_hash="hash1",
            title="Intern Network",
            company=CompanyInfo.create(name="FPT"),
            role_category=RoleCategory.NETWORK,
            experience_level=ExperienceLevel.INTERN,
            skills=[],
            locations=[],  # Min length is 1, must raise validation error
            source_url="https://example.com",
            source_platform="Test",
            description_summary="Desc",
            posted_at=now,
        )


def test_deduplicator_handles_empty_incoming():
    """Deduplication processor must gracefully handle empty incoming list."""
    processor = DeduplicationProcessor(existing_jobs=[])
    merged, new_count, updated_count = processor.process_incoming([])
    assert merged == []
    assert new_count == 0
    assert updated_count == 0


def test_senior_classifier_rejects_tricky_senior_labels():
    """Verify senior titles disguised with tricky casing or phrases are filtered out."""
    assert determine_experience_level("SENIOR SysAdmin Specialist", "5+ năm kinh nghiệm") is None
    assert determine_experience_level("Tech Lead DevOps", "Leader cho team infra") is None
    assert determine_experience_level("Trưởng Nhóm Vận Hành Mạng", "Quản lý 10 kỹ sư NOC") is None
