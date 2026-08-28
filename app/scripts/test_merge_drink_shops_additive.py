# -*- coding: utf-8 -*-
"""Unit tests for merge-drink-shops-additive / propose_update guards."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent

_SPEC = importlib.util.spec_from_file_location("mdl", HERE / "match-drink-listings.py")
mdl = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(mdl)

_SPEC2 = importlib.util.spec_from_file_location("merge", HERE / "merge-drink-shops-additive.py")
merge = importlib.util.module_from_spec(_SPEC2)
assert _SPEC2.loader is not None
_SPEC2.loader.exec_module(merge)


class ProposeUpdateGuards(unittest.TestCase):
    def test_weak_url_gets_listing(self) -> None:
        drink = {
            "id": "rum-x",
            "priceUrl": None,
            "shopHR": None,
            "priceEUR": {"min": 10, "max": 10},
        }
        listing = {
            "url": "https://tipsy.hr/proizvod/foo",
            "price_eur": 42.5,
            "shop": "tipsy",
            "shopLabel": "tipsy.hr",
        }
        after = mdl.propose_update(drink, listing, score=0.95)
        self.assertIsNotNone(after)
        assert after is not None
        self.assertEqual(after["priceUrl"], listing["url"])
        self.assertEqual(after["priceEUR"]["min"], 42.5)
        self.assertEqual(after["shopHR"], "tipsy.hr")

    def test_allez_lock_blocks_tipsy_replace(self) -> None:
        drink = {
            "id": "rum-x",
            "priceUrl": "https://allez.hr/shop/svi-proizvodi/foo",
            "shopHR": "allez.hr",
            "priceEUR": {"min": 50, "max": 50},
        }
        listing = {
            "url": "https://tipsy.hr/proizvod/foo",
            "price_eur": 40,
            "shop": "tipsy",
            "shopLabel": "tipsy.hr",
        }
        after = mdl.propose_update(drink, listing, score=0.99)
        self.assertIsNone(after)

    def test_idempotent_same_url_price(self) -> None:
        url = "https://tipsy.hr/proizvod/foo"
        drink = {
            "id": "rum-x",
            "priceUrl": url,
            "shopHR": "tipsy.hr",
            "priceEUR": {"min": 40, "max": 40},
        }
        listing = {
            "url": url,
            "price_eur": 40,
            "shop": "tipsy",
            "shopLabel": "tipsy.hr",
        }
        after = mdl.propose_update(drink, listing, score=0.95)
        self.assertIsNone(after)

    def test_humidor_does_not_overwrite_strong_url(self) -> None:
        drink = {
            "id": "rum-x",
            "priceUrl": "https://tipsy.hr/proizvod/foo",
            "shopHR": "tipsy.hr",
            "priceEUR": {"min": 40, "max": 40},
        }
        listing = {
            "url": "https://humidor.hr/hr/proizvod/bar",
            "price_eur": 41,
            "shop": "humidor",
            "shopLabel": "humidor.hr",
        }
        after = mdl.propose_update(drink, listing, score=0.95)
        self.assertIsNone(after)

    def test_build_updates_holds_unknown_id(self) -> None:
        updates, held = merge.build_updates(
            [
                {
                    "matchId": "rum-does-not-exist",
                    "url": "https://tipsy.hr/x",
                    "price_eur": 10,
                    "shop": "tipsy",
                    "shopLabel": "tipsy.hr",
                    "bestScore": 0.95,
                    "tier": "B",
                }
            ],
            {},
        )
        self.assertEqual(updates, [])
        self.assertEqual(len(held), 1)

    def test_tier_a_does_not_promote_sourceurl_sibling(self) -> None:
        drink = {
            "id": "rum-x",
            "priceUrl": "https://allez.hr/shop/svi-proizvodi/correct",
            "shopHR": "allez.hr",
            "priceEUR": {"min": 50, "max": 50},
        }
        updates, held = merge.build_updates(
            [
                {
                    "matchId": "rum-x",
                    "url": "https://allez.hr/shop/svi-proizvodi/sibling",
                    "price_eur": 55,
                    "shop": "allez",
                    "shopLabel": "allez.hr",
                    "bestScore": 1.0,
                    "tier": "A",
                }
            ],
            {"rum-x": ("rums.json", drink)},
        )
        self.assertEqual(updates, [])
        self.assertTrue(any("not auto-promoted" in (h.get("holdReason") or "") for h in held))


class ScrapeMivaNoWine(unittest.TestCase):
    def test_miva_categories_exclude_vina(self) -> None:
        sdl_spec = importlib.util.spec_from_file_location(
            "sdl", HERE / "scrape-drink-shop-listings.py"
        )
        sdl = importlib.util.module_from_spec(sdl_spec)
        assert sdl_spec.loader is not None
        # Avoid running network — only load constants by reading source
        text = (HERE / "scrape-drink-shop-listings.py").read_text(encoding="utf-8")
        self.assertIn("zestoka-pica", text)
        self.assertNotIn("miva.com.hr/vina", text)


if __name__ == "__main__":
    unittest.main()
