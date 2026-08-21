# -*- coding: utf-8 -*-
"""Unit tests for youtube_classify_lib (no network)."""
from __future__ import annotations

import unittest

from youtube_classify_lib import (
    TAG_BAR_TECHNIQUE,
    TAG_COCKTAIL,
    TAG_RUM,
    TAG_SKIP,
    TAG_WHISKY,
    classify_video,
    summarize_tags,
)


class ClassifyVideoTests(unittest.TestCase):
    def test_rum_title(self) -> None:
        tags = classify_video("Doorly's Rum Guide & Tasting", "")
        self.assertIn(TAG_RUM, tags)

    def test_cocktail_recipe(self) -> None:
        tags = classify_video("How to make a Daiquiri cocktail", "")
        self.assertIn(TAG_COCKTAIL, tags)

    def test_whisky(self) -> None:
        tags = classify_video("Best peated Scotch whisky under £40", "")
        self.assertIn(TAG_WHISKY, tags)

    def test_rum_in_caption_body(self) -> None:
        tags = classify_video("Weekly pours", "Today we open a Jamaican rum from...")
        self.assertIn(TAG_RUM, tags)

    def test_technique(self) -> None:
        tags = classify_video("Stop drinking rum wrong — glassware tips", "Use a Glencairn")
        self.assertIn(TAG_BAR_TECHNIQUE, tags)
        self.assertIn(TAG_RUM, tags)

    def test_unknown_becomes_skip(self) -> None:
        tags = classify_video("Hello from the pub garden", "nice weather today")
        self.assertEqual(tags, [TAG_SKIP])

    def test_summarize(self) -> None:
        counts = summarize_tags([[TAG_RUM], [TAG_RUM, TAG_COCKTAIL], [TAG_SKIP]])
        self.assertEqual(counts[TAG_RUM], 2)
        self.assertEqual(counts[TAG_COCKTAIL], 1)
        self.assertEqual(counts[TAG_SKIP], 1)


if __name__ == "__main__":
    unittest.main()
