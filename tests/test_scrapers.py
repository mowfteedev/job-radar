"""Tests for Scraper Adapters & Resilience Handling."""
from unittest.mock import AsyncMock, patch
import httpx
import pytest

from schemas.job import ExperienceLevel, RoleCategory
from src.scrapers.community_tech import CommunityTechScraper
from src.scrapers.fpt_telecom import FPTTelecomScraper
from src.scrapers.viettel_careers import ViettelCareersScraper


SAMPLE_FPT_HTML = """
<div class="job-list">
    <div class="job-item">
        <h3 class="title">
            <a href="/job/fresher-noc-engineer">Fresher NOC Engineer (Giám sát hệ thống mạng)</a>
        </h3>
        <div class="location">Hà Nội</div>
        <p class="desc">Yêu cầu CCNA, nắm vững TCP/IP, Routing và Switching Cisco.</p>
    </div>
    <div class="job-item">
        <h3 class="title">
            <a href="/job/senior-network-architect">Senior Network Solution Architect</a>
        </h3>
        <div class="location">Hồ Chí Minh</div>
        <p class="desc">Yêu cầu 5+ năm kinh nghiệm thiết kế giải pháp mạng viễn thông.</p>
    </div>
</div>
"""

SAMPLE_VIETTEL_HTML = """
<div class="search-result">
    <div class="job-box">
        <a class="title" href="/job/it-support-fresher">Kỹ sư IT Support / Helpdesk Nội bộ</a>
        <span class="location">Hà Nội</span>
        <p class="desc">Hỗ trợ người dùng, cấu hình Active Directory, quản trị mạng LAN văn phòng.</p>
    </div>
</div>
"""

SAMPLE_COMMUNITY_ISSUES = [
    {
        "title": "[VNG] Fresher DevOps Engineer (Kubernetes & CI/CD)",
        "body": "Tuyển Fresher DevOps làm việc tại TP.HCM. Kỹ năng: Docker, Kubernetes, Linux, CI/CD.",
        "html_url": "https://github.com/awesome-jobs/vietnam/issues/101",
    },
    {
        "title": "[TechCorp] Senior Lead Cloud Architect (10+ years)",
        "body": "Tuyển vị trí Lead với 10 năm kinh nghiệm AWS.",
        "html_url": "https://github.com/awesome-jobs/vietnam/issues/102",
    },
]


@pytest.mark.asyncio
async def test_fpt_scraper_parse_html():
    scraper = FPTTelecomScraper()
    jobs = scraper._parse_html(SAMPLE_FPT_HTML)
    
    # Should include fresher NOC, but exclude Senior Architect
    assert len(jobs) == 1
    job = jobs[0]
    assert "Fresher NOC" in job.title
    assert job.role_category == RoleCategory.NETWORK
    assert job.experience_level == ExperienceLevel.FRESHER
    assert "CCNA" in job.skills
    assert "ha_noi" in [loc.value for loc in job.locations]


@pytest.mark.asyncio
async def test_viettel_scraper_parse_html():
    scraper = ViettelCareersScraper()
    jobs = scraper._parse_html(SAMPLE_VIETTEL_HTML)
    
    assert len(jobs) == 1
    job = jobs[0]
    assert "IT Support" in job.title
    assert job.role_category == RoleCategory.HELPDESK
    assert "Active Directory" in job.skills


@pytest.mark.asyncio
async def test_community_scraper_parse_issues():
    scraper = CommunityTechScraper()
    jobs = scraper._parse_github_issues(SAMPLE_COMMUNITY_ISSUES)

    # Should include Fresher DevOps, exclude Senior Lead Architect
    assert len(jobs) == 1
    job = jobs[0]
    assert job.company.name == "VNG"
    assert job.role_category == RoleCategory.DEVOPS
    assert job.experience_level == ExperienceLevel.FRESHER
    assert "Docker" in job.skills
    assert "Kubernetes" in job.skills


@pytest.mark.asyncio
async def test_scraper_network_failure_resilience():
    """Verify scrapers do not crash when encountering HTTP 500 or timeout."""
    scraper = FPTTelecomScraper()

    # Mock client raising TimeoutException
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.side_effect = httpx.ReadTimeout("Connection timed out")

    # Should catch gracefully and return fallback fixtures
    jobs = await scraper.scrape(client=mock_client)
    assert len(jobs) >= 1
    assert any("FPT Telecom" in j.company.name for j in jobs)
