# -*- coding: utf-8 -*-
"""Unit tests for youtube_match_cigar_lib (no network)."""
from __future__ import annotations

import unittest

from youtube_match_cigar_lib import cigar_match_keys, match_video_to_cigars


class MatchCigarLibTests(unittest.TestCase):
    def test_cigar_keys_brand_line(self) -> None:
        keys = cigar_match_keys(
            {"id": "cig-padron-1964", "brand": "Padron", "line": "1964 Anniversary"}
        )
        self.assertTrue(any("padron" in k and "1964" in k for k in keys))

    def test_match_in_title(self) -> None:
        cigars = [
            {"id": "cig-oliva-serie-v", "brand": "Oliva", "line": "Serie V"},
            {"id": "cig-padron-1964", "brand": "Padron", "line": "1964 Anniversary"},
        ]
        video = {
            "videoId": "abc123",
            "title": "Oliva Serie V Melanio review — full tasting",
            "url": "https://www.youtube.com/watch?v=abc123",
            "text": "Medium-full Nicaraguan puro.",
        }
        props = match_video_to_cigars(video=video, cigars=cigars, min_confidence=0.65)
        ids = {p["cigarId"] for p in props}
        self.assertIn("cig-oliva-serie-v", ids)
        self.assertNotIn("cig-padron-1964", ids)

    def test_no_false_match_on_generic_cigar(self) -> None:
        cigars = [{"id": "cig-obscure-unicorn", "brand": "Obscure", "line": "Unicorn Reserve"}]
        video = {
            "videoId": "xyz",
            "title": "Why most cigars are overpriced",
            "url": "https://www.youtube.com/watch?v=xyz",
            "text": "Generic cigar lounge talk.",
        }
        props = match_video_to_cigars(video=video, cigars=cigars, min_confidence=0.65)
        self.assertEqual(props, [])


if __name__ == "__main__":
    unittest.main()
