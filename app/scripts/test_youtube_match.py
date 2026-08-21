# -*- coding: utf-8 -*-
"""Unit tests for youtube_match_lib (no network)."""
from __future__ import annotations

import unittest

from youtube_match_lib import drink_match_keys, match_video_to_rums


class MatchLibTests(unittest.TestCase):
    def test_drink_keys_prefer_name(self) -> None:
        keys = drink_match_keys({"id": "rum-appleton-12", "name": "Appleton Estate 12 Year Old"})
        self.assertTrue(any("appleton" in k for k in keys))

    def test_match_in_title(self) -> None:
        rums = [
            {"id": "rum-foursquare-sovereignty", "name": "Foursquare Sovereignty"},
            {"id": "rum-havana-club-7", "name": "Havana Club 7"},
        ]
        video = {
            "videoId": "abc123",
            "title": "Foursquare Sovereignty tasting notes",
            "url": "https://www.youtube.com/watch?v=abc123",
            "text": "A dry Barbados rum.",
        }
        props = match_video_to_rums(video=video, rums=rums, min_confidence=0.65)
        ids = {p["drinkId"] for p in props}
        self.assertIn("rum-foursquare-sovereignty", ids)
        self.assertNotIn("rum-havana-club-7", ids)
        hit = next(p for p in props if p["drinkId"] == "rum-foursquare-sovereignty")
        self.assertGreaterEqual(hit["confidence"], 0.75)

    def test_no_false_match_on_generic_rum(self) -> None:
        rums = [{"id": "rum-obscure-unicorn", "name": "Obscure Unicorn Reserve"}]
        video = {
            "videoId": "xyz",
            "title": "Why most rum is garbage",
            "url": "https://www.youtube.com/watch?v=xyz",
            "text": "Industrial rum factories add sugar.",
        }
        props = match_video_to_rums(video=video, rums=rums, min_confidence=0.65)
        self.assertEqual(props, [])


if __name__ == "__main__":
    unittest.main()
