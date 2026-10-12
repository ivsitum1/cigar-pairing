# -*- coding: utf-8 -*-
"""Offline tests for report-new-shop-bottles.py and scan failure handling."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


rep = _load("rep", "report-new-shop-bottles.py")
sg = _load("sg_fail", "scan-drink-shop-gaps.py")


def _row(name, shop, url, price, tier="D", cat="rum", new=True):
    return {
        "name": name,
        "shop": shop,
        "shopLabel": shop,
        "url": url,
        "price_eur": price,
        "tier": tier,
        "suggestedCategory": cat,
        "newSinceLastRun": new,
    }


class Report(unittest.TestCase):
    def test_same_bottle_across_shops_collapses(self) -> None:
        rows = [
            _row("Hampden 8 Y.O. 0,7 L", "allez.hr", "https://allez.hr/a", 55.0),
            _row("HAMPDEN 8 y.o. 0.7l", "ecuga.com", "https://ecuga.com/proizvod/h8", 52.9),
        ]
        groups = rep.group_bottles(rows)
        self.assertEqual(len(groups), 1)
        self.assertEqual([o["shop"] for o in groups[0]["offers"]], ["ecuga.com", "allez.hr"])

    def test_render_lists_tier_d_and_failed_shops(self) -> None:
        md = rep.render(
            {
                "generatedAt": "2026-10-01T05:00:00Z",
                "shops": ["allez", "ecuga"],
                "hadPreviousSnapshot": True,
                "failedShops": {"tipsy": "0 listings"},
                "items": [
                    _row("Worthy Park 109", "ecuga.com", "https://ecuga.com/proizvod/wp", 49.9),
                    _row("Foursquare 2009", "allez.hr", "https://allez.hr/f", 80.0, tier="C", new=False),
                ],
            }
        )
        self.assertIn("### Rum (1, od toga 1 novo od prošlog scana)", md)
        self.assertIn("🆕 Worthy Park 109", md)
        self.assertIn("[ecuga.com](https://ecuga.com/proizvod/wp) 49,90 €", md)
        self.assertIn("`tipsy`: 0 listings", md)
        self.assertIn("Foursquare 2009", md)

    def test_first_scan_has_no_new_marks(self) -> None:
        md = rep.render(
            {
                "hadPreviousSnapshot": False,
                "items": [_row("Worthy Park 109", "ecuga.com", "https://ecuga.com/proizvod/wp", 49.9)],
            }
        )
        self.assertNotIn("🆕", md)
        self.assertIn("### Rum (1)", md)


class ScanFailures(unittest.TestCase):
    def test_failing_shop_is_recorded_not_raised(self) -> None:
        def fake(shop, _category):
            if shop == "tipsy":
                raise TimeoutError("timed out")
            if shop == "miva":
                return []
            return [{"shop": shop, "url": f"https://{shop}/x", "name": "X Y"}]

        orig = sg._scrape_one
        sg._scrape_one = fake
        try:
            failed: dict[str, str] = {}
            items = sg.scrape_shops(["allez", "tipsy", "miva", "ecuga"], None, failed)
        finally:
            sg._scrape_one = orig
        self.assertEqual([i["shop"] for i in items], ["allez", "ecuga"])
        self.assertEqual(set(failed), {"tipsy", "miva"})
        self.assertIn("TimeoutError", failed["tipsy"])

    def test_ecuga_in_default_shops(self) -> None:
        self.assertIn("ecuga", sg.ALL_SHOPS)
        self.assertEqual(sg.SHOP_LABEL["ecuga"], "ecuga.com")


if __name__ == "__main__":
    unittest.main()
