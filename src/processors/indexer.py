"""Static Inverted Indexer & Storage Optimizer for VN Tech Job Radar."""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Set
from schemas.job import JobPost

logger = logging.getLogger("job_radar.indexer")


class JobSearchIndexer:
    """Compiles optimized static inverted indexes and compact search payloads.
    
    Acts as the in-memory database index engine for client-side O(1) lookups.
    """

    def __init__(self, jobs: List[JobPost]) -> None:
        self.jobs = jobs

    def build_indexes(self) -> Dict[str, Any]:
        """Constructs an inverted index mapping tokens, categories, and skills to Job IDs."""
        by_role: Dict[str, List[str]] = {}
        by_location: Dict[str, List[str]] = {}
        by_level: Dict[str, List[str]] = {}
        by_skill: Dict[str, List[str]] = {}
        by_keyword: Dict[str, List[str]] = {}
        lookup_table: Dict[str, Dict[str, Any]] = {}

        for job in self.jobs:
            jid = job.id

            # 1. Compact record for instantaneous client consumption
            lookup_table[jid] = {
                "id": jid,
                "canonical_hash": job.canonical_hash,
                "title": job.title,
                "company": {
                    "name": job.company.name,
                    "location": job.company.location.value,
                },
                "role": job.role_category.value,
                "level": job.experience_level.value,
                "locations": [loc.value for loc in job.locations],
                "skills": job.skills,
                "salary": job.salary.display_text,
                "source_url": job.source_url,
                "source_platform": job.source_platform,
                "desc": job.description_summary[:220],
                "score": job.relevance_score,
                "posted_at": job.posted_at.isoformat(),
            }

            # 2. Index by Role Category
            role_key = job.role_category.value
            by_role.setdefault(role_key, []).append(jid)

            # 3. Index by Location
            for loc in job.locations:
                by_location.setdefault(loc.value, []).append(jid)

            # 4. Index by Seniority Level
            level_key = job.experience_level.value
            by_level.setdefault(level_key, []).append(jid)

            # 5. Index by Technical Skills (normalized lowercase)
            for skill in job.skills:
                s_norm = skill.lower().strip()
                by_skill.setdefault(s_norm, []).append(jid)

            # 6. Full-Text Inverted Index (Tokenization)
            text_corpus = f"{job.title} {job.company.name} {job.description_summary} {' '.join(job.skills)}"
            tokens = self._tokenize(text_corpus)
            for token in tokens:
                by_keyword.setdefault(token, []).append(jid)

        return {
            "version": "1.0.0",
            "total_records": len(self.jobs),
            "indexes": {
                "by_role": by_role,
                "by_location": by_location,
                "by_level": by_level,
                "by_skill": by_skill,
                "by_keyword": by_keyword,
            },
            "records": lookup_table,
        }

    def _tokenize(self, text: str) -> Set[str]:
        """Extracts search tokens (3+ alphanumeric characters), removing common stop words."""
        stop_words = {
            "and", "the", "for", "with", "của", "và", "cho", "các", "tại",
            "trong", "về", "khi", "được", "yêu", "cầu", "với", "tuyển", "dụng",
            "công", "ty", "việc", "làm", "nhân", "viên"
        }
        words = re.findall(r"\b[a-zA-Z0-9_+#.-]{2,}\b", text.lower())
        return {w for w in words if w not in stop_words and len(w) >= 2}

    def save_index(self, output_file: str | Path) -> Path:
        """Serializes the index structure to disk atomically."""
        out_path = Path(output_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        payload = self.build_indexes()

        temp_path = out_path.with_suffix(".tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
        temp_path.replace(out_path)

        logger.info(
            f"Saved search index to {out_path} ({len(payload['records'])} records, "
            f"{len(payload['indexes']['by_keyword'])} keyword tokens)."
        )
        return out_path
