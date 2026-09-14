"""Security module: Repository Secret Scanner for Zero Secret Leaks."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple

# Regex patterns matching potential leaked credentials and tokens
SECRET_PATTERNS: Dict[str, re.Pattern] = {
    "GitHub Token": re.compile(r"\b(ghp_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9_]{82})\b"),
    "AWS Access Key": re.compile(r"\b(AKIA[0-9A-Z]{16})\b"),
    "Telegram Bot Token": re.compile(r"\b([0-9]{8,10}:[a-zA-Z0-9_-]{35})\b"),
    "Slack Webhook": re.compile(r"https://hooks\.slack\.com/services/T[a-zA-Z0-9_]+/B[a-zA-Z0-9_]+/[a-zA-Z0-9_]+"),
    "Private Key Block": re.compile(r"-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----"),
    "Generic Password Assignment": re.compile(r"""(?i)(?:password|secret|api_key|token)\s*=\s*['"][a-zA-Z0-9@#$%^&*()_+=-]{8,}['"]"""),
}

# Directories and files to exclude from scanner
SCAN_EXCLUDES = {
    ".git", ".venv", "venv", "node_modules", "dist", ".astro", "__pycache__",
    ".pytest_cache", "package-lock.json"
}


class SecretScanner:
    """Scans repository code and text files for accidental credential commits."""

    def __init__(self, root_dir: str | Path = ".") -> None:
        self.root_dir = Path(root_dir)

    def scan(self) -> List[Tuple[str, int, str, str]]:
        """Scans the repository.
        
        Returns:
            List of tuples: (relative_file_path, line_number, secret_type, matched_snippet)
        """
        findings: List[Tuple[str, int, str, str]] = []

        for path in self.root_dir.rglob("*"):
            if path.is_file() and not self._is_excluded(path):
                # Skip binary files
                if path.suffix in {".pyc", ".png", ".jpg", ".ico", ".woff", ".woff2", ".ttf"}:
                    continue

                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        for line_no, line in enumerate(f, start=1):
                            # Skip comment lines explaining regexes or examples
                            if "SECRET_PATTERNS" in line or "# Generic Password Assignment" in line:
                                continue

                            for secret_name, pattern in SECRET_PATTERNS.items():
                                match = pattern.search(line)
                                if match:
                                    snippet = match.group(0)[:25] + "..."
                                    findings.append((str(path.relative_to(self.root_dir)), line_no, secret_name, snippet))
                except Exception:
                    continue

        return findings

    def _is_excluded(self, path: Path) -> bool:
        for part in path.parts:
            if part in SCAN_EXCLUDES:
                return True
        return False
