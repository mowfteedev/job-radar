import asyncio
from datetime import datetime, timezone
import time
import pytest
from pydantic import ValidationError

from schemas.job import (
    CompanyInfo,
    ExperienceLevel,
    JobPost,
    LocationCategory,
    RoleCategory,
    SalaryInfo,
)
from src.security.rate_limiter import AsyncPoliteRateLimiter
from src.security.sanitizer import sanitize_text, validate_and_sanitize_url
from src.security.secret_scanner import SecretScanner
from src.security.user_agents import UserAgentRotator


def test_ssrf_prevention_rejects_internal_networks():
    """Verify that private IP ranges, loopbacks, and cloud metadata IPs are blocked."""
    assert validate_and_sanitize_url("http://127.0.0.1/admin") is None
    assert validate_and_sanitize_url("http://localhost:8080/metrics") is None
    assert validate_and_sanitize_url("http://169.254.169.254/latest/meta-data/") is None
    assert validate_and_sanitize_url("http://192.168.1.1/config") is None
    assert validate_and_sanitize_url("http://10.0.0.1/internal-api") is None
    assert validate_and_sanitize_url("http://172.16.0.1/dashboard") is None

    # Legitimate external domains must be allowed
    assert validate_and_sanitize_url("https://tuyendung.fpt.vn/job/101") == "https://tuyendung.fpt.vn/job/101"
    assert validate_and_sanitize_url("http://careers.viettel.vn/job/it") == "http://careers.viettel.vn/job/it"


def test_xss_prevention_rejects_malicious_schemes():
    """Verify that executable or local URI schemes are immediately blocked."""
    assert validate_and_sanitize_url("javascript:alert(document.cookie)") is None
    assert validate_and_sanitize_url("data:text/html,<script>alert(1)</script>") is None
    assert validate_and_sanitize_url("file:///etc/shadow") is None
    assert validate_and_sanitize_url("vbscript:msgbox('pwned')") is None


def test_job_post_schema_enforces_url_security():
    """JobPost pydantic model must reject posts containing dangerous URLs."""
    with pytest.raises(ValidationError):
        JobPost(
            id="bad-ssrf-job",
            canonical_hash="hash123",
            title="DevOps Intern",
            company=CompanyInfo.create(name="HackerCorp"),
            role_category=RoleCategory.DEVOPS,
            experience_level=ExperienceLevel.INTERN,
            skills=["Docker"],
            locations=[LocationCategory.HA_NOI],
            salary=SalaryInfo(),
            source_url="javascript:alert('xss')",  # Malicious scheme
            source_platform="HackerSite",
            description_summary="Desc",
            posted_at=datetime.now(timezone.utc),
        )


def test_text_sanitizer_removes_dangerous_tags_and_escapes():
    """Ensures untrusted HTML descriptions are sanitized against stored XSS."""
    dirty = "<script>stealCookies();</script><b>Job Title</b> <img src=x onerror='alert(1)'>"
    clean = sanitize_text(dirty)
    assert "<script>" not in clean
    assert "stealCookies" not in clean
    assert "onerror" not in clean
    assert "&lt;b&gt;" in clean or "Job Title" in clean


def test_user_agent_rotator_returns_valid_profiles():
    """Verifies User-Agent rotator returns realistic headers with responsible contact info."""
    rotator = UserAgentRotator(contact_email="test@jobradar.vn")
    headers = rotator.get_headers()

    assert "User-Agent" in headers
    assert "Mozilla/5.0" in headers["User-Agent"]
    assert headers["X-Crawler-Contact"] == "test@jobradar.vn"
    assert headers["DNT"] == "1"


@pytest.mark.asyncio
async def test_async_rate_limiter_throttles_calls():
    """Verifies AsyncPoliteRateLimiter enforces time intervals between successive calls."""
    limiter = AsyncPoliteRateLimiter(
        requests_per_second=5.0,
        min_delay_seconds=0.1,
        max_delay_seconds=0.2,
        max_concurrent=2,
    )

    t0 = time.monotonic()
    async with limiter:
        pass
    async with limiter:
        pass
    elapsed = time.monotonic() - t0

    # Two sequential acquisitions should take at least min_delay
    assert elapsed >= 0.1


def test_zero_secret_leaks_audit():
    """Scans all repository files to guarantee ZERO hardcoded credentials exist."""
    scanner = SecretScanner(root_dir=".")
    findings = scanner.scan()

    assert len(findings) == 0, f"Found leaked secrets in repo: {findings}"
