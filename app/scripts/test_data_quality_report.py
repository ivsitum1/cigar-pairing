#!/usr/bin/env python3
"""Unit tests for the W1 slug_line_names metric in data-quality-report.py.

Run from app/:  python scripts/test_data_quality_report.py

Documents which line names are counted as slugs and which are not:
  - All-lowercase text with letters → slug  ("xo 61 2 52", "serie r no")
  - Has at least one uppercase letter → real name  ("Padrón 1926", "Asylum 13")
  - Digits / symbols only, no letters → model number / year  (858, 1926, #3)
  - Ordinal suffix only → anniversary designator  ("115th", "250th")
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parent / "data-quality-report.py"
_spec = importlib.util.spec_from_file_location("data_quality_report", _SCRIPT)
assert _spec and _spec.loader
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
junk_line = _mod.junk_line


def _c(line: str) -> dict:
    """Minimal cigar record stub with the given line name."""
    return {"line": line}


class TestJunkLineNotSlug(unittest.TestCase):
    """Lines that should NOT be counted as slugs."""

    def test_title_case_with_year(self) -> None:
        self.assertFalse(junk_line(_c("Padrón 1926")))

    def test_title_case_with_small_number(self) -> None:
        self.assertFalse(junk_line(_c("Asylum 13")))

    def test_title_case_three_digit_model(self) -> None:
        self.assertFalse(junk_line(_c("La Aurora 107")))

    def test_anniversary_phrase(self) -> None:
        self.assertFalse(junk_line(_c("10th Anniversary")))

    def test_anniversary_maduro(self) -> None:
        self.assertFalse(junk_line(_c("20th Anniversary Maduro")))

    def test_ordinal_only_250th(self) -> None:
        self.assertFalse(junk_line(_c("250th")))

    def test_ordinal_only_115th(self) -> None:
        self.assertFalse(junk_line(_c("115th")))

    def test_pure_year(self) -> None:
        self.assertFalse(junk_line(_c("1926")))

    def test_pure_small_number(self) -> None:
        self.assertFalse(junk_line(_c("13")))

    def test_three_digit_model(self) -> None:
        self.assertFalse(junk_line(_c("858")))

    def test_hash_number(self) -> None:
        self.assertFalse(junk_line(_c("#3")))

    def test_hash_large_number(self) -> None:
        self.assertFalse(junk_line(_c("#6000")))

    def test_empty_string(self) -> None:
        self.assertFalse(junk_line(_c("")))

    def test_missing_key(self) -> None:
        self.assertFalse(junk_line({}))

    def test_title_case_alphanumeric(self) -> None:
        self.assertFalse(junk_line(_c("Serie R No. 7")))

    def test_all_caps_abbreviation(self) -> None:
        self.assertFalse(junk_line(_c("AFR-75")))

    def test_mixed_case_anniversary(self) -> None:
        self.assertFalse(junk_line(_c("Improvisation 30 Year LE")))


class TestJunkLineIsSlug(unittest.TestCase):
    """Lines that SHOULD be counted as slugs."""

    def test_dimension_tail_slug(self) -> None:
        self.assertTrue(junk_line(_c("xo 61 2 52")))

    def test_all_lower_with_letters(self) -> None:
        self.assertTrue(junk_line(_c("serie r no")))

    def test_all_lower_no_digits(self) -> None:
        self.assertTrue(junk_line(_c("pca exclusive")))

    def test_lower_with_digits_not_ordinal(self) -> None:
        # Not an ordinal suffix — "no" at end is text, not "th/st/nd/rd"
        self.assertTrue(junk_line(_c("xo no")))


if __name__ == "__main__":
    unittest.main()
