"""Data Contracts & Schema Definitions for VN Tech Job Radar."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator


class RoleCategory(str, Enum):
    """Core tech specializations tracked by Job Radar."""
    NETWORK = "network"                  # Network Engineer, NOC, CCNA/CCNP
    HELPDESK = "helpdesk"                # IT Helpdesk, Desktop Support, IT Officer
    SYSADMIN = "sysadmin"                # System Administrator (Linux/Windows), MCSA
    DEVOPS = "devops"                    # DevOps Engineer, CI/CD, IaC, Kubernetes
    CLOUD = "cloud"                      # Cloud Engineer (AWS/Azure/GCP)
    SECURITY_SOC = "security_soc"        # SOC Analyst, Security Intern


class LocationCategory(str, Enum):
    """Normalized workplace locations in Vietnam."""
    HA_NOI = "ha_noi"
    HO_CHI_MINH = "ho_chi_minh"
    DA_NANG = "da_nang"
    REMOTE = "remote"
    HYBRID = "hybrid"
    OTHER = "other"


class ExperienceLevel(str, Enum):
    """Target candidate experience levels."""
    INTERN = "intern"
    FRESHER = "fresher"
    JUNIOR = "junior"


class JobStatus(str, Enum):
    """Lifecycle status of a job post."""
    ACTIVE = "active"
    EXPIRED = "expired"
    CLOSED = "closed"


class WorkType(str, Enum):
    """Employment arrangement."""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    INTERNSHIP = "internship"
    CONTRACT = "contract"


class SalaryInfo(BaseModel):
    """Standardized salary information."""
    currency: str = Field(default="VND", description="Currency code (VND, USD)")
    min_amount: Optional[int] = Field(default=None, description="Minimum salary amount")
    max_amount: Optional[int] = Field(default=None, description="Maximum salary amount")
    is_negotiable: bool = Field(default=True, description="True if salary is negotiable or undisclosed")
    display_text: str = Field(default="Thỏa thuận", description="Human-friendly salary display string")


class CompanyInfo(BaseModel):
    """Standardized company metadata."""
    name: str = Field(..., min_length=1, description="Company name")
    normalized_name: str = Field(..., description="Lowercase trimmed company name for matching")
    logo_url: Optional[str] = Field(default=None, description="Company logo image URL")
    website: Optional[str] = Field(default=None, description="Company website URL")
    location: LocationCategory = Field(default=LocationCategory.OTHER)
    address: Optional[str] = Field(default=None, description="Detailed office address")

    @classmethod
    def create(cls, name: str, logo_url: Optional[str] = None, website: Optional[str] = None,
               location: LocationCategory = LocationCategory.OTHER, address: Optional[str] = None) -> CompanyInfo:
        norm = re.sub(r"[^\w\s]", "", name.lower()).strip()
        norm = re.sub(r"\s+", " ", norm)
        return cls(
            name=name.strip(),
            normalized_name=norm,
            logo_url=logo_url,
            website=website,
            location=location,
            address=address
        )


def compute_canonical_hash(company_name: str, title: str, location: str) -> str:
    """Generate deterministic SHA256 canonical hash to deduplicate jobs across platforms."""
    norm_comp = re.sub(r"[^\w]", "", company_name.lower())
    norm_title = re.sub(r"[^\w]", "", title.lower())
    norm_loc = re.sub(r"[^\w]", "", location.lower())
    seed = f"{norm_comp}:{norm_title}:{norm_loc}".encode("utf-8")
    return hashlib.sha256(seed).hexdigest()[:16]


class JobPost(BaseModel):
    """Core Job Post entity for the Radar pipeline."""
    id: str = Field(..., description="Unique job identifier (e.g. SHA256 prefix or platform slug)")
    canonical_hash: str = Field(..., description="Deduplication hash (company + title + location)")
    title: str = Field(..., min_length=3, description="Job title")
    company: CompanyInfo = Field(..., description="Hiring company details")
    role_category: RoleCategory = Field(..., description="Primary technical domain")
    experience_level: ExperienceLevel = Field(..., description="Seniority level (intern, fresher, junior)")
    skills: List[str] = Field(default_factory=list, description="Extracted skill tags (e.g. CCNA, Docker, Linux)")
    locations: List[LocationCategory] = Field(..., min_length=1, description="Work locations")
    salary: SalaryInfo = Field(default_factory=SalaryInfo, description="Salary details")
    source_url: str = Field(..., description="Direct link to original job posting")
    source_platform: str = Field(..., description="Source platform name (e.g. TopCV, ITviec, FPT, Viettel)")
    description_summary: str = Field(..., description="Brief summary of duties and requirements (< 300 words)")
    posted_at: datetime = Field(..., description="Original publication timestamp")
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Scrape timestamp")
    expires_at: Optional[datetime] = Field(default=None, description="Expiration date (TTL)")
    status: JobStatus = Field(default=JobStatus.ACTIVE, description="Active status")
    relevance_score: int = Field(default=80, ge=0, le=100, description="Quality & relevancy score (0-100)")
    work_type: WorkType = Field(default=WorkType.FULL_TIME)

    @field_validator("title")
    @classmethod
    def clean_title(cls, v: str) -> str:
        return re.sub(r"\s+", " ", v).strip()

    @field_validator("source_url")
    @classmethod
    def validate_safe_url(cls, v: str) -> str:
        from src.security.sanitizer import validate_and_sanitize_url
        clean = validate_and_sanitize_url(v)
        if not clean:
            raise ValueError(f"Insecure, malicious or invalid source_url: {v}")
        return clean


class SkillFrequency(BaseModel):
    """Aggregated metrics for a single skill."""
    skill: str
    count: int
    percentage: float
    category: str = Field(default="general", description="network, devops, system, cloud, etc.")


class RadarMetrics(BaseModel):
    """Aggregated statistics for the Radar Dashboard."""
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    total_active_jobs: int = Field(default=0)
    fresh_jobs_24h: int = Field(default=0)
    jobs_by_role: Dict[str, int] = Field(default_factory=dict)
    jobs_by_location: Dict[str, int] = Field(default_factory=dict)
    top_skills: List[SkillFrequency] = Field(default_factory=list)


def export_json_schema(target_dir: str | Path = "data") -> Path:
    """Exports Pydantic JSON schemas to a static JSON file for external validators."""
    out_dir = Path(target_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    schema_file = out_dir / "schema_jobs.json"
    
    combined_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "VNTechJobRadarSchemas",
        "definitions": {
            "JobPost": JobPost.model_json_schema(),
            "RadarMetrics": RadarMetrics.model_json_schema(),
            "CompanyInfo": CompanyInfo.model_json_schema(),
            "SalaryInfo": SalaryInfo.model_json_schema(),
        }
    }
    
    with open(schema_file, "w", encoding="utf-8") as f:
        json.dump(combined_schema, f, indent=2, ensure_ascii=False)
        
    return schema_file
