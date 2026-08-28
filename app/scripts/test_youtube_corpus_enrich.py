# -*- coding: utf-8 -*-
"""Offline tests for YouTube corpus drink enrichment."""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent


def _load(name: str, file: str):
    scripts = str(HERE)
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


class CorpusEnrichLibTests(unittest.TestCase):
    def test_draft_notes_from_tags(self) -> None:
        yce = _load("youtube_corpus_enrich_lib", "youtube_corpus_enrich_lib.py")
        drink = {
            "id": "rum-foursquare-sovereignty",
            "name": "Foursquare Sovereignty",
            "region": "Barbados",
            "body": 4,
            "sweetness": 2,
        }
        notes = yce.draft_notes_from_material(
            drink,
            "rum",
            tags=["hrast", "karamela", "suho-voce"],
            body=4,
            sweet=2,
        )
        self.assertIn("Foursquare", notes["hr"])
        self.assertIn("hrast", notes["hr"].lower())
        self.assertTrue(yce.hr_notes_ok(notes))

    def test_material_ok_requires_tags_or_review(self) -> None:
        yce = _load("youtube_corpus_enrich_lib", "youtube_corpus_enrich_lib.py")
        blob = (
            "On the nose there is vanilla, caramel and dried fruit with medium body. "
            "The palate shows oak and molasses with a long finish on Foursquare Sovereignty."
        )
        self.assertTrue(
            yce._material_ok(
                "Foursquare Sovereignty review and tasting",
                blob,
                ["hrast", "karamela", "suho-voce"],
                matched_key="foursquare sovereignty",
            )
        )
        self.assertFalse(
            yce._material_ok(
                "Random rum chat",
                "short",
                ["hrast"],
                matched_key="foursquare sovereignty",
            )
        )

    def test_title_specific_rejects_sibling(self) -> None:
        yce = _load("youtube_corpus_enrich_lib", "youtube_corpus_enrich_lib.py")
        drink = {"name": "Hampden Estate 8 YO"}
        self.assertFalse(yce.title_specific_enough(drink, "Hampden Estate Great House 2022 review"))
        self.assertTrue(yce.title_specific_enough(drink, "Hampden Estate 8 year rum tasting"))

    def test_find_match_with_fixture_corpus(self) -> None:
        yce = _load("youtube_corpus_enrich_lib", "youtube_corpus_enrich_lib.py")
        drink = {
            "id": "rum-foursquare-sovereignty",
            "name": "Foursquare Sovereignty",
            "region": "Barbados",
            "body": 3,
            "sweetness": 2,
            "additiveStatus": "none",
        }
        corpus = {
            "entries": [
                {
                    "videoId": "vid123",
                    "channelId": "testch",
                    "title": "Foursquare Sovereignty rum review and tasting",
                    "primaryDomain": "rum",
                    "domains": ["rum"],
                    "researchExcerpt": "vanilla caramel oak",
                }
            ]
        }
        transcript = (
            "Welcome to the rum review. Today we taste Foursquare Sovereignty. "
            "On the nose vanilla, caramel and dried fruit. Medium full body with oak, "
            "molasses and a long Barbados finish. Pairs well with a cigar if you keep sips slow."
        )

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            bundle = out / "corpus_knowledge_by_topic.json"
            bundle.write_text(json.dumps(corpus), encoding="utf-8")
            vdir = out / "testch" / "videos"
            vdir.mkdir(parents=True)
            (vdir / "vid123.json").write_text(
                json.dumps(
                    {
                        "videoId": "vid123",
                        "channelId": "testch",
                        "captionStatus": "ok",
                        "text": transcript,
                    }
                ),
                encoding="utf-8",
            )

            with mock.patch.object(yce, "CORPUS_BUNDLE", bundle), mock.patch.object(
                yce, "OUTPUT_ROOT", out
            ), mock.patch("youtube_corpus_enrich_lib.OUTPUT_ROOT", out), mock.patch(
                "youtube_common.OUTPUT_ROOT", out
            ):
                yce.load_corpus_entries.cache_clear()
                hit = yce.find_corpus_match(drink, "rum")

        self.assertIsNotNone(hit)
        assert hit is not None
        self.assertEqual(hit["sourceVideoIds"], ["vid123"])
        self.assertIn("Foursquare", hit["notes"]["hr"])
        self.assertTrue(yce.hr_notes_ok(hit["notes"]))
        self.assertTrue(yce.hr_notes_ok(hit["cigarHint"]))


