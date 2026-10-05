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


class ObjectSlice(unittest.TestCase):
    """patch_block must only ever touch the drink it was asked to patch."""

    TEXT = (
        "[\n"
        "  {\n"
        '    "id": "rum-23",\n'
        '    "notes": {"hr": "a } in \\"text\\" {"},\n'
        '    "priceUrl": "https://humidor.hr/hr/proizvod/m23/",\n'
        '    "priceEUR": {\n      "min": 50.0,\n      "max": 50.0\n    },\n'
        '    "shopHR": "humidor.hr"\n'
        "  },\n"
        "  {\n"
        '    "id": "rum-30",\n'
        '    "priceUrl": null,\n'
        '    "priceEUR": {\n      "min": 28.0,\n      "max": 35.0\n    },\n'
        '    "priceApprox": true,\n'
        '    "shopHR": null\n'
        "  }\n"
        "]\n"
    )

    def test_slice_stops_at_own_object(self) -> None:
        start, end = mdl.object_slice(self.TEXT, "rum-23")
        block = self.TEXT[start:end]
        self.assertTrue(block.startswith("{") and block.endswith("}"))
        self.assertNotIn("rum-30", block)

    def test_patch_leaves_next_drink_alone(self) -> None:
        import json as _json

        start, end = mdl.object_slice(self.TEXT, "rum-23")
        after = {
            "priceUrl": "https://humidor.hr/hr/proizvod/m23/",
            "shopHR": "humidor.hr",
            "priceEUR": {"min": 48.0, "max": 48.0},
        }
        text = self.TEXT[:start] + mdl.patch_block(self.TEXT[start:end], after) + self.TEXT[end:]
        rows = {d["id"]: d for d in _json.loads(text)}
        self.assertEqual(rows["rum-23"]["priceEUR"], {"min": 48.0, "max": 48.0})
        self.assertIsNone(rows["rum-30"]["priceUrl"])
        self.assertIsNone(rows["rum-30"]["shopHR"])
        self.assertIs(rows["rum-30"]["priceApprox"], True)

    def test_patch_replaces_null_price_eur(self) -> None:
        import json as _json

        text = (
            "[\n"
            "  {\n"
            '    "id": "wh-null-price",\n'
            '    "priceUrl": "https://allez.hr/shop/product/x",\n'
            '    "priceEUR": null,\n'
            '    "shopHR": "allez.hr"\n'
            "  }\n"
            "]\n"
        )
        start, end = mdl.object_slice(text, "wh-null-price")
        after = {
            "priceUrl": "https://allez.hr/shop/product/x",
            "shopHR": "allez.hr",
            "priceEUR": {"min": 99.0, "max": 99.0},
        }
        out = text[:start] + mdl.patch_block(text[start:end], after) + text[end:]
        row = _json.loads(out)[0]
        self.assertEqual(row["priceEUR"], {"min": 99.0, "max": 99.0})
        self.assertEqual(row["priceUrl"], after["priceUrl"])

    def test_propose_update_ignores_zero_price(self) -> None:
        drink = {
            "id": "br-x",
            "priceUrl": "https://allez.hr/shop/product/x",
            "priceEUR": {"min": 170.0, "max": 170.0},
            "shopHR": "allez.hr",
        }
        after = mdl.propose_update(
            drink,
            {
                "url": "https://allez.hr/shop/product/x",
                "price_eur": 0.0,
                "shop": "allez",
                "shopLabel": "allez.hr",
            },
            score=1.0,
        )
        self.assertIsNone(after)


if __name__ == "__main__":
    unittest.main()
