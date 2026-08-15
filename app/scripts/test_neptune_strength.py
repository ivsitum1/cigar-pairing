#!/usr/bin/env python3
"""Cuvar redoslijeda uzoraka za snagu iz Neptuneova opisa.

Uzorci se citaju odozgo i prvi pogodak pobjeduje, pa je redoslijed dio
znacenja: raspon ("medium to full") mora stajati prije svoje krajnje tocke
("full"). Kad je "full-strength" stajao prvi, "a medium-full strength puro"
je davalo 5 umjesto 4 — 209 cigara u katalogu ocijenjeno punu tocku
prejakima, a s njima i tijelo (merge-neptune-profiles.py tijelo prepisuje
snagom). Ovaj test lovi upravo tu regresiju.

Pokreni iz app/:  python scripts/test_neptune_strength.py
"""
import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("nep", HERE / "scrape-neptune-profiles.py")
nep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nep)
parse = nep._parse_strength_from_text


class TestStrengthFromText(unittest.TestCase):
    def test_range_beats_its_endpoint(self):
        """Raspon se cita kao raspon, kako god bio pisan."""
        for text in (
            "a medium-full strength Nicaraguan Puro",
            "a medium to full-bodied stick with deep notes of spice",
            "this cigar is full to medium in strength",
        ):
            self.assertEqual(parse(text), 4, text)

    def test_mild_range_is_not_medium(self):
        for text in (
            "A mild to medium-strength cigar with a smooth creamy profile",
            "this mild to medium-bodied blend offers cedar and cream",
        ):
            self.assertEqual(parse(text), 2, text)

    def test_plain_endpoints_still_read(self):
        self.assertEqual(parse("a full-bodied powerhouse"), 5)
        self.assertEqual(parse("a medium-bodied everyday smoke"), 3)
        self.assertEqual(parse("a mild-strength morning cigar"), 2)
        self.assertEqual(parse("a very mild breakfast cigar"), 1)

    def test_dual_blend_lands_in_the_middle(self):
        """Kutija s dva blenda opisuje oba kraja — sredina, ne redoslijed."""
        text = (
            "One end is a mild to medium-bodied Connecticut, the other provides "
            "an immediate, bold, full-bodied intensity."
        )
        self.assertEqual(parse(text), 3)

    def test_silence_stays_silent(self):
        self.assertIsNone(parse("Handcrafted at the Joya de Nicaragua factory."))
        self.assertIsNone(parse(""))


if __name__ == "__main__":
    unittest.main(verbosity=2)
