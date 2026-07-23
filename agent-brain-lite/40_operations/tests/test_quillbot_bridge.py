"""Tests for quillbot_bridge helpers (no Playwright required)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "40_operations" / "scripts"))

import quillbot_bridge as qb  # noqa: E402


def test_word_count() -> None:
    assert qb._word_count("one two three four") == 4


def test_read_input_text_from_string() -> None:
    assert qb._read_input_text(text="hello world", file_path=None) == "hello world"


def test_read_input_text_from_file(tmp_path: Path) -> None:
    f = tmp_path / "sample.txt"
    f.write_text("alpha beta", encoding="utf-8")
    assert qb._read_input_text(text=None, file_path=f) == "alpha beta"
