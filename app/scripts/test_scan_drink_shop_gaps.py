# -*- coding: utf-8 -*-
"""Unit tests for scan-drink-shop-gaps helpers (offline)."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "sg",
    Path(__file__).resolve().parent / "scan-drink-shop-gaps.py",
)
sg = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(sg)


class GapHelpers(unittest.TestCase):
    def test_normalize_url(self) -> None:
        self.assertEqual(
            sg.normalize_url("https://www.Allez.hr/shop/x/?utm=1#frag"),
            "https://allez.hr/shop/x",
        )

    def test_skip_mini(self) -> None:
        self.assertEqual(
            sg.should_skip_listing({"name": "Sample set 5 x 20 ml rum"}),
            "mini/sample",
        )

    def test_skip_advent(self) -> None:
        self.assertEqual(
            sg.should_skip_listing({"name": "Rum Advent Calendar 2026"}),
            "packaging/set",
        )

    def test_diff_new_urls(self) -> None:
        cur = [{"url": "https://allez.hr/a"}, {"url": "https://allez.hr/b"}]
        prev = {"urls": ["https://allez.hr/a"]}
        self.assertEqual(sg.diff_new_urls(cur, prev), {"https://allez.hr/b"})

    def test_suggested_category_rum(self) -> None:
        self.assertEqual(
            sg.suggested_category(
                {"category": "rum", "name": "Hampden 8", "url": "https://allez.hr/shop/rum4/x"}
            ),
            "rum",
        )

    def test_canonical_raw_path(self) -> None:
        self.assertEqual(sg.RAW_JSON.name, "drink_shop_listings_raw.json")

    def test_load_catalog_reads_price_url(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            data = Path(td)
            drinks = [
                {
                    "id": "rum-test",
                    "name": "Hampden Estate 8",
                    "priceUrl": "https://allez.hr/shop/svi-proizvodi/hampden-8",
                }
            ]
            (data / "rums.json").write_text(json.dumps(drinks), encoding="utf-8")
            orig = sg.DATA
            try:
                sg.DATA = data
                urls, by_url, indexed = sg.load_catalog()
            finally:
                sg.DATA = orig
            self.assertIn("https://allez.hr/shop/svi-proizvodi/hampden-8", urls)
            self.assertEqual(len(indexed), 1)
            self.assertIn("https://allez.hr/shop/svi-proizvodi/hampden-8", by_url)

    def test_classify_tier_a(self) -> None:
        known = {"https://allez.hr/shop/x"}
        by_url = {
            "https://allez.hr/shop/x": (
                "rums.json",
                {"id": "rum-x", "name": "X"},
            )
        }
        row = sg.classify_listing(
            {"name": "Anything", "url": "https://allez.hr/shop/x", "category": "rum"},
            known_urls=known,
            by_url=by_url,
            indexed=[],
            new_urls=set(),
            min_score=0.88,
        )
        self.assertEqual(row["tier"], "A")
        self.assertEqual(row["matchId"], "rum-x")


if __name__ == "__main__":
    unittest.main()
