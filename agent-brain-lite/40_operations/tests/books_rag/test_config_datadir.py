"""Tests for books_rag config data dir override."""
from __future__ import annotations

import sys
from pathlib import Path

from books_rag.config import WINDOWS_DEFAULT_DATA_DIR, _resolve_data_dir, load_config


def test_resolve_data_dir_default(tmp_path, monkeypatch):
    monkeypatch.delenv("BOOKS_RAG_DATA_DIR", raising=False)
    if sys.platform == "win32":
        assert _resolve_data_dir(tmp_path) == WINDOWS_DEFAULT_DATA_DIR
    else:
        assert _resolve_data_dir(tmp_path) == tmp_path / "data" / "books_rag"


def test_resolve_data_dir_env_override(tmp_path, monkeypatch):
    custom = tmp_path / "custom_rag"
    monkeypatch.setenv("BOOKS_RAG_DATA_DIR", str(custom))
    assert _resolve_data_dir(tmp_path) == custom.resolve()


def test_load_config_has_compute_device(tmp_path, monkeypatch):
    monkeypatch.delenv("BOOKS_RAG_DATA_DIR", raising=False)
    monkeypatch.setenv("AGENT_COMPUTE_DEVICE", "cpu")
    monkeypatch.setenv("BOOKS_RAG_DEVICE", "cpu")
    cfg = load_config(tmp_path)
    assert cfg.compute_device == "cpu"
    assert "compute_device" in cfg.__dataclass_fields__
