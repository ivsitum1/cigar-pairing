#!/usr/bin/env python3
"""Unit tests for the line-nomenclature helpers in taxonomy_lib.

Run from app/:  python scripts/test_taxonomy_lib.py
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from taxonomy_lib import (  # noqa: E402
    cigar_id,
    shape_canon_index,
    shape_fits_dims,
    split_bare_dimension_tail,
    title_case_line,
)


class TestBareDimensionTail(unittest.TestCase):
    def test_reads_separatorless_shop_titles(self):
        # `1502 XO Torpedo 6"1/2 * 52` → "xo 61 2 52" ("61 2" is 6 1/2)
        self.assertEqual(split_bare_dimension_tail("xo 61 2 52"), ("xo", "52 x 165mm"))
        self.assertEqual(split_bare_dimension_tail("xo 7 40"), ("xo", "40 x 178mm"))
        self.assertEqual(
            split_bare_dimension_tail("cuellar caribe 6 1 4 52"),
            ("cuellar caribe", "52 x 159mm"),
        )
        # some shops title ring first
        self.assertEqual(
            split_bare_dimension_tail("pca exclusive 50 5"), ("pca exclusive", "50 x 127mm")
        )

    def test_keeps_names_that_merely_end_in_a_number(self):
        for line in ("Project 40", "Asylum 13", "domaine 50", "AFR-75", "858"):
            self.assertIsNone(split_bare_dimension_tail(line), line)

    def test_keeps_the_model_number_before_the_dimensions(self):
        self.assertEqual(
            split_bare_dimension_tail("time capsule limited edition 770 7 70"),
            ("time capsule limited edition 770", "70 x 178mm"),
        )

    def test_refuses_implausible_runs(self):
        # 54 x 48 is neither a length in inches nor a sane pair
        self.assertIsNone(split_bare_dimension_tail("time capsule 54 48"))
        # never strips the whole name away
        self.assertIsNone(split_bare_dimension_tail("6 52"))


class TestTitleCaseLine(unittest.TestCase):
    def test_capitalises_slug_shaped_imports(self):
        self.assertEqual(title_case_line("blue amber blue maestro"), "Blue Amber Blue Maestro")
        self.assertEqual(title_case_line("xo"), "XO")
        self.assertEqual(title_case_line("pca exclusive 2025"), "PCA Exclusive 2025")
        self.assertEqual(title_case_line("serie r black no 48"), "Serie R Black No. 48")
        self.assertEqual(title_case_line("havana vi nobles"), "Havana VI Nobles")
        self.assertEqual(title_case_line("chunk shade 3xl"), "Chunk Shade 3XL")
        self.assertEqual(title_case_line("year of the horse"), "Year of the Horse")

    def test_restores_lost_punctuation(self):
        self.assertEqual(title_case_line("devil s night"), "Devil's Night")
        self.assertEqual(title_case_line("fume d amour lagunas"), "Fume d'Amour Lagunas")
        # a lone "d" before a consonant is an initial, not an elision
        self.assertEqual(title_case_line("d magnus ii caligula"), "D Magnus II Caligula")

    def test_leaves_already_spelled_lines_alone(self):
        for line in ("Aniversario 10", "ART-56 Claro", "Special Edition XO Series", ""):
            self.assertEqual(title_case_line(line), line)

    def test_is_id_neutral(self):
        """Casing must never change a cigar id — collections key on those."""
        for line in (
            "blue eyed jack s revenge",
            "fume d amour lagunas",
            "serie r black no 48",
            "xo",
        ):
            self.assertEqual(
                cigar_id("Brand", line),
                cigar_id("Brand", title_case_line(line)),
                line,
            )


class TestShapeFit(unittest.TestCase):
    def test_maps_synonyms_to_canonical_vitolas(self):
        index = shape_canon_index()
        self.assertEqual(index["salomon"], "Figurado")
        self.assertEqual(index["sixty"], "Gordo")
        self.assertEqual(index["robusto"], "Robusto")

    def test_scores_dimensions_against_the_lexicon(self):
        # 1502 XO Salomon, 7 x 58 — a Figurado, definitely not a Robusto
        self.assertIs(shape_fits_dims("Figurado", 58, 178), True)
        self.assertIs(shape_fits_dims("Robusto", 58, 178), False)
        self.assertIsNone(shape_fits_dims("Robusto", None, 178))
        self.assertIsNone(shape_fits_dims("Not A Vitola", 50, 127))


if __name__ == "__main__":
    unittest.main(verbosity=2)
