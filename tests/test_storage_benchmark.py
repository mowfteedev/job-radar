"""Storage & Query Latency Benchmarks for VN Tech Job Radar Data Store."""
import gzip
import json
import time
from datetime import datetime, timezone
from pathlib import Path
import pytest

from schemas.job import (
    CompanyInfo,
    ExperienceLevel,
    JobPost,
    LocationCategory,
    RoleCategory,
    SalaryInfo,
    compute_canonical_hash,
)
from src.processors.indexer import JobSearchIndexer


def generate_mock_dataset(count: int = 500) -> list[JobPost]:
    """Generates synthetic job records for stress and scale benchmarking."""
    now = datetime.now(timezone.utc)
    roles = list(RoleCategory)
    locs = [LocationCategory.HA_NOI, LocationCategory.HO_CHI_MINH, LocationCategory.DA_NANG]
    dataset = []

    for i in range(count):
        role = roles[i % len(roles)]
        loc = locs[i % len(locs)]
        title = f"Test Job {role.value.capitalize()} #{i}"
        comp = f"Enterprise Corp {i % 20}"
        h = compute_canonical_hash(comp, title, loc.value)
        dataset.append(
            JobPost(
                id=f"synth-{i}",
                canonical_hash=h,
                title=title,
                company=CompanyInfo.create(name=comp, location=loc),
                role_category=role,
                experience_level=ExperienceLevel.FRESHER,
                skills=["Docker", "Linux", "CCNA", "Python"][: (i % 4 + 1)],
                locations=[loc],
                salary=SalaryInfo(display_text="Thỏa thuận"),
                source_url=f"https://example.com/job/{i}",
                source_platform="BenchmarkSuite",
                description_summary=f"Detailed description for synthetic job {i} with technical requirements.",
                posted_at=now,
            )
        )
    return dataset


def test_inverted_index_query_latency_under_5ms():
    """Validates that filtered queries via inverted index resolve in < 5ms."""
    dataset = generate_mock_dataset(500)
    indexer = JobSearchIndexer(dataset)
    index_payload = indexer.build_indexes()
    indexes = index_payload["indexes"]
    records = index_payload["records"]

    # 1. Benchmark: Point Lookup by ID
    t0 = time.perf_counter()
    target_record = records.get("synth-250")
    point_latency_ms = (time.perf_counter() - t0) * 1000.0

    assert target_record is not None
    assert point_latency_ms < 5.0, f"Point lookup too slow: {point_latency_ms:.3f}ms"

    # 2. Benchmark: Compound Filter (Role: Network AND Location: Hanoi)
    t0 = time.perf_counter()
    network_ids = set(indexes["by_role"].get("network", []))
    hanoi_ids = set(indexes["by_location"].get("ha_noi", []))
    matched_ids = network_ids.intersection(hanoi_ids)
    results = [records[jid] for jid in matched_ids]
    filter_latency_ms = (time.perf_counter() - t0) * 1000.0

    assert len(results) > 0
    assert filter_latency_ms < 5.0, f"Compound query took too long: {filter_latency_ms:.3f}ms"


def test_storage_payload_compression_ratio(tmp_path: Path):
    """Verifies that static JSON compresses efficiently via Gzip (> 65% reduction)."""
    dataset = generate_mock_dataset(300)
    indexer = JobSearchIndexer(dataset)
    index_payload = indexer.build_indexes()

    raw_json = json.dumps(index_payload, separators=(",", ":")).encode("utf-8")
    compressed = gzip.compress(raw_json)

    raw_size_kb = len(raw_json) / 1024.0
    compressed_size_kb = len(compressed) / 1024.0
    reduction_pct = (1.0 - (len(compressed) / len(raw_json))) * 100.0

    print(f"\n[Storage Benchmark] Raw: {raw_size_kb:.1f} KB | Gzipped: {compressed_size_kb:.1f} KB | Saved: {reduction_pct:.1f}%")
    assert reduction_pct >= 65.0, f"Compression ratio below target: {reduction_pct:.1f}%"
    assert compressed_size_kb < 100.0, "300 records compressed payload exceeds 100KB budget"
