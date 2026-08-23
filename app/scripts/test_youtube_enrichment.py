# -*- coding: utf-8 -*-
"""Schema tests for curated YouTube rum/cigar/drink enrichments (no network)."""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUM_ENRICH = HERE / "data" / "youtube" / "rum_enrichments.json"
CIGAR_ENRICH = HERE / "data" / "youtube" / "cigar_enrichments.json"
WHISKY_ENRICH = HERE / "data" / "youtube" / "whisky_enrichments.json"
GIN_ENRICH = HERE / "data" / "youtube" / "gin_enrichments.json"
TEQUILA_ENRICH = HERE / "data" / "youtube" / "tequila_enrichments.json"
RUMS = HERE.parent / "src" / "data" / "rums.json"
CIGARS = HERE.parent / "src" / "data" / "cigars.json"
WHISKIES = HERE.parent / "src" / "data" / "whiskies.json"
GINS = HERE.parent / "src" / "data" / "gins.json"
TEQUILAS = HERE.parent / "src" / "data" / "tequilas.json"


def _assert_lang_block(test: unittest.TestCase, block: dict, drink_id: str) -> None:
    test.assertIn("hr", block)
    test.assertIn("en", block)
    test.assertGreaterEqual(len(block["hr"]), 40, drink_id)
    test.assertGreaterEqual(len(block["en"]), 40, drink_id)
    hr = block["hr"].lower()
    test.assertNotRegex(hr, r"\bwrapper\b", drink_id)
    test.assertNotRegex(hr, r"\bcigar\b", drink_id)
    test.assertNotIn("heuristika", hr, drink_id)


class YoutubeRumEnrichmentTests(unittest.TestCase):
    def test_enrichments_schema(self):
        payload = json.loads(RUM_ENRICH.read_text(encoding="utf-8"))
        self.assertIn("enrichments", payload)
        for drink_id, entry in payload["enrichments"].items():
            self.assertTrue(drink_id.startswith("rum-"), drink_id)
            for key in ("notes", "cigarHint"):
                if key not in entry:
                    continue
                _assert_lang_block(self, entry[key], drink_id)

            forbidden = set(entry) - {
                "notes",
                "cigarHint",
                "sourceVideoIds",
            }
            self.assertFalse(forbidden, f"{drink_id} has forbidden keys: {forbidden}")

    def test_enrichment_ids_exist_in_catalog(self):
        payload = json.loads(RUM_ENRICH.read_text(encoding="utf-8"))
        rums = json.loads(RUMS.read_text(encoding="utf-8"))
        ids = {r["id"] for r in rums}
        for drink_id in payload["enrichments"]:
            self.assertIn(drink_id, ids, drink_id)

    def test_no_generic_cigar_hints_in_enrichments(self):
        payload = json.loads(RUM_ENRICH.read_text(encoding="utf-8"))
        for drink_id, entry in payload["enrichments"].items():
            hint = entry.get("cigarHint")
            if not hint:
                continue
            self.assertNotIn(
                "biraj cigaru prema tijelu",
                hint.get("hr", "").lower(),
                drink_id,
            )


class YoutubeSpiritEnrichmentTests(unittest.TestCase):
    def test_whisky_gin_tequila_schema_and_ids(self):
        cases = [
            (WHISKY_ENRICH, WHISKIES, "wh-"),
            (GIN_ENRICH, GINS, "gin-"),
            (TEQUILA_ENRICH, TEQUILAS, "tq-"),
        ]
        for enrich_path, catalog_path, prefix in cases:
            self.assertTrue(enrich_path.is_file(), enrich_path.name)
            payload = json.loads(enrich_path.read_text(encoding="utf-8"))
            ids = {r["id"] for r in json.loads(catalog_path.read_text(encoding="utf-8"))}
            for drink_id, entry in payload["enrichments"].items():
                self.assertTrue(drink_id.startswith(prefix), drink_id)
                self.assertIn(drink_id, ids, drink_id)
                for key in ("notes", "cigarHint"):
                    self.assertIn(key, entry, drink_id)
                    _assert_lang_block(self, entry[key], drink_id)


class CatalogBottleSentenceTests(unittest.TestCase):
    """Every bottle in the offer must have a sayable HR sentence + cigarHint."""

    def test_spirits_have_notes_and_hints(self):
        for path in (RUMS, WHISKIES, GINS, TEQUILAS):
            rows = json.loads(path.read_text(encoding="utf-8"))
            for r in rows:
                notes = r.get("notes") or {}
                hint = r.get("cigarHint") or {}
                hr = (notes.get("hr") if isinstance(notes, dict) else "") or ""
                hhr = (hint.get("hr") if isinstance(hint, dict) else "") or ""
                self.assertGreaterEqual(len(hr), 40, r["id"])
                self.assertGreaterEqual(len(hhr), 40, r["id"])
                self.assertNotIn("Heuristika", hr, r["id"])
                self.assertIsNone(re.search(r"\bcigar\b", hr, re.I), r["id"])


class YoutubeCigarEnrichmentTests(unittest.TestCase):
    def test_cigar_enrichments_schema(self):
        payload = json.loads(CIGAR_ENRICH.read_text(encoding="utf-8"))
        self.assertIn("enrichments", payload)
        for cigar_id, entry in payload["enrichments"].items():
            self.assertTrue(cigar_id.startswith("cig-"), cigar_id)
            notes = entry.get("notes")
            self.assertIsInstance(notes, dict, cigar_id)
            self.assertIn("hr", notes)
            self.assertIn("en", notes)
            self.assertGreaterEqual(len(notes["hr"]), 40, cigar_id)
            self.assertGreaterEqual(len(notes["en"]), 40, cigar_id)
            forbidden = set(entry) - {"notes", "sourceVideoIds"}
            self.assertFalse(forbidden, f"{cigar_id} has forbidden keys: {forbidden}")
            hr = notes["hr"].lower()
            self.assertNotIn(" short filler", hr, cigar_id)
            self.assertNotRegex(hr, r"\bwrapper\b", cigar_id)
            self.assertNotRegex(hr, r"\bcigar\b", cigar_id)

    def test_cigar_enrichment_ids_exist_in_catalog(self):
        payload = json.loads(CIGAR_ENRICH.read_text(encoding="utf-8"))
        cigars = json.loads(CIGARS.read_text(encoding="utf-8"))
        ids = {c["id"] for c in cigars}
        for cigar_id in payload["enrichments"]:
            self.assertIn(cigar_id, ids, cigar_id)


if __name__ == "__main__":
    unittest.main()
