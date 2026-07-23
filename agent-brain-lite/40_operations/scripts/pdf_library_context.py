"""Shared path → domain classification for reference-library PDFs and derived notes."""

from __future__ import annotations

import hashlib
import re

# Keeps filenames under typical Windows limits when combined with vault path.
_MAX_STEM_SLUG_TOTAL_CHARS = 90


def stem_slug_for_pdf(pdf_stem: str, rel_pdf: str, *, max_total: int = _MAX_STEM_SLUG_TOTAL_CHARS) -> str:
    """
    Canonical `{slugified_stem truncated}__{sha1(rel path)[:10]}` used for books_md and pdf stubs.

    Stable per relative PDF path so re-runs and ingest stay aligned.
    """
    short_id = hashlib.sha1(rel_pdf.encode("utf-8")).hexdigest()[:10]
    suffix = f"__{short_id}"
    base = slugify(pdf_stem)
    max_base = max(1, max_total - len(suffix))
    if len(base) > max_base:
        base = base[:max_base].rstrip("_")
    return f"{base}{suffix}"


def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"\s+", "_", s)
    s = s.replace("-", "_")
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "unnamed"


def infer_library_context(rel_pdf_posix: str) -> tuple[str, str, str]:
    """
    Returns (domain_key, subgroup, books_md_subdir).

    domain_key is used for indexing; books_md_subdir is a folder under
    20_knowledge/wiki/sources/books_md/
    """
    rel = rel_pdf_posix.lower().replace("\\", "/")

    if "20_knowledge/reference_library/writing" in rel:
        return "writing", "books", "writing"

    if "20_knowledge/reference_library/opinions" in rel:
        if "editorials" in rel or "commentar" in rel:
            return "opinions", "editorials_commentaries", "opinions"
        return "opinions", "guidelines_consensus", "opinions"

    if "20_knowledge/reference_library/coding" in rel:
        return "coding", "books", "coding"

    if "20_knowledge/reference_library/statistics" in rel:
        if "/papers/" in rel:
            return "statistics", "papers", "statistics"
        if "/books/" in rel:
            return "statistics", "books", "statistics"
        return "statistics", "general", "statistics"

    if "20_knowledge/reference_library/medicine" in rel:
        if "/anesthesiology" in rel:
            return "medicine", "anesthesiology", "medicine_anesthesiology"
        if "/emergency" in rel:
            return "medicine", "emergency", "medicine_emergency"
        if "/intensive_care" in rel:
            return "medicine", "intensive_care", "medicine_intensive_care"
        if "/textbooks/" in rel:
            return "medicine", "textbooks", "medicine_general"
        return "medicine", "general", "medicine_general"

    # Inbox / other locations under workspace
    if "00_inbox/raw" in rel:
        return "inbox", "raw", "inbox_raw"

    return "general", "unsorted", "general"