class EnrichStubCorpusFallback(unittest.TestCase):
    def test_heuristic_when_no_corpus(self) -> None:
        enr = _load("enrich_shop", "enrich-shop-ingest-stubs.py")
        stub = {
            "id": "rum-no-corpus-xyz",
            "name": "Totally Obscure Unicorn Reserve 99 YO",
            "style": "other",
            "region": "Nepoznato",
            "body": 3,
            "sweetness": 2,
            "flavorTags": ["hrast"],
            "priceEUR": {"min": 999, "max": 999},
            "pairable": False,
            "shopIngest": True,
            "notes": {"hr": "Automatski unos", "en": "Auto"},
        }
        profile = {
            "style": "aged",
            "region": "Barbados",
            "body": 3,
            "sweetness": 2,
            "flavorTags": ["hrast"],
            "additiveStatus": "none",
            "qualityScore": 3,
            "serving": "neat",
            "pairable": False,
            "profileEstimated": True,
        }
        with mock.patch.dict(enr.PROFILE_FN, {"rum": lambda drink: profile}), mock.patch(
            "youtube_corpus_enrich_lib.try_corpus_enrich",
            return_value=None,
        ):
            d = dict(stub)
            enr.enrich_drink("rum", d, prefer_corpus=True)
        self.assertNotIn("Automatski unos", (d.get("notes") or {}).get("hr", ""))


class LocaleAndLengthGates(unittest.TestCase):
    """Locale + length gates so --apply cannot re-break integrity/curated tests."""

    def test_draft_cigar_notes_en_uses_nicaragua_not_nikaragva(self) -> None:
        stub = _load("youtube_curate_stub", "youtube-curate-stub-enrichments.py")
        notes = stub.draft_cigar_notes(
            {
                "country": "Nikaragva",
                "strength": 2,
                "wrapper": "corojo",
            },
            "1502",
            "Emerald",
        )
        self.assertIn("Nicaragua", notes["en"])
        self.assertNotIn("Nikaragva", notes["en"])
        self.assertIn("Nikaragva", notes["hr"])

    def test_tequila_blanco_hint_both_locales_at_least_80(self) -> None:
        yce = _load("youtube_corpus_enrich_lib", "youtube_corpus_enrich_lib.py")
        hint = yce._hint_from_blob(
            "tequila",
            {"name": "Don Julio Blanco", "style": "blanco"},
            "",
            [],
        )
        self.assertGreaterEqual(len(hint["hr"]), 80, hint["hr"])
        self.assertGreaterEqual(len(hint["en"]), 80, hint["en"])

    def test_tags_phrase_en_karamela_is_english(self) -> None:
        yce = _load("youtube_corpus_enrich_lib", "youtube_corpus_enrich_lib.py")
        phrase = yce.tags_phrase_en(["karamela"])
        self.assertEqual(phrase, "caramel")
        self.assertNotEqual(phrase, "karamela")

    def test_en_notes_ok_rejects_nikaragva(self) -> None:
        yce = _load("youtube_corpus_enrich_lib", "youtube_corpus_enrich_lib.py")
        self.assertFalse(yce.en_notes_ok({"hr": "x" * 80, "en": "from Nikaragva with cedar"}))
        self.assertTrue(
            yce.en_notes_ok(
                {
                    "hr": "x" * 80,
                    "en": "from Nicaragua with cedar and a calm rhythm beside the glass.",
                }
            )
        )


if __name__ == "__main__":
    unittest.main()
