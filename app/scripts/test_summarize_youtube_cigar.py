# -*- coding: utf-8 -*-
"""Unit tests for summarize-youtube-cigar-proposals (offline)."""
from __future__ import annotations

import unittest

from summarize_youtube_cigar_lib import build_queue


class SummarizeCigarProposalsTests(unittest.TestCase):
    def test_build_queue_prefers_stubs(self) -> None:
        proposals = {
            "cig-a": {
                "cigarId": "cig-a",
                "matchedKey": "oliva serie v",
                "confidence": 0.9,
                "inTitle": True,
                "channelId": "test",
                "videoId": "v1",
                "url": "https://youtu.be/v1",
                "title": "Oliva Serie V review",
                "snippet": "medium body",
            }
        }
        cigars = {
            "cig-a": {
                "id": "cig-a",
                "brand": "Oliva",
                "line": "Serie V",
                "notes": {"en": "Short.", "hr": "Kratko."},
            }
        }
        queue = build_queue(proposals, cigars, stub_en_max=80, prefer_stubs=True)
        self.assertEqual(len(queue), 1)
        self.assertTrue(queue[0]["isStubNote"])


if __name__ == "__main__":
    unittest.main()
