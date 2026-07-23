"""Resolve `.cursor` helper scripts (canonical `.cursor/scripts`, legacy `.cursor/40_operations/scripts`)."""
from __future__ import annotations

from pathlib import Path


def resolve_cursor_script(workspace: Path, filename: str) -> Path | None:
    """Return first existing path to *filename* under known `.cursor` layouts."""
    candidates = (
        workspace / ".cursor" / "40_operations" / "scripts" / filename,
        workspace / ".cursor" / "scripts" / filename,
    )
    for p in candidates:
        if p.is_file():
            return p
    return None
