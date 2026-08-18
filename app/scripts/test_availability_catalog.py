#!/usr/bin/env python3
"""Tests for collecting product URLs and writing inStock back onto records.

Run from app/:  python scripts/test_availability_catalog.py
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from availability_catalog import (  # noqa: E402
    apply_stock_to_cigar,
    apply_stock_to_drink,
    collect_cigar_urls,
    collect_drink_urls,
    is_listing_url,
    is_pingable_url,
    normalize_url,
    wants_stealth,
)


HUMIDOR = "https://humidor.hr/hr/product/padron-1964-anniversary-pricipal"
FAMOUS = "https://www.famous-smoke.com/padron-1964-anniversary-pricipal-cigars"
HOLTS_LINE = "https://www.holts.com/cigars/all-cigar-brands/padron.html"
FAMOUS_BRAND = "https://www.famous-smoke.com/brand/padron"
SEARCH = "https://humidor.hr/?s=padron&post_type=product"
ALLEZ = "https://allez.hr/shop/svi-proizvodi/hampden-hlcf-classic-estate-pure-single-jamaican-rum-60-vol-07l-u-poklon-kutiji"
WINE_SEARCHER = "https://www.wine-searcher.com/find/hampden"


class TestUrlHelpers(unittest.TestCase):
    def test_normalize_strips_trailing_slash_and_fragment(self):
        self.assertEqual(
            normalize_url("https://humidor.hr/x/#reviews"),
            "https://humidor.hr/x",
        )
        self.assertEqual(normalize_url("https://humidor.hr/x/"), "https://humidor.hr/x")

    def test_listing_urls(self):
        self.assertTrue(is_listing_url(HOLTS_LINE))
        self.assertTrue(is_listing_url(FAMOUS_BRAND))
        self.assertFalse(is_listing_url(HUMIDOR))
        self.assertFalse(is_listing_url(FAMOUS))

    def test_search_and_ref_are_not_pingable(self):
        self.assertFalse(is_pingable_url(SEARCH))
        self.assertFalse(is_pingable_url(WINE_SEARCHER))
        self.assertFalse(is_pingable_url(HOLTS_LINE))
        self.assertTrue(is_pingable_url(HUMIDOR))
        self.assertTrue(is_pingable_url(ALLEZ))

    def test_famous_wants_stealth(self):
        self.assertTrue(wants_stealth(FAMOUS))
        self.assertFalse(wants_stealth(HUMIDOR))
        self.assertFalse(wants_stealth(ALLEZ))


class TestCollectCigarUrls(unittest.TestCase):
    def test_collects_product_urls_skips_listings(self):
        cigar = {
            "id": "cig-x",
            "priceUrl": SEARCH,
            "regionLinks": {
                "EU": {"shop": "Holt's", "url": HOLTS_LINE},
                "USA": {"shop": "Famous Smoke", "url": FAMOUS},
            },
            "vitolas": [
                {
                    "name": "Robusto",
                    "url": HUMIDOR,
                    "regionLinks": {
                        "USA": {"shop": "Famous Smoke", "url": FAMOUS + "/"},
                    },
                }
            ],
        }
        urls = collect_cigar_urls(cigar)
        self.assertEqual(sorted(urls), sorted([HUMIDOR, FAMOUS]))

    def test_dedupes_normalized_urls(self):
        cigar = {
            "vitolas": [
                {"url": HUMIDOR + "/"},
                {"url": HUMIDOR},
            ]
        }
        self.assertEqual(collect_cigar_urls(cigar), [HUMIDOR])


class TestApplyCigarStock(unittest.TestCase):
    def test_writes_in_stock_on_matching_vitola_and_region_link(self):
        cigar = {
            "regionLinks": {"USA": {"shop": "Famous Smoke", "url": FAMOUS, "priceEUR": 12}},
            "vitolas": [{"name": "Robusto", "url": HUMIDOR, "priceEUR": 9.5}],
        }
        n = apply_stock_to_cigar(cigar, HUMIDOR, True, "2026-08-17")
        self.assertEqual(n, 1)
        self.assertIs(cigar["vitolas"][0]["inStock"], True)
        self.assertEqual(cigar["vitolas"][0]["stockFetchedAt"], "2026-08-17")
        self.assertNotIn("inStock", cigar["regionLinks"]["USA"])

        n2 = apply_stock_to_cigar(cigar, FAMOUS + "/", False, "2026-08-17")
        self.assertEqual(n2, 1)
        self.assertIs(cigar["regionLinks"]["USA"]["inStock"], False)
        self.assertEqual(cigar["regionLinks"]["USA"]["priceEUR"], 12)

    def test_unknown_url_writes_nothing(self):
        cigar = {"vitolas": [{"url": HUMIDOR}]}
        self.assertEqual(apply_stock_to_cigar(cigar, FAMOUS, True, "2026-08-17"), 0)
        self.assertNotIn("inStock", cigar["vitolas"][0])


class TestDrinkUrls(unittest.TestCase):
    def test_collects_price_url_only_when_pingable(self):
        self.assertEqual(collect_drink_urls({"priceUrl": ALLEZ}), [ALLEZ])
        self.assertEqual(collect_drink_urls({"priceUrl": WINE_SEARCHER}), [])
        self.assertEqual(collect_drink_urls({"priceUrl": None, "shopHR": "allez.hr"}), [])

    def test_apply_stock_to_drink(self):
        drink = {"priceUrl": ALLEZ, "shopHR": "allez.hr"}
        self.assertEqual(apply_stock_to_drink(drink, ALLEZ, False, "2026-08-17"), 1)
        self.assertIs(drink["inStock"], False)
        self.assertEqual(drink["stockFetchedAt"], "2026-08-17")
        other = {"priceUrl": ALLEZ}
        self.assertEqual(apply_stock_to_drink(other, HUMIDOR, True, "2026-08-17"), 0)


if __name__ == "__main__":
    unittest.main()
