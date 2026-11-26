from __future__ import annotations

import re
from enum import Enum
from pathlib import PurePosixPath


class SensitivityTag(str, Enum):
    """Data egress classification for indexed sources."""

    API_OK = "api-ok"
    LOCAL_ONLY = "local-only"
    EXCLUDED = "excluded"


class AccessLevel(str, Enum):
    """Role-based access tier enforced prior to prompt construction."""

    PUBLIC = "public"
    TEAM_INTERNAL = "team-internal"
    MAINTAINER_ONLY = "maintainer-only"


EXCLUDED_PATH_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(^|/)\.env(\.|$)", re.IGNORECASE),
    re.compile(r"(secret|credential|private[_-]?key|api[_-]?key|token)", re.IGNORECASE),
    re.compile(r"survey", re.IGNORECASE),
    re.compile(r"alumni.*(contact|phone|number)", re.IGNORECASE),
    re.compile(r"slide[_-]?51", re.IGNORECASE),
    re.compile(r"\.(pem|key|p12|pfx|sqlite|db|bag|mcap)$", re.IGNORECASE),
)

SECRET_CONTENT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("anthropic_key", re.compile(r"sk-ant-[A-Za-z0-9\-_]{16,}")),
    ("openai_or_openrouter_key", re.compile(r"sk-(?:or-v1-|proj-)?[A-Za-z0-9\-_]{20,}")),
    ("github_pat", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("langfuse_secret", re.compile(r"sk-lf-[A-Za-z0-9\-_]{16,}")),
)

PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?\d[\d\s\-]{8,14}\d)(?!\d)")


def is_path_excluded(path: str) -> tuple[bool, str | None]:
    """Return (True, reason) if a file path matches a mandatory exclusion rule."""
    normalized = PurePosixPath(path.replace("\\", "/")).as_posix()
    for pattern in EXCLUDED_PATH_PATTERNS:
        if pattern.search(normalized):
            return True, f"path matches excluded pattern: {pattern.pattern}"
    return False, None


def find_sensitive_content(text: str) -> list[str]:
    """Detect embedded API keys/secrets in text before indexing."""
    findings: list[str] = []
    for label, pattern in SECRET_CONTENT_PATTERNS:
        if pattern.search(text):
            findings.append(label)
    return findings


def can_index(tag: SensitivityTag) -> bool:
    """Return True if a source with this tag is permitted in the retrieval index."""
    return tag != SensitivityTag.EXCLUDED


def can_send_to_cloud_parser(tag: SensitivityTag) -> bool:
    """Return True only when external cloud parsers (e.g. LlamaParse) are allowed."""
    return tag == SensitivityTag.API_OK


def enforce_cloud_parser_policy(tag: SensitivityTag, source_id: str) -> None:
    """Raise PermissionError if a non-api-ok source is routed to a cloud parser."""
    if not can_send_to_cloud_parser(tag):
        raise PermissionError(
            f"Source {source_id!r} has sensitivity {tag.value!r} and cannot be sent "
            "to an external cloud parser (requires 'api-ok')."
        )
