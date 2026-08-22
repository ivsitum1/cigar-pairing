# -*- coding: utf-8 -*-
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENRICH = HERE / "data" / "youtube" / "rum_enrichments.json"
RUMS = HERE.parent / "src" / "data" / "rums.json"


class YoutubeEnrichmentTests(unittest.TestCase):
    def test_enrichments_schema(self):
        payload = json.loads(ENRICH.read_text(encoding="utf-8"))
        self.assertIn("enrichments", payload)
        for drink_id, entry in payload["enrichments"].items():
            self.assertTrue(drink_id.startswith("rum-"), drink_id)
            for key in ("notes", "cigarHint"):
                if key not in entry:
                    continue
                block = entry[key]
                self.assertIn("hr", block)
                self.assertIn("en", block)
                self.assertGreaterEqual(len(block["hr"]), 40, drink_id)
                self.assertGreaterEqual(len(block["en"]), 40, drink_id)
            forbidden = set(entry) - {
                "notes",
                "cigarHint",
                "sourceVideoIds",
            }
            self.assertFalse(forbidden, f"{drink_id} has forbidden keys: {forbidden}")

    def test_enrichment_ids_exist_in_catalog(self):
        payload = json.loads(ENRICH.read_text(encoding="utf-8"))
        rums = json.loads(RUMS.read_text(encoding="utf-8"))
        ids = {r["id"] for r in rums}
        for drink_id in payload["enrichments"]:
            self.assertIn(drink_id, ids, drink_id)

    def test_no_generic_cigar_hints_in_enrichments(self):
        payload = json.loads(ENRICH.read_text(encoding="utf-8"))
        for drink_id, entry in payload["enrichments"].items():
            hint = entry.get("cigarHint")
            if not hint:
                continue
            self.assertNotIn(
                "biraj cigaru prema tijelu",
                hint.get("hr", "").lower(),
                drink_id,
            )


if __name__ == "__main__":
    unittest.main()
