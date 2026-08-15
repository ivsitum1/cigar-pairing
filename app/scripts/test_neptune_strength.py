#!/usr/bin/env python3
"""Cuvar citanja snage i tijela iz Neptuneova opisa.

Dvije stvari se ovdje brane:

1. REDOSLIJED. Uzorci se citaju odozgo i prvi pogodak pobjeduje, pa raspon
   ("medium to full") mora stajati prije svoje krajnje tocke ("full"). Kad je
   "full-strength" stajao prvi, "a medium-full strength puro" davalo je 5
   umjesto 4 — 194 cigare u katalogu bile su punu tocku prejake.

2. DVIJE OSI. "-bodied" govori o tijelu, "strength / strong" o snazi. Cigara
   zna biti full-bodied a medium-strength; dok se citao jedan broj, oba su
   polja dobivala istu vrijednost.

Pokreni iz app/:  python scripts/test_neptune_strength.py
"""
import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("nep", HERE / "scrape-neptune-profiles.py")
nep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nep)
parse = nep.parse_profile_from_text


class TestRangeBeatsEndpoint(unittest.TestCase):
    def test_body_range_is_not_its_endpoint(self):
        for text in (
            "a medium to full-bodied stick with deep notes of spice",
            "a medium-full bodied Nicaraguan blend",
        ):
            self.assertEqual(parse(text)["body"], 4, text)

    def test_strength_range_is_not_its_endpoint(self):
        self.assertEqual(parse("a medium-full strength Nicaraguan Puro")["strength"], 4)

    def test_mild_range_is_not_medium(self):
        self.assertEqual(parse("A mild to medium-strength cigar, creamy")["strength"], 2)
        self.assertEqual(parse("this mild to medium-bodied blend offers cedar")["body"], 2)


class TestTwoAxes(unittest.TestCase):
    def test_body_talk_does_not_claim_strength(self):
        p = parse("a full-bodied smoke with cocoa and espresso")
        self.assertEqual(p["body"], 5)
        self.assertIsNone(p["strength"], "opis o tijelu ne smije tvrditi snagu")

    def test_strength_talk_does_not_claim_body(self):
        p = parse("a mild-strength morning cigar")
        self.assertEqual(p["strength"], 2)
        self.assertIsNone(p["body"], "opis o snazi ne smije tvrditi tijelo")

    def test_both_axes_read_independently(self):
        # poznat par: gust dim, umjeren nikotin
        p = parse("a full-bodied but medium-strength Ecuadorian Habano")
        self.assertEqual(p["body"], 5)
        self.assertEqual(p["strength"], 3)

    def test_overall_only_when_no_axis_named(self):
        p = parse("a medium to full cigar from Esteli")
        self.assertEqual(p["overall"], 4)
        self.assertIsNone(p["body"])
        self.assertIsNone(p["strength"])
        # cim je os imenovana, ukupni dojam se ne puni
        self.assertIsNone(parse("a medium-bodied cigar")["overall"])


class TestRestraint(unittest.TestCase):
    def test_marketing_adjectives_claim_nothing(self):
        # "potent" i slicno Neptune lijepi i na kremaste Connecticute
        p = parse("A potent yet flavorful cigar with warm notes of cream and cedar.")
        self.assertIsNone(p["strength"])
        self.assertIsNone(p["body"])

    def test_dual_blend_lands_in_the_middle(self):
        text = (
            "One end is a mild to medium-bodied Connecticut, the other provides "
            "an immediate, bold, full-bodied intensity."
        )
        p = parse(text)
        self.assertEqual((p["strength"], p["body"]), (3, 3))

    def test_silence_stays_silent(self):
        for text in ("Handcrafted at the Joya de Nicaragua factory.", ""):
            p = parse(text)
            self.assertEqual((p["strength"], p["body"], p["overall"]), (None, None, None))


if __name__ == "__main__":
    unittest.main(verbosity=2)
