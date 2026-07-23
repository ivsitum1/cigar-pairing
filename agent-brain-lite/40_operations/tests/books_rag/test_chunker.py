"""Tests for books_rag chunker."""
from __future__ import annotations

from pathlib import Path

from books_rag.chunker import _parse_frontmatter, _split_text, iter_book_chunks


SAMPLE_MD = """---
title: "Test Book"
source_pdf: 20_knowledge/reference_library/medicine/test.pdf
domain: medicine
subgroup: textbooks
pages: 2
extracted_utc: 2026-05-19
content_note: full_text_extract_py_pdf2
---

## Agent and graph hubs

- [[20_knowledge/wiki/index]]

## Page 1

First page about regional anesthesia.

## Page 2

Second page about ultrasound guidance.
"""


def test_parse_frontmatter(tmp_path: Path) -> None:
    f = tmp_path / "medicine" / "sample.md"
    f.parent.mkdir(parents=True)
    f.write_text(SAMPLE_MD, encoding="utf-8")
    meta, body = _parse_frontmatter(f.read_text(encoding="utf-8"))
    assert meta["domain"] == "medicine"
    assert meta["title"] == "Test Book"
    assert "regional anesthesia" in body


def test_split_text_overlap() -> None:
    text = "word " * 2000
    parts = _split_text(text, chunk_size=500, overlap=50)
    assert len(parts) > 1
    assert all(len(p) <= 520 for p in parts)


def test_smaller_chunk_size_yields_more_parts() -> None:
    text = "sentence. " * 400
    large = _split_text(text, chunk_size=2400, overlap=320)
    small = _split_text(text, chunk_size=900, overlap=120)
    assert len(small) > len(large)


def test_iter_book_chunks(tmp_path: Path) -> None:
    books_dir = tmp_path / "books_md"
    sub = books_dir / "medicine"
    sub.mkdir(parents=True)
    (sub / "sample.md").write_text(SAMPLE_MD, encoding="utf-8")
    chunks = list(
        iter_book_chunks(books_dir, chunk_size_chars=400, chunk_overlap_chars=50)
    )
    assert len(chunks) >= 1
    assert chunks[0].domain == "medicine"
    assert "regional" in chunks[0].text.lower()
