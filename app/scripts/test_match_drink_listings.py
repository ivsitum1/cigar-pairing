# -*- coding: utf-8 -*-
"""Unit tests for drink listing match guards (age + extra expression words)."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "mdl",
    Path(__file__).resolve().parent / "match-drink-listings.py",
)
mdl = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(mdl)


class AgeAndExtras(unittest.TestCase):
    def test_mint_id_unique(self) -> None:
        used = {"rum-plantacion-xo"}
        a = mdl.mint_drink_id("rum", "Plantation XO", used)
        used.add(a)
        b = mdl.mint_drink_id("rum", "Plantation XO", used)
        self.assertNotEqual(a, b)
        self.assertTrue(a.startswith("rum-"))

    def test_resolve_category_from_name(self) -> None:
        self.assertEqual(
            mdl.resolve_category({"name": "Plantation XO Rum", "category": "all"}),
            "rum",
        )
        self.assertEqual(mdl.resolve_category({"name": "Something", "category": "gin"}), "gin")
        self.assertIsNone(mdl.resolve_category({"name": "Appleton Estate 8", "category": "all"}))

    def test_keeps_age_10(self) -> None:
        self.assertIn("10", mdl.tokens("Lagavulin 10YO 0,70 L"))
        self.assertEqual(mdl.meaningful_years("Lagavulin 10YO 0,70 L"), {"10"})

    def test_volume_is_not_age(self) -> None:
        self.assertNotIn("70", mdl.tokens("Green Spot 0,70 L"))
        self.assertEqual(mdl.meaningful_years("Green Spot 0,70 L"), set())

    def test_rejects_wrong_age(self) -> None:
        self.assertFalse(
            mdl.years_compatible(
                mdl.meaningful_years("Lagavulin 10YO"),
                mdl.meaningful_years("Lagavulin 8"),
            )
        )

    def test_rejects_aged_vs_nas(self) -> None:
        self.assertFalse(
            mdl.years_compatible(
                mdl.meaningful_years("Ardbeg AN OA"),
                mdl.meaningful_years("Ardbeg 10"),
            )
        )

    def test_rejects_other_expression(self) -> None:
        self.assertFalse(
            mdl.listing_extras_ok(
                mdl.tokens("Woodford Reserve Rye"),
                mdl.tokens("Woodford Reserve"),
            )
        )
        self.assertFalse(
            mdl.listing_extras_ok(
                mdl.tokens("Nikka Coffey Malt"),
                mdl.tokens("Nikka Coffey Grain"),
            )
        )
        self.assertFalse(
            mdl.listing_extras_ok(
                mdl.tokens("Johnnie Walker Blue Label"),
                mdl.tokens("Johnnie Walker Blue Label Elusive Umami"),
            )
        )
        cleaned = mdl.clean_display_name(
            "A.H. Riise X.O. Reserve Port Cask Rum 45% Vol. 0,7l u poklon kutiji"
        )
        self.assertTrue(
            mdl.listing_extras_ok(mdl.tokens(cleaned), mdl.tokens("A.H. Riise XO Reserve Port Cask"))
        )

    def test_weak_url_does_not_treat_ecuga_product_as_gap(self) -> None:
        self.assertFalse(
            mdl.is_weak_price_url(
                "https://ecuga.com/katalog/whisky/skotski-blended-whisky/johnnie-walker-black-label"
            )
        )
        self.assertTrue(mdl.is_weak_price_url("https://ecuga.com/katalog/whisky"))
        self.assertTrue(mdl.is_weak_price_url(None))
    def test_allows_packaging_words(self) -> None:
        self.assertTrue(
            mdl.listing_extras_ok(
                mdl.tokens("Kavalan Concertmaster Port Cask Finish"),
                mdl.tokens("Kavalan Concertmaster"),
            )
        )
        self.assertTrue(
            mdl.listing_extras_ok(
                mdl.tokens("Brugal 1888 Gran Reserva Familiar GIFT BOX"),
                mdl.tokens("Brugal 1888"),
            )
        )


if __name__ == "__main__":
    unittest.main()
