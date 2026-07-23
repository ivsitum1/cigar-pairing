"""Tests for context_compress MVP."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "40_operations" / "python"))

from brain_assist.context_compress import compress_context  # noqa: E402


def test_compress_noop_short() -> None:
    text = "hello world"
    r = compress_context(text)
    assert r["applied"] is False
    assert r["text"] == text


def test_compress_dedupe_and_truncate() -> None:
    block = "line a\nline b\nline c\n"
    text = block * 200
    r = compress_context(text, max_chars=3000)
    assert r["compressed_chars"] <= 3000
    assert r["applied"] is True
