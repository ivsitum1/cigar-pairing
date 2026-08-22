# -*- coding: utf-8 -*-
"""Schema tests for curated YouTube cigar enrichments (no network)."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
CIGAR_ENRICH = HERE / "data" / "youtube" / "cigar_enrichments.json"
CIGARS = HERE.parent / "src" / "data" / "cigars.json"


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
