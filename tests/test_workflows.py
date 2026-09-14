"""Verification tests for GitHub Actions CI/CD Workflows."""
from pathlib import Path
import pytest
import re


def parse_simple_yaml_structure(filepath: Path) -> str:
    """Reads and asserts that workflow file is valid UTF-8 and contains mandatory keys."""
    assert filepath.exists(), f"Workflow file missing: {filepath}"
    content = filepath.read_text(encoding="utf-8")
    assert "name:" in content, f"Missing workflow name in {filepath}"
    assert "jobs:" in content, f"Missing jobs definition in {filepath}"
    return content


def test_ci_workflow_structure():
    ci_file = Path(".github/workflows/ci.yml")
    content = parse_simple_yaml_structure(ci_file)

    assert "pull_request:" in content
    assert "push:" in content
    assert "backend-test:" in content
    assert "frontend-test:" in content
    assert "pytest -v" in content
    assert "SecretScanner" in content


def test_pipeline_workflow_schedule_and_pages():
    pipeline_file = Path(".github/workflows/pipeline.yml")
    content = parse_simple_yaml_structure(pipeline_file)

    # Validate cron schedule 06:00 and 18:00 UTC+7 (23:00 and 11:00 UTC)
    assert "cron: '0 23,11 * * *'" in content
    assert "workflow_dispatch:" in content

    # Permissions
    assert "pages: write" in content
    assert "contents: write" in content
    assert "id-token: write" in content

    # Bot commit check
    assert "github-actions[bot]" in content
    assert "[skip ci]" in content

    # Deploy action
    assert "actions/deploy-pages@v4" in content
    assert "actions/upload-pages-artifact@v3" in content
