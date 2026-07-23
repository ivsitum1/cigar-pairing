"""
Hierarchical chunk policy for RAG ingest (parent-child + contextual framing).

NotebookLM Strategic RAG Chunking slice (cea806f1).
"""
from __future__ import annotations

import hashlib
import re
import uuid
from dataclasses import asdict, dataclass, field
from typing import Iterator

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
DEFAULT_CHILD_MAX_CHARS = 1800
DEFAULT_CHILD_MIN_CHARS = 200


@dataclass
class ChunkRecord:
    chunk_id: str
    parent_id: str | None
    text: str
    embed_text: str
    section_path: str
    doc_title: str
    doc_version: str
    source_type: str
    environment: str = "agent-rules"
    char_start: int = 0
    char_end: int = 0
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    def validates(self) -> list[str]:
        errors: list[str] = []
        if not self.doc_title.strip():
            errors.append("missing doc_title")
        if not self.source_type.strip():
            errors.append("missing source_type")
        if not self.doc_version.strip():
            errors.append("missing doc_version")
        if self.parent_id is not None and not self.parent_id.strip():
            errors.append("empty parent_id")
        if len(self.text.strip()) < 1:
            errors.append("empty text")
        return errors


def _stable_id(*parts: str) -> str:
    raw = "|".join(parts).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def framed_embed_text(doc_title: str, section_path: str, body: str) -> str:
    """Contextual retrieval framing: prepend location context before embed."""
    title = doc_title.strip() or "Untitled"
    path = section_path.strip() or "root"
    return f"{title} > {path}\n\n{body.strip()}"


def split_markdown_sections(
    text: str,
    *,
    doc_title: str,
    doc_version: str,
    source_type: str,
    environment: str = "agent-rules",
    child_max_chars: int = DEFAULT_CHILD_MAX_CHARS,
) -> list[ChunkRecord]:
    """Layout-aware split: sections by Markdown headings; children by size within section."""
    if not text.strip():
        return []

    sections: list[tuple[str, str, int, int]] = []
    matches = list(HEADING_RE.finditer(text))
    if not matches:
        sections.append(("root", text, 0, len(text)))
    else:
        path_counts: dict[str, int] = {}
        for i, m in enumerate(matches):
            level = len(m.group(1))
            title = m.group(2).strip()
            start = m.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            base_path = title if level <= 2 else f"h{level}/{title}"
            path_counts[base_path] = path_counts.get(base_path, 0) + 1
            path = (
                base_path
                if path_counts[base_path] == 1
                else f"{base_path}@{start}"
            )
            sections.append((path, body, start, end))

    records: list[ChunkRecord] = []
    for section_path, section_body, sec_start, sec_end in sections:
        parent_id = _stable_id(doc_title, section_path, "parent")
        parent_rec = ChunkRecord(
            chunk_id=parent_id,
            parent_id=None,
            text=section_body,
            embed_text=framed_embed_text(doc_title, section_path, section_body[:8000]),
            section_path=section_path,
            doc_title=doc_title,
            doc_version=doc_version,
            source_type=source_type,
            environment=environment,
            char_start=sec_start,
            char_end=sec_end,
            metadata={"role": "parent"},
        )
        records.append(parent_rec)

        if len(section_body) <= child_max_chars:
            child_id = _stable_id(parent_id, "child", "0")
            records.append(
                ChunkRecord(
                    chunk_id=child_id,
                    parent_id=parent_id,
                    text=section_body,
                    embed_text=framed_embed_text(doc_title, section_path, section_body),
                    section_path=section_path,
                    doc_title=doc_title,
                    doc_version=doc_version,
                    source_type=source_type,
                    environment=environment,
                    char_start=sec_start,
                    char_end=sec_end,
                    metadata={"role": "child", "child_index": 0},
                )
            )
            continue

        offset = 0
        idx = 0
        while offset < len(section_body):
            end = min(offset + child_max_chars, len(section_body))
            if end < len(section_body):
                break_at = section_body.rfind("\n\n", offset, end)
                if break_at > offset + DEFAULT_CHILD_MIN_CHARS:
                    end = break_at
            piece = section_body[offset:end].strip()
            if piece:
                child_id = _stable_id(parent_id, "child", str(idx))
                records.append(
                    ChunkRecord(
                        chunk_id=child_id,
                        parent_id=parent_id,
                        text=piece,
                        embed_text=framed_embed_text(doc_title, section_path, piece),
                        section_path=section_path,
                        doc_title=doc_title,
                        doc_version=doc_version,
                        source_type=source_type,
                        environment=environment,
                        char_start=sec_start + offset,
                        char_end=sec_start + end,
                        metadata={"role": "child", "child_index": idx},
                    )
                )
                idx += 1
            offset = end

    return records


def resolve_parent(records: list[ChunkRecord], chunk_id: str) -> ChunkRecord | None:
    by_id = {r.chunk_id: r for r in records}
    child = by_id.get(chunk_id)
    if not child or not child.parent_id:
        return child
    return by_id.get(child.parent_id)


def orphan_chunks(records: list[ChunkRecord]) -> list[ChunkRecord]:
    """Children whose parent_id is missing from the batch."""
    ids = {r.chunk_id for r in records}
    return [r for r in records if r.parent_id and r.parent_id not in ids]


def iter_valid_chunks(records: list[ChunkRecord]) -> Iterator[ChunkRecord]:
    for rec in records:
        if not rec.validates():
            yield rec
