"""Tests for automatic context-saving policy."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from books_rag.config import make_test_config
from books_rag.context_policy import resolve_context_policy


def test_auto_mode_uses_summary_without_ollama(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BOOKS_RAG_OLLAMA_ENABLED", raising=False)
    monkeypatch.setenv("BOOKS_RAG_CONTEXT_MODE", "auto")
    monkeypatch.setattr(
        "books_rag.context_policy.ollama_available",
        lambda _cfg: False,
    )
    cfg = make_test_config(Path("."), context_mode="auto", ollama_enabled=True)
    policy = resolve_context_policy(cfg)
    assert policy.mode == "auto"
    assert policy.use_summary is True
    assert policy.use_ollama is False
    assert policy.mcp_default_mode == "summary"


def test_off_mode_raw_chunks(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOOKS_RAG_CONTEXT_MODE", "off")
    cfg = make_test_config(Path("."), context_mode="off")
    policy = resolve_context_policy(cfg)
    assert policy.use_summary is False
    assert policy.mcp_default_mode == "chunks"


def test_on_mode_uses_ollama_when_reachable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOOKS_RAG_CONTEXT_MODE", "on")
    monkeypatch.setattr(
        "books_rag.context_policy.ollama_available",
        lambda _cfg: True,
    )
    cfg = make_test_config(Path("."), context_mode="on", ollama_enabled=True)
    policy = resolve_context_policy(cfg)
    assert policy.use_ollama is True
