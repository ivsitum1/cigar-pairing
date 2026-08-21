#!/usr/bin/env python3
"""Unit tests for Neptune profile merge overwrite rules and worklist selection."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


merge = _load("merge_neptune_profiles", "merge-neptune-profiles.py")
worklist = _load("build_neptune_worklist", "build-neptune-worklist.py")


class MergeOverwriteTests(unittest.TestCase):
    def test_estimated_tags_yield_to_shop_description(self):
        cigar = {
            "id": "cig-x",
            "flavorTags": ["cedar", "kava", "koza", "zacini"],
            "profileEstimated": True,
            "wrapper": "—",
            "strength": 3,
            "body": 3,
        }
        raw = {
            "description": (
                "A medium-bodied smoke with notes of dark chocolate, "
                "black pepper, and earthy oak."
            ),
            "strength": 3,
            "wrapper": "Ecuadorian Habano",
        }
        changed = merge.merge_one(cigar, raw)
        self.assertTrue(changed)
        self.assertNotEqual(
            tuple(sorted(cigar["flavorTags"])),
            ("cedar", "kava", "koza", "zacini"),
        )
        self.assertGreaterEqual(len(cigar["flavorTags"]), 2)
        self.assertFalse(cigar.get("profileEstimated"))

    def test_curated_non_estimated_tags_preserved(self):
        cigar = {
            "id": "cig-y",
            "flavorTags": ["kakao", "kremasto"],
            "profileEstimated": False,
            "wrapper": "Maduro",
            "strength": 4,
            "body": 4,
        }
        raw = {
            "description": "Full of coffee, leather, spice and cedar notes.",
            "strength": 5,
            "wrapper": "Connecticut",
        }
        merge.merge_one(cigar, raw)
        self.assertEqual(cigar["flavorTags"], ["kakao", "kremasto"])
        self.assertEqual(cigar["wrapper"], "Maduro")
        self.assertFalse(cigar.get("profileEstimated"))

    def test_market_stays_estimated_after_shop_tags(self):
        cigar = {
            "id": "cig-z",
            "flavorTags": ["cedar", "kava", "koza", "zacini"],
            "profileEstimated": True,
            "catalogSource": "market",
            "wrapper": "—",
        }
        raw = {
            "description": "Medium strength with sweet cream and honey notes.",
        }
        merge.merge_one(cigar, raw)
        self.assertTrue(cigar.get("profileEstimated"))
        self.assertGreaterEqual(len(cigar.get("flavorTags") or []), 2)

    def test_mild_house_strength_not_raised_by_shop(self):
        cigar = {
            "id": "cig-macanudo-cafe",
            "brand": "Macanudo",
            "flavorTags": ["kremasto", "cedar", "orasasti", "med", "trava-slatka"],
            "profileEstimated": True,
            "wrapper": "Connecticut shade",
            "strength": 1,
            "body": 1,
        }
        raw = {
            "description": "A medium-bodied Connecticut shade cigar with cream notes.",
            "strength": 3,
            "wrapper": "Connecticut",
        }
        merge.merge_one(cigar, raw)
        self.assertEqual(cigar["strength"], 1)
        self.assertEqual(cigar["body"], 1)
        self.assertNotEqual(cigar.get("strengthFromShop"), True)

    def test_neptune_description_fills_generated_notes(self):
        cigar = {
            "id": "cig-notes",
            "flavorTags": ["cedar"],
            "profileEstimated": True,
            "wrapper": "Habano",
            "notes": {
                "hr": "Nikaragva, Habano pokrov — jače snage, punijeg tijela. Okusi: cedrovina.",
                "en": "Habano wrapper (Nicaragua); fuller and expressive. Notes of cedar.",
            },
        }
        raw = {
            "description": (
                "A small-batch Nicaraguan blend with dark chocolate, black pepper, "
                "and cedar on a long finish. Handmade in Esteli."
            ),
        }
        self.assertTrue(merge.merge_one(cigar, raw))
        self.assertGreaterEqual(len(cigar["notes"]["en"]), 80)
        self.assertIn("dark chocolate", cigar["notes"]["en"])
        self.assertEqual(cigar["notes"]["hr"], "")
        self.assertFalse(cigar.get("profileEstimated"))

    def test_curated_notes_not_overwritten(self):
        cigar = {
            "id": "cig-curated-notes",
            "flavorTags": ["kakao"],
            "profileEstimated": False,
            "wrapper": "Maduro",
            "notes": {
                "hr": "Tamna, mirisna linija s kakaoom i suhim voćem; večernja, bez žurbe.",
                "en": "A dark, fragrant line with cocoa and dried fruit; evening pace.",
            },
        }
        raw = {
            "description": "Shop text about coffee leather spice cedar that should not win.",
        }
        merge.merge_one(cigar, raw)
        self.assertIn("kakaoom", cigar["notes"]["hr"])
        self.assertIn("evening pace", cigar["notes"]["en"])


class WorklistSelectionTests(unittest.TestCase):
    def test_includes_estimated_with_neptune_url(self):
        cigars = [
            {
                "id": "cig-a",
                "brand": "A",
                "line": "Line",
                "flavorTags": ["cedar", "kava"],
                "profileEstimated": True,
                "vitolas": [
                    {"name": "Robusto", "url": "https://www.neptunecigar.com/cigars/a"}
                ],
            },
            {
                "id": "cig-b",
                "brand": "B",
                "line": "Curated",
                "flavorTags": ["kakao"],
                "profileEstimated": False,
                "vitolas": [
                    {"name": "Toro", "url": "https://www.neptunecigar.com/cigars/b"}
                ],
            },
            {
                "id": "cig-c",
                "brand": "C",
                "line": "Bare",
                "flavorTags": [],
                "vitolas": [
                    {"name": "Gordo", "url": "https://www.neptunecigar.com/cigars/c"}
                ],
            },
        ]
        items = worklist.build(cigars)
        ids = {i["id"] for i in items}
        self.assertIn("cig-a", ids)
        self.assertIn("cig-c", ids)
        self.assertNotIn("cig-b", ids)


if __name__ == "__main__":
    unittest.main()
