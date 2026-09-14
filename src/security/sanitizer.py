"""Security module: Untrusted Input Sanitization & SSRF/XSS Prevention."""
from __future__ import annotations

import html
import ipaddress
import re
from typing import Optional
from urllib.parse import urlparse

# Private / Internal IP subnets for SSRF defense
PRIVATE_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),       # Loopback
    ipaddress.ip_network("10.0.0.0/8"),        # Private Class A
    ipaddress.ip_network("172.16.0.0/12"),     # Private Class B
    ipaddress.ip_network("192.168.0.0/16"),    # Private Class C
    ipaddress.ip_network("169.254.0.0/16"),    # Cloud Link-local & Metadata (AWS/GCP)
    ipaddress.ip_network("::1/128"),           # IPv6 Loopback
    ipaddress.ip_network("fc00::/7"),          # IPv6 Unique Local
]

# Disallowed malicious schemes
FORBIDDEN_SCHEMES = {"javascript", "data", "file", "vbscript", "blob", "about"}


def validate_and_sanitize_url(raw_url: str) -> Optional[str]:
    """Validates and sanitizes external URLs to prevent SSRF and XSS attacks.
    
    Returns:
        Clean sanitized URL string if safe, or None if rejected.
    """
    if not raw_url or not isinstance(raw_url, str):
        return None

    cleaned_url = raw_url.strip()

    # Reject dangerous schemes immediately
    lower_url = cleaned_url.lower()
    for scheme in FORBIDDEN_SCHEMES:
        if lower_url.startswith(f"{scheme}:"):
            return None

    try:
        parsed = urlparse(cleaned_url)
    except Exception:
        return None

    # Enforce strict protocol whitelist
    if parsed.scheme not in ("http", "https"):
        return None

    hostname = parsed.hostname
    if not hostname:
        return None

    # Check for localhost / loopback aliases
    if hostname.lower() in ("localhost", "127.0.0.1", "::1"):
        return None

    # SSRF Prevention: Check if hostname is an IP pointing to private/internal network
    try:
        ip = ipaddress.ip_address(hostname)
        for net in PRIVATE_NETWORKS:
            if ip in net:
                return None
    except ValueError:
        # Hostname is a standard FQDN domain string, not a numerical IP literal
        hostname_is_ip = False

    return cleaned_url


def sanitize_text(raw_text: str, max_length: int = 500) -> str:
    """Strips executable markup, scripts, and normalizes untrusted text strings."""
    if not raw_text or not isinstance(raw_text, str):
        return ""

    # Remove script and iframe tags entirely
    cleaned = re.sub(r"<(script|iframe|style|object|embed)[^>]*>.*?</\1>", "", raw_text, flags=re.IGNORECASE | re.DOTALL)
    # Remove all remaining HTML tags
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    # Remove inline event handler attributes like onerror=, onload=
    cleaned = re.sub(r"on\w+\s*=\s*['\"].*?['\"]", "", cleaned, flags=re.IGNORECASE)
    # Collapse multiple whitespaces
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    # Escape HTML entities for defense-in-depth against stored XSS
    escaped = html.escape(cleaned)
    return escaped[:max_length]
