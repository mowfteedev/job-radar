"""Job Classification & Seniority Rules Engine."""
from __future__ import annotations

import re
from typing import List, Optional, Set, Tuple
from schemas.job import ExperienceLevel, LocationCategory, RoleCategory

# Whitelist keywords mapped to Role Categories
ROLE_KEYWORDS = {
    RoleCategory.NETWORK: [
        "network", "mạng", "noc", "ccna", "ccnp", "routing", "switching",
        "cisco", "juniper", "mikrotik", "firewall", "fortinet", "wan", "lan"
    ],
    RoleCategory.HELPDESK: [
        "helpdesk", "it support", "hỗ trợ kỹ thuật", "it officer", "desktop support",
        "kỹ thuật it", "it nội bộ", "cài đặt máy tính", "quản trị thiết bị"
    ],
    RoleCategory.SYSADMIN: [
        "sysadmin", "system admin", "quản trị hệ thống", "linux", "ubuntu", "centos",
        "windows server", "active directory", "mcsa", "vmware", "virtualization"
    ],
    RoleCategory.DEVOPS: [
        "devops", "ci/cd", "docker", "kubernetes", "k8s", "ansible", "terraform",
        "jenkins", "gitlab ci", "helm", "prometheus", "grafana"
    ],
    RoleCategory.CLOUD: [
        "cloud", "aws", "azure", "gcp", "openstack", "cloud engineer", "cloud practitioner"
    ],
    RoleCategory.SECURITY_SOC: [
        "soc", "security", "an ninh mạng", "bảo mật", "siem", "incident response"
    ]
}

# Negative keywords indicating seniority (should be filtered out for Fresher radar)
SENIOR_BLACKLIST = [
    r"\bsenior\b", r"\blead\b", r"\bprincipal\b", r"\bmanager\b", r"\btrưởng nhóm\b",
    r"\btrưởng phòng\b", r"\btrưởng bộ phận\b", r"\bchuyên gia\b", r"\barchitect\b",
    r"\bdirector\b", r"\bgiám đốc\b", r"\bvice president\b", r"\bvp\b", r"\bhead of\b",
    r"\bquản lý\b",
    r"3\s*-\s*5\s*năm", r"3\+\s*năm", r"4\+\s*năm", r"5\+\s*năm",
    r"3\s*-\s*5\s*years", r"3\+\s*years", r"4\+\s*years", r"5\+\s*years"
]

# Intern & Fresher positive keywords
FRESHER_WHITELIST = [
    r"\bfresher\b", r"\bintern\b", r"\binternship\b", r"\bthực tập\b", r"\btrainee\b",
    r"\bmới tốt nghiệp\b", r"\bkhông yêu cầu kinh nghiệm\b", r"\b0\s*-\s*1\s*năm\b",
    r"\bdưới 1 năm\b", r"\bchưa có kinh nghiệm\b", r"\bjunior\b"
]


def classify_role(title: str, description: str) -> Optional[RoleCategory]:
    """Classifies a job into a primary RoleCategory based on title and description."""
    text = f"{title.lower()} {description.lower()}"
    
    # Priority check based on Title first
    title_lower = title.lower()
    for role, keywords in ROLE_KEYWORDS.items():
        for kw in keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", title_lower):
                return role

    # Fallback check on description
    scores = {}
    for role, keywords in ROLE_KEYWORDS.items():
        count = sum(1 for kw in keywords if kw in text)
        if count > 0:
            scores[role] = count

    if scores:
        return max(scores, key=scores.get)
    return None


def determine_experience_level(title: str, description: str) -> Optional[ExperienceLevel]:
    """Determines if the role fits intern, fresher, or junior. Returns None if senior/excluded."""
    text = f"{title.lower()} {description.lower()}"

    # Filter out senior roles
    for pattern in SENIOR_BLACKLIST:
        if re.search(pattern, text):
            # If explicit fresher in title, allow override
            if "fresher" not in title.lower() and "thực tập" not in title.lower():
                return None

    # Check for intern
    if any(re.search(p, text) for p in [r"\bintern\b", r"\bthực tập\b", r"\btrainee\b"]):
        return ExperienceLevel.INTERN

    # Check for fresher
    if any(re.search(p, text) for p in [r"\bfresher\b", r"\bmới tốt nghiệp\b", r"\b0\s*-\s*1\s*năm\b", r"\bchưa có kinh nghiệm\b"]):
        return ExperienceLevel.FRESHER

    # Fallback to junior if explicitly mentioned
    if "junior" in text:
        return ExperienceLevel.JUNIOR

    return ExperienceLevel.FRESHER


def extract_skills(text: str) -> List[str]:
    """Extracts known technical skills from job text."""
    known_skills = [
        "CCNA", "CCNP", "Cisco", "Mikrotik", "Juniper", "Fortinet", "Palo Alto",
        "Linux", "Ubuntu", "CentOS", "RedHat", "Windows Server", "Active Directory",
        "Docker", "Kubernetes", "Ansible", "Terraform", "CI/CD", "GitLab CI", "Jenkins",
        "AWS", "Azure", "GCP", "Python", "Bash", "Shell Script", "PowerShell",
        "Prometheus", "Grafana", "Zabbix", "Nginx", "Apache", "TCP/IP", "DNS", "DHCP", "VPN"
    ]
    found = []
    text_lower = text.lower()
    for skill in known_skills:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(list(set(found)))


def detect_locations(text: str) -> List[LocationCategory]:
    """Detects normalized workplace locations from job text with word-boundary accuracy."""
    locs: List[LocationCategory] = []
    text_lower = text.lower()

    if re.search(r"\b(hà nội|ha noi|hn)\b", text_lower):
        locs.append(LocationCategory.HA_NOI)
    if re.search(r"\b(hồ chí minh|ho chi minh|hcm|sài gòn|sai gon|tphcm)\b", text_lower):
        locs.append(LocationCategory.HO_CHI_MINH)
    if re.search(r"\b(đà nẵng|da nang|đn|dn)\b", text_lower):
        locs.append(LocationCategory.DA_NANG)
    if re.search(r"\b(remote|từ xa|tu xa|làm việc tại nhà|lam viec tai nha)\b", text_lower):
        locs.append(LocationCategory.REMOTE)

    if not locs:
        locs.append(LocationCategory.OTHER)
    return locs
