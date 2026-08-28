# -*- coding: utf-8 -*-
"""Unit tests for ingest-staged-drink-shops helpers (offline)."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "ingest",
    Path(__file__).resolve().parent / "ingest-staged-drink-shops.py",
)
ing = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(ing)


class IngestHelpers(unittest.TestCase):
    def test_mint_id_unique(self) -> None:
        existing = {"rum-hampden-8"}
        a = ing.mint_id("rum", "Hampden Estate 8 YO", existing)
        existing.add(a)
        b = ing.mint_id("rum", "Hampden Estate 8 YO", existing)
        self.assertNotEqual(a, b)
        self.assertTrue(a.startswith("rum-"))

    def test_stub_fields_and_auto_enrich(self) -> None:
        stub = ing.build_stub(
            {
                "name": "Test Rum 40% Vol. 0,7l u poklon kutiji",
                "url": "https://allez.hr/shop/x",
                "price_eur": 55.0,
                "shopLabel": "allez.hr",
                "suggestedCategory": "rum",
            },
            "rum-test-stub",
        )
        self.assertEqual(stub["shopHR"], "allez.hr")
        self.assertEqual(stub["priceUrl"], "https://allez.hr/shop/x")
        self.assertTrue(stub.get("shopIngest"))
        self.assertTrue(stub.get("shopIngestEnriched"))
        self.assertNotIn("poklon kutiji", stub["name"].lower())
        notes = stub.get("notes") or {}
        self.assertNotIn("Automatski unos", (notes.get("hr") or ""))

    def test_mini_re(self) -> None:
        self.assertTrue(ing.MINI_RE.search("Sample set 50 ml"))


if __name__ == "__main__":
    unittest.main()
