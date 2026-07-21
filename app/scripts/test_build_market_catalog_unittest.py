#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parent / "build-market-catalog.py"
_SPEC = importlib.util.spec_from_file_location("build_market_catalog", _SCRIPT)
assert _SPEC and _SPEC.loader
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)
build_sources = _MOD.build_sources
offer_from_raw = _MOD.offer_from_raw


class BuildSourcesTests(unittest.TestCase):
    def test_shop_offer_is_verified_with_url(self) -> None:
        offers = [
            {
                "sourceShopId": "humidor_hr",
                "region": "HR",
                "name": "Test Toro",
                "url": "https://humidor.hr/hr/proizvod/test-toro/",
                "amount": 12.0,
                "details": {"wrapper": "Habano", "binder": "Nicaragua", "filler": "Nicaragua"},
                "detailsSource": {
                    "url": "https://humidor.hr/hr/proizvod/test-toro/",
                    "extractedFrom": "humidor-product-specs",
                    "extractedAt": "2026-07-21T00:00:00Z",
                },
                "scrapedAt": "2026-07-21T00:00:00Z",
            }
        ]
        sources, urls, verified = build_sources(offers=offers, in_catalog=False)
        self.assertTrue(verified)
        self.assertEqual(urls, ["https://humidor.hr/hr/proizvod/test-toro/"])
        self.assertEqual(sources[0]["type"], "shop-scrape")
        self.assertTrue(sources[0]["verified"])
        self.assertIn("details.wrapper", sources[0]["provides"])

    def test_catalog_pairing_marked_curated(self) -> None:
        pairing = {
            "notes": {"en": "curated"},
            "flavorTags": ["cedar"],
            "profileEstimated": True,
            "priceUrl": "https://humidor.hr/hr/proizvod/x/",
        }
        sources, urls, verified = build_sources(
            offers=[],
            pairing=pairing,
            catalog_id="x",
            in_catalog=True,
        )
        self.assertTrue(verified)
        self.assertEqual(urls, ["https://humidor.hr/hr/proizvod/x/"])
        catalog_src = next(s for s in sources if s["type"] == "app-catalog")
        self.assertTrue(catalog_src["profileEstimated"])
        self.assertIn("Curated", catalog_src["note"])

    def test_offer_from_raw_keeps_details_source(self) -> None:
        row = {
            "sourceShopId": "havana_hr",
            "region": "HR",
            "scrapedAt": "2026-07-21T00:00:00Z",
            "item": {
                "name": "Oscar Toro",
                "url": "https://havana-cigar-shop.com/proizvod/oscar/",
                "price": {"amount": 10.0, "currency": "EUR"},
                "availability": {"inStock": True},
                "details": {"wrapper": "Habano"},
                "detailsSource": {
                    "url": "https://havana-cigar-shop.com/proizvod/oscar/",
                    "extractedFrom": "woocommerce-store-api-attributes",
                    "extractedAt": "2026-07-21T00:00:00Z",
                },
                "images": [],
                "categories": [],
                "attributes": {},
                "packaging": {},
            },
        }
        offer = offer_from_raw(row)
        self.assertEqual(offer["detailsSource"]["extractedFrom"], "woocommerce-store-api-attributes")
        self.assertEqual(offer["url"], "https://havana-cigar-shop.com/proizvod/oscar/")


if __name__ == "__main__":
    unittest.main()
