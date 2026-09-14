"""Mock HTTP Responses and Adversarial Payload Fixtures for Tester Reality Check."""
from __future__ import annotations

# Corrupted, truncated, and malicious HTML snippets
CORRUPTED_HTML_SAMPLES = {
    "truncated": """
    <div class="job-item">
        <h3><a href="/jobs/incomplete">Fresher Network Engineer
    """,
    "xss_payload": """
    <div class="job-item">
        <h3><a href="javascript:alert('pwn')"><script>alert('xss')</script>Fresher Helpdesk IT</a></h3>
        <p class="desc"><img src=x onerror=alert('img-xss')>Hỗ trợ người dùng nội bộ, cài win, mạng LAN</p>
        <div class="location">Hà Nội</div>
    </div>
    """,
    "ssrf_metadata_url": """
    <div class="job-item">
        <h3><a href="http://169.254.169.254/latest/meta-data/iam">Cloud DevOps Trainee</a></h3>
        <p class="desc">Thực tập sinh Cloud AWS, Docker, Kubernetes</p>
        <div class="location">TP.HCM</div>
    </div>
    """,
    "massive_fuzz_payload": f"""
    <div class="job-item">
        <h3><a href="https://example.com/job/massive">Fresher SysAdmin {'A' * 50000}</a></h3>
        <p class="desc">{'Unicode \\u200b \\u202e 👨‍👩‍👧‍👦 ' * 1000}</p>
        <div class="location">Đà Nẵng</div>
    </div>
    """,
    "no_matching_cards": """
    <html>
        <body>
            <div class="random-wrapper">
                <p>Không có tin tuyển dụng nào ở đây cả.</p>
            </div>
        </body>
    </html>
    """,
}

# Malformed salary payloads for testing validation boundaries
INVALID_SALARY_TEST_CASES = [
    {"min_amount": -1000000, "max_amount": 5000000, "expected_error": "greater than or equal to 0"},
    {"min_amount": 20000000, "max_amount": 10000000, "expected_error": "cannot exceed max_amount"},
    {"min_amount": -500, "max_amount": -100, "expected_error": "greater than or equal to 0"},
]

# Tricky titles to verify strict seniority filtering
TRICKY_SENIORITY_CASES = [
    ("Principal Cloud & DevOps Architect", "Hà Nội", None),
    ("Senior Director of Network Infrastructure", "TP.HCM", None),
    ("Lead Systems Engineer (5+ years experience)", "Đà Nẵng", None),
    ("Vice President of IT Operations", "Hà Nội", None),
    ("Fresher Network Engineer", "Hà Nội", "fresher"),
    ("Thực tập sinh IT Helpdesk (Internship)", "TP.HCM", "intern"),
    ("Junior DevOps Engineer (0-1 năm)", "Đà Nẵng", "fresher"),
]
