# -*- coding: utf-8 -*-
"""Offline tests for shop-ingest profile enrichment."""
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


class RumShared(unittest.TestCase):
    def test_hampden_jamaica(self) -> None:
        rs = _load("rum_shared", "rum_shared.py")
        style, region, body, sweet, tags = rs.detect_style_region(
            "Hampden Estate 8 YO Pure Single Jamaican Rum 46%"
        )
        self.assertEqual(style, "jamaica")
        self.assertIn("Jamajka", region)
        self.assertIn("ester-funk", tags)


class EnrichStub(unittest.TestCase):
    def test_notes_name_specific_not_generic(self) -> None:
        enr = _load("enrich_shop", "enrich-shop-ingest-stubs.py")
        stub = {
            "id": "rum-hampden-test-enrich",
            "category": "rum",
            "name": "Hampden Estate 8 YO",
            "style": "other",
            "region": "Nepoznato",
            "body": 3,
            "sweetness": 2,
            "flavorTags": ["hrast"],
            "priceEUR": {"min": 75, "max": 75},
            "pairable": False,
            "shopIngest": True,
            "notes": {
                "hr": "Automatski unos iz HR shopa (rum). Profil i pairable treba potvrditi ručno za X.",
                "en": "Auto-ingested",
            },
        }
        out = enr.enrich_stub_fields("rum", stub)
        hr = (out.get("notes") or {}).get("hr") or ""
        self.assertNotIn("Automatski unos", hr)
        self.assertIn("Hampden", hr)
        self.assertEqual(out.get("style"), "jamaica")
        self.assertTrue(out.get("pairable"))
        self.assertTrue(out.get("cigarHint", {}).get("hr"))


if __name__ == "__main__":
    unittest.main()
