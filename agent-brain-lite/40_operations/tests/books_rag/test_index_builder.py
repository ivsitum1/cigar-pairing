"""Tests for micro-batch index builder."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from books_rag.config import BooksRagConfig, make_test_config
from books_rag.index_builder import _load_manifest, build_index


def _cfg(tmp_path: Path) -> BooksRagConfig:
    books = tmp_path / "books_md"
    books.mkdir(parents=True)
    return make_test_config(tmp_path, books_md_dir=books)


SAMPLE = """---
title: "T"
domain: medicine
---
## Page 1
""" + ("regional anesthesia. " * 80) + "\n"


def test_load_manifest_strips_chunk_ids(tmp_path: Path) -> None:
    path = tmp_path / "m.json"
    path.write_text(
        json.dumps({"files": {}, "chunk_ids_by_file": {"a": ["id1"]}}),
        encoding="utf-8",
    )
    data = _load_manifest(path)
    assert "chunk_ids_by_file" not in data


def test_micro_flush_and_slim_manifest(monkeypatch, tmp_path: Path) -> None:
    cfg = _cfg(tmp_path)
    (cfg.books_md_dir / "small.md").write_text(SAMPLE, encoding="utf-8")

    store = MagicMock()
    store.count.return_value = 5
    store.upsert_chunks.return_value = 5

    embedder = MagicMock()
    embedder.embed_passages.return_value = [[0.1], [0.2], [0.3], [0.4], [0.5]]

    monkeypatch.setattr("books_rag.index_builder.BooksVectorStore", lambda *a, **k: store)
    monkeypatch.setattr("books_rag.index_builder.BooksEmbedder", lambda *a, **k: embedder)

    stats = build_index(cfg, force=True, embed_buffer_size=12, use_lock=False)
    assert stats["files_updated"] >= 1
    assert stats["chunks_added"] >= 1

    manifest = json.loads(cfg.manifest_path.read_text(encoding="utf-8"))
    assert "chunk_ids_by_file" not in manifest
    assert "files" in manifest
    store.delete_by_source_md.assert_not_called()

    progress = json.loads(cfg.progress_path.read_text(encoding="utf-8"))
    assert progress.get("chunks_total", 0) >= 1


def test_delete_by_source_on_reindex(monkeypatch, tmp_path: Path) -> None:
    cfg = _cfg(tmp_path)
    md = cfg.books_md_dir / "small.md"
    md.write_text(SAMPLE, encoding="utf-8")

    store = MagicMock()
    store.count.return_value = 3
    store.upsert_chunks.return_value = 3
    embedder = MagicMock()
    embedder.embed_passages.return_value = [[0.1], [0.2], [0.3]]

    monkeypatch.setattr("books_rag.index_builder.BooksVectorStore", lambda *a, **k: store)
    monkeypatch.setattr("books_rag.index_builder.BooksEmbedder", lambda *a, **k: embedder)

    build_index(cfg, force=True, use_lock=False)
    md.write_text(SAMPLE + "\nextra line.\n", encoding="utf-8")
    build_index(cfg, force=False, use_lock=False)
    assert store.delete_by_source_md.called
