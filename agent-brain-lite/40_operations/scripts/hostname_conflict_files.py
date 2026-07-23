#!/usr/bin/env python3
"""Detect sync/OneDrive hostname-suffixed duplicate filenames (generic, no machine brands)."""

from __future__ import annotations

import re
from pathlib import Path

# e.g. README-HOST-SEGMENT-SEGMENT.md or file-DESKTOP-ABC123.pdf
_HOSTNAME_SUFFIX_RE = re.compile(
    r"^(?P<base>.+?)(?P<suffix>-[A-Z][A-Za-z0-9]+(?:-[A-Za-z0-9]+)+)(?P<ext>\.[^.]+)$"
)

# Doc naming tokens that look like multi-segment suffixes but are not hostnames
_DOC_SUFFIX_TOKENS = frozenset(
    {"NOTE", "SCHEMA", "AUTO", "COPY", "BACKUP", "OLD", "NEW", "DRAFT", "FINAL", "EXTENDED", "TEMPLATE"}
)


def _looks_like_hostname_suffix(suffix: str) -> bool:
    """Heuristic: sync conflicts embed hostnames or model ids, not doc vocabulary."""
    if "-DESKTOP-" in suffix or suffix.upper().startswith("-DESKTOP"):
        return True
    parts = [p for p in suffix.split("-") if p]
    if not parts:
        return False
    if all(p.upper() in _DOC_SUFFIX_TOKENS for p in parts):
        return False
    if any(re.search(r"\d", p) for p in parts):
        return True
    if any(len(p) >= 5 and p.isupper() and p.upper() not in _DOC_SUFFIX_TOKENS for p in parts):
        return True
    if len(parts) >= 2 and all(p and p[0].isupper() for p in parts):
        if all(p.upper() in _DOC_SUFFIX_TOKENS or len(p) <= 5 for p in parts):
            return False
        return True
    return False


def is_hostname_conflict_filename(name: str) -> bool:
    """True if filename looks like a sync conflict copy (canonical + hostname suffix)."""
    if "-DESKTOP-" in name:
        return True
    m = _HOSTNAME_SUFFIX_RE.match(name)
    if not m:
        return False
    suffix = m.group("suffix")
    if re.match(r"^-[vV]?\d", suffix):
        return False
    if len(suffix) < 8:
        return False
    return _looks_like_hostname_suffix(suffix)


def canonical_name_for_conflict(name: str) -> str | None:
    """Derive canonical filename from a conflict copy name."""
    if "-DESKTOP-" in name:
        idx = name.index("-DESKTOP-")
        return name[:idx] + name[name.rfind(".") :] if "." in name[idx:] else name[:idx]
    m = _HOSTNAME_SUFFIX_RE.match(name)
    if not m:
        return None
    return m.group("base") + m.group("ext")


def is_hostname_conflict_path(path: Path) -> bool:
    return path.is_file() and is_hostname_conflict_filename(path.name)
